## @file ConvergeTables.py
#  @brief A short script that looks into the descrepency between the Scholar and IEEE tables and fills the
#  Scholar table with the missing articles from IEEE full data search.


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
    cursor.executescript('drop table if exists BufferTable;')
    
    # Create the table to hold scholar data
    cursor.execute('''CREATE TABLE IF NOT EXISTS BufferTable
                      (title VARCHAR[700], url VARCHAR[600], num_citations INT, num_versions INT, 
                      url_citations VARCHAR[600], url_versions VARCHAR[600], abstract TEXT, year INT)''')
    
    # Find the number of descrepencies between the two tables with the following query
    cursor.execute('''select count(*) from IEEETable WHERE Document_Title not in (SELECT title from ScholarTable);''')
    diffCount = cursor.fetchall()[0][0]
    print "Difference count between tables:", diffCount
    
    # Fill up the buffer table
    cursor.execute('''INSERT INTO BufferTable 
                      select Document_Title, PDF_link, Article_Citation_Count, NULL, NULL, NULL, Abstract, Publication_Year 
                      from IEEETable WHERE Document_Title not in (SELECT title from ScholarTable);''')
    
    # Find the count of the elements in the buffer table
    cursor.execute('''SELECT count(*) from BufferTable;''')
    print "Number of elements in the buffer table:", cursor.fetchall()[0][0]
    
    # TODO: Add error handling mechanisms to ensure sanity of database
    
    # Number of elements before Append
    cursor.execute('''SELECT count(*) from ScholarTable;''')
    print "Pre-append number of elements of ScholarTable:", cursor.fetchall()[0][0]
    # Append the data from BufferTable to the ScholarTable
    cursor.execute('''INSERT INTO ScholarTable SELECT * FROM BufferTable;''')
    # Number of elements after Append
    cursor.execute('''SELECT count(*) from ScholarTable;''')
    print "Post-append number of elements of ScholarTable:", cursor.fetchall()[0][0]
    
    print "Time Taken: %.3f sec" % (time.time()-t)
    

except sqlite3.Error, e:
    
    print "Error %s:" % e.args[0]
    sys.exit(1)

finally:
    if connection:
        # Commit the results and close the connection
        connection.commit()
        cursor.execute('SELECT * FROM ScholarTable;')
        connection.close()