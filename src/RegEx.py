import sqlite3
import sys
import re
import time

connection = None

def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None

def searchQuery(selectExpr, tableExpr, columnExpr, regEx):
    cursorString = "'SELECT %(selectExpr)s FROM %(tableExpr)s WHERE %(columnExpr)s REGEXP ?',['%(regEx)s']" % \
                   {'selectExpr':selectExpr, 'tableExpr':tableExpr, 'columnExpr':columnExpr, 'regEx':regEx}
    
    print cursorString
    cursor.execute(cursorString)
    data=cursor.fetchall()
    print(data)
    
    

try:
    t = time.time()
    # Connect to the database
    connection = sqlite3.connect('PySysMapDB.db')
    # Create the regex function map for sqlite
    connection.create_function("REGEXP", 2, regexp)
    cursor = connection.cursor()
    data = {}
    
    # IEEE Data only
    cursor.execute('SELECT Document_Title, PDF_Link, Abstract, Publication_Year FROM IEEETable WHERE Document_Title REGEXP ? or Abstract REGEXP ?',
                   ['synthesis' or 'high level synthesis', 'design exploration' and 'synthesis' or 'high level synthesis' or 'HLS'])
    data['IEEEHLS'] = cursor.fetchall()
    
    
    cursor.execute('SELECT Document_Title, PDF_Link, Abstract, Publication_Year FROM IEEETable WHERE Document_Title REGEXP ? or Abstract REGEXP ?',
                   ['virtual [environment|prototype|platform]', 'virtual [environment|prototype|platform]'])
    data['IEEEvirtualPlatform'] = cursor.fetchall()
    
    
    # Merged Data with Scholar + IEEE
    cursor.execute('SELECT title, abstract, year FROM ScholarTable WHERE title REGEXP ? or abstract REGEXP ?',
                   ['synthesis' or 'high level synthesis', 'design exploration' and 'synthesis' or 'high level synthesis' or 'HLS'])
    data['HLS'] = cursor.fetchall()
    
    
    cursor.execute('SELECT title, abstract, year FROM ScholarTable WHERE title REGEXP ? or abstract REGEXP ?',
                   ['virtual [environment|prototype|platform]', 'virtual [environment|prototype|platform]'])
    data['virtualPlatform'] = cursor.fetchall()
    
    # To look through the data
    for key, values in data.iteritems():
        print key, len(values)
    
    print "\n Time Taken: %.3f sec" % (time.time()-t)
    
    
    

except sqlite3.Error, e:
    
    print "Error %s:" % e.args[0]
    sys.exit(1)



#finally:
#    if connection:
#        # Commit the results and close the connection
#        connection.commit()