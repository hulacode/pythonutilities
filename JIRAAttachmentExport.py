# MIT License
#
# Copyright (c) 2016 HulaCode.com, Allen Plummer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import base64
import getpass
import argparse
import os
import urllib
import urllib2
import json
parser = argparse.ArgumentParser(description='Exports Attachments from JIRA cloud')
parser.add_argument('-jql',
                    '--jql',
                    help='A valid JQL query: example would be "jql=project=KEY"',
                    required=True)
parser.add_argument('-baseurl',
                    '--baseurl',
                    help='The base URL: example would be "https://test.atlassian.net"',
                    required=True)
parser.add_argument('-throttleissues',
                    '--throttleissues',
                    help='Number of issues to return per set. Default is 10.',
                    required=False)
args = vars(parser.parse_args())
baseurl = args['baseurl'] + '/rest/api/2/'
numberOfIssues = 10
if args['throttleissues'] is not None:
    try:
        numberOfIssues = int(args['throttleissues'])
    except:
        pass


def login():
    user = raw_input("Username: ")
    if not user:
        user = getpass.getuser()
    p1 = getpass.getpass()
    return user, p1


def downloadfile(issuekey, fileurl, base64userpass):
    file_name = fileurl.split('/')[-2] + "_" + fileurl.split('/')[-1]
    directory = os.path.join('attachments', issuekey)
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_name = os.path.join(directory, file_name)
    filerequest = urllib2.Request(fileurl)
    filerequest.add_header("Authorization", "Basic %s" % base64userpass)
    u = urllib2.urlopen(filerequest)

    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status
    f.close()

username, password = login()

base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
searchurl = baseurl + 'search/?jql=' + args['jql'] + "&maxResults=" + str(numberOfIssues)

receivedCount = 0
while True:
    try:
        print 'Attempting to retrieve the next ' + str(numberOfIssues)
        pagingURL = urllib.quote(searchurl + '&startAt=' + str(receivedCount), safe="%/:=&?~#+!$,;'@()*[]")
        print pagingURL
        searchrequest = urllib2.Request(pagingURL)
        searchrequest.add_header("Authorization", "Basic %s" % base64string)
        searchresponse = urllib2.urlopen(searchrequest)
        rs = json.load(searchresponse)
        issues = rs['issues']
        total = rs['total']
        for issue in issues:
            receivedCount += 1
            print 'Getting detailed data for ' + issue["key"]
            issueurl = baseurl + 'issue/' + issue["key"]
            issuerequest = urllib2.Request(issueurl)
            issuerequest.add_header("Authorization", "Basic %s" % base64string)
            try:
                issueresponse = urllib2.urlopen(issuerequest)
                rsissue = json.load(issueresponse)
                attachments = rsissue['fields']['attachment']
                if len(attachments) > 0:
                    print 'There are ' + str(len(attachments)) + ' attachment(s) for issue ' + issue["key"] + ', attempting to retrieve URLs now.'
                    for attachment in attachments:
                        attachmenturl = attachment['content']
                        print attachmenturl
                        downloadfile(issue["key"], attachmenturl, base64string)
            except:
                print 'There was an issue getting issue ' + issue["key"]
        if receivedCount >= total:
            break
    except:
        print 'There was an error searching issues.'
