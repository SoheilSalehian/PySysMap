## @file AddPDFtoTable.py
#  @brief A short script that puts the pdf content in the IEEE table as a new column
import csv,sqlite3
import sys
import time
import PdfDownload
import re
import subprocess
import KeyWording
import IEEEToSqlite
import PyPDF2

connection = None
# For first time use of the script please set these flags to be True to download pdfs and create the columns
downloadPDF = False
# Sqlite doesn't support if not exist column clause hence this ugly workaround
firstColumnCreation = True

pdfFileBasePath = '/home/soheil/Downloads/PySysMapPDFs/'

def addPDFtoDB():
    try:
        t = time.time()
        # Connect to the database
        connection = sqlite3.connect('PySysMapDB.db')
        # Set the connection to return string (UTF-8)
        connection.text_factory = str
        connection.create_function("REGEXP", 2, KeyWording.regexp)
        cursor = connection.cursor()
        
#        if firstColumnCreation:
#            # Add the pdf column to the IEEETable
#            print "Adding PDF Column to Database..."
#            cursor.execute('ALTER TABLE IEEETable ADD PDF BLOB DEFAULT NONE;')
#            cursor.fetchall()
        
        # Mine for the pdf links
        cursor.execute('SELECT PDF_Link FROM IEEETable;')
        pdfLinks = cursor.fetchall()
        print len(pdfLinks)
        
        # If downloading for the first time
        if downloadPDF:
            # Step through each link
            for link in pdfLinks:
                print "downloading:", link
                # Download each pdf
                PdfDownload.pdfEmbeddedDownloadage(link[0])
            
        
        # set the directory of the pdfs
        for link in pdfLinks:
            print link[0]
            pdfFilePath = pdfFileBasePath + pdfNameProvider(link[0], zeroFillFlag = 0) + '.pdf'
            textFilePath = pdfFileBasePath + 'TextFile/' + pdfNameProvider(link[0], zeroFillFlag = 0) + '.txt'
            # Call from shell to change the file to text using exception handling
            try:
                # Try to convert the pdf file based on link article number
                subprocess.check_call(["pdftotext", "-q", pdfFilePath, textFilePath])
                
    
            except subprocess.CalledProcessError:
                # If there is need for zeropadding the name
#                print "[PySysMap] ",  "File name is missing a zero...zero appending"
                # Do the zero padding by setting @var zeroFillFlag to 1
                pdfFilePath = pdfFileBasePath + pdfNameProvider(link[0], zeroFillFlag = 1) + '.pdf'
                try:
                    # Convert to text again
                    subprocess.check_call(["pdftotext", "-q", pdfFilePath, textFilePath])
                # Exception handling for uncorrectly downloaded pdfs
                except: 
                    PdfDownload.pdfEmbeddedDownloadage(link[0])
                # Finally run the tex conversion again
                finally:
                    subprocess.check_call(["pdftotext", "-q", pdfFilePath, textFilePath])
                
                
                if not textFilePath:
                    raise IOError
                    
                
                textFile = readTextFile(textFilePath)
                
                if not textFile:
                    return
                
                # TODO: Fix the reference Bug 
                # Make sure the references section is seperated
#                textFile = re.split('REFERENCES|References', textFile)
                # Find the id to be updated
                cursor.execute('SELECT id FROM IEEETable WHERE Pdf_Link REGEXP ?',[pdfNameProvider(link[0], zeroFillFlag = 0)])
                id = cursor.fetchone()
                if not id:
                    print 'No id was retrieved'
                    sys.exit(1)
                print "id:", id[0]
                # Update the PDF column with the textFile (w/o References) based on unique key(id)
                cursor.execute("UPDATE IEEETable SET PDF=? WHERE id=?", (textFile,id[0]))
                cursor.fetchone()
            
        # Commit the results and close the connection
        connection.commit()
        connection.close()
        print "\n Time Taken: %.3f sec" % (time.time()-t)
        
    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
        sys.exit(1)


def readTextFile(textFilePath):
    try:
        # Open the temporary text file
        fp = open(textFilePath, "rb")
    # Error handling for IO
    except IOError as inst: 
        print inst 
        return
    # Read the whole file in as text and return it
    return fp.read()

    

def pdfNameProvider(pdfLink, zeroFillFlag):
    if zeroFillFlag:
        return str('0'+re.search('arnumber=(\d+)',pdfLink).group(1))
    else:
        return str(re.search('arnumber=(\d+)',pdfLink).group(1))    
        

def getPDFContent(path):
    content = ""
    # Load PDF into pyPDF
    pdf = PyPDF2.PdfFileReader(file(path, "rb"))
    # Iterate pages
    for i in range(0, pdf.getNumPages()):
        # Extract text from page and add to content
        content += pdf.getPage(i).extractText() + "\n"
    # Collapse whitespace
    content = " ".join(content.replace("\xa0", " ").strip().split())
    return content



if __name__ == '__main__':
#    pdfNameProvider('http://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=5247153', zeroFillFlag=1)
    if firstColumnCreation:
        IEEEToSqlite.IEEEToSqlite()
    addPDFtoDB()
#    print getPDFContent("/home/soheil/Downloads/PySysMapPDFs/06336987.pdf")
