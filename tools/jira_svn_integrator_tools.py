# -*- coding: utf-8 -*-
"""
tools.jira__svn_integrator_tools
~~~~~~~~~~~~

Modul obslugi jiry

:copyright:
:license:

"""

from svn_tools import get_svn_log_with_jira_issues_keys_id_as_dictionary
from jira_tools import get_jira_key_for_project, get_issue_type_for_jira_key
from data_source_db_tools import get_list_of_data_sources_for_projects_ready_for_prediction
from settings import JIRA_BUGS_ISSUE_TYPE_ID_LIST


def merge_svn_with_jira_for_all_project(projects_data_sources=None):
    """Zwraca liste slownikow z danych dla projektow

    :param projects_data_sources: slownik projektow z jira 
    :return: lista slowniko z zrodlami danych dla projektow
    [
        {
            'metric_generator_name': ''
            'jira_key': ''
            'repository_log':   [
                                    {
                                        'paths': ['', ...],
                                        'message': '',
                                        'id': '',
                                        'jira_issues_keys_id': ['', ...]
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
        projects_data_sources = get_list_of_data_sources_for_projects_ready_for_prediction()
        
        
    projects_collected_data_from_data_sources = []
    

    for project_data_sources in projects_data_sources:
        project_collected_data_from_data_sources = {}
        
        project_collected_data_from_data_sources['metric_generator_name'] = project_data_sources['SonarName']
        print project_collected_data_from_data_sources['metric_generator_name']
        
        print '\t\tJIRA'
        #    JIRA KEY
        project_collected_data_from_data_sources['jira_key'] = get_jira_key_for_project(project_data_sources['BugTrackerName'])
        
        print '\t\tSVN'
#   SVN LOG
# TODO Change TO URL
        project_collected_data_from_data_sources['repository_log'] = get_svn_log_with_jira_issues_keys_id_as_dictionary(svn_repo_url=project_data_sources['RepositoryURL'],jira_key_prefix = project_collected_data_from_data_sources['jira_key'])
#         project_collected_data_from_data_sources['repository_log'] = get_svn_log_wiht_jira_issues_keys_id_as_dictionary(svn_file_path='/home/a217292/testData/' + project_data_sources['BugTrackerName'], jira_key_prefix=project_collected_data_from_data_sources['jira_key'])
        
        project_collected_data_from_data_sources['defective_file_set'] = __get_defective_file_set_for_project(project_collected_data_from_data_sources)
        print '\t\tIntegrate'
        projects_collected_data_from_data_sources.append(project_collected_data_from_data_sources)
        
    return projects_collected_data_from_data_sources


def __get_defective_file_set_for_project(project_data):
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
    for repository_log_entry in project_data['repository_log']:
        if repository_log_entry.has_key('jira_issues_keys_id'):
            deffective = False;
            for isses_id in repository_log_entry['jira_issues_keys_id']:
                if get_issue_type_for_jira_key(project_data['jira_key'] + '-' + isses_id) in JIRA_BUGS_ISSUE_TYPE_ID_LIST:
                    deffective = True
            if deffective:
                defective_file_list.extend(repository_log_entry['paths'])
    return set(defective_file_list)
