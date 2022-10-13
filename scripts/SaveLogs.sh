#!/bin/bash
eName=$(date '+%Y_%m' -d "1 day ago")
cd /DePress/logs/sonar6_collector/
mv exception_logs.log $eName"_exception_logs.log"
touch exception_logs.log
mv logs.log $eName"_logs.log"
touch logs.log
chown a217292:adept exception_logs.log
chown a217292:adept logs.log
cd /DePress/logs/add_defects/
mv exception_logs.log $eName"_exception_logs.log"
touch exception_logs.log
chmod 660 exception_logs.log
mv logs.log $eName"_logs.log"
touch logs.log
chmod 660 logs.log
chown a217292:adept exception_logs.log
chown a217292:adept logs.log
cd /DePress/logs/adept/
mv exception_logs.log $eName"_exception_logs.log"
touch exception_logs.log
mv logs.log $eName"_logs.log"
touch logs.log
chown a217292:adept exception_logs.log
chown a217292:adept logs.log
