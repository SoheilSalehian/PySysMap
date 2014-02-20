import urllib2
from urllib2 import Request, urlopen
from PyPDF2 import PdfFileWriter, PdfFileReader
from StringIO import StringIO
import re
import subprocess


url = "http://www.cecs.uci.edu/~papers/date07_universitybooth/Sessions/Session1/S12.pdf"
#url = "http://www.enel.ucalgary.ca/People/Norman/encm501winter2014/assignments/encm501w14assign04-complete.pdf"

## @fn pdfDownload(url)
#  @brief This function downloads the pdf file based on a url given
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


def throughUCProxy():
    proxy = urllib2.ProxyHandler({'http': 'http://username:ssalehia:Acdsee32!@http://ieeexplore.ieee.org.ezproxy.lib.ucalgary.ca:2048'})
    auth = urllib2.HTTPBasicAuthHandler()
    opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
    urllib2.install_opener(opener)

## @fn pdfCount(pdfFilePath, patternList)
#  @brief This function looks into a pdf file for the number of occurances of the pattern given
#  Due to inconsistant behaviour of the PyPDF.extract(), this function turns the file into a text 
#  file and then looks for the pattern.
def pdfCount(pdfFilePath, patternList):
    # Call from shell to change the file to text
    subprocess.call(['pdftotext', pdfFilePath, 'output.txt'])
    # Dictionary for book keeping of pattern and occurance
    patternToOccurance = {}
    try:
        # Open the temporary text file
        fp = open('output.txt', "r")
    # Error handling for IO
    except IOError as inst: 
        print inst 
        return
    # Read the whole file in as text
    fileText = fp.read()
    for pattern in patternList:
        # Make sure the references section is seperated
        refSeperated = fileText.split('References\n[')
        # Find all the occurances of the case insensitive pattern up to the References section 
        reLookup = re.findall(pattern, refSeperated[0], re.IGNORECASE)
        # Store in the dictionary
        patternToOccurance[pattern]=len(reLookup)
    # Cleanup the temporary text file
    subprocess.call("rm output.txt", shell=True)
    # Return the dictionary that maps pattern to # of occurances 
    return patternToOccurance
    
        

if __name__ == "__main__":
    pdfDownload(url)
    print 'The Number is: ', pdfCount('/home/soheil/workspace/PySysMap/src/output.pdf',['chippo', 'computer'])