# ADePT

## General info
ADePT (stands for Automatic DEfect PredicTion) is a python application that enables automatic software defect prediction process. It uses machine learning algorithms and source code metrics downloaded automatically from SonarQube API. Additionally, it uses data about changes in source code (which occurred as a result of defect repair) retrieved from SVN and data about software defects retrieved from defect tracking system.

Results of software defect prediction are stored in database (default: mySQL), from where they can be retrieved for any purpose, e.g. displayed on web page or for indicating potentially defectogenic files by integrated development environment plugin.

