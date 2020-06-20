import csv
import MSQLDBAdapter as db
import sys
import argparse

def ingest(DBName: str, TableName: str, TSVFilename: str) -> None:
    with open('test.tsv') as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')
        for row in reader:
            print('Inserting row: ', end=' ')
            print(row)
            db.insert('TestTable', 'testdb', row)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest Args Handler')
    parser.add_argument('srcFile')
    parser.add_argument('dbName')
    parser.add_argument('tableName')
    options = vars(parser.parse_args())
    ingest(options['dbName'], options['tableName'], options['srcFile'])
