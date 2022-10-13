# -*- coding: utf-8 -*-
"""
tools.api_tools
~~~~~~~~~~~~

Modul obslugi restowego api

:copyright:
:license:

"""
from sonar_tools import get_metics_for_version_with_subproject_path, get_oldest_db_name_for_project
from data_source_db_tools import get_list_of_data_sources_for_projects_ready_for_prediction_and_with_tfs
from tfs_tools import get_modified_files_for_project


def get_sonar_data_list_with_oldest_sonar_snapshot_and_defect_pron_area_mark_for_all_tfs_project():
    sonar_data_list = []
    projects_data = get_list_of_data_sources_for_projects_ready_for_prediction_and_with_tfs()
    for project_data in projects_data:
        sonar_data_list.append(__get_data_from_oldest_sonar_snapshot_with_defect_pron_area_mark_for_project_data(project_data))
    return sonar_data_list
    

def __get_data_from_oldest_sonar_snapshot_with_defect_pron_area_mark_for_project_data(project_data):
    modified_files = get_modified_files_for_project(project_data['TfsName'], project_data['TfsCollection'], project_data['TfsQuery'])
    sonar_data = get_metics_for_version_with_subproject_path(get_oldest_db_name_for_project(project_data['SonarName']))
    defective_files = []
    for sonar_record in sonar_data:
        if sonar_record['path'] in modified_files:
            sonar_record['prediction'] = 1
            defective_files.append(sonar_record['file_name'])
    project_data['sonar_data'] = sonar_data
    project_data['defective_file_set'] = set(defective_files)
    return project_data