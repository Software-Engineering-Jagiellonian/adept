#!/bin/bash
# skrypt odpala sie codziennie o 1:05 w nocy -> crontab -l
mysql --user= --password= --database= --execute="TRUNCATE TABLE Sources_SVN"
mysql --user= --password= --database= --execute="TRUNCATE TABLE SonarDictionary"
mysql --user= --password= --database= --execute="INSERT INTO SonarDictionary (MetricGeneratorKey, SonarName) SELECT Projects.key, Projects.name FROM Projects WHERE Projects.key NOT IN (SELECT Projects.key FROM Projects INNER JOIN SonarDictionary ON Projects.key=SonarDictionary.MetricGeneratorKey GROUP BY Projects.key, Projects.name) GROUP BY Projects.key, Projects.name"
/DePress/scripts/SourceToDatabase.py
/DePress/scripts/SourceQuery.py
/DePress/scripts/AnalyzeNamespacesDepth.py
/DePress/scripts/CountNames_in_Namespaces.py