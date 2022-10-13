# -*- coding: utf-8 -*-
"""
tools.data_source_db_tools
~~~~~~~~~~~~

Modul pobierani danych dotyczocych zrodel danych dla projektow

:copyright:
:license:

"""

from db_tools import get_select_result_list


def get_list_of_data_sources_for_all_projects():
    """Zwraca liste slownikow z zrodlami danych dla projektow

    :return: lista slowniko z zrodlami danych dla projektow
    [
        {
            'id': int,
            'RepositoryURL': '',
            'RepositoryName': '',
            'RepositoryType': int,
            'SonarName': '',
            'MetricGeneratorKey': '',
            'MetricGeneratorType': int,
            'BugTrackerName': '',
            'BugTrackerType': int,
            'Ready': int,
            'RepoSimilarRatio': double,
            'TrackerSimilarRatio': double
        }
        ...
    ]
    :rtype: list
    """

    select = "SELECT * FROM SonarDictionary"
    return get_select_result_list(select)


def get_list_of_data_sources_for_projects_with_sonar_bugtracke_repository_data():
    """Zwraca liste slownikow z zrodlami danych dla projektow

    :return: lista slowniko z zrodlami danych dla projektow
    [
        {
            'id': int,
            'RepositoryURL': '',
            'RepositoryName': '',
            'RepositoryType': int,
            'SonarName': '',
            'MetricGeneratorKey': '',
            'MetricGeneratorType': int,
            'BugTrackerName': '',
            'BugTrackerType': int,
            'Ready': int,
            'RepoSimilarRatio': double,
            'TrackerSimilarRatio': double
        }
        ...
    ]
    :rtype: list
    """

    select = "SELECT * FROM SonarDictionary WHERE Ready>0"
    return get_select_result_list(select)


def get_list_of_data_sources_for_projects_ready_for_prediction():
    """Zwraca liste slownikow z zrodlami danych dla projektow

    :return: lista slowniko z zrodlami danych dla projektow
    [
        {
            'id': int,
            'RepositoryURL': '',
            'RepositoryName': '',
            'RepositoryType': int,
            'SonarName': '',
            'MetricGeneratorKey': '',
            'MetricGeneratorType': int,
            'BugTrackerName': '',
            'BugTrackerType': int,
            'Ready': int,
            'RepoSimilarRatio': double,
            'TrackerSimilarRatio': double
        }
        ...
    ]
    :rtype: list
    """

    select = "SELECT * FROM SonarDictionary WHERE Ready>0 AND BugTrackerType <> 2"
    return get_select_result_list(select)


def get_list_of_data_sources_for_projects_ready_for_prediction_and_with_quality_center_bug_tracker():
    """Zwraca liste slownikow z zrodlami danych dla projektow ktore uzywaja quality center

    :return: lista slowniko z zrodlami danych dla projektow uzywaja quality center
    [
        {
            'id': int,
            'RepositoryURL': '',
            'RepositoryName': '',
            'RepositoryType': int,
            'SonarName': '',
            'MetricGeneratorKey': '',
            'MetricGeneratorType': int,
            'BugTrackerName': '',
            'BugTrackerType': int,
            'Ready': int,
            'RepoSimilarRatio': double,
            'TrackerSimilarRatio': double
        }
        ...
    ]
    :rtype: list
    """

    select = "SELECT * FROM SonarDictionary WHERE Ready>0 AND BugTrackerType = 2"
    return get_select_result_list(select)


def get_list_of_data_sources_for_projects_ready_for_prediction_and_with_tfs():
    """Zwraca liste slownikow z zrodlami danych dla projektow ktore uzywaja quality center

    :return: lista slowniko z zrodlami danych dla projektow uzywaja quality center
    [
        {
            'id': int,
            'RepositoryURL': '',
            'RepositoryName': '',
            'RepositoryType': int,
            'SonarName': '',
            'MetricGeneratorKey': '',
            'MetricGeneratorType': int,
            'BugTrackerName': '',
            'BugTrackerType': int,
            'Ready': int,
            'RepoSimilarRatio': double,
            'TrackerSimilarRatio': double,
            'TfsCollection': ,
            'TfsName': ,
            'TfsQuery':
        }
        ...
    ]
    :rtype: list
    """

    select = "SELECT * FROM SonarDictionary INNER JOIN (SELECT id, collection AS TfsCollection, query as TfsQuery, name AS TfsName FROM Sources_TFS) AS TfsData ON SonarDictionary.BugTrackerName=TfsData.id WHERE Ready > 0"
    return get_select_result_list(select)

