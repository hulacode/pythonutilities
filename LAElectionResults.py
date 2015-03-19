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
import feedparser
import argparse
from BeautifulSoup import BeautifulSoup

class CandidateIssue:
    def __init__(self,name):
        self.Name = name
        self.TotalNumber = ''
        self.Percentage = ''
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        template = "{0:40}{1:10}{2:15}"
        printstring = template.format(self.Name, self.Percentage, self.TotalNumber)
        #return self.Name + "  " + self.Percentage + ", Number of Votes: " + self.TotalNumber
        return printstring
class Election:
    def __init__(self,title):
        self.Title = title
        self.Progress = ''
        self.CandidateIssues = []
    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        printstring = '======' + self.Title
        printstring += '\nProgress: ' + self.Progress
        for c in self.CandidateIssues:
            printstring += '\n' + str(c)
        return printstring

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Gets Election Results')
    parser.add_argument('-url','--url',help='Base URL',required=True)
    parser.add_argument('-election', '--election', help='Election to show', required=False)
    args = vars(parser.parse_args())
    url = args['url']
    efilter = args['election']

    d = feedparser.parse(url)
    elections = []
    for item in d.entries:
        #print item
        #print item['title_detail']
        title = item['title_detail']['value']
        election = Election(title)
        #print item['summary']
        soup = BeautifulSoup(item['summary'])

        tables = soup.findChildren('table')
        # This will get the first (and only) table. Your page may have more.
        my_table = tables[0]

        # You can find children with multiple tags by passing a list of strings
        rows = my_table.findChildren(['th', 'tr'])
        i = 0
        for row in rows:
            i += 1
            cells = row.findChildren('td')
            if i == 1:
                election.Progress = cells[0].text.strip()
            else:
                candidate = CandidateIssue(cells[0].text.strip())
                candidate.Percentage = cells[1].text.strip()
                candidate.TotalNumber = cells[2].text.strip()
                election.CandidateIssues.append(candidate)


        elections.append(election)

    for e in elections:
        if efilter != None:
            if e.Title.upper().find(efilter.upper()) >= 0:
                print(e)
        else:
            print(e)
