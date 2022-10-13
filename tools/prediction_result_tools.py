"""
tools.db_tools
~~~~~~~~~~~~

Modul przetowrzenia wynikow Adepta do table z ktorych kozysta API 

:copyright:
:license:

"""

from db_tools import save_to_db, get_select_result_field_value_or_None, get_select_result_field_value_or_default, get_select_result_list
from sonar_tools import get_latest_snapshot_date_adept_prediction_result_for_project, get_latest_snapshot_name_adept_prediction_result_for_project, get_metrics_for_version
from data_source_db_tools import get_list_of_data_sources_for_all_projects
from settings import R_TABLE_MODEL_ID, R_TABLE_DEFAULT_VERSION, R_TABLE_DEFAULT_PREDICTION_VERSION
from warnings import filterwarnings, resetwarnings
import MySQLdb


def move_raw_predicton_to_R_tables_for_all_projects():
    """Uzupelnia nam dostpeno przez api baze dancyh najnowszymi wynikami predykcji dla pojektow

    :return:   Nic
    :rtype: None
    """

    data_sources_for_projects = get_list_of_data_sources_for_all_projects()
    for data_sources_for_project in data_sources_for_projects:
        try:
            move_raw_predicton_to_R_tables_for_project(data_sources_for_project.get('SonarName'), data_sources_for_project.get('MetricGeneratorKey'))
        except Exception as e:
            print e

def move_raw_predicton_to_R_tables_for_project(project_sonar_name, sonar_key):
    """Uzupelnia nam dostpeno przez api baze dancyh najnowszymi wynikami predykcji dla pojektu

    :param project_sonar_name:  Nazwa projektu z sonara
    :return:   Nic
    :rtype: None
    """

    if not __exitst_result_table_for_sonar_key(sonar_key):
        __creat_R_table_if_not_exist(project_sonar_name, sonar_key)
        print 'Create table for project {}, and sonar key {}'.format(project_sonar_name, sonar_key)
    print project_sonar_name, ': ',
    if __can_move_raw_predicton_to_R_tables(project_sonar_name):
        print "update"
        R_table_prediction_results_list = __get_R_table_prediction_results_list(project_sonar_name)
        __save_R_table_results_list_to_database(R_table_prediction_results_list)
        return R_table_prediction_results_list
    else:
        print "No update"


def __save_R_table_results_list_to_database(R_table_prediction_results_list):
    """Zapisuje wyniki predykcji do bazy danych dostpenej z api

    :param R_table_prediction_results_list:  Lista metryk z wynikami predykjic dla plikow 
    :return:  Nic
    :rtype: None
    """

    for R_table_prediction_result_dict in R_table_prediction_results_list:
        save_query = __creat_save_query_to_R_table_results_list_to_database(R_table_prediction_result_dict)
        save_to_db(save_query, True)


def __get_R_table_prediction_results_list(project_sonar_name):
    """Zwraca wyniki predykcji w poscati listy

    :param project_sonar_name:  Nazwa projektu z sonara
    :return:   wyniki predykcji w poscati listy
    :rtype: List
    """

    latest_snapshot_name_adpept_prediction_result = get_latest_snapshot_name_adept_prediction_result_for_project(project_sonar_name)
    print latest_snapshot_name_adpept_prediction_result
    metrics_for_latest_snapshot_adpept_prediction_result = get_metrics_for_version(latest_snapshot_name_adpept_prediction_result)
    R_table_prediction_result_list = []
    c = 0
    for metric_for_latest_snapshot_adpept_prediction_result in metrics_for_latest_snapshot_adpept_prediction_result:
#         if metrics_for_latest_snapshot_adpept_prediction_result[c]['prediction'] >0:
#         print '{}/{}'.format(c,len(metrics_for_latest_snapshot_adpept_prediction_result))
#         print metrics_for_latest_snapshot_adpept_prediction_result[c]['prediction']
        c = c + 1
        R_table_prediction_result_list.append(__get_R_table_prediction_result_dict(metric_for_latest_snapshot_adpept_prediction_result, project_sonar_name))
    return R_table_prediction_result_list


def __exitst_result_table_for_sonar_key(sonar_key):
    query = "SELECT * FROM ResultTables WHERE sonarKey = '{}'".format(sonar_key)
    result = get_select_result_list(query, True)
    return len(result) > 0


def __creat_R_table_if_not_exist(project_sonar_name, sonar_key):
    """Sprawdza czy istnieje R_table jesli nie to ja tworzy 

    :param project_sonar_name: Nazwa projektu z sonara
    :return: Nie zwracamy nic 
    :rtype: None
    """

    R_table_name = __project_sonar_name_to_R_table_name(project_sonar_name)
    count = 0
    while __R_table_name_exists(R_table_name):
        count = count + 1
        R_table_name = __project_sonar_name_to_R_table_name(project_sonar_name, count=count)
    create_query = 'CREATE TABLE IF NOT EXISTS R_{0} ( Project varchar(255), Version varchar(255), Date date, Module text, Prediction char(2), UsedModel int(11), PredictionVersion int(11), Function  varchar(255), Notes  varchar(255) );'.format(R_table_name)
    filterwarnings('ignore', category = MySQLdb.Warning)
    save_to_db(create_query, result = True)
    resetwarnings()
    __add_to_resultTable(project_sonar_name, sonar_key, R_table_name)
    __add_admin_user_to_project(R_table_name, project_sonar_name, sonar_key)


def __can_move_raw_predicton_to_R_tables(project_sonar_name):
    """Sprawdza czy mamy nowsze wyniki predyckji do umieszczenia w api

    :param project_sonar_name:  Nazwa projektu z sonara
    :return: mozliwosc przeniesiena nowych wynikow predykji
    :rtype: Bool
    """

    latest_snapshot_date_adept_prediction = get_latest_snapshot_date_adept_prediction_result_for_project(project_sonar_name)
    latest_R_table_date_prediction_result = __get_latest_R_table_date_prediction_result_for_project(project_sonar_name)
    if latest_snapshot_date_adept_prediction:
        if not latest_R_table_date_prediction_result:
            return True
        if latest_snapshot_date_adept_prediction.date() > latest_R_table_date_prediction_result:
            return True
    return False


def __creat_save_query_to_R_table_results_list_to_database(R_table_prediction_result_dict):
    """Tworzy zapytanie zapisujace wyniki preducji w bazie danych 

    :param R_table_prediction_result_dict: Wyniki predyckji do zapisania w bazie dancyh
    :return: nic
    :rtype: None
    """

    return 'INSERT INTO R_{0} (Project, Version, Date, Module, Prediction, UsedModel, PredictionVersion, Function, Notes) VALUES (\'{project}\', {version}, CAST(\'{date}\' AS date),  \'{module}\', {prediction}, {used_model}, {prediction_version}, "", "")'.format(__project_sonar_name_to_R_table_name(R_table_prediction_result_dict.get('project')), **R_table_prediction_result_dict)


def __get_R_table_prediction_result_dict(metric_for_latest_snapshot_adpept_prediction_result, project_sonar_name):
    """Zwraca wynik predykcji dla metryk

    :param metric_for_latest_snapshot_adpept_prediction_result:  Matryki sonarowe dla pluku
    :param project_sonar_name:  Nazwa projektu z sonara
    :return:  wynik predykcji dla metryk
    :rtype: dict
    """

    R_table_prediction_result_dict = {}
    R_table_prediction_result_dict['module'] = __get_module_name_from_metric_for_latest_snapshot_adpept_prediction_result(metric_for_latest_snapshot_adpept_prediction_result)
    R_table_prediction_result_dict['prediction'] = __get_prediction_result_from_metric_for_latest_snapshot_adpept_prediction_result(metric_for_latest_snapshot_adpept_prediction_result)
    R_table_prediction_result_dict['used_model'] = R_TABLE_MODEL_ID
    R_table_prediction_result_dict['version'] = R_TABLE_DEFAULT_VERSION
    R_table_prediction_result_dict['project'] = project_sonar_name
    R_table_prediction_result_dict['date'] = get_latest_snapshot_date_adept_prediction_result_for_project(project_sonar_name).date()
    R_table_prediction_result_dict['prediction_version'] = __get_incremented_prediction_version_for_project(project_sonar_name)
    return R_table_prediction_result_dict


def __get_module_name_from_metric_for_latest_snapshot_adpept_prediction_result(metric_for_latest_snapshot_adpept_prediction_result):
    """Zwraca nazwe modulu dla metryk 

    :param metric_for_latest_snapshot_adpept_prediction_result:  Matryki sonarowe dla pluku
    :return:  nazwa modulu dla metryk
    :rtype: str
    """

    subproject_name = __get_subproject_name_from_metric_for_latest_snapshot_adpept_prediction_result(metric_for_latest_snapshot_adpept_prediction_result)
    file_path = __get_file_path_from_metric_for_latest_snapshot_adpept_prediction_result(metric_for_latest_snapshot_adpept_prediction_result)
    file_path = file_path.replace('/', '\\\\')
    return '{0}\\\\{1}'.format(subproject_name, file_path)


def __get_incremented_prediction_version_for_project(project_sonar_name):
    """Zwraca powiekszona wercje predykcji dla projektu

    :param project_sonar_name:  Nazwa projektu z sonara
    :return: powiekszona wercje predykcji dla projektu
    :rtype: int
    """

    return __get_latest_prediction_version_for_project(project_sonar_name) + 1


def __get_file_path_from_metric_for_latest_snapshot_adpept_prediction_result(metric_for_latest_snapshot_adpept_prediction_result):
    """Zwraca scierzke pliku dla metryk

    :param metric_for_latest_snapshot_adpept_prediction_result:  Matryki sonarowe dla pluku
    :return: scierzke pliku dla metryk
    :rtype: str
    """

    return metric_for_latest_snapshot_adpept_prediction_result.get('file_name').split(':')[-1]


def __get_subproject_name_from_metric_for_latest_snapshot_adpept_prediction_result(metric_for_latest_snapshot_adpept_prediction_result):
    """Zwraca nazwe podprojektu dla danego pliku 

    :param metric_for_latest_snapshot_adpept_prediction_result:  Matryki sonarowe dla pluku
    :return: nazwe podprojektu dla danego pliku
    :rtype: str
    """

    return metric_for_latest_snapshot_adpept_prediction_result.get('file_name').split(':')[-2]


def __get_latest_prediction_version_for_project(project_sonar_name):
    """Zwracamy nazwe date najnowszego zrzutu metryk dla nazwy projetku z sonara 

    :param project_sonar_name: Nazwa projektu z sonara
    :return: data najnowszego zrzutu metryk 
    :rtype: Datetime
    """

    select_query = 'SELECT PredictionVersion FROM R_{0} GROUP BY Version, PredictionVersion ORDER BY PredictionVersion DESC, Version DESC LIMIT 1;'.format(__project_sonar_name_to_R_table_name(project_sonar_name))
    return get_select_result_field_value_or_default(select_query, 'PredictionVersion', R_TABLE_DEFAULT_PREDICTION_VERSION, True)



def __get_prediction_result_from_metric_for_latest_snapshot_adpept_prediction_result(metric_for_latest_snapshot_adpept_prediction_result):
    """Zwraca wynik predykcji dla metryk

    :param metric_for_latest_snapshot_adpept_prediction_result:  Matryki sonarowe dla pluku
    :return:  wynik predykcji dla metryk
    :rtype: int
    """

    return metric_for_latest_snapshot_adpept_prediction_result.get('prediction')


def __add_admin_user_to_project(R_table_name, project_sonar_name, sonar_key):
    insert_query = 'INSERT INTO Users(User, R_Table, ProjectName, Extension, SonarKey) VALUES ("admin", "{0}", "{1}", "", "{2}")'.format(R_table_name, project_sonar_name, sonar_key)
    save_to_db(insert_query)


def __add_to_resultTable(project_sonar_name, sonar_key, R_table_name):
    insert_query = "INSERT INTO ResultTables(sonarKey, sonarName, resultTableName) VALUES('{}', '{}', '{}')".format(sonar_key, project_sonar_name, R_table_name)
    save_to_db(insert_query, True) 


def __R_table_name_exists(R_table_name):
    query = "SELECT * FROM ResultTables WHERE resultTableName = '{}'".format(R_table_name)
    result = get_select_result_list(query, True)
    return len(result) > 0


def __project_sonar_name_to_R_table_name(project_sonar_name, count = 0):
    """Zwracamy nazwe projektu do stworzenia R_table 

    :param project_sonar_name: Nazwa projektu z sonara
    :return: nazwe projektu do stworzenia R_table 
    :rtype: str
    """

    return ''.join(e for e in project_sonar_name if e.isalnum()) + '_' +str(count)


def __get_latest_R_table_date_prediction_result_for_project(project_sonar_name):
    """Zwracamy nazwe date najnowszego zrzutu metryk dla nazwy projetku z sonara 

    :param project_sonar_name: Nazwa projektu z sonara(
    :return: data najnowszego zrzutu metryk 
    :rtype: Datetime
    """

    select_query = 'SELECT Date FROM R_{0} ORDER BY Date DESC LIMIT 1'.format(__project_sonar_name_to_R_table_name(project_sonar_name))
    return get_select_result_field_value_or_None(select_query, 'Date', True)

