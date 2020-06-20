import csv
import MSQLDBAdapter as db

with open('test.tsv') as tsvfile:
  reader = csv.DictReader(tsvfile, dialect='excel-tab')
  for row in reader:
    print('Inserting row: ', end=' ')
    print(row)
    db.insert('TestTable', 'testdb', row)