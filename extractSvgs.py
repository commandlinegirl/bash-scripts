import sys
from datetime import datetime
from xml.dom import minidom

""" Program for extracting graphics (svgs) from an XML file. """

def readFileXMLParse(name):
    xmldoc = minidom.parse(name)
    graphics = xmldoc.getElementsByTagName('graphic') 
    print "Found %s svg files." % len(graphics) 
    return graphics

def createFileName(index):
    #return 'file' + index + '-' + datetime.now().strftime("%Y%m%d%H%M%S") + '.svg'
    return 'file' + index + '.svg'

def createFile(cdataContent, index):
    filename = createFileName(index)
    with open(filename, 'w') as f:
       f.write(cdataContent)

if __name__ == "__main__":
    if len(sys.argv) is not 2:
        print "Usage: python extractSvgs.py <path to input file>"
        sys.exit()

    graphics = readFileXMLParse(sys.argv[1])
    for index, g in enumerate(graphics):
        for node in g.childNodes:
            if node.nodeType == 4:
                cdataContent = node.data.strip()
                createFile(cdataContent, str(index))


