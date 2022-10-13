# -*- coding: utf-8 -*-
"""
tools.quality_center_tools
~~~~~~~~~~~~

Modul obslugi HP quality center

:copyright:
:license:

"""

from settings import AUTHORIZATION_STRING, QUALITY_CENTER_DEFECT_BY_CQ_ID_GET, QUALITY_CENTER_IS_AUTHENTICATED_GET, QUALITY_CENTER_AUTHENTICATE_GET, QUALITY_CENTER_LOGOUT_GET, QUALITY_CENTER_OPENING_SESSION_POST, QUALITY_CENTER_CLOSING_SESSION_DELETE, QUALITY_CENTER_DEFECT_GET, QUALITY_CENTER_ISSUE_CATEGORY_DEFECT_IN_ADEPT_DB, QUALITY_CENTER_ISSUE_CATEGORY_ENHANCEMENT_SUGGESTION_IN_ADEPT_DB, QUALITY_CENTER_ISSUE_CATEGORY_CHANGE_REQUEST_IN_ADEPT_DB, QUALITY_CENTER_ISSUE_CATEGORY_OTHER_IN_ADEPT_DB
from api_tools import get_from_api_with_session, post_from_api_with_session, delete_from_api_with_session
from xml.etree import cElementTree as ET
from db_tools import get_select_result, save_to_db
import requests


def session_test():
    """Metoda testujaca autoryzuje tworzy sesje sprawdza zamyka sesje i wylogowuje sie z systemu wyswietlajac odpowiednie komunikaty 

    :return: Nic
    :rtype: None
    """

    session = requests.session()
    print 'is_authorized: \t' + str(__is_authenticated(session))
    print 'authorized: \t' + str(__authenticate(session))
    print 'is_authorized: \t' + str(__is_authenticated(session))
    print 'open_ses: \t' + str(__open_session(session))
    print 'close_ses: \t' + str(__close_session(session))
    print 'logout: \t' + str(__logout(session))
    print 'is_authorized: \t' + str(__is_authenticated(session))


def start_quality_center_connection():
    """Zwraca objekt sesji ktory jest juz zautoryzowany na serwerze oraz jest jest storzona sesja HPQC

    :return: sesja przez ktora pobieramy dane z HPQC
    :rtype: requests.sessions.Session
    """

    session = requests.session()
    __authenticate(session)
    __open_session(session)
    if __is_authenticated(session): 
        return session
    return None


def end_quality_center_connection(session):
    """Dla przekazanej w parametrze sesji zamyka nam sesje HPQC oraz wylogowuje nas z systemu

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :return: Nic
    :rtype: None
    """

    if __is_authenticated(session): 
        __close_session(session)
        __logout(session)


def is_issue_defect_for_issue_id(session, domain, project, issue_id, extra_field=(None,None)):
    """Sprawdza czy incydent jest bledem dla podanej domeny, projekt, identyfiaktora oraz przekazanej w parametrze sesji

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :param domain: nazwa domeny z  HPQC w ktorej znajduje sie projetk
    :param project: nazwa projektu z HPQC
    :param issue_id: identyfikator incydentu
    :param extra_field: krotka przechowujaca wartości dla dodatkowego pola wyszukiwania
    :return: sprawdza
    :rtype: bool
    """

    issue_dict = get_or_update_issue_dict(session, domain, project, issue_id, extra_field)
    if issue_dict:
        return issue_dict['categoryId'] == QUALITY_CENTER_ISSUE_CATEGORY_DEFECT_IN_ADEPT_DB
    return False


def get_or_update_issue_dict(session, domain, project, issue_id, extra_field=(None,None)):
    """Zwraca nam dane dotyczące incydentu dla podanej domeny, projekt, identyfiaktora oraz przekazanej w parametrze sesji z bazy danych lub 
    w przypadku braku wersji lokalnej z HPQC

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :param domain: nazwa domeny z  HPQC w ktorej znajduje sie projetk
    :param project: nazwa projektu z HPQC
    :param issue_id: identyfikator incydentu
    :param extra_field: krotka przechowujaca wartości dla dodatkowego pola wyszukiwania
    :return: dane dotyczące incydentu
    {
        'project': str,
        'domain': str,
        'issueId': str,
        'extraFieldName': str,
        'extraFieldValue': str,
        'versionName': str,
        'categoryId': str
    }
    :rtype: dict
    """

    issue_dict = __get_issue_dict_for_issue_id_from_db(domain, project, issue_id, extra_field)
    if not issue_dict:
        issue_dict = get_issue_data_from_api_as_dict(session, domain, project, issue_id, extra_field)
        if issue_dict:
            __save_issue_to_db(issue_dict)
    return issue_dict


def __get_issue_dict_for_issue_id_from_db(domain, project, issue_id, extra_field=(None,None)):
    """Zwraca nam dane dotyczące incydentu dla podanej domeny, projekt, identyfiaktora z bazy danych

    :param domain: nazwa domeny z  HPQC w ktorej znajduje sie projetk
    :param project: nazwa projektu z HPQC
    :param issue_id: identyfikator incydentu
    :param extra_field: krotka przechowujaca wartości dla dodatkowego pola wyszukiwania
    :return: dane dotyczące incydentu
    {
        'project': str,
        'domain': str,
        'issueId': str,
        'extraFieldName': str,
        'extraFieldValue': str,
        'versionName': str,
        'categoryId': str
    }
    :rtype: dict
    """

    query = "SELECT * FROM QualityCenterIssues WHERE domain = \"" + domain + "\" AND project = \"" + project + "\""
    if extra_field[1]:
        query = query + " AND extraFieldName = \"" + extra_field[0] + "\" AND extraFieldValue = \"" + extra_field[1] + "\""
    else:
        query = query + " AND issueId = \"" + issue_id + "\""
    return get_select_result(query)


def __save_issue_to_db(issue_dict):
    """Zapisuej nam dane dotyczące incydentu dla podanej domeny, projekt, identyfiaktora do bazy danych

    :param issue_dict: dane dotyczące incydentu
    {
        'project': str,
        'domain': str,
        'issueId': str,
        'extraFieldName': str,
        'extraFieldValue': str,
        'versionName': str,
        'categoryId': str
    }
    :return: Nic 
    :rtype: None
    """

    update_query  = "INSERT INTO QualityCenterIssues VALUES (\"{domain}\", \"{project}\", \"{issueId}\", \"{extraFieldName}\", \"{extraFieldValue}\", \"{categoryId}\", \"{versionName}\");".format(**issue_dict)
    save_to_db(update_query)


def get_issue_data_from_api_as_dict(session, domain, project, issue_id, extra_field=(None,None)):
    """Zwraca nam dane dotyczące incydentu dla podanej domeny, projekt, identyfiaktora z api HPQC

    :param domain: nazwa domeny z  HPQC w ktorej znajduje sie projetk
    :param project: nazwa projektu z HPQC
    :param issue_id: identyfikator incydentu    
    :param extra_field: krotka przechowujaca wartości dla dodatkowego pola wyszukiwania
    :return: dane dotyczące incydentu
    {
        'project': str,
        'domain': str,
        'issueId': str,
        'extraFieldName': str,
        'extraFieldValue': str,
        'versionName': str,
        'categoryId': str
    }
    :rtype: dict
    """

    xml_fields_tree = __get_xml_fields_tree_with_defect(session, domain, project, issue_id, extra_field)
    if xml_fields_tree:
        issue_dict = __get_issue_data_from_xml_fields_tree_as_dict(xml_fields_tree, extra_field)
        issue_dict['issueId'] = __get_issue_id_from_xml_fields_tree(xml_fields_tree)
        issue_dict['domain'] = domain
        issue_dict['project'] = project
        return issue_dict
    return None




def __get_issue_data_from_xml_fields_tree_as_dict(xml_fields_tree, extra_field=(None,None)):
    """Zwraca nam dane dotyczące incydentu dla podanej domeny, projekt, identyfiaktora z api HPQC

    :param xml_fields_tree: dane z api HPQC w postaci drzewa xml
    :param extra_field: krotka przechowujaca wartości dla dodatkowego pola wyszukiwania
    :return: dane dotyczące incydentu
    {
        'versionName': str,
        'categoryId': str
    }
    :rtype: dict
    """

    issue_dict = {
        'versionName': __get_version_name_from_xml_fields_tree(xml_fields_tree),
        'categoryId': __get_category_id_from_xml_fields_tree(xml_fields_tree),
        'extraFieldName': extra_field[0],
        'extraFieldValue':  __get_extra_field_value_from_xml_fields_tree(xml_fields_tree, extra_field[0]),
    }
    return issue_dict


def __get_version_name_from_api(session, domain, project, issue_id, extra_field=(None,None)):
    """Zwraca nam wersje w ktorej wykryto incydent z api HPQC

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :param domain: nazwa domeny z  HPQC w ktorej znajduje sie projetk
    :param project: nazwa projektu z HPQC
    :param issue_id: identyfikator incydentu
    :param extra_field: krotka przechowujaca wartości dla dodatkowego pola wyszukiwania
    :return: wersje w ktorej wykryto incydent
    :rtype: str
    """

    xml_fields_tree = __get_xml_fields_tree_with_defect(session, domain, project, issue_id, extra_field)
    if xml_fields_tree:
        return __get_version_name_from_xml_fields_tree(xml_fields_tree)


def __get_version_name_from_xml_fields_tree(xml_fields_tree):
    """Zwraca nam wersje w ktorej wykryto incydent z drzewa xml

    :param xml_fields_tree: dane z api HPQC w postaci drzewa xml
    :return: wersje w ktorej wykryto incydent
    :rtype: str
    """

    version_name = None
    for field in xml_fields_tree:
        if field.attrib['Name'] == 'detected-in-rel':
            version_name = field.find('Value').get('ReferenceValue')
    return version_name


def __get_category_id_from_api(session, domain, project, issue_id, extra_field=(None,None)):
    """Zwraca nam kategorie incydentu z api HPQC

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :param domain: nazwa domeny z  HPQC w ktorej znajduje sie projetk
    :param project: nazwa projektu z HPQC
    :param issue_id: identyfikator incydentu
    :param extra_field: krotka przechowujaca wartości dla dodatkowego pola wyszukiwania
    :return: kategoria incydentu
    :rtype: str
    """

    xml_fields_tree = __get_xml_fields_tree_with_defect(session, domain, project, issue_id, extra_field)
    if xml_fields_tree:
        return __get_category_id_from_xml_fields_tree(xml_fields_tree)


def __get_category_id_from_xml_fields_tree(xml_fields_tree):
    """Zwraca nam kategorie incydentu z drzewa xml

    :param xml_fields_tree: dane z api HPQC w postaci drzewa xml
    :return: kategoria incydentu
    :rtype: str
    """

    issue_categoty = ''
    for field in xml_fields_tree:
        if field.attrib['Name'] == 'user-02':
            issue_categoty = field.find('Value').text
    if 'Defect' in issue_categoty:
        return QUALITY_CENTER_ISSUE_CATEGORY_DEFECT_IN_ADEPT_DB
    if 'Change Request' in issue_categoty:
        return QUALITY_CENTER_ISSUE_CATEGORY_CHANGE_REQUEST_IN_ADEPT_DB
    if 'Enhancement Suggestion' in issue_categoty:
        return QUALITY_CENTER_ISSUE_CATEGORY_ENHANCEMENT_SUGGESTION_IN_ADEPT_DB
    return QUALITY_CENTER_ISSUE_CATEGORY_OTHER_IN_ADEPT_DB


def __get_issue_id_from_api(session, domain, project, issue_id, extra_field=(None,None)):
    """Zwraca nam id incydentu z api HPQC

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :param domain: nazwa domeny z  HPQC w ktorej znajduje sie projetk
    :param project: nazwa projektu z HPQC
    :param issue_id: identyfikator incydentu
    :param extra_field: krotka przechowujaca wartości dla dodatkowego pola wyszukiwania
    :return: id incydentu
    :rtype: str
    """

    xml_fields_tree = __get_xml_fields_tree_with_defect(session, domain, project, issue_id, extra_field)
    if xml_fields_tree:
        return __get_issue_id_from_xml_fields_tree(xml_fields_tree)


def __get_issue_id_from_xml_fields_tree(xml_fields_tree):
    """Zwraca nam id incydentu z drzewa xml

    :param xml_fields_tree: dane z api HPQC w postaci drzewa xml
    :return: id incydentu
    :rtype: str
    """

    return __get_extra_field_value_from_xml_fields_tree(xml_fields_tree, 'id')


def __get_extra_field_value_from_api(session, domain, project, issue_id, extra_field=(None,None)):
    """Zwraca nam wartosc dla pola incydentu z drzewa xml

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :param domain: nazwa domeny z  HPQC w ktorej znajduje sie projetk
    :param project: nazwa projektu z HPQC
    :param issue_id: identyfikator incydentu
    :param extra_field: krotka przechowujaca wartości dla dodatkowego pola wyszukiwania
    :return: extra field value incydentu
    :rtype: str
    """

    xml_fields_tree = __get_xml_fields_tree_with_defect(session, domain, project, issue_id, extra_field)
    if xml_fields_tree:
        return __get_extra_field_value_from_xml_fields_tree(xml_fields_tree, extra_field[0])


def __get_extra_field_value_from_xml_fields_tree(xml_fields_tree, extra_field_name):
    """Zwraca nam wartosc dla pola incydentu z drzewa xml

    :param xml_fields_tree: dane z api HPQC w postaci drzewa xml
    :param extra_field_name: nazwa pola z dodatkowa wartoscia
    :return: extra field value incydentu
    :rtype: str
    """

    extra_field_value = ''
    for field in xml_fields_tree:
        if field.attrib['Name'] == extra_field_name:
            extra_field_value = field.find('Value').text
    return extra_field_value


def __get_xml_fields_tree_with_defect(session, domain, project, issue_id, extra_field=(None,None)):
    """Zwraca nam przefiltrowane w drzewo xml dande z api HPQC

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :param domain: nazwa domeny z  HPQC w ktorej znajduje sie projetk
    :param project: nazwa projektu z HPQC
    :param issue_id: identyfikator incydentu
    :param extra_field: krotka przechowujaca wartości dla dodatkowego pola wyszukiwania
    :return: drzewo xml
    :rtype: Entity
    """

    xml_tree = __get_xml_tree_with_defect(session, domain, project, issue_id, extra_field)
    if xml_tree:
        return xml_tree.find('Fields')
    return None
    

def __get_xml_tree_with_defect(session, domain, project, issue_id, extra_field=(None,None)):
    """Zwraca nam przeksztalocne w drzewo xml dande z api HPQC

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :param domain: nazwa domeny z  HPQC w ktorej znajduje sie projetk
    :param project: nazwa projektu z HPQC
    :param issue_id: identyfikator incydentu
    :param extra_field: krotka przechowujaca wartości dla dodatkowego pola wyszukiwania
    :return: drzewo xml
    :rtype: Entity
    """

    api_response = __get_resp_with_defect_xml(session, domain, project, issue_id, extra_field)
    if __is_http_ok_status(api_response):
        xml_tree = ET.fromstring(api_response.text.encode('utf-8'))
        return xml_tree.find('Entity')
    return None


def __get_resp_with_defect_xml(session, domain, project, issue_id, extra_field=(None,None)):
    """Zwraca nam odpowiedz http z api HPQC

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :param domain: nazwa domeny z  HPQC w ktorej znajduje sie projetk
    :param project: nazwa projektu z HPQC
    :param issue_id: identyfikator incydentu
    :param extra_field: krotka przechowujaca wartości dla dodatkowego pola wyszukiwania
    :return: odpowiedz HPQC
    :rtype: requests.models.Response
    """

    url = str(QUALITY_CENTER_DEFECT_GET).format(domain, project, issue_id)
    if extra_field[1]:
        url = str(QUALITY_CENTER_DEFECT_BY_CQ_ID_GET).format(domain, project, extra_field[0], extra_field[1])
    resp = get_from_api_with_session(session= session, url= url, ssl = True)
    return resp


def __open_session(session):
    """Otwiera sesje HPQC

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :return: Poprwnosc otworzenia sesji
    :rtype: bool
    """

    url = QUALITY_CENTER_OPENING_SESSION_POST
    resp = post_from_api_with_session(session= session, url= url, ssl = True)
    return __is_http_ok_status(resp)


def __close_session(session):
    """Zamyka sesje HPQC

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :return: Poprwnosc zamkniecia sesji
    :rtype: bool
    """

    url = QUALITY_CENTER_CLOSING_SESSION_DELETE
    resp = delete_from_api_with_session(session= session, url= url, ssl = True)
    return __is_http_ok_status(resp)


def __authenticate(session):
    """Loguje sie w  HPQC

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :return: Poprwnosc logowania w HPQC
    :rtype: bool
    """

    url = QUALITY_CENTER_AUTHENTICATE_GET
    headers = {
        'Authorization': AUTHORIZATION_STRING
    }
    resp = get_from_api_with_session(session = session, url = url, headers = headers, ssl = True)
    return resp

def __logout(session):
    """Wylogowuje size z HPQC

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :return: Poprwnosc wylogowania z HPQC
    :rtype: bool
    """

    url = QUALITY_CENTER_LOGOUT_GET
    resp = get_from_api_with_session(session = session, url= url, ssl= True)
    return __is_http_ok_status(resp)


def __is_authenticated(session):
    """Sprawdza czy jestescmy zalogowani w HPQC

    :param session: sesja w której w plikach cooki przechowywane sa identyfikatory HPQC
    :return: czy jestescmy zalogowani w HPQC
    :rtype: bool
    """

    url = QUALITY_CENTER_IS_AUTHENTICATED_GET
    resp = get_from_api_with_session(session = session, url = url, ssl = True)  
    return __is_http_ok_status(resp)
    

def __is_http_ok_status(resp):
    """Sprawdza czy odpowiedz ma odpwiedni status http

    :param resp: odpowiedz http
    :return: czy odpowiedz ma odpowiedni status http
    :rtype: bool
    """

    if resp.status_code in [200, 201, 202]:
        return True
    return False
