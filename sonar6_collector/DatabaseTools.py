# -*- coding: utf-8 -*-
from models import Base, Project
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loggerTools import get_normal_logger, get_exception_logger
from SonarSettings import db_engine_url

eng = create_engine(db_engine_url)
Session = sessionmaker(bind=eng)

def update_database(metrics_tuple_list):
    create_tables(Base)
    ses = Session()
    new_data_count = 0
    unchanged_data_count = 0
    for metics_tuple in metrics_tuple_list:
        if not __project_exists(metics_tuple[0], ses):
            new_data_count = new_data_count + 1
            save_in_database_metric_list(metics_tuple[1], ses)
            ses.add(metics_tuple[0])
            ses.commit()
        else:
            unchanged_data_count = unchanged_data_count + 1
    ses.close_all()
    if new_data_count < 1:
        get_exception_logger().warning('Saved metrics for {0} projects.'.format(new_data_count))
    get_normal_logger().info('Saved metrics for {0} projects.'.format(new_data_count))
    get_normal_logger().info('{0} projects were unchanged.'.format(unchanged_data_count))
    
def create_tables(Base):
    Base.metadata.bind = eng
    Base.metadata.create_all()


def __project_exists(project_obejctt, ses):
    query = ses.query(Project).filter(Project.db_name==project_obejctt.db_name)
    return len(query.all())>0
    
    
def save_in_database_metric_list(metrics, ses):
    ses.add_all(metrics)
    

def project_exists(db_name):
    ses = Session()
    query = ses.query(Project).filter(Project.db_name==db_name)
    ses.close_all()
    return len(query.all())>0
