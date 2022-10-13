"""
tools.db_tools
~~~~~~~~~~~~

Modul obslugi bazy danych

:copyright:
:license:

"""

import MySQLdb
from settings import MYSQL_HOST, MYSQL_LOGIN, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_DATABASE_RESULTS


def get_select_result_list(sql_select, result=False):
    """Zwraca wynik sapytania SELECT jako lista 

    :param sql_select: SELECT ktory wykonamy na bazie danych
    :return: lista wynikowa z zapytania SELECT
    :rtype: list
    """

    db = __get_MySQLdb_connect()
    if result:
        db = __get_MySQLdb_connect(True)
    cursor = __get_MySQLdb_coursor(db)
    cursor.execute(sql_select)
    db.close()
    return list(cursor.fetchall())


def get_select_result_field_value_or_None(sql_select, field, result=False):
    return get_select_result_field_value_or_default(sql_select, field, None, result)


def get_select_result_field_value_or_default(sql_select, field, default, result=False):
    result = get_select_result(sql_select, result)
    if result:
        return result.get(field)
    return default


def get_select_result(sql_select, result=False):
    """Zwraca pierwszy wynik sapytania SELECT jako slownik 

    :param sql_select: SELECT ktory wykonamy na bazie danych
    :return: slownik z pierwszego elementu zapytania SELECT
    :rtype: dict
    """

    db = __get_MySQLdb_connect()
    if result:
        db = __get_MySQLdb_connect(True)
    cursor = __get_MySQLdb_coursor(db)
    cursor.execute(sql_select)
    db.close()
    return cursor.fetchone()


def save_to_db(update_query, result=False):
    """Wykonuje podany UPDATE na bazie danych 

    :param update_query: UPDATE ktory wykonamy na bazie danych
    :return: Nie zwracamy nic 
    :rtype: None
    """

    db = __get_MySQLdb_connect()
    if result:
        db = __get_MySQLdb_connect(True)
    cursor = __get_MySQLdb_coursor(db)
    try:
        cursor.execute(update_query)
        db.commit()
    except Exception, e:
        print update_query
        print "not working query: " + str(e)
    db.close()


def __get_MySQLdb_connect(result=False):
    db = MySQLdb.connect(MYSQL_HOST, MYSQL_LOGIN, MYSQL_PASSWORD, MYSQL_DATABASE)
    if result:
        db = MySQLdb.connect(MYSQL_HOST, MYSQL_LOGIN, MYSQL_PASSWORD, MYSQL_DATABASE_RESULTS)
    return  db

  
def __get_MySQLdb_coursor(db):
    return db.cursor(MySQLdb.cursors.DictCursor)
