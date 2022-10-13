"""
tools.svn_tools
~~~~~~~~~~~~

Modul obslugi svn (Offline) + (Online)

:copyright:
:license:

"""

from xml.etree import cElementTree as ET
from subprocess import Popen, PIPE
from settings import USERNAME, PASSWORD
import re


def get_svn_log_with_jira_issues_keys_id_as_dictionary(svn_file_path=None, svn_repo_url=None, jira_key_prefix=None):
    """Zwraca dla podanego zrodla svn(albo plik albo link do repozytorium) i przedrostka klucza jira dane odnosnie commitow z ich powiazaniem z jira

    :param svn_file_path: sciezka do pliku log z svn
    :param svn_repo_url: link do repozytorum svn
    :param jira_key_prefix: przedrostek klucza jira
    :return: Lista zawierajaca slownik z danymi commitow
    [
        {
            'paths' : list of str, <Lista plikow>
            'message': str, <wiadomosc commit>
            'id': str, <id commita>
            'jira_issues_keys_id': list of str, <<Klucze issues z jiry ktore zostaly powiazane z tym commit>
        }
        ...
    ]
    :rtype: list of dicts
    """

    project_log = __get_svn_log_as_dictionary(svn_file_path=svn_file_path, svn_repo_url=svn_repo_url)
    for log_entry in project_log:
        if not log_entry['message'] is None:
            finded_id_typles = re.findall('((' + jira_key_prefix + ')(\s|-|\s-\s|-\s|\s-|--|_)?[0-9]+)', log_entry['message'], re.IGNORECASE)
            if len(finded_id_typles) > 0:
                key_ids = []
                for key_id in finded_id_typles:
                    key_ids.append(re.findall('[0-9]+', key_id[0])[0])
                log_entry['jira_issues_keys_id'] = key_ids
    return project_log


def get_svn_log_with_quality_center_id_as_dictionary(svn_file_path=None, svn_repo_url=None, quality_center_prefix_list = []):
    """Zwraca dla podanego zrodla svn(albo plik albo link do repozytorium) i przedrostka prefixow quality center dane odnosnie commitow z ich powiazaniem z quality center

    :param svn_file_path: sciezka do pliku log z svn
    :param svn_repo_url: link do repozytorum svn
    :param jira_key_prefix: przedrostek klucza jira
    :return: Lista zawierajaca slownik z danymi commitow
    [
        {
            'paths' : list of str, <Lista plikow>
            'message': str, <wiadomosc commit>
            'id': str, <id commita>
            'quality_center_issues_keys_id': list of str, <<Klucze issues z qc ktore zostaly powiazane z tym commit>
        }
        ...
    ]
    :rtype: list of dicts
    """
    project_log = __get_svn_log_as_dictionary(svn_file_path=svn_file_path, svn_repo_url=svn_repo_url)
    for log_entry in project_log:
        key_ids = __get_issues_keys_ids_list(quality_center_prefix_list, log_entry)
        log_entry['quality_center_issues_keys_id'] = key_ids
    return  project_log



def __get_issues_keys_ids_list(quality_center_prefix_list, log_entry):
    """zwraca liste prefixow jako string

    :param quality_center_prefix_list: Lista prefixow
    :param log_entry: pojedynczy element logu svn
    :return: Lista id dla podanych prefixow
    :rtype: list od string
    """

    key_ids = []
    if log_entry['message']:
        quality_center_regexp_prefix_list = __get_regexp_from_prefix_list(quality_center_prefix_list)
        finded_id_typles = re.findall('((' + quality_center_regexp_prefix_list + ')(\s|-|\s-\s|-\s|\s-|--|_)?[0-9]+)', log_entry['message'], re.IGNORECASE)
        if len(finded_id_typles) > 0:
            for key_id in finded_id_typles:
                key_ids.append(key_id[1]+re.findall('[0-9]+', key_id[0])[0])
    return key_ids


def __get_regexp_from_prefix_list(prefix_list):
    """zwraca liste prefixow jako string

    :param prefix_list: Lista prefixow
    :return: Lista prefixow dla danego projeku jako string
    :rtype: string
    """

    return '|'.join(prefix_list)


def __get_svn_log_as_dictionary(svn_file_path=None, svn_repo_url=None):
    """Zwraca dla podanego zrodla svn(albo plik albo link do repozytorium) dane odnosnie commitow
    
    :param svn_file_path: sciezka do pliku log z svn
    :param svn_repo_url: link do repozytorum svn
    :return: Lista zawierajaca slownik z danymi commitow
    [
        {
            'paths' : list of str, <Lista plikow>
            'message': str, <wiadomosc commit>
            'id': str, <id commita>
        }
        ...
    ]
    :rtype: list of dicts
    """

    if not svn_file_path == None:
        xmlTree = __get_svn_log_as_xml_tree_from_file(svn_file_path)
    else:
        xmlTree = __get_svn_log_as_xml_tree_from_url(svn_repo_url)
    revisions = []
    for logentry in xmlTree.findall('logentry'):
        revisionID = logentry.attrib['revision']
        msg = logentry.find('msg')
        if not msg == None:
            msg = msg.text
        else:
            msg = 'Empty message'
        paths = logentry.find('paths')
        files = []
        if paths != None:
            for path in paths:
                if path.attrib['kind'] == 'file':
                    files.append(path.text)
        revision = {}
        revision['id'] = revisionID 
        revision['message'] = msg
        revision['paths'] = files
        revisions.append(revision)
    return revisions


def __get_svn_log_as_xml_tree_from_file(svn_file_path):
    """Zwraca dla pliku log z svn dane odnosnie commitow w postaci ElementTree
    
    :param svn_file_path: sciezka do pliku log z svn
    :return: Korzen ElementTree z logiem svn
    :rtype: Element
    """

    xmlTree = ET.ElementTree()
    return xmlTree.parse(svn_file_path)


def __get_svn_log_as_xml_tree_from_url(svn_repo_url):
    """Zwraca dla adresu repozytrium svn dane odnosnie commitow w postaci ElementTree
    
    :param svn_file_path: sciezka do pliku log z svn
    :param svn_repo_url: link do repozytorum svn
    :rtype: Element
    """

    cmd = 'svn log --xml -v -g --trust-server-cert --non-interactive --username ' + USERNAME + ' --password \'' + PASSWORD + '\' '
    outputXML = Popen(cmd + svn_repo_url, shell=True, stdout=PIPE).communicate()[0]
    root = ET.fromstring(outputXML)
    return root
