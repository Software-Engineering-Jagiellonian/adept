# -*- coding: utf-8 -*-
import ApiTools
import models
import json
from loggerTools import get_normal_logger, PREFIX_LOG_LENGTH

SONAR_URL = ''
RESOURCES_API = 'api/resources/index'
PROJECTS_API = 'api/projects/index'

#TempVariable
TEXAS_KEY = ''


#Metoda zwracając wszystkie możliwe metryki w wersji 4.5
def get_all_metric_keys():
    by_line = 'conditions_by_line,covered_conditions_by_line,coverage_line_hits_data,lines_to_cover,new_lines_to_cover'
    complexity = 'complexity,class_complexity,file_complexity,function_complexity'
    design = 'file_cycles,file_edges_weight,package_tangles,file_tangles,file_tangle_index,package_cycles,package_feedback_edges,package_tangle_index,package_edges_weight,file_feedback_edges'
    documentation = 'comment_lines,comment_lines_density,public_documented_api_density,public_undocumented_api'
    duplications = 'duplicated_blocks,duplicated_files,duplicated_lines,duplicated_lines_density'
    issues = 'new_violations,new_xxxxx_violations,violations,xxxxx_violations,false_positive_issues,open_issues,confirmed_issues,reopened_issues,weighted_violations,violations_density,sqale_index'
    size = 'accessors,classes,directories,files,generated_lines,generated_ncloc,cobol_inside_ctrlflow_statements,lines,ncloc,cobol_data_division_ncloc'
    tests = 'branch_coverage,new_branch_coverage,branch_coverage_hits_data,coverage,new_coverage,line_coverage,new_line_coverage,skipped_tests,uncovered_conditions,new_uncovered_conditions,uncovered_lines,new_uncovered_lines,tests,test_execution_time,test_errors,test_failures,test_success_density'
    keys_list = [complexity, design, documentation, duplications, issues, size, tests ]
    return ','.join(keys_list)


# Metoda zwracająca wszystkie dane z sonara w postaci listy krotek (Project, [Metrics]) 
def get_compleate_metrics_tuple_list():
    tuple_list = []
    projects_list = get_project_objects_list(get_projects_APIlist())
    for project in projects_list:
        tuple_list.append((project, get_metrics_objects_list_per_file(project.key, project.db_name)))
    get_normal_logger().info('Collected {0} projects with metrics per file.'.format(len(tuple_list)))
    return tuple_list


# Metoda zwraca nam listę słowników zapytania API z danymi o projektach 
def get_projects_APIlist():
    params = dict(
        format = 'json',
        desc = 'false',
        versions = 'true',
    )
    Api_response = ApiTools.get_json_from_api(SONAR_URL+PROJECTS_API, params)
    get_normal_logger().info('Sonar API returned {0} projects.'.format(len(Api_response)))
    return Api_response


# metoda zwraca name listę obiektów Project
def get_project_objects_list(projects_APIlist):
    result_list = []
    for project in projects_APIlist:
        if set(['k', 'nm', 'v']).issubset(project.keys()) and len(project['v'])>0:
            proj = models.Project(key=project['k'], name=project['nm'], creation_date=__get_create_data_from_project_Last_version(project))
            result_list.append(proj)
        else:
            get_normal_logger().warn('Cannot create Project object form this project JSON response:\n{0:{1}}{2}.'.format('', PREFIX_LOG_LENGTH, project))
    get_normal_logger().info('Created {0} corrected Project objects.'.format(len(result_list)))
    return result_list


# Metoda zwraca nam listę słowników z miarami zapytania API dla każdego pliku należącego do projektu przekazanago w parametrze 
def get_metrics_APIlist_per_file_for_project(projectKey):
    params = dict(
        format = 'json',
        resource = projectKey,
        scopes = 'FIL',
        depth = -1,
        metrics = get_all_metric_keys(),
    )
    Api_response = ApiTools.get_json_from_api(SONAR_URL+RESOURCES_API, params)
    return Api_response


# Metoda zwraca nam listę obiektów Metric
def get_metrics_objects_list_per_file(projectKey, db_name):
    metric_object_list = []
    metrics_list = get_metricsTuple_list_per_file(get_metrics_APIlist_per_file_for_project(projectKey))
    for metric in metrics_list:
        metric_object = models.Metric(file_name=metric[0], metric_dump=json.dumps(metric[1]), db_name=db_name)
        metric_object_list.append(metric_object)
    return metric_object_list


# Metoda zwraca nam listę krotek zawierając (klucz, {metryki}) 
def get_metricsTuple_list_per_file(metrics_APIlist_per_file):
    metrics_list = []
    for metric in metrics_APIlist_per_file:
        if metric.has_key('msr'):
            metrics_list.append((metric['key'], __get_metrics_dict_from_API_MSRlist(metric['msr'])))
    return metrics_list


# metoda zwraca nam datę utworzenia ostatniej wersji metryk
def __get_create_data_from_project_Last_version(project):
    if not project.has_key('lv'):
        project['lv'] =  project['v'].keys()[0]
    return project['v'][project['lv']]['d']


# Przerabia słownik metryk otrzymany z API na nasz słownik
def __get_metrics_dict_from_API_MSRlist(API_MSRmetric_dict):
    metrics_dict = {}
    for metric in API_MSRmetric_dict:
        metrics_dict[metric['key']] = __get_value_from_APIMSRmetric(metric)
    return metrics_dict    


def __get_value_from_APIMSRmetric(metric):
    if metric.has_key('val'):
        return metric['val']
    elif metric.has_key('data'):
        return metric['data']
    return ''
