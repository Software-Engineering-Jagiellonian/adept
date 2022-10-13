# -*- coding: utf-8 -*-
"""
tools.quality_center_svn_integrator_tools
~~~~~~~~~~~~

Modul integracji danych z quality center i svn

:copyright:
:license:

"""

import json
from data_source_db_tools import get_list_of_data_sources_for_projects_ready_for_prediction_and_with_quality_center_bug_tracker
from svn_tools import get_svn_log_with_quality_center_id_as_dictionary
from quality_center_tools import start_quality_center_connection, end_quality_center_connection, is_issue_defect_for_issue_id
from tfs_sonar_integrator import get_sonar_data_list_with_oldest_sonar_snapshot_and_defect_pron_area_mark_for_all_tfs_project
from sonar_tools import add_defect_prone_flag_to_oldest_metric_for_project


def add_defect_prone_flag_to_oldest_metric_for_quality_center_projects():
    """ Metoda pobiera dane z quality center i svn a nastepnie oznacza pliki defektogenne w najstarszych metrykach dla sonara 4

    :return: nic nie zwraca
    :rtype: None
    """

    projects_data = merge_repository_with_quality_center_for_projects()
    for project_data in projects_data:
        add_defect_prone_flag_to_oldest_metric_for_project(project_data)


def add_defect_prone_flag_to_oldest_metric_for_tfs_projects():
    """ Metoda pobiera dane z quality center i svn a nastepnie oznacza pliki defektogenne w najstarszych metrykach dla sonara 4

    :return: nic nie zwraca
    :rtype: None
    """

    projects_data = merge_repository_with_tfs_for_projects()
    for project_data in projects_data:
        add_defect_prone_flag_to_oldest_metric_for_project(project_data)


def merge_repository_with_tfs_for_projects(projects_data_sources=None):
    """Zwraca liste slownikow z danych dla projektow z bug trackerem tfs
 
    :param projects_data_sources: slownik projektow
    :return: lista slowniko z zrodlami danych dla projektow
    [
        {
            'metric_generator_name': '',
            'defective_file_set':   [
                                        '',
                                        ...
                                    ]
        }
        ...
    ]
    :rtype: list
    """
 
    if projects_data_sources == None:
        projects_data_sources = get_sonar_data_list_with_oldest_sonar_snapshot_and_defect_pron_area_mark_for_all_tfs_project()
    result = []
    for project_data_sources in projects_data_sources:
        merged_sources = {}
        merged_sources['metric_generator_name'] = project_data_sources['SonarName']
        merged_sources['defective_file_set'] = project_data_sources['defective_file_set']
        result.append(merged_sources)
    return result

    


def merge_repository_with_quality_center_for_projects(projects_data_sources=None):
    """Zwraca liste slownikow z danych dla projektow z bug trackerem Quality center

    :param projects_data_sources: slownik projektow
    :return: lista slowniko z zrodlami danych dla projektow
    [
        {
            'metric_generator_name': ''
            'bug_tracker_prefix_list': ''
            'repository_log':   [
                                    {
                                        'paths': ['', ...],
                                        'message': '',
                                        'id': '',
                                        'quality_center_issues_keys_id': ['', ...]
                                    }
                                    ...
                                ]
            'defective_file_set':   [
                                        '',
                                        ...
                                    ]
        }
        ...
    ]
    :rtype: list
    """

    if projects_data_sources == None:
        projects_data_sources = get_list_of_data_sources_for_projects_ready_for_prediction_and_with_quality_center_bug_tracker()
    return merge_repository_with_bug_tracker_for_projects(projects_data_sources)


def merge_repository_with_bug_tracker_for_projects(projects_data_sources=None):
    """Zwraca liste slownikow z danych dla projektow z bug trackerem Quality center

    :param projects_data_sources: slownik projektow
    :return: lista slowniko z zrodlami danych dla projektow
    [
        {
            'metric_generator_name': ''
            'bug_tracker_prefix_list': ''
            'repository_log':   [
                                    {
                                        'paths': ['', ...],
                                        'message': '',
                                        'id': '',
                                        'quality_center_issues_keys_id': ['', ...]
                                    }
                                    ...
                                ]
            'defective_file_set':   [
                                        '',
                                        ...
                                    ]
        }
        ...
    ]
    :rtype: list
    """

    for project_data_sources in projects_data_sources:
        project_data_sources['BugTrackerName'] = json.loads(project_data_sources['BugTrackerName'])

    projects_collected_data_from_data_sources = []

    for project_data_sources in projects_data_sources:
        project_collected_data_from_data_sources = {}

        project_collected_data_from_data_sources['metric_generator_name'] = project_data_sources['SonarName']
        project_collected_data_from_data_sources['quality_center_data'] = project_data_sources['BugTrackerName']
        project_collected_data_from_data_sources['bug_tracker_prefix_list'] = __get_quality_center_prefix_list(project_data_sources) 
#   SVN LOG
# TODO Change TO URL
        print project_data_sources['RepositoryURL']
        project_collected_data_from_data_sources['repository_log'] = get_svn_log_with_quality_center_id_as_dictionary(svn_repo_url=project_data_sources['RepositoryURL'], quality_center_prefix_list=project_collected_data_from_data_sources['bug_tracker_prefix_list'])
#         project_collected_data_from_data_sources['repository_log'] = get_svn_log_with_quality_center_id_as_dictionary(svn_file_path='/home/a217292/testData/' + str(project_data_sources['SonarName']), quality_center_prefix_list=project_collected_data_from_data_sources['bug_tracker_prefix_list'])

        project_collected_data_from_data_sources['defective_file_set'] = __get_defective_file_set_from_quality_center_for_project(project_collected_data_from_data_sources)
        print '\t\tIntegrate'
        projects_collected_data_from_data_sources.append(project_collected_data_from_data_sources)

    return projects_collected_data_from_data_sources


def __get_defective_file_set_from_quality_center_for_project(project_data):
    """Zwraca zbiór plików modufikowanych w wyniku bledow

    :param project_data: slownik z zrodlami danych dla projektu
    :return: zbiór plików modufikowanych w wyniku bledow
    [
        '',
        ...
    ]
    :rtype: set
    """

    defective_file_list = []
    session = start_quality_center_connection()
    domain = project_data['quality_center_data']['domain']
    project = project_data['quality_center_data']['project']
    qcPrefix = project_data['quality_center_data']['qcPrefix']
    extraField = project_data['quality_center_data']['extraField']
    extraFieldPrefix = project_data['quality_center_data']['extraFieldPrefix']

    for repository_log_entry in project_data['repository_log']:
        if repository_log_entry.has_key('quality_center_issues_keys_id'):
            deffective = False
            for isses_id in repository_log_entry['quality_center_issues_keys_id']:
                qc_id = None
                extra_field_value = None
                if isses_id.startswith(qcPrefix):
                    qc_id = isses_id.replace(qcPrefix, '')
                if isses_id.startswith(extraFieldPrefix):
                    extra_field_value = isses_id.replace(extraFieldPrefix, '')
                if qc_id or extra_field_value:
                    print  domain, project, qc_id, (extraField, extra_field_value)
                    if is_issue_defect_for_issue_id(session, domain, project, qc_id, extra_field=(extraField, extra_field_value)):
                        deffective = True
            if deffective:
                defective_file_list.extend(repository_log_entry['paths'])
    end_quality_center_connection(session)
    return set(defective_file_list)


def __get_quality_center_prefix_list(project_data_sources):
    """Zwraca zbior prefixow dla quality center dla projektu

    :param project_data_sources: slownik z zrodlami danych dla projektu
    :return: zbior prefixow dla quality center dla projektu
    [
        '',
        ...
    ]
    :rtype: set
    """

    prefix_list  = []
    prefix_list.append(project_data_sources['BugTrackerName']['qcPrefix'])
    if project_data_sources['BugTrackerName']['extraFieldPrefix']:
        prefix_list.append(project_data_sources['BugTrackerName']['extraFieldPrefix'])
    return prefix_list
