# The MIT License (MIT)
# Copyright (C) 2014 Hulacode.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import argparse
import os
import xml.etree.ElementTree as ET
from collections import defaultdict

#vdict = defaultdict(dict)
#vdict['A']['A'] = 'A'
#vdict['A']['']

baselist = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
        '0','1','2','3','4','5','6','7','8','9',' ',';',',','!','?','.','$',':','*','#','@']

def AdjustKeyLength(plain,key):
    adjustedKey = key

    if len(key) > len(plain):
        adjustedKey = ''

    kpos = 0
    while len(adjustedKey) < len(plain):
        adjustedKey += key[kpos]
        kpos += 1
        if kpos > len(key)-1:
            kpos = 0

    return adjustedKey

def EncryptPassword(matrix,plain,key):
    cipher = ''
    if plain != None:
        key = AdjustKeyLength(plain,key)
    else:
        return 'NOTHING TO ENCRYPT'
    #key and plain are equal lengths.
    currpos = 0
    totallength = len(key)
    while currpos < totallength:
        forcedKeyLower = False
        forcedPlainLower = False
        charkey = key[currpos].lower()
        charplain = plain[currpos].lower()
        if charkey != key[currpos]:
            forcedKeyLower = True
        if charplain != plain[currpos]:
            forcedPlainLower = True
        try:
            cipherchar = matrix[charkey.upper()][charplain.upper()]
            if forcedPlainLower:
                cipherchar = '(' + cipherchar + ')'
            cipher += cipherchar
        except:
            cipher = 'INVALID KEY for character "' + charplain.upper() + '"'
            break
        currpos += 1

    return cipher

def BuildMatrix():
    #for entry in entries:
     #   print(entry)
    vdict = defaultdict(dict)
    #work row by row, first column
    #vdict['A']['A'] = 'A'
    #vdict['B']['A'] = 'B'
    #vdict['C']['A'] = 'C'
    #...
    #vdict['A']['B'] = 'B'
    #vdict['B']['B'] = 'C'
    #...
    currchar = ''
    for c in baselist:
        for r in baselist:
            currchar = GetNextChar(currchar)
            #print r, c, currchar
            vdict[r][c] = currchar
        currchar = GetNextChar(currchar)
    #WalkList('Z')
    #now, matrix is built in vdict
    return vdict

def PrintMatrix(matrix):


    #this does top row
    line = '   '
    for x in baselist:
        for y in baselist:
            line += matrix[x][y]
        print line
        break
    print '   ---------------------------------------------'
    #ensure first column
    colchar = GetNextChar('')
    line = colchar + '| '
    for x in baselist:
        for y in baselist:
            line += matrix[x][y]
        print line

        colchar = GetNextChar(colchar)
        line = colchar + '| '


def WalkList(startingchar):
    currpos = 0
    startpos = None
    for k in baselist:
        if k == startingchar:
            startpos = currpos
            break
        currpos += 1
    if startpos != None:
        totlength = len(baselist)
        for num in range(startpos, totlength):
            print baselist[num]
            #do something here.
        for num in range(0,startpos):
            print baselist[num]
            #do something here.
def GetNextChar(lastchar):
    currpos = 0
    startpos = None
    for k in baselist:
        if k == lastchar:
            startpos = currpos
            break
        currpos += 1
    if startpos != None:
        totlength = len(baselist)
        for num in range(startpos+1, totlength):
            #print baselist[num]
            ##do something here.
            return baselist[num]
        for num in range(0,startpos):
            #print baselist[num]
            #do something here.
            return baselist[num]
    else:
        return baselist[0]
class KPEntry:
    def __init__(self,node):
        self.Node = node
        self.Title = ''
        self.UserName = ''
        self.Password = ''
        self.Ciphered = ''
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        printstring = str(self.Title) + ' / ' + str(self.UserName) + ' / ' + str(self.Ciphered)
        return  printstring

class KP2Entry(KPEntry):
    def __init__(self,node):
        KPEntry.__init__(self,node)
        self.Title = self.GetValue('Title')
        self.UserName = self.GetValue('UserName')
        self.Password = self.GetValue('Password')
    def GetValue(self,key):
        stringNodes = self.Node.findall('.//String')
        for sn in stringNodes:
            keynode = sn.find('Key')
            valnode = sn.find('Value')
            if keynode.text == key:
                return valnode.text
class KP1Entry(KPEntry):
    def __init__(self,node):
        KPEntry.__init__(self,node)
        self.Title = self.GetValue('title')
        self.UserName = self.GetValue('username')
        self.Password = self.GetValue('password')
    def GetValue(self,key):
        foundNode = self.Node.find(key)
        if foundNode != None:
            return foundNode.text

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parses XML output from KeePass, and encrypts passwords based on key.')
    parser.add_argument('-key','--key', help='Key', required = True)
    parser.add_argument('-file','--file', help='XML file output from KeyPass2', required = True)
    parser.add_argument('-debug','--debug', help='Show all', required = False)
    parser.add_argument('-action','--action',help='action to perform', required = True)

    args = vars(parser.parse_args())

    action = args['action'].upper()
    if action == 'PARSE2.0' or action == 'PARSE1.0':
        debug = False
        if args['debug'] != None and args['debug'].upper() == 'TRUE':
            debug = True
        key = args['key']
        filename = args['file']
        if not os.path.exists(filename):
            print ('File does not exists')
            exit(1)

        entries = []
        tree = ET.parse(filename)
        entryNodes = tree.findall('.//Entry')
        for entryNode in entryNodes:
            entry = KP2Entry(entryNode)
            inserted = False
            for e in entries:
                if e.Title == e.Title and e.UserName == entry.UserName:# and e.Password == entry.Password:
                    inserted = True
                    break
            if not inserted:
                entries.append(entry)
        entryNodes = tree.findall('.//entry')
        for entryNode in entryNodes:
            entry = KP1Entry(entryNode)
            inserted = False
            for e in entries:
                if e.Title == e.Title and e.UserName == entry.UserName:# and e.Password == entry.Password:
                    inserted = True
                    break
            if not inserted:
                entries.append(entry)

        matrix = BuildMatrix()
        for entry in entries:
            entry.Ciphered = EncryptPassword(matrix, entry.Password, key)
            print(entry)

    elif action == 'PRINTMATRIX':
        matrix = BuildMatrix()
        PrintMatrix(matrix)
    else:
        print('Please provide valid action.')
        exit(1)

