#!/usr/bin/python

# skrypt leci po namespace'ach i liczy unikalne nazwy w nich wystepujace
# UWAGA !!! najpierw nalezy odpalic AnalyzeNamespacesDepth.py zeby wypelnic tabele FunctDictSummary

import MySQLdb
import requests
import datetime

def ModuleStrip(module,inside_counter):
    if module.rfind("\\") > -1:
        # Zeby zrozumiec rekurencje, trzeba najpierw zrozumiec rekurencje
        return ModuleStrip(module[:module.rfind("\\")],inside_counter + 1)
    else:
        return inside_counter


db = MySQLdb.connect(" "," "," ")
cursor = db.cursor()

try:
    #print("1")
    cursor.execute("SELECT a.R_Table, a.Date, a.TotalNamespacesDepth, a.ID FROM prediction.FunctDictSummary a LEFT JOIN prediction.FunctNameComplexity b ON a.ID = b.ID WHERE b.ID IS NULL")
    AllDailyResults = cursor.fetchall()
    for DailyResult in AllDailyResults:
        OldModule = ''
        MaxDepth = 0
        Modules = []
        ResultTable = DailyResult[0]
        ResultDate = DailyResult[1].strftime('%Y-%m-%d')
        MaxDepth = DailyResult[2]
        ResultsID = DailyResult[3]
        print ResultTable, ResultDate
        for y in range(MaxDepth):
            Modules.append([])
        cursor.execute("SELECT Module,Prediction FROM prediction_result.%s WHERE Date='%s'" % (ResultTable, ResultDate))
        AllModules = cursor.fetchall()
        for SingleModule in AllModules:
            Is_DefectProne = '0'
            if SingleModule[1] is not None:
                Is_DefectProne = SingleModule[1] ### This ugly workaround with +DefectProneFlag had to be done due to customer's request
            StripCounter = ModuleStrip(SingleModule[0],1)
            Inside_Module = SingleModule[0]
            while Inside_Module.rfind("\\") > -1:
                if Is_DefectProne == '1':
                    Modules[StripCounter - 1].append(Inside_Module + '+DefectProneFlag')
                else:
                    Modules[StripCounter - 1].append(Inside_Module)
                Inside_Module = Inside_Module[:Inside_Module.rfind("\\")]
                StripCounter -= 1
            if Is_DefectProne == '1':
                Modules[0].append(Inside_Module + '+DefectProneFlag')
            else:
                Modules[0].append(Inside_Module)
        Offset = 1
        #print("2")
        for MainLoop in range(MaxDepth):
            Modules[MainLoop] = list(set(Modules[MainLoop])) #usuwa duplikaty !!!
            cursor.execute("INSERT INTO prediction.FunctNameComplexity (ID, NamespaceDepth, NamesNumber) VALUES (%d, %d, %d)" % (ResultsID, MainLoop + Offset, len(Modules[MainLoop])))
            for EachModule in Modules[MainLoop]:
                Prediction = 0
                EachModuleSQL = EachModule.replace("\\", "\\\\") # wazne!!!
                if EachModuleSQL.endswith("+DefectProneFlag"):
                    EachModuleSQL = EachModuleSQL[:-16]
                    Prediction = 1
                    cursor.execute("SELECT Prediction FROM prediction.FunctionDictionary WHERE ID='%d' AND NamespaceDepth='%d' AND Namespace='%s'" % (ResultsID, MainLoop+Offset, EachModuleSQL))
                    SuchNamespaceExists = cursor.fetchone()
                    if SuchNamespaceExists is not None:
                        cursor.execute("UPDATE prediction.FunctionDictionary SET Prediction='1' WHERE ID=%d AND NamespaceDepth=%d AND Namespace='%s'" % (ResultsID, MainLoop+Offset, EachModuleSQL))
                        continue
                else:
                    cursor.execute("SELECT Prediction FROM prediction.FunctionDictionary WHERE ID='%d' AND NamespaceDepth='%d' AND Namespace='%s'" % (ResultsID, MainLoop+Offset, EachModuleSQL))
                    SuchNamespaceExists = cursor.fetchone()
                    if SuchNamespaceExists is not None:
                        continue
                cursor.execute("INSERT INTO prediction.FunctionDictionary (ID, NamespaceDepth, Namespace, Prediction) VALUES (%d, %d, '%s', %d)" % (ResultsID, MainLoop+Offset, EachModuleSQL, Prediction))
                # tutaj sprawdzanie w petli, poczawszy od najnizszego ResultsID, czy dla danej kombinacji MainLoop+Offset (NamespaceDepth) 
                # oraz EachModuleSQL (Namespace) = AllPreviousCombinations istnieja juz jakies wpisy w kolumnie Function MainLoop Notes
                cursor.execute("SELECT Function FROM prediction.FunctionDictionary WHERE Function IS NOT NULL AND NamespaceDepth='%d' AND Namespace='%s' ORDER BY ID DESC LIMIT 1" % (MainLoop+Offset, EachModuleSQL))
                PreviousFunction = cursor.fetchone()
                if PreviousFunction is not None:
                    cursor.execute("UPDATE prediction.FunctionDictionary SET Function='%s' WHERE ID=%d AND NamespaceDepth=%d AND Namespace='%s'" % (PreviousFunction[0],ResultsID, MainLoop+Offset, EachModuleSQL))
                cursor.execute("SELECT Notes FROM prediction.FunctionDictionary WHERE Notes IS NOT NULL AND NamespaceDepth='%d' AND Namespace='%s' ORDER BY ID DESC LIMIT 1" % (MainLoop+Offset, EachModuleSQL))
                PreviousNote = cursor.fetchone()
                if PreviousNote is not None:
                    cursor.execute("UPDATE prediction.FunctionDictionary SET Notes='%s' WHERE ID=%d AND NamespaceDepth=%d AND Namespace='%s'" % (PreviousNote[0], ResultsID, MainLoop+Offset, EachModuleSQL))
                #OldModule = EachModule
except Exception as e:
    print str(e)
print ("Completed.")
cursor.close()
db.commit()
db.close()