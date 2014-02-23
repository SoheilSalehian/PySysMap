from urllib2 import Request, urlopen
from PyPDF2 import PdfFileWriter, PdfFileReader
from StringIO import StringIO
import re
import time
import os
import webbrowser
import subprocess, signal
import sqlite3

#url = "http://ieeexplore.ieee.org/xpl/articleDetails.jsp?tp=&arnumber=5247153&queryText%3Delectronic+system+level+methodologies"
#url = "http://ieeexplore.ieee.org/ielx5/5638200/5648785/05654090.pdf"
#url = "http://ieeexplore.ieee.org/ielx5/5638200/5648785/05654090.pdf?tp=&arnumber=5654090&isnumber=5648785"
url = "http://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=5247153"
#url = "http://www.enel.ucalgary.ca/People/Norman/encm501winter2014/assignments/encm501w14assign04-complete.pdf"
#USER_AGENT = 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11'


## @fn pdfDownload(url)
#  @brief This function downloads normal non Javascript embedded pdf file based on a url given
#  and writes the binary version as "output.pdf"
#  Use this function for general purpose downloading needs if embedded pdfs are not an issue.
def pdfDownload(url):
    writer = PdfFileWriter()
    remoteFile = urlopen(Request(url)).read()
    memoryFile = StringIO(remoteFile)
    pdfFile = PdfFileReader(memoryFile)
    for pageNum in xrange(pdfFile.getNumPages()):
            currentPage = pdfFile.getPage(pageNum)
            #currentPage.mergePage(watermark.getPage(0))
            writer.addPage(currentPage)    
    outputStream = open("output.pdf","wb")
    writer.write(outputStream)
    outputStream.close()


## @fn pdfEmbeddedDownloadage(url)
#  @brief This function downloads the embedded pdf file based on a article link provided
#  NOTE: To avoid firefox crashes, about:config into the firefox location bar -> toolkit.startup.max_resumed_crashes = -1
def pdfEmbeddedDownloadage(articleLink):
    # Open the browser with "save to disk" enabled
    webbrowser.get('firefox').open_new(articleLink)
    # Wait for the download to finish
    time.sleep(10)
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    for line in out.splitlines():
        if 'firefox' in line:
            pid = int(line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)
    
## @fn urlProvider(articleNumber)
#  @brief This method constructs the proper url to download in case it doesn't exist
def urlProvider(articleNumber):
    targetURL = "http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=%(number)s&userType=inst"
    return targetURL % {'number': articleNumber}    

     

## @fn pdfCount(pdfFilePath, patternList, dbMineFlag=False)
#  @brief This function looks into a pdf file for the number of occurances of the pattern given
#  Due to inconsistant behaviour of the PyPDF.extract(), this function turns the file into a text 
#  file and then looks for the pattern. @var dbMineFlag is used to use the function to mine the pdf already in the database and not the actual PDF
def pdfCount(patternList, fileText=None, pdfFilePath=None):
    # Dictionary for book keeping of pattern and occurance
    patternToOccurance = {}
    if pdfFilePath:
        # Call from shell to change the file to text
        subprocess.call(['pdftotext', pdfFilePath, 'output.txt'])
        try:
            # Open the temporary text file
            fp = open('output.txt', "r")
        # Error handling for IO
        except IOError as inst: 
            print inst 
            return
        # Read the whole file in as text
        fileText = fp.read()
    else:
        fileText = fileText
    
    
    for pattern in patternList:
        # Make sure the references section is seperated
        refSeperated = fileText.split('References\n[')
        # Find all the occurances of the case insensitive pattern up to the References section 
        reLookup = re.findall(pattern, refSeperated[0], re.IGNORECASE)
        # Store in the dictionary
        patternToOccurance[pattern]=len(reLookup)
    
    if pdfFilePath:
        # Cleanup the temporary text file
        subprocess.call("rm output.txt", shell=True)
    # Return the dictionary that maps pattern to # of occurances 
    return patternToOccurance
    

if __name__ == "__main__":
    t = time.time()
#    pdfDownload(url)
#    artNumList = ['5247153','6628330']
#    pdfEmbeddedDownloadage(artNumList)
    print 'The Number is: ', pdfCount(patternList=['ESL', 'level synthesis', 'HLS'],pdfFilePath ='/home/soheil/workspace/PySysMap/src/output.pdf', fileText=None)
    print "\n Time Taken: %.3f sec" % (time.time()-t)