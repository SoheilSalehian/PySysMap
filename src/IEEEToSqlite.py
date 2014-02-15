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
                      (Document_Title VARCHAR[500],Authors VARCHAR[500],Author_Affiliations VARCHAR[500],Publication_Title VARCHAR[500],\
                       Publication_Date VARCHAR[500],Publication_Year VARCHAR[500],Volume VARCHAR[500],\
                       Issue VARCHAR[500],Start_Page VARCHAR[500],End_Page VARCHAR[500],Abstract VARCHAR[5000],\
                       ISSN VARCHAR[500],ISBN VARCHAR[500],EISBN VARCHAR[500],DOI VARCHAR[500],PDF_Link VARCHAR[500],\
                       Author_Keywords VARCHAR[500],IEEE_Terms VARCHAR[500],INSPEC_Controlled_Terms VARCHAR[500],\
                       INSPEC_Non_Controlled_Terms VARCHAR[500],DOE_Terms VARCHAR[500],PACS_Terms VARCHAR[500],\
                       MeSH_Terms VARCHAR[500],Article_Citation_Count VARCHAR[500],Patent_Citation_Count VARCHAR[500],\
                       Reference_Count VARCHAR[500],Copyright_Year VARCHAR[500],Online_Date VARCHAR[500],\
                       Date_Added_To_Xplore VARCHAR[500],Meeting_Date VARCHAR[500],Publisher VARCHAR[500],Sponsors VARCHAR[500],\
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