import csv
import MySQLdb

mydb = MySQLdb.connect(host='localhost',
    user='root',
    passwd='acdsee32',
    db='PySysMapDB')
cursor = mydb.cursor()

csv_data = csv.reader(file('/home/soheil/workspace/PySysMap/src/agileEmbedded.csv'))
for row in csv_data:
#    print row
#    print len(row[0].split('|'))
    cursor.execute("INSERT INTO ScholarInputData(title,\
                                                 url, \
                                                 num_citations, \
                                                 num_versions, \
                                                 url_citations, \
                                                 url_versions, \
                                                 abstract, \
                                                 year) \
                                                 VALUES(%s|%s|%s|%s|%s|%s|%s|%s)", 
                                                 row)
     

#close the connection to the database.
mydb.commit()
cursor.close()
print "Done"