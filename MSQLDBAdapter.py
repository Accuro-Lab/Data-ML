import mysql.connector
from typing import Dict

def setupDB(databaseName):
    cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database=databaseName)

    return [cnx.cursor(), cnx]


def tearDownDB(cursor, connection):
    cursor.close()
    connection.close()

def insert(tableName: str, databaseName: str, rowDict: Dict[str, str]) -> None:
    '''
    insert row into tableName
    '''
    [cursor, connection] = setupDB(databaseName)
    headerList = list(rowDict.keys())
    columnHeaders = ", ".join(headerList)
    valuesList = list(map(lambda header: f'%({header})s', headerList))
    valuesPlaceHolders = ", ".join(valuesList)
    
    insertCommand = f'INSERT INTO {tableName} ({columnHeaders}) VALUES ({valuesPlaceHolders})'

    cursor.execute(insertCommand, rowDict)

    #Make sure data is committed to db
    connection.commit()

    tearDownDB(cursor, connection)



    