import json
from api_tools import get_json_from_ntml_api, post_json_from_ntml_api


TFS_ADDRES = ''
# QA 
# TFS_ADDRES = ''
TFS_WORK_ITEMS_API = '_apis/wit/wiql'
TFS_WORK_ITEM_UPDATES_API = '_apis/wit/workItems/%d/updates'
TFS_MODIFIED_FILE_FROM_CHANGESET_API= '_apis/tfvc/changesets/%d/changes'
# COLLECTION_URL = TFS_ADDRES + TFS_COLLECTION
USERNAME = ''
PASSWORD = ''
# proj = ''
# col = ''
# proj_query = 'Select [System.Id] From WorkItems Where [] = \'12.0\' and [System.WorkItemType] = \'Bug\' and [System.ExternalLinkCount] > 0 and [Microsoft.VSTS.Common.Severity] <> \'Minor\''
# proj = ''
# col = ''
# # proj_query = 'Select [System.Id] From WorkItems Where [System.WorkItemType] CONTAINS \'Bug\' and [System.ExternalLinkCount] > 0 and [Microsoft.VSTS.Common.ClosedDate] > \'2000-00-00\''
# proj_query = 'Select [System.Id] From WorkItems Where [System.WorkItemType] CONTAINS \'Bug\' and [System.ExternalLinkCount] > 0'


def get_work_item_ids_list(tfs_project, tfs_collection, query):
    workItems = __get_work_items_list(tfs_project, tfs_collection, query)
    workItemIds = []
    for workItem in workItems:
        workItemIds.append(workItem['id'])
    return workItemIds


def __get_work_items_list(tfs_project, tfs_collection, query):
    project_url = TFS_ADDRES + tfs_collection + '/' + tfs_project + '/'
    api_url = project_url + TFS_WORK_ITEMS_API

    request_body = {
        'query': query,
    }
    
    request_body_json = json.dumps(request_body)
    
    query_result = post_json_from_ntml_api(api_url, USERNAME, PASSWORD, request_body_json)
    
    return query_result['workItems']


def get_all_changeset_ids_for_project(tfs_project, tfs_collection, query):
    changesetIds = []
    for workItemId in get_work_item_ids_list(tfs_project, tfs_collection, query):
        changesetIds.extend(get_changeset_ids_for_workItem(tfs_project, tfs_collection, workItemId))
    return changesetIds


def get_changeset_ids_for_workItem(tfs_project, tfs_collection, workItemId):
    api_url = TFS_ADDRES + tfs_collection + '/' + TFS_WORK_ITEM_UPDATES_API % workItemId
    
    updates = get_json_from_ntml_api(api_url, USERNAME, PASSWORD)['value']
    
    changeset_ids = []
    for update in updates:
        if update.has_key('relations'):
            changeset_ids.extend(__get_chengsets_ids_from_relation(update['relations'], 'added'))
            changeset_ids.extend(__get_chengsets_ids_from_relation(update['relations'], 'removed'))
    return changeset_ids


def __get_chengsets_ids_from_relation(relations, type_of_change):
    ids = []
    if relations.has_key(type_of_change):
        for changes in relations[type_of_change]:
            if 'Changeset' in changes['url']:
                ids.append(changes['url'].split('/')[-1])
    return ids


def get_modified_files_for_project(tfs_project, tfs_collection, query):
    chanesetIds = get_all_changeset_ids_for_project(tfs_project, tfs_collection, query)
    modified_files = []
    for chanesetId in chanesetIds:
        modified_files.extend(__get_modified_files_for_changeset(tfs_collection, int(chanesetId)))
    return __make_absolute_path_for_modified_files(modified_files)

# PROSTI
# def __make_absolute_path_for_modified_files(modified_files):
#     modified_files_with_absolute_path = []
#     for modified_file in modified_files:
#         modified_files_with_absolute_path.append(modified_file[modified_file.find("Src")+4:])
#     return modified_files_with_absolute_path

# GILM
# def __make_absolute_path_for_modified_files(modified_files):
#     modified_files_with_absolute_path = []
#     for modified_file in modified_files:
#         tmp_path = modified_file[modified_file.find('GILM.'):]
#         modified_files_with_absolute_path.append(tmp_path)
#     return modified_files_with_absolute_path


# LDS
def __make_absolute_path_for_modified_files(modified_files):
    modified_files_with_absolute_path = []
    for modified_file in modified_files:
        tmp_path = 'Infrastructure/.NetFramework4.0' + modified_file[modified_file.rfind('/Source'):]
        modified_files_with_absolute_path.append(tmp_path)
    return modified_files_with_absolute_path


def __get_modified_files_for_changeset(tfs_collection, changesetId):
    api_url = TFS_ADDRES + tfs_collection + '/' + TFS_MODIFIED_FILE_FROM_CHANGESET_API % changesetId
    
    updates = get_json_from_ntml_api(api_url, USERNAME, PASSWORD)['value']
    
    modified_files = []
    for item in updates:
        modified_files.append(item['item']['path'])
    
    return modified_files
