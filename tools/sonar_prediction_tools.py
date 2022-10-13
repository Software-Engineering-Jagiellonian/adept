# -*- coding: utf-8 -*-
"""
tools.sonar4_prediction_tools
~~~~~~~~~~~~

Modul pobiera dane ze zrodel i wykonuje dla nich predyckcje

Uzyte klasyfikatory
Random Forest


Algorytm przeciwdzia�aniu niezbalanoswaniu klas:
SMOTE

:copyright:
:license:

"""

import json
import numpy
from sklearn.feature_extraction import DictVectorizer
from sonar_tools import get_oldest_db_name_for_project, get_latest_db_name_for_project, get_metrics_for_version
from data_source_db_tools import get_list_of_data_sources_for_projects_with_sonar_bugtracke_repository_data, get_list_of_data_sources_for_all_projects
from db_tools import get_select_result_list, get_select_result, save_to_db
from logger_tools import initialize_loggers, get_normal_logger, get_exception_logger
from sklearn.cross_validation import train_test_split
from sklearn.ensemble  import RandomForestClassifier
from sklearn.metrics import matthews_corrcoef
from imblearn.over_sampling import SMOTE


def make_prediction_for_all_projects():
    """Metoda przechodz po wszystkich projektach posiadajacych uzupelnione zrodla dancyh i wykonuje dla nich predykcje z zapsiem do bazy danych

    :return: Nic
    :rtype: None
    """

#     initialize_loggers()
    normal_logger = get_normal_logger()
    data_sources_for_projects = get_list_of_data_sources_for_all_projects()
    normal_logger.info('Prediction for ' + str(len(data_sources_for_projects)) + ' project')
    [default_classifier, default_vectorizer] = get_default_classifier_and_vectorizer_for_global_prediction()
    for data_sources_for_project in data_sources_for_projects:
        if __ready_for_prediction(data_sources_for_project) and __can_create_prediction(data_sources_for_project):
            normal_logger.info('Start  prediction for : ' + data_sources_for_project['SonarName'])
            vectorizer = DictVectorizer()
            classifier = __get_classifier_for_project(data_sources_for_project, vectorizer)
            new_metric_for_files = __get_metrics_for_latest_version(data_sources_for_project)
            new_features, _, _ = __get_feature_for_project(new_metric_for_files)
            X = vectorizer.transform(new_features).toarray()
            X = __remove_indexes_from_feature_array(X, vectorizer.get_feature_names())
            predicted_categories = classifier.predict(X)
            for i in range(len(new_metric_for_files)):
                new_metric_for_files[i]['prediction'] = predicted_categories[i]
                __save_prediction_to_database(new_metric_for_files[i]['db_name'], new_metric_for_files[i]['file_name'], new_metric_for_files[i]['prediction'])
        else:
            normal_logger.info('Default classifier: ' + data_sources_for_project['SonarName'])
            new_metric_for_files = __get_metrics_for_latest_version(data_sources_for_project)
            if len(new_metric_for_files) > 0:
                new_features, _, _ = __get_feature_for_project(new_metric_for_files)
                X = default_vectorizer.transform(new_features).toarray()
                X = __remove_indexes_from_feature_array(X, default_vectorizer.get_feature_names())
                predicted_categories = default_classifier.predict(X)
                count = 0
                for i in range(len(new_metric_for_files)):
                    if new_metric_for_files[i]['prediction'] > 0:
                        count = count + 1
                    new_metric_for_files[i]['prediction'] = predicted_categories[i]
                    __save_prediction_to_database(new_metric_for_files[i]['db_name'], new_metric_for_files[i]['file_name'], new_metric_for_files[i]['prediction'])


def get_default_classifier_and_vectorizer_for_global_prediction():
    """Metoda zwraca nam klasyfikator wytrenowany na wszystkich możliwych projektach oraz vectorizer

    :param data_sources_for_project: slownik zawieracjacy dane projektu
    {
        'RepositoryURL': '',
        'RepositoryType': int, //(Repository type id from database)
        'MetricGeneratorType': int, //(MetricGenerator type id from database)
        'MetricGeneratorKey': '',
        'BugTrackerName': '',
        'SonarName': '',
        'RepositoryName': '',
        'BugTrackerType': int, //(BugTracker type id from database)
    }
    :return: (Wytrenowany klasyfikator; vectorizer)
    :rtype: (Classifier //sklearna, vectorizer)
    """
    
    data_sources_for_projects = get_list_of_data_sources_for_projects_with_sonar_bugtracke_repository_data()
    metrics_for_files = []
    for data_sources_for_project in data_sources_for_projects:
        if __have_project_real_classification_for_oldest_version(data_sources_for_project):
            metrics_for_files.extend(__get_metrics_for_oldest_version(data_sources_for_project))
    vectorizer = DictVectorizer()
    classifier = get_default_classifier_for_global_prediction(metrics_for_files, vectorizer)
    return (classifier, vectorizer)


def get_default_classifier_for_global_prediction(metrics_for_files, vectorizer):
    """Metoda zwraca nam klasyfikator wytrenowany na wszystkich możliwych projektach 

    :param data_sources_for_project: slownik zawieracjacy dane projektu
    {
        'RepositoryURL': '',
        'RepositoryType': int, //(Repository type id from database)
        'MetricGeneratorType': int, //(MetricGenerator type id from database)
        'MetricGeneratorKey': '',
        'BugTrackerName': '',
        'SonarName': '',
        'RepositoryName': '',
        'BugTrackerType': int, //(BugTracker type id from database)
    }
    :return: Wytrenowany klasyfikator
    :rtype: Classifier //sklearna
    """

    features, categories, _ = __get_feature_for_project(metrics_for_files)
    __add_indexes_for_features(features)
    X = vectorizer.fit_transform(features).toarray()
    X_train, X_test, Y_train, Y_test = train_test_split(X, categories, test_size=.5)
    X_train = __remove_indexes_from_feature_array(X_train, vectorizer.get_feature_names())
    sm = SMOTE(kind='regular')
    try:
        X_resampled, Y_resampled = sm.fit_sample(X_train, Y_train)
    except Exception:
        X_resampled = X_train
        Y_resampled = Y_train
    my_classifier = __create_classifier()
    my_classifier.fit(X_resampled, Y_resampled)
    X_test = __remove_indexes_from_feature_array(X_test, vectorizer.get_feature_names())
    test_predicted_categories = my_classifier.predict(X_test)
    get_normal_logger().info("\tDefault matthews:\t" + str(matthews_corrcoef(Y_test, test_predicted_categories)))
    return my_classifier


def __get_classifier_for_project(data_sources_for_project, vectorizer):
    """Metoda zwraca nam wytrenowany na najstarszych metrykach klasyfikator

    :param data_sources_for_project: slownik zawieracjacy dane projektu
    {
        'RepositoryURL': '',
        'RepositoryType': int, //(Repository type id from database)
        'MetricGeneratorType': int, //(MetricGenerator type id from database)
        'MetricGeneratorKey': '',
        'BugTrackerName': '',
        'SonarName': '',
        'RepositoryName': '',
        'BugTrackerType': int, //(BugTracker type id from database)
    }
    :return: Wytrenowany klasyfikator
    :rtype: Classifier //sklearna
    """

    metrics_for_files = __get_metrics_for_oldest_version(data_sources_for_project)
    features, categories, file_names = __get_feature_for_project(metrics_for_files)
    classifier = __get_classifier_for_fatures(features, categories, file_names, data_sources_for_project['SonarName'], vectorizer)
    return classifier


def __get_feature_for_project(metrics_for_files):
    """Metoda zwraca nam cechy oraz klasy dla plikow

    :param metrics_for_files: Lista slownikow z metrykami
    [
        {
            'nazwa metryki': int,
            ...
        },
        ...
    ]
    :return: [lista slownikow z metrykami dla plikow, lista klas dla plikow]
    :rtype: [List of dicts, list]
    """

    X = []
    Y = []
    file_names = []
    for metrics_for_file in metrics_for_files:
        if  metrics_for_file.has_key('metric_dump'):
            metrics = __get_adept_normalized_metrics(json.loads(metrics_for_file['metric_dump']))
            X.append(metrics)
            Y.append(metrics_for_file['defects'])
            file_names.append(metrics_for_file['file_name'])
    return [X, Y, file_names]


def __get_adept_normalized_metrics(metric_dump):
    """Metoda zwraca nam cechy w postanci znormalizowanej(każdy plik ma wypelnione wszystkie metryki jakie pobieramy z sonara, Puste uzupelniamy 0

    :param metric_dump: slownik z metrykami
    {
        'nazwa metryki': int,
        ...
    }
    :return: cechy w postanci znormalizowanej
    :rtype: dict
    """

    adept_metrics_list = __get_adept_metrics_list()
    adept_normalized_metrics_dict = {}
    for adept_metric in adept_metrics_list:
        adept_normalized_metrics_dict[adept_metric] = metric_dump.get(adept_metric, 0)
    return adept_normalized_metrics_dict


def __get_classifier_for_fatures(features, categories, file_names, sonar_project_name, vectorizer):
    """Metoda zwraca nam wytrenowany na najstarszych metrykach klasyfikator i zapisuje predykcje testowa do bazy danych 

    :param features: lista slownikow z znormalizowanymi metrykami  dla plikow
    :param categories: lista klas dla plikow
    :return: Wytrenowany klasyfikator
    :rtype: Classifier //sklearn
    """

    __add_indexes_for_features(features)
    X = vectorizer.fit_transform(features).toarray()
    X_train, X_test, Y_train, Y_test = train_test_split(X, categories, test_size=.5)
    X_train = __remove_indexes_from_feature_array(X_train, vectorizer.get_feature_names())
    sm = SMOTE(kind='regular')
    try:
        X_resampled, Y_resampled = sm.fit_sample(X_train, Y_train)
    except Exception:
        X_resampled = X_train
        Y_resampled = Y_train
    my_classifier = __create_classifier()
    my_classifier.fit(X_resampled, Y_resampled)
    test_metric_ids = __get_ids_list_from_metrics(X_test, vectorizer.get_feature_names())
    X_test = __remove_indexes_from_feature_array(X_test, vectorizer.get_feature_names())
    test_predicted_categories = my_classifier.predict(X_test)
    __save_test_preidiction_to_database(test_metric_ids, test_predicted_categories, file_names, sonar_project_name)
    get_normal_logger().info("\tmatthews:\t" + str(matthews_corrcoef(Y_test, test_predicted_categories)))
    return my_classifier


def __remove_indexes_from_feature_array(train_features, feature_names):
    return numpy.delete(train_features, numpy.s_[feature_names.index('id')], axis=1)


def __add_indexes_for_features(features):
    for i in range(len(features)):
        features[i]['id'] = i


def __get_ids_list_from_metrics(metrics, feature_names):
    ids = []
    for metric in metrics:
        ids.append(metric[feature_names.index('id')])
    return ids


def __create_classifier():
    """Metoda zwraca nowa klase z niewytrenowanym klasyfikatorem

    :return: Niewytrenowany klasyfikator
    :rtype: Classifier //sklearn
    """

    return RandomForestClassifier(n_estimators=100)


def __can_create_prediction(data_sources_for_project):
    """Sprawdza czy dane projektu spelniaja minimalne wymagania do zbudowania modelu predyckji

    :param data_sources_for_project: slownik zawieracjacy dane projektu
    {
        'RepositoryURL': '',
        'RepositoryType': int, //(Repository type id from database)
        'MetricGeneratorType': int, //(MetricGenerator type id from database)
        'MetricGeneratorKey': '',
        'BugTrackerName': '',
        'SonarName': '',
        'RepositoryName': '',
        'BugTrackerType': int, //(BugTracker type id from database)
    }
    :return: Wynik sprawdzenia czy dane projektu spelniaja minimalne wymagania do zbudowania modelu predyckji
    :rtype: Boolean
    """
    
    return __have_project_more_that_one_metric_snapshot(data_sources_for_project) and __have_project_real_classification_for_oldest_version(data_sources_for_project)


def __ready_for_prediction(data_sources_for_project):
    """Sprawdza czy dane projektu maja ustawiona flage gotowosci do predykcji

    :param data_sources_for_project: slownik zawieracjacy dane projektu
    {
        'RepositoryURL': '',
        'RepositoryType': int, //(Repository type id from database)
        'MetricGeneratorType': int, //(MetricGenerator type id from database)
        'MetricGeneratorKey': '',
        'BugTrackerName': '',
        'SonarName': '',
        'RepositoryName': '',
        'BugTrackerType': int, //(BugTracker type id from database)
    }
    :return: Wynik sprawdzenia czy dane projektu maja ustawiona flage gotowosci do predykcji
    :rtype: Boolean
    """
    
    return data_sources_for_project['Ready'] > 0


def __have_project_real_classification_for_oldest_version(data_sources_for_project):
    """Sprawdza czy dany projekt ma zklasyfikowne pliki dla pierwszego zrzutu metryk z sonara

    :param data_sources_for_project: slownik zawieracjacy dane projektu
    {
        'RepositoryURL': '',
        'RepositoryType': int, //(Repository type id from database)
        'MetricGeneratorType': int, //(MetricGenerator type id from database)
        'MetricGeneratorKey': '',
        'BugTrackerName': '',
        'SonarName': '',
        'RepositoryName': '',
        'BugTrackerType': int, //(BugTracker type id from database)
    }
    :return: Wynik sprawdzenia czy dany projekt ma zklasyfikowne pliki dla pierwszego zrzutu metryk z sonara
    :rtype: Boolean
    """

    metric_for_files = __get_metrics_for_oldest_version(data_sources_for_project)
    for metric_for_file in metric_for_files:
        if metric_for_file['defects'] not in [1, 0]:
            return False
    return True


def __have_project_more_that_one_metric_snapshot(data_sources_for_project):
    """Sprawdza czy dany projekt ma ponad 1 zrzut metryk z sonara

    :param data_sources_for_project: slownik zawieracjacy dane projektu
    {
        'RepositoryURL': '',
        'RepositoryType': int, //(Repository type id from database)
        'MetricGeneratorType': int, //(MetricGenerator type id from database)
        'MetricGeneratorKey': '',
        'BugTrackerName': '',
        'SonarName': '',
        'RepositoryName': '',
        'BugTrackerType': int, //(BugTracker type id from database)
    }
    :return: Wynik sprawdzenia czy dany projekt ma ponad 1 zrzut metryk z sonara
    :rtype: Boolean
    """

    query = 'SELECT COUNT(*) \"len\" FROM Projects WHERE name = \"' + data_sources_for_project['SonarName'] + '\"'
    return get_select_result(query)['len'] > 1


def __get_metrics_for_oldest_version(data_sources_for_project):
    """Metoda oczytuje z bazy danych i zwraca najstarszy zrzut metryk z sonara4 dla podancyh zrodel danych 

    :param data_sources_for_project: slownik zawieracjacy dane projektu
    {
        'RepositoryURL': '',
        'RepositoryType': int, //(Repository type id from database)
        'MetricGeneratorType': int, //(MetricGenerator type id from database)
        'MetricGeneratorKey': '',
        'BugTrackerName': '',
        'SonarName': '',
        'RepositoryName': '',
        'BugTrackerType': int, //(BugTracker type id from database)
    }
    :return: Lista slownikow z metrykami
    [
        {
            'nazwa metryki': int,
            ...
        },
        ...
    ]
    :rtype: List
    """

    db_name = get_oldest_db_name_for_project(data_sources_for_project['SonarName'])
    return get_metrics_for_version(db_name)


def __get_metrics_for_latest_version(data_sources_for_project):
    """Metoda oczytuje z bazy danych i zwraca najnowszy zrzut metryk z sonara4 dla podancyh zrodel danych 

    :param data_sources_for_project: slownik zawieracjacy dane projektu
    {
        'RepositoryURL': '',
        'RepositoryType': int, //(Repository type id from database)
        'MetricGeneratorType': int, //(MetricGenerator type id from database)
        'MetricGeneratorKey': '',
        'BugTrackerName': '',
        'SonarName': '',
        'RepositoryName': '',
        'BugTrackerType': int, //(BugTracker type id from database)
    }
    :return: Lista slownikow z metrykami dla najnowszego zrzutu
    [
        {
            'nazwa metryki': int,
            ...
        },
        ...
    ]
    :rtype: List
    """

    db_name = get_latest_db_name_for_project(data_sources_for_project['SonarName'])
    return get_metrics_for_version(db_name)


def __save_test_preidiction_to_database(test_metric_ids, test_predicted_categories, file_names, sonar_project_name):
    db_name = get_oldest_db_name_for_project(sonar_project_name)
    save_to_db('UPDATE Metrics SET prediction= -2 WHERE db_name=\"' + db_name + '\";')
    for i in range(len(test_predicted_categories)):
        file_name = file_names[test_metric_ids[i].astype(int)]
        save_to_db('UPDATE Metrics SET prediction=' + str(test_predicted_categories[i]) + ' WHERE db_name=\"' + db_name + '\" AND file_name=\"' + file_name + '\";')


def __save_prediction_to_database(db_name, file_name, prediction_result):
    """Metoda zapisuje do bazy dancyh wynik predykcji dla pliku

    :param db_name: nazwa zwrzutu w bazie danych
    :param file_name: nazwa pliku dla ktorego chcemy zapisan wynik predykcji
    :param prediction_result: wynik predycji do zapisania w bazie danych
    :return: nic
    :rtype: None
    """

    save_to_db('UPDATE Metrics SET prediction=' + str(prediction_result) + ' WHERE db_name=\"' + db_name + '\" AND file_name=\"' + file_name + '\";')


def __get_adept_metrics_list():
    """Wykonuje zwraca nam liste nazw metryk pobieranych z sonara4

    :return: Lista zawierajaca nazwy metryk z sonra4 w naszej bazie danych
    :rtype: list
    """

    query = 'SELECT Metric FROM MetricTypes'
    metrics_dict = get_select_result_list(query)
    metrics_list = []
    for metric_dict in metrics_dict:
        metrics_list.append(metric_dict['Metric'])
    return metrics_list 
