## @file CSVtoSqlite
#  @brief A short script that creates the table in the sqlite database based on
#         the input csv data file.
#  Please be aware that the file overwrites the table in case it existed already.

import csv, sqlite3
import sys
import time

connection = None

try:
    t = time.time()
    # Connect to the database
    connection = sqlite3.connect('PySysMapDB.db')
    connection.text_factory = str
    cursor = connection.cursor()
    
    #Uncomment to drop the table and recreate
    cursor.executescript('drop table if exists ScholarTable;')
    
    # Create the table to hold scholar data
    cursor.execute('''CREATE TABLE IF NOT EXISTS ScholarTable
                      (title VARCHAR[700], url VARCHAR[600], num_citations INT, num_versions INT, 
                      url_citations VARCHAR[600], url_versions VARCHAR[600], abstract TEXT, year INT)''')
    

    # Read the CSV file with the seperator "|"
    csv_data = csv.reader(open('/home/soheil/workspace/PySysMap/src/Data/ESL.csv', "rb"), delimiter='|')
    # Iterate through each article
    for title, url, num_citations, num_versions, url_citations, url_versions, abstract, year in csv_data:
        cursor.execute("INSERT INTO ScholarTable(title, url, num_citations, num_versions, url_citations, url_versions, abstract, year)VALUES(?,?,?,?,?,?,?,?)", (title, url, num_citations, num_versions, url_citations, url_versions, abstract, year))

    print "\n Time Taken: %.3f sec" % (time.time()-t)
    

except sqlite3.Error, e:
    
    print "Error %s:" % e.args[0]
    sys.exit(1)

finally:
    if connection:
        # Commit the results and close the connection
        connection.commit()
        cursor.execute('SELECT * FROM ScholarTable;')
        connection.close()