# -*- coding: utf-8 -*-
"""
tools.api_tools
~~~~~~~~~~~~

Modul obslugi restowego api

:copyright:
:license:

"""

import json, requests, urllib2
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from ntlm import HTTPNtlmAuthHandler

def get_json_from_api(url, headers, params={}, ssl=False):
    """Zwraca slownik z RESTOWEGO GET

    :param url: Url z ktorego pobieramy odpowiedz dane
    :param headers: Naglowek ktory wysylamy z GET
    :param params: Parametry przekazywane w url
    :return: dict from GET
    :rtype: dict
    """

    return json.loads(get_text_from_api(url, headers, params, ssl))


def post_json_from_api(url, params, headers, data, ssl=False):
    """Zwraca slownik z RESTOWEGO POST

    :param url: Url z ktorego pobieramy odpowiedz dane
    :param params: Parametry przekazywane w url
    :param headers: Naglowek ktory wysylamy z POST
    :param data: Zawartosc w postaci słownika jakie przekazujemy do POST
    :return: dict from GET
    :rtype: dict
    """

    resp = post_from_api(url, headers, params, data, ssl)
    return json.loads(resp.text)


def get_text_from_api(url, headers, params={}, ssl=False):
    """Zwraca text z RESTOWEGO GET

    :param url: Url z ktorego pobieramy odpowiedz dane
    :param headers: Naglowek ktory wysylamy z GET
    :param params: Parametry przekazywane w url
    :return: string from GET
    :rtype: str
    """

    return get_from_api(url, headers, params, ssl).text


def get_text_from_api_with_session(session, url, headers=None, params={}, ssl=False):
    """Zwraca text z RESTOWEGO GET

    :param session: sesja ktora przechowuje dane
    :param url: Url z ktorego pobieramy odpowiedz dane
    :param headers: Naglowek ktory wysylamy z GET
    :param params: Parametry przekazywane w url
    :return: string from GET
    :rtype: str
    """

    return get_from_api_with_session(session, url, headers, params, ssl).text


def get_headers_from_api(url, headers, params={}, ssl=False):
    """Zwraca naglowek z RESTOWEGO GET

    :param url: Url z ktorego pobieramy odpowiedz dane
    :param headers: Naglowek ktory wysylamy z GET
    :param params: Parametry przekazywane w url
    :return: naglowek w formie dict from GET
    :rtype: dict
    """

    return get_from_api(url, headers, params, ssl).headers


def get_from_api(url, headers, params={}, ssl=False):
    """Zwraca objekt z RESTOWEGO GET

    :param url: Url z ktorego pobieramy odpowiedz dane
    :param headers: Naglowek ktory wysylamy z GET
    :param params: Parametry przekazywane w url
    :return: objekt from GET
    :rtype: class 'requests.models.Response'
    """
    if ssl:
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':RC4-SHA'
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        return requests.get(url=url, headers=headers, params=params, verify=False)
    else:
        return requests.get(url=url, headers=headers, params=params)


def post_from_api(url, headers, params=None, data=None, ssl=False):
    """Zwraca objekt z RESTOWEGO POST

    :param url: Url z ktorego pobieramy odpowiedz dane
    :param params: Parametry przekazywane w url
    :param headers: Naglowek ktory wysylamy z POST
    :param data: Zawartosc w postaci słownika jakie przekazujemy do POST
    :return: objekt from GET
    :rtype: class 'requests.models.Response'
    """
    if ssl:
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':RC4-SHA'
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        return requests.post(url=url, headers=headers, params=params, data=json.dumps(data), verify=False)
    else:
        return requests.post(url=url, headers=headers, params=params, data=json.dumps(data))


def get_from_api_with_session(session, url, headers=None, params={}, ssl=False):
    """Zwraca objekt z RESTOWEGO GET

    :param session: sesja ktora przechowuje dane
    :param url: Url z ktorego pobieramy odpowiedz dane
    :param headers: Naglowek ktory wysylamy z GET
    :param params: Parametry przekazywane w url
    :return: objekt from GET
    :rtype: class 'requests.models.Response'
    """
    if ssl:
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':RC4-SHA'
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        return session.get(url=url, headers=headers, params=params, verify=False)
    else:
        return session.get(url=url, headers=headers, params=params)


def post_from_api_with_session(session, url, headers=None, params=None, data=None, ssl=False):
    """Zwraca objekt z RESTOWEGO POST

    :param session: sesja ktora przechowuje dane
    :param url: Url z ktorego pobieramy odpowiedz dane
    :param params: Parametry przekazywane w url
    :param headers: Naglowek ktory wysylamy z POST
    :param data: Zawartosc w postaci słownika jakie przekazujemy do POST
    :return: objekt from GET
    :rtype: class 'requests.models.Response'
    """
    if ssl:
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':RC4-SHA'
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        return session.post(url=url, headers=headers, params=params, data=json.dumps(data), verify=False)
    else:
        return session.post(url=url, headers=headers, params=params, data=json.dumps(data))


def delete_from_api_with_session(session, url, ssl=False):
    """Usuwa objekt z RESTOWEGO POST

    :param session: sesja ktora przechowuje dane
    :param url: Url z ktorego pobieramy odpowiedz dane
    :return: objekt from GET
    :rtype: class 'requests.models.Response'
    """
    if ssl:
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':RC4-SHA'
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        return session.post(url=url, verify=False)
    else:
        return session.post(url=url)


def get_json_from_ntml_api(url, user, password):
    """Zwraca slownik z RESTOWEGO GET z uzyciem ntml
    
    :param url: Url z ktorego pobieramy odpowiedz dane
    :param user: username
    :param password: password
    :return: dict from GET
    :rtype: dict
    """
    return post_json_from_ntml_api(url, user, password, None)


def post_json_from_ntml_api(url, user, password, request_body):
    """Zwraca slownik z RESTOWEGO GET z uzyciem ntml
    
    :param url: Url z ktorego pobieramy odpowiedz dane
    :param user: username
    :param password: password
    :return: dict from GET
    :rtype: dict
    """
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, url, user, password)
    auth_NTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)
    opener = urllib2.build_opener(auth_NTLM) 
    urllib2.install_opener(opener)
    request = urllib2.Request(url, headers={"Accept" : "application/json; api-version=1.0", "Content-Type" : "application/json"}, data=request_body)
    response = urllib2.urlopen(request) 
    return json.loads(response.read())