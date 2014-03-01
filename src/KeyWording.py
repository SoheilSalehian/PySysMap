## @file KeyWording.py
#  @brief This module sends the proper keywords to the database 
#  and works on the number of occurances of each keyword per article.

import sqlite3
import sys
import re
import time
import PdfDownload
from collections import defaultdict
import math

connection = None

## @fn regexp(expr, item)
#  @brief This function implements python regular expression mechanisms for sqlite3 queries
def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item, re.IGNORECASE) is not None

def generateYearTrendData(cursor, keyWord, threshold):
    dic, tot = keyWordingDB(cursor=cursor, keyWord=keyWord, threshold=threshold)
    for year, idList in dic.iteritems():
        print year,len(idList)

## @fn keyWordingDB(cursor, keyWord, threshold)
#  @brief The main keywording function that mines the database PDF section to report keywording results
#  This function uses @var KeyWord to find the IDs that match the expression 
def keyWordingDB(cursor, keyWord, threshold):
    data = {}
    print keyWord
    # Request for the count of the keywords
    cursor.execute('SELECT count(*) FROM IEEETable WHERE PDF REGEXP ? and PDF REGEXP ?',
                   keyWord)
    
    dataKey = str(keyWord).replace(',', ' & ')[1:-1]
    data[dataKey] = cursor.fetchall()
    
    # To print the keyword and number of articles found data
    for key, values in data.iteritems():
        print key, values
    
    # Do the same query but for id, document title, and PDF 
    cursor.execute('SELECT id,Document_Title,PDF,Publication_Year FROM IEEETable WHERE PDF REGEXP ? and PDF REGEXP ?',
                   keyWord)
    idPDF = cursor.fetchall()
    
#    print "length",len(idPDF)
    idYearDic = defaultdict(list)
    # Use the queried data to find the count of occurances of each keyword
    for id,title, pdfText, year in idPDF:
        countDic = PdfDownload.pdfCount(keyWord,fileText=pdfText)
#        print "title:", title
        if countDic[keyWord[0]] >= threshold and countDic[keyWord[1]] >= 4:   
#            print "( id:", id, ")",
#            print countDic
    
            idYearDic[year].append(id)
    
    # Get the total number of classified articles
    totalNumber = 0
    for values in idYearDic.values():
        totalNumber += len(values)        
    print "Total classified articles:", totalNumber     

    print "\n---------------------------------------------------------------\n" 
    return idYearDic, totalNumber



def checkDuplicates(firstData, secondData):
    firstFullIDList = []
    secondFullIDList = []
    for ids in firstData[0]:
        for id in ids:
            firstFullIDList.append(id)
    
    for ids in secondData[0]:
        for id in ids:
            secondFullIDList.append(id)
    
    return len(set(firstFullIDList) & set(secondFullIDList))
    
         
    
    

## @fn classifyQ1(cursor)
#  @brief This functions makes the classifcation for Q1 and reports results
def classifyQ1(cursor):
    data = {}
    tot = 0
    # IEEE Data only
    data['hardware'] =keyWordingDB(cursor=cursor, keyWord=['high level synthesis|synthesis|HLS',''],threshold=5)
    data['software'] = keyWordingDB(cursor=cursor, keyWord=['virtual prototype|embedded software|virtual platform|driver|software debug',''],threshold=1)
    data['system'] = keyWordingDB(cursor=cursor, keyWord=['design exploration|system designer|optimization|behavioral model|partition point',''],threshold=5)
    
    # Check for duplicates to determine intersection between classes
    print 'hw/sw duplicates:', checkDuplicates(data['hardware'], data['software'])
    print 'hw/system duplicates:', checkDuplicates(data['hardware'], data['system'])
    print 'system/sw duplicates:', checkDuplicates(data['system'], data['software'])

#    
#    keyWordingDB(cursor=cursor, keyWord=['embedded software','automation'])
#    keyWordingDB(cursor=cursor, keyWord= 'Computer')
#    print type(data['hardware'])
#    print "hw/sw", len(set(data['hardware'][0]) & set(data['software'][0]))
#    print "hw/sys", len(set(data['hardware']) & set(data['system']))
#    print "sw/sys", len(set(data['system']) & set(data['software']))
    

    
    print "classification coverage:", (tot1+tot2+tot3)/float(695-108) 
    
## @fn classifyQ2(cursor)
#  @brief This functions makes the classifcation for Q1 and reports results
def classifyQ2(cursor):
    data = {}
    tot = 0
    # TODO: Fix the total calculations without too many local vars
    # Check to see the number of tools roughly for coverage % calculation
    data['tools']= keyWordingDB(cursor=cursor, keyWord=['tools|Tool|language|framework',''], threshold=5)
    data['Matlab']=keyWordingDB(cursor=cursor, keyWord=['Matlab|Simulink',''],threshold=10)
    data['systemC'] = keyWordingDB(cursor=cursor, keyWord=['SystemC|IEEE 1666|systemC',''],threshold=10)

    data['C/C++'] = keyWordingDB(cursor=cursor, keyWord=['C\+\+|C language|C Language',''],threshold=10)
#    data['C'] = keyWordingDB(cursor=cursor, keyWord=['C language|C Language',''],threshold=10)
    data['TLM'] = keyWordingDB(cursor=cursor, keyWord=['TLM|tlm 2.0|transaction level modeling',''],threshold=10)
    data['HDL'] = keyWordingDB(cursor=cursor, keyWord=['VHDL|verilog|SVA|system verilog|HDVL',''],threshold=10)
    data['ptolemy'] = keyWordingDB(cursor=cursor, keyWord=['ptolemy',''],threshold=10)
    data['UML'] = keyWordingDB(cursor=cursor, keyWord=['UML',''],threshold=10)
    data['SysML'] = keyWordingDB(cursor=cursor, keyWord=['SysML',''],threshold=10)
    data['MARTE'] = keyWordingDB(cursor=cursor, keyWord=['MARTE',''],threshold=1)
    data['Rosetta'] = keyWordingDB(cursor=cursor, keyWord=['Rosetta',''],threshold=1)
    data['IP-XACT'] = keyWordingDB(cursor=cursor, keyWord=['IP-XACT',''],threshold=1)
    
#    # Check for duplicates to determine intersection between classes
    print 'C++ & SystemC duplicates:', checkDuplicates(data['C/C++'], data['systemC'])
#    print 'C & SystemC duplicates:', checkDuplicates(data['C'], data['systemC'])
    print 'SystemC & Matlab duplicates:', checkDuplicates(data['Matlab'], data['systemC'])
    print 'SystemC & TLM duplicates:', checkDuplicates(data['systemC'], data['TLM'])
    print 'SystemC & UML duplicates:', checkDuplicates(data['systemC'], data['UML'])
    print 'SystemC & HDL duplicates:', checkDuplicates(data['systemC'], data['HDL'])
   
    total = 0
    for key in data.keys():
        # Set the precision of the decimal representation to 3
        print str(int(math.ceil(float('%.3f'%(((data[key][1])/float(data['tools'][1]))*100)))))+'/'+key+','
        total += data[key][1]/float('%.2f'%(float(data['tools'][1])))
    
    print "Classification Coverage:", total-1
        
 
        
#    keyWordingDB(cursor=cursor, keyWord=['embedded software','automation'])
#    keyWordingDB(cursor=cursor, keyWord= 'Computer')
#    print type(data['hardware'])
#    print "systemC/Matlab", len(set(data['systemC']) & set(data['Matlab']))
#    print "systemC/C++", len(set(data['C++']) & set(data['systemC']))
#    print "Matlab/C++", len(set(data['C++']) & set(data['Matlab']))

#    print "classification coverage:", (tot1+tot2+tot3+tot4+tot5+tot6+tot7+tot8+tot9+tot10+tot11+tot12)/float(tot0)

try:
    t = time.time()
    # Connect to the database
    connection = sqlite3.connect('PySysMapDB.db')
    # Set the connection to return string (UTF-8)
    connection.text_factory = str
    # Create the regex function map for sqlite
    connection.create_function("REGEXP", 2, regexp)
    cursor = connection.cursor()
    
    
    classifyQ2(cursor)
#    generateYearTrendData(cursor,keyWord=['high level synthesis|synthesis|HLS',''], threshold=6)
#    generateYearTrendData(cursor,keyWord=['virtual prototype|embedded software|virtual platform|driver|software debug|software/hardware partition',''], threshold=5)
#    generateYearTrendData(cursor,keyWord=['design exploration|system designer|optimization|behavioral model|partition point',''], threshold=6)

    
#    for year, id in dic.iteritems():
#        print "year", year, "num", id

    print "\n Time Taken: %.3f sec" % (time.time()-t)
    
    

except sqlite3.Error, e:
    
    print "Error %s:" % e.args[0]
    sys.exit(1)




#finally:
#    if connection:
#        # Commit the results and close the connection
#        connection.commit()