#!/usr/bin/python

# Skrypt parsuje kazdy z pobranych z SonarQube JSON-ow zapisanych wczesniej w surowej formie w tabeli Metrics.
# Skrypt sprawdza, czy id z Metrics nie jest juz obecny w tabeli MetricsParsed, jesli nie, parsuje JSONy z nowymi id 
# i wstawia wartosci metryk z odpowiednimi identyfikatorami liczbowymi metryk ("MetricsType", wziete z Tabeli MetricTypes)
# do tabeli MetricsParsed.
#
# Dobrze jest wczesniej uruchomic skrypt MetricsKindCollection.py, aby miec pewnosc, ze kazda z metryk dostarczonych
# przez SonarQube bedzie miala swoj identyfikator liczbowy w tabeli MetricTypes.


import MySQLdb
import requests
import json
import ApiTools
import urllib2
import time
from pprint import pprint

print ("Connecting to database...")
db = MySQLdb.connect(" "," "," "," " )
cursor = db.cursor()


try:
	print("Dumping METRIC TYPES from database...")
	cursor.execute("SELECT id,Metric FROM MetricTypes")
	MetricTypes = cursor.fetchall()  # tablica MetricTypes zawiera mapowanie id <-> typ metryki
	print MetricTypes
	print("Dumping NEW metric Sonar JSONs from database...")
	cursor.execute("SELECT id,metric_dump FROM Metrics WHERE id NOT IN (SELECT MetricsId FROM MetricsParsed)")
	MetricsDump = cursor.fetchall()  # zmienna MetricsDump zawiera WSZYSTKIE JSONy + id
	print("Parsing JSONs...")
	for MetricsRow in MetricsDump:   # zmienna MetricsRow zawiera pojedynczego JSONa + id
		# MetricsRow[0] - id
		# MetricsRow[1] - JSON
		SingleJSON = json.loads(MetricsRow[1])  
		for SingleMetric in SingleJSON:
			# SingleMetric - nazwa metryki
			# SingleMetricsJSON[SingleMetric] - wartosc metryki
			MetricsId = MetricsRow[0]
			for SingleMetricType in MetricTypes:
				if SingleMetricType[1] == SingleMetric: 
					MetricsType = SingleMetricType[0]
			MetricsValue = SingleJSON[SingleMetric]
			sql = "INSERT INTO MetricsParsed(MetricsId,MetricsType,MetricsValue) VALUES (%s, %s, %s)" % (MetricsId,MetricsType,MetricsValue)
			print(sql)
			cursor.execute(sql)
except Exception as e:
   print str(e)

print ("Completed.")
cursor.close()
db.commit()
db.close()