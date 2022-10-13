# -*- coding: utf-8 -*-
import ApiTools
import models
import json
from loggerTools import get_normal_logger, get_exception_logger
from SonarSettings import SONAR_URL, PROJECTS_API, RESOURCES_API, COMPONENTS_API, METRICS_API
from SonarSettings import AVAILABLE_METRICS_TYPE_LIST, MAX_METRICS_PER_REQUEST, PAGE_SIZE, PREFIX_LOG_LENGTH
from DatabaseTools import project_exists


def get_all_metric_keys_as_list():
    metric_keys_list  = []
    metrics_keys_from_api = get_all_metric_keys_from_api()
    if metrics_keys_from_api['total'] > metrics_keys_from_api['ps']:
        get_exception_logger().exception("Not collected all metrics")
    for metric_data in metrics_keys_from_api['metrics']:
        if metric_data['type'] in AVAILABLE_METRICS_TYPE_LIST:
            metric_keys_list.append(metric_data['key'])
    return metric_keys_list


def get_all_metric_keys_from_api():
    params = dict(
        ps = PAGE_SIZE,
    )
    return ApiTools.get_json_from_api(SONAR_URL+METRICS_API, params)


def get_all_parts_of_metric_keys_list_of_string():
    result_list = []
    all_metric_keys_as_list = get_all_metric_keys_as_list()
    metrics_keys_count = len(all_metric_keys_as_list)
    for i in range(0,metrics_keys_count, MAX_METRICS_PER_REQUEST):
        result_list.append(','.join(all_metric_keys_as_list[i:i+15]))
    return result_list


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
        creation_date = __get_create_data_from_project_Last_version(project)
        if set(['k', 'nm']).issubset(project.keys()) and creation_date:
            proj = models.Project(key=project['k'], name=project['nm'], creation_date=creation_date)
            result_list.append(proj)
        else:
            get_normal_logger().warn('Cannot create Project object form this project JSON response:\n{0:{1}}{2}.'.format('', PREFIX_LOG_LENGTH, project))
    get_normal_logger().info('Created {0} corrected Project objects.'.format(len(result_list)))
    return result_list


# Metoda zwraca nam listę słowników z miarami zapytania API dla każdego pliku należącego do projektu przekazanago w parametrze 
def get_metrics_APIlist_per_file_for_project(projectKey):
    metrics_dict_all_files = {}
    pageIndex = 1
    totalFiles = -1
    savedFiles = 0
    while totalFiles == -1 or savedFiles < totalFiles:
        for part_of_metric_keys in get_all_parts_of_metric_keys_list_of_string():
            params = dict(
                baseComponentKey = projectKey,
                metricKeys = part_of_metric_keys,
                qualifiers = 'FIL',
                p=pageIndex,
                ps=PAGE_SIZE,
            )
            x = ApiTools.get_json_from_api(SONAR_URL+RESOURCES_API, params)
            if totalFiles == -1:
                totalFiles = x['paging']['total']
                print "W projecie " + str(projectKey) + " jest " + str(totalFiles) + " plikow"
            savedFiles = pageIndex*PAGE_SIZE
            for component in x['components']:
                metrics_dict_for_file = {}
                for measure in  component['measures']:
                    value = None
                    if measure.has_key('periods'):
                        value = measure['periods'][0]['value']
                    elif measure.has_key('value'):
                        value = measure['value']
                    metrics_dict_for_file[measure['metric']] = value
                if metrics_dict_all_files.has_key(component['key']):
                    metrics_dict_all_files[component['key']].update(metrics_dict_for_file)
                else:
                    metrics_dict_all_files[component['key']] = metrics_dict_for_file
        pageIndex = pageIndex + 1
    return metrics_dict_all_files.items()


# Metoda zwraca nam listę obiektów Metric
def get_metrics_objects_list_per_file(projectKey, db_name):
    metric_object_list = []
#     metrics_list = get_metricsTuple_list_per_file(get_metrics_APIlist_per_file_for_project(projectKey))
    if not project_exists(db_name):
        metrics_list = get_metrics_APIlist_per_file_for_project(projectKey)
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
    if project.has_key('k'):
        params = dict(
            component = project['k'],
        )
        api_response = ApiTools.get_json_from_api(SONAR_URL+COMPONENTS_API, params)
        if api_response['component'].has_key('analysisDate'):
            return api_response['component']['analysisDate']
    return None


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
