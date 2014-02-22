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
    cursor.executescript('drop table if exists IEEETable;')
    
    # Create the table to hold scholar data
    cursor.execute('''CREATE TABLE IF NOT EXISTS IEEETable
                      (id INTEGER PRIMARY KEY autoincrement, Document_Title BLOB,Authors BLOB,Author_Affiliations BLOB,Publication_Title BLOB,\
                       Publication_Date BLOB,Publication_Year BLOB,Volume BLOB,\
                       Issue BLOB,Start_Page BLOB,End_Page BLOB,Abstract VARCHAR[5000],\
                       ISSN BLOB,ISBN BLOB,EISBN BLOB,DOI BLOB,PDF_Link BLOB,\
                       Author_Keywords BLOB,IEEE_Terms BLOB,INSPEC_Controlled_Terms BLOB,\
                       INSPEC_Non_Controlled_Terms BLOB,DOE_Terms BLOB,PACS_Terms BLOB,\
                       MeSH_Terms BLOB,Article_Citation_Count BLOB,Patent_Citation_Count BLOB,\
                       Reference_Count BLOB,Copyright_Year BLOB,Online_Date BLOB,\
                       Date_Added_To_Xplore BLOB,Meeting_Date BLOB,Publisher BLOB,Sponsors BLOB,\
                       Document_Identifier)''')
    

    # Read the IEEE CSV file with the seperator ","
    csv_data = csv.reader(open('/home/soheil/workspace/PySysMap/src/Data/IEEE_ESL.csv', "rb"), delimiter=',')
    # Iterate through each article
    for Document_Title,Authors,Author_Affiliations,Publication_Title,Publication_Date,Publication_Year,Volume,Issue,Start_Page,End_Page,\
    Abstract,ISSN,ISBN,EISBN,DOI,PDF_Link,Author_Keywords,IEEE_Terms,INSPEC_Controlled_Terms,INSPEC_Non_Controlled_Terms,\
    DOE_Terms,PACS_Terms,MeSH_Terms,Article_Citation_Count,Patent_Citation_Count,Reference_Count,Copyright_Year,Online_Date,\
    Date_Added_To_Xplore,Meeting_Date,Publisher,Sponsors,Document_Identifier in csv_data:
        
        cursor.execute("INSERT INTO IEEETable(Document_Title,Authors,Author_Affiliations,Publication_Title,Publication_Date,Publication_Year,Volume,Issue,Start_Page,End_Page,\
                        Abstract,ISSN,ISBN,EISBN,DOI,PDF_Link,Author_Keywords,IEEE_Terms,INSPEC_Controlled_Terms,INSPEC_Non_Controlled_Terms,\
                        DOE_Terms,PACS_Terms,MeSH_Terms,Article_Citation_Count,Patent_Citation_Count,Reference_Count,Copyright_Year,Online_Date,\
                        Date_Added_To_Xplore,Meeting_Date,Publisher,Sponsors,Document_Identifier)\
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",\
                        (Document_Title,Authors,Author_Affiliations,Publication_Title,Publication_Date,Publication_Year,Volume,Issue,Start_Page,End_Page,\
                        Abstract,ISSN,ISBN,EISBN,DOI,PDF_Link,Author_Keywords,IEEE_Terms,INSPEC_Controlled_Terms,INSPEC_Non_Controlled_Terms,\
                        DOE_Terms,PACS_Terms,MeSH_Terms,Article_Citation_Count,Patent_Citation_Count,Reference_Count,Copyright_Year,Online_Date,\
                        Date_Added_To_Xplore,Meeting_Date,Publisher,Sponsors,Document_Identifier))

    print "\n Time Taken: %.3f sec" % (time.time()-t)
    

except sqlite3.Error, e:
    
    print "Error %s:" % e.args[0]
    sys.exit(1)

finally:
    if connection:
        # Commit the results and close the connection
        connection.commit()
        connection.close()