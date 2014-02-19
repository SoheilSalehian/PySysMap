import sqlite3
import sys
import re

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
    # Connect to the database
    connection = sqlite3.connect('PySysMapDB.db')
    # Create the regex function map for sqlite
    connection.create_function("REGEXP", 2, regexp)
    cursor = connection.cursor()
    data = {}
    
    
    cursor.execute('SELECT Document_Title FROM IEEETable WHERE document_title REGEXP ?',['FPGA'])
    data['methodology'] = cursor.fetchall()
    
    
#    cursor.execute('SELECT count(*) FROM IEEETable WHERE Document_Title REGEXP ?',['FPGA'])
#    data['FPGA'] = cursor.fetchall()
    i = 0
    for key, values in data.iteritems():
        print len(values)
        for doc in values:
            print doc
            i = i+1
    print i

#    regEx = 'ESA'

#    cursor.execute('SELECT count(*) FROM IEEETable WHERE Document_Title REGEXP ?',['%(regEx)s' % {'regEx': regEx}])
#    data['%(regEx)s' % {'regEx': regEx}] = cursor.fetchall()
#    print(data)
#    cursor.execute('SELECT Document_Title FROM IEEETable WHERE Abstract REGEXP ?',['virtual prototype'])
#    data=cursor.fetchall()
#    
#    for doc in data:
#        print doc
    
    

except sqlite3.Error, e:
    
    print "Error %s:" % e.args[0]
    sys.exit(1)



#finally:
#    if connection:
#        # Commit the results and close the connection
#        connection.commit()