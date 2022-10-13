#!/usr/bin/python

# Program przeszukuje JSONy z tabeli Metrics pod katem nowych typow metryk
# Nowy typ metryki to taki, ktorego nie ma w tabeli MetricTypes
# Jak nowy typ jest znaleziony, to tabelka MetricTypes jest uaktualniana

import MySQLdb
import requests
import json
import ApiTools
import urllib2
import time

print ("Connecting to database...")
db = MySQLdb.connect(" "," "," "," " )
cursor = db.cursor()


try:
   print("Dumping ALL metric Sonar JSONs from database...")
   cursor.execute("SELECT metric_dump FROM Metrics")
   MetricsDump = cursor.fetchall()
   print("Looking for unique metric kinds...")
   for MetricsRow in MetricsDump:
      SingleMetricsSet = json.loads(MetricsRow[0])
      for SingleMetrics in SingleMetricsSet:
		cursor.execute("SELECT Metric FROM MetricTypes WHERE Metric=\'%s\'" % (SingleMetrics))
		MetricExistResult = cursor.fetchall()
		if not MetricExistResult:
			print("New metric found: %s" % (SingleMetrics))
			cursor.execute("INSERT INTO MetricTypes(Metric) VALUES (\'%s\')" % (SingleMetrics))
except Exception as e:
   print str(e)

print ("Completed.")
cursor.close()
db.commit()
db.close()