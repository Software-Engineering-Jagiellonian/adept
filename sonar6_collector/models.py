from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()

class Project(Base):
    __tablename__ = 'Projects'
    
    def __init__(self, key = None, name = None, creation_date = None):
        self.key = key
        self.name = name
        self.creation_date = creation_date
        if self.name and self.creation_date:
            self.db_name = self.name+'_'+self.creation_date
        
    
    id = Column(Integer, primary_key=True)
    key = Column(String(255))
    name = Column(String(100))
    creation_date = Column(String(25))
    db_name = Column(String(125), unique = True)
    

class Metric(Base):
    __tablename__ = 'Metrics'
    
    def __init__(self, file_name=None, metric_dump=None, db_name=None):
        self.file_name = file_name
        self.metric_dump = metric_dump
        self.db_name = db_name
        self.defects = -1
        self.prediction = -1
    
    id = Column(Integer, primary_key=True)
    file_name = Column(String(255))
    metric_dump = Column(String(2500))
    db_name = Column(String(125))
    defects = Column(Integer)
    prediction = Column(Integer)
    
    __table_args__ = (UniqueConstraint('db_name', 'file_name', name='_project_uc'),)