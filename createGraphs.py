import sys
import os
import time
from os import listdir
from os.path import isfile, join
from xml.dom import minidom
import xml.sax
from xml.etree.ElementTree import iterparse
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import xml.parsers.expat

counters = {}
domains = {}
counterPrettyNames = {}

def listFiles(path):
    return [join(path, f) for f in listdir(path) if isfile(join(path, f))]

def putIntoCounters(name, value):
    if name not in counters:
        counters[name] = []
    counters[name].append(value)

def readFile(name):
    with open(name) as file:
        for line in file:
            if "ns1:CounterNameType" in line:
                countername = line.replace("<Name xsi:type=\"ns1:CounterNameType\">", "").replace("</Name>", "").strip()
            elif "<Value xsi:type" in line:
                value = line.replace("<Value xsi:type=\"xsd:long\">", "").replace("</Value>", "").strip()
                putIntoCounters(countername, value)

def findChildNodeByName(parent, name):
    for node in parent.childNodes:
        if node.nodeType == node.ELEMENT_NODE and node.localName == name:
            return node
    return None

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def readFileXMLParse(name):
    # safer but takes too long (ca. 1s per file)
    xmldoc = minidom.parse(name)
    itemlist = xmldoc.getElementsByTagName('item') 
    print len(itemlist)
    for s in itemlist:
        if s.attributes['xsi:type'].value == "ns1:CounterInfoType":
            name = findChildNodeByName(s, 'Name')
            if name is not None:
                counterName = getText(name.childNodes)
            value = findChildNodeByName(s, 'Value')
            if value is not None:
                counterValue = getText(value.childNodes)
            if name is not None and value is not None:
                putIntoCounters(counterName, counterValue)

def replaceBadChars(string):
    return string.replace(" ", "").replace("%", "Percent").replace("/", "")
    #.replace("#", "") 

def createDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def extractGroupName(name):
    splitted = name.split("(")
    dirname = splitted[0].replace(" ", "")
    entity = ""
    # if entity exists it will be prefixed to counter name
    if len(splitted) == 2 and len(splitted[1]) > 0 and splitted[1].endswith(")"):
            entity = splitted[1][:-1].replace(" ", "") # remove closing bracket
    return (dirname, entity)

class Domain:

    def __init__(self, name):
        self.name = name
        self.groups = {}

    def addGroup(self, group):
        self.groups[group.getName()] = group

    def getGroup(self, name):
        try:
            return self.groups[name]
        except KeyError:
            return None

    def getGroups(self):
        return self.groups

class Group:

    def __init__(self, groupPath, name, entity=""):
        self.groupPath = groupPath
        self.name = name
        self.entity = entity
        self.groupCounters = {}

    def addCounter(self, name, values):
        self.groupCounters[name] = values

    def getName(self):
        return self.name

    def getEntity(self):
        if len(entity) > 0:
            return entity + "__" 
        return ""

    def getCounters(self):
        return self.groupCounters

    def getPath(self):
        return self.groupPath

def getDomain(name):
    try:
        return domains[name]
    except KeyError:
        domain = Domain(name)
        domains[name] = domain
        return domain

def counterPrettyName(string):
    return counterPrettyNames[string]

def createPlots():
    for domainName, dom in domains.items():
        print "Domain: " + domainName
        createDir(domainName)

        totalCounters = 0
        for groupName, group in dom.getGroups().items():
            createDir(group.getPath())
            print "Creating plots for " + group.getName() + " (" + str(len(group.getCounters())) + " counters)" 
            for k, v in group.getCounters().items():
                totalCounters += 1
                pngPath = group.getPath() + "/" + k + ".png"
                print pngPath
                vector = robjects.StrVector(v)
                grdevices = importr('grDevices')
                grdevices.png(file=pngPath, width=512, height=512)
                r = robjects.r
                try:
                    counterName = counterPrettyNames[k]
                except KeyError:
                    counterName = k
                r.plot(vector,  type="o", col="blue", xlab="time", ylab=counterName, main=counterName)
                grdevices.dev_off()

        print "Created plots for " + str(totalCounters)  + " counters in " + str(len(dom.getGroups()))  + " groups." 

if __name__ == "__main__":
    if len(sys.argv) is not 2:
        print "Usage: prog <path to CollectedData>" 
        sys.exit()

    fileList = listFiles(sys.argv[1])
    fileList.sort()

    #start_time = time.time()
    for file in fileList:
        readFile(file)
    #print("--- %s seconds ---" % str(time.time() - start_time))

    for item in counters.keys():
        # \\cucm91\Cisco Annunciator Device(ANN_2)\ResourceActive
        # entity is ANN_2
        splitted = item.split("\\")
        domain = getDomain(splitted[2])
        parsedDirAndEntity = extractGroupName(splitted[3])
        groupName = parsedDirAndEntity[0].replace(" ", "")
        entity = replaceBadChars(parsedDirAndEntity[1])
        groupPath = splitted[2] + "/" + groupName
        group = domain.getGroup(groupName)
        if group is None:
            group = Group(groupPath, groupName, entity)
            domain.addGroup(group)
        counterPrettyName = replaceBadChars(splitted[4])
        group.addCounter(group.getEntity()+counterPrettyName, counters[item])
        counterPrettyNames[group.getEntity()+counterPrettyName] = counterPrettyName

    createPlots()    

