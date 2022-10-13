#!/usr/bin/python

# Skrypt dopisuje do tabel Sources_JIRA oraz Sources_SVN zrodla danych z tych dwoch systemow

# TODO!!! skrypt nie uaktualnia danych!! jesli nazwa projektu juz jest w tabeli !!!!

import MySQLdb
import requests
import json
import ApiTools
import urllib2
from difflib import SequenceMatcher as SeqMat
import urllib2
from bs4 import BeautifulSoup
import time

print ("Connecting to database...")
db = MySQLdb.connect(" "," "," "," " )
cursor = db.cursor()

urlJira = " "
urlSVN = " "
SimilarRatio = 0.85 # prog akceptowania predykcji automatycznej dla projektu
FoundJIRA = ""
FoundSVN = ""
JiraRatioMax = 0
SVNRatioMax = 0


try:

	print ("Dumping JSON from JIRA...")
	response = requests.get(urlJira, auth=(" ", " "), verify= )
	ResponseJira = response.json()
	DumpJira = json.dumps(ResponseJira)
	JSONJira = json.loads(DumpJira) # przechowuje calego JSONA z JIRA
	for ProjektJira in JSONJira:
		DumpProjektJira = json.dumps(ProjektJira)
		JSONProjektJira = json.loads(DumpProjektJira)
		JSONProjektJiraName = JSONProjektJira["name"]
		sqlSelect = "SELECT Name FROM Sources_JIRA WHERE Name =\'%s\'" % (JSONProjektJiraName.encode('utf-8'))
		cursor.execute(sqlSelect)
		sqlInsert = "INSERT INTO Sources_JIRA (Name) VALUES (\'%s\')" % (JSONProjektJiraName.encode('utf-8'))
		#print(sqlInsert)
		if not cursor.fetchall():
			cursor.execute(sqlInsert)
	
	#pobranie tabelki z nazwami projektow ze strony glownej SVN
	print ("Parsing SVN page...")
	SVNPage = urllib2.urlopen(urlSVN)
	soup = BeautifulSoup(SVNPage)
	SVNPageTable = soup.find('table')
	SVNPageRows = SVNPageTable.findAll('tr')
	
	print ("Retrieving SVN repositories from table...")
	SVNProjekty = []
	for tr in SVNPageRows:
		cols = tr.findAll('td')
		if not cols:
			continue
		#print(cols)
		SVNName = cols[0].string.strip()
		print(SVNName)
		if SVNName == "Repository Name":
			continue
		elif SVNName == "idc":
			continue # DIRTYFIX - "idc" ma blad w opisie (falszywy tag html)
		SVNDescription = cols[1].string.strip()
		column_1 = cols[0].find('a')
		SVNURL = urlSVN
		if column_1:
			SVNURL = column_1.get('href')
			if not SVNURL.endswith('/'):
				SVNURL+="/"
		sqlSelect = "SELECT Name FROM Sources_SVN WHERE Name =\'%s\'" % SVNName
		cursor.execute(sqlSelect)
		SonarDictResults = cursor.fetchall()
		sqlInsert = "INSERT INTO Sources_SVN (Name, Description, URL) VALUES (\'%s\', \'%s\', \'%s\')" % (SVNName.encode('utf-8'), SVNDescription.encode('utf-8'), SVNURL)
		if not SonarDictResults:
			cursor.execute(sqlInsert)
	print ("Completed.")

except Exception as e:
	print str(e)


cursor.close()
db.commit()
db.close()