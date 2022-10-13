#!/usr/bin/python

# skrypt bada jak gleboko siegaja nazwy - tj. ile jest max namespace w nazwach pliku 
# w R_**** (osobno dla kazdej daty) i umieszcza wynik w tabeli FunctDictSummary

import MySQLdb
import requests
import datetime

Depth = 0
MaxDepth = 0

def ModuleStrip(module,inside_counter):
    if module.rfind("\\") > -1:
        # Zeby zrozumiec rekurencje, trzeba najpierw zrozumiec rekurencje
        return ModuleStrip(module[:module.rfind("\\")],inside_counter + 1)
    else:
        return inside_counter

db = MySQLdb.connect(" "," "," ")
cursor = db.cursor()

db_results = MySQLdb.connect(" "," "," "," " )
cursor_results = db_results.cursor()

try:
    # zapewnione jest odczytanie tylko nowych dat z tablicy R_****
    cursor_results.execute("SHOW TABLES")
    AllTables = cursor_results.fetchall()
    for SingleTable in AllTables:
        if SingleTable[0][:2] == "R_":
            ResultTable = SingleTable[0]
            cursor.execute("SELECT a.Date FROM prediction_result.%s a LEFT JOIN prediction.FunctDictSummary b ON a.Date = b.Date WHERE b.Date IS NULL GROUP BY a.Date" % (ResultTable))
            AllDates = cursor.fetchall()
            for SingleDate in AllDates:
                print ResultTable,
                MaxDepth = 0
                Depth = 0
                if SingleDate[0] is not None:
        	    #print(SingleDate[0])
                    SingleDateSQL = SingleDate[0].strftime('%Y-%m-%d')
                    #cursor.execute("SELECT Module FROM %s WHERE Date='%s' AND Prediction='1'" % (ResultTable, SingleDateSQL))
                    cursor_results.execute("SELECT Module FROM %s WHERE Date='%s'" % (ResultTable, SingleDateSQL))
                    AllModules = cursor_results.fetchall()
                    for SingleModule in AllModules:
                        Depth = ModuleStrip(SingleModule[0],1)
                        if Depth > MaxDepth:
                            MaxDepth = Depth
                    cursor.execute("INSERT INTO prediction.FunctDictSummary (R_Table, Date, TotalNamespacesDepth) VALUES ('%s', '%s', %d)" % (ResultTable, SingleDateSQL, MaxDepth))
                    print MaxDepth
                else:
                    print ("Warning: NULL date detected in table %s!" % (ResultTable))
                
except Exception as e:
    print str(e)

print ("Completed.")
cursor.close()
db.commit()
db.close()