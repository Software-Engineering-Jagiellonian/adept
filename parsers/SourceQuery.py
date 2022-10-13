#!/usr/bin/python

# Program przepytuje zrodla - Jira i SVN - i dla kazdego projektu
# z Sonara szuka najlepiej pasujacych nazw projektow z Jira i SVN
# Wynik jest zapisywany w tabeli SonarDictionary

# Jira jest przepytywana przez API, SVN jest odczytywane z tabeli Sources_SVN

import MySQLdb
import requests
import json
import ApiTools
import urllib2
from difflib import SequenceMatcher as SeqMat
import urllib2
from bs4 import BeautifulSoup
import time

print ("Connecting to database..."),
db = MySQLdb.connect(" "," "," "," " )
cursor = db.cursor()
print ("OK")

urlJira = " "
urlSVN = " "
SimilarRatio = 0.85 # prog akceptowania predykcji automatycznej dla projektu
FoundJIRA = ""
FoundSVN = ""
JiraRatioMax = 0
SVNRatioMax = 0
ProjektSVNNameMax = ""
ProjektJiraNameMax = ""
ProjektSVNURLMax = ""


try:

    print ("Dumping JSON from JIRA...")
    print "URL: %s" % (urlJira)
    #response = requests.get(urlJira, auth=(" ", " "), verify= ) # odkomencic po naprawie Jiry
    #ResponseJira = response.json() # odkomencic po naprawie Jiry
    #DumpJira = json.dumps(ResponseJira) # odkomencic po naprawie Jiry
    #JSONJira = json.loads(DumpJira) # przechowuje calego JSONA z JIRA
    JSONJira = ""
    print("OK")
    print ("Retrieving JIRA repository data from table..."),
    cursor.execute("SELECT * FROM Sources_JIRA")
    JSONJira = cursor.fetchall()  # wszystkie projekty z SVN
    print("OK")
    print ("Retrieving SVN repository data from table..."),
    cursor.execute("SELECT * FROM Sources_SVN")
    SVNProjekty = cursor.fetchall()  # wszystkie projekty z SVN
    print("OK")
    print("Retrieving Sonar projects from SonarDictionary table..."),
    cursor.execute("SELECT * FROM SonarDictionary")
    SonarDictResults = cursor.fetchall()  # wszystkie projekty z Sonara
    print("OK")
    print("Project comparison: ")
    for DictRow in SonarDictResults:
        SonarName = DictRow[0]
        #BugTrackerType = DictRow[1]
        BugTrackerName = DictRow[2]
        #RepositoryType = DictRow[3]
        RepositoryName = DictRow[4]
        MetricGeneratorKey = DictRow[10]
        #print ("Jira..."),
        for ProjektJira in JSONJira:
            #DumpProjektJira = json.dumps(ProjektJira) # odkomencic po naprawie Jiry
            #JSONProjektJira = json.loads(DumpProjektJira) # odkomencic po naprawie Jiry
            #JSONProjektJiraName = JSONProjektJira["name"] # odkomencic po naprawie Jiry
	    JSONProjektJiraName = ProjektJira[0] # "INVALID" # usunac po naprawie Jiry
            JiraRatioLocal = SeqMat(None, SonarName.lower(), JSONProjektJiraName.lower()).ratio()
            if JiraRatioLocal > JiraRatioMax:
                JiraRatioMax = JiraRatioLocal
                ProjektJiraNameMax = JSONProjektJiraName
        sql = "UPDATE SonarDictionary SET BugTrackerType=%s, TrackerSimilarRatio=%r, BugTrackerName=\'%s\' WHERE MetricGeneratorKey=\'%s\' " % ("1", JiraRatioMax, ProjektJiraNameMax.encode('utf-8'), MetricGeneratorKey)
        cursor.execute(sql)
        if JiraRatioMax >= SimilarRatio:
            FoundJIRA = SonarName
        JiraRatioMax = 0
        ProjektJiraNameMax = ""
        #print("OK")
        #print("SVN..."),
        for ProjektSVN in SVNProjekty:
            #print ProjektSVN[1]
            SVNRatioLocal = SeqMat(None, SonarName.lower(), ProjektSVN[1].lower()).ratio()
            #print SVNRatioLocal
            if SVNRatioLocal > SVNRatioMax:
                SVNRatioMax = SVNRatioLocal
                ProjektSVNNameMax = ProjektSVN[1]
                ProjektSVNURLMax = ProjektSVN[3]
        sql = "UPDATE SonarDictionary SET RepositoryType=%s, RepositoryName=\'%s\', RepositoryURL=\'%s\', RepoSimilarRatio=%r WHERE MetricGeneratorKey=\'%s\'" % ("1", ProjektSVNNameMax.encode('utf-8'), ProjektSVNURLMax.encode('utf-8'), SVNRatioMax, MetricGeneratorKey)
        cursor.execute(sql)
        if SVNRatioMax >= SimilarRatio:
            FoundSVN = SonarName
        SVNRatioMax = 0
        ProjektSVNNameMax = ""
        ProjektSVNURLMax = ""
        #print("OK")
        #print("Selecting as ready for predicton..."),
        if FoundJIRA == FoundSVN and FoundJIRA <> "":
            FoundJIRA = ""
            FoundSVN = ""
            sql = "UPDATE SonarDictionary SET Ready=1 WHERE SonarName=\'%s\'" % (SonarName)
            cursor.execute(sql)
        sql = "SELECT COUNT(*) FROM Projects WHERE name=\'%s\'" % (SonarName)
        cursor.execute(sql)
        TotalNumberOfSnapshots = 0
        if cursor.fetchall():
            for Numbers in cursor:
                NumberOfSnapshots = Numbers[0]
                TotalNumberOfSnapshots = TotalNumberOfSnapshots + NumberOfSnapshots
            if TotalNumberOfSnapshots < 2:
                sql = "UPDATE SonarDictionary SET Ready=-2 WHERE SonarName=\'%s\'" % (SonarName)
                cursor.execute(sql)
        #print ("ProjectsData <=> MetricGeneratorKey;")
        sql = "SELECT * FROM ProjectsData WHERE MetricGeneratorKey=\'%s\'" % (MetricGeneratorKey)
        #print (sql)
        cursor.execute(sql)
        if cursor.fetchall():
            #print("BUM!!!")
            #ProjectsDataResultsAll = cursor.fetchall()
            for ProjectsDataResults in cursor:
                MetricGeneratorName = ProjectsDataResults[2]
                MetricGeneratorKey = ProjectsDataResults[3]
                BugTrackerType = ProjectsDataResults[4]
                BugTrackerName = ProjectsDataResults[5]
                RepositoryType = ProjectsDataResults[6]
                RepositoryURL = ProjectsDataResults[7]
                RepositoryName = ProjectsDataResults[8]
                ProjectReady = ProjectsDataResults[9]
                sql = "UPDATE SonarDictionary SET RepositoryName=\'%s\', RepositoryURL=\'%s\', RepositoryType=\'%i\', BugTrackerType=\'%i\', BugTrackerName=\'%s\', SonarName=\'%s\', Ready=\'%s\' WHERE MetricGeneratorKey=\'%s\'" % (RepositoryName, RepositoryURL, RepositoryType, BugTrackerType, BugTrackerName, MetricGeneratorName, ProjectReady, MetricGeneratorKey)
                #print(sql)
                cursor.execute(sql)
    print("Retrieving unique records from ProjectsData table...")
    cursor.execute("SELECT * FROM ProjectsData WHERE MetricGeneratorKey NOT IN (SELECT MetricGeneratorKey FROM SonarDictionary)")
    if cursor.fetchall():
        ProjectsDataResultsUnique = cursor.fetchall()
        for ProjectsData in ProjectsDataResultsUnique:
            MetricGeneratorName = ProjectsData[2]
            MetricGeneratorKey = ProjectsData[3]
            BugTrackerType = ProjectsData[4]
            BugTrackerName = ProjectsData[5]
            RepositoryType = ProjectsData[6]
            RepositoryURL = ProjectsData[7]
            RepositoryName = ProjectsData[8]
            ProjectReady = ProjectsData[9]
            sql = "INSERT INTO SonarDictionary (RepositoryName, RepositoryURL, RepositoryType, BugTrackerType, BugTrackerName, SonarName, MetricGeneratorKey, Ready) VALUES (%s, %s, %i, %i, %s, %s, %s, %s)" % (RepositoryName, RepositoryURL, RepositoryType, BugTrackerType, BugTrackerName, MetricGeneratorName, MetricGeneratorKey, ProjectReady)
            cursor.execute(sql)
    print ("SCRIPT COMPLETED.")

except Exception as e:
    print ("*** ERROR ***")
    print str(e)


cursor.close()
db.commit()
db.close()