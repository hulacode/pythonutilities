# The MIT License (MIT)
# Copyright (C) 2015 Hulacode.com
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
import json
import urllib2
import argparse
import sqlite3
from BeautifulSoup import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

conn = sqlite3.connect('obits.db')
c = conn.cursor()

class Obituary(object):
    def __init__(self):
        self.ObitID = None
        self.DisplayName = None
        self.PersonName = None
        self.Url = None
        self.ImageUrl = None
        self.ObituaryText = None

    def GetObit(self):
        print 'getting: ' + self.Url
        request = urllib2.Request(self.Url)
        response = urllib2.urlopen(request)
        html = response.read()
        soup = BeautifulSoup(html)
        obittext = soup.body.find('span', attrs={'class': 'ObitTextHtml'})
        self.ObituaryText = obittext

    def __str__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        return self.DisplayName + ', ' + str(self.ObitID)

def ConnectToDB():
    sql = 'create table if not exists obits (id integer)'
    c.execute(sql)
    conn.commit()

def JustRetrieved(obitID):
    sql = 'insert into obits (id) values (%d)' % (obitID)
    c.execute(sql)
    conn.commit()

def HasAlreadyRetrieved(obitID):
    returnValue = False
    sql = 'select id from obits where id = ' + str(obitID)
    c.execute(sql)
    data=c.fetchall()
    if len(data) == 0:
        print 'Obit not retrieved yet for: ' + str(obitID)
    else:
        print 'Obit ALREADY retrieved for: ' + str(obitID)
        returnValue = True

    return returnValue

def GenerateHtml(obits):
    returnValue = '<html>'
    for obit in obits:
        if obit.ObituaryText != None:
            returnValue += '<br/>'
            returnValue += str(obit.ObituaryText)
    returnValue += '</html>'
    return returnValue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grabs all the obits")
    parser.add_argument('-url','--url',help='URL', required=True)
    parser.add_argument('-recipient','--recipient',help='Email Recipient', required=True)
    parser.add_argument('-smtpuser','--smtpuser',help='SMTP User', required=False)
    parser.add_argument('-smtppassword','--smtppassword',help='SMTP Password', required=False)
    parser.add_argument('-smtpserver','--smtpserver',help='SMTP Server', required=True)
    ConnectToDB()

    args = vars(parser.parse_args())
    url = args['url']
    print 'Using: ' + url
    request = urllib2.Request(url)


    response = urllib2.urlopen(request)
    html = response.read()
    lines = html.split('\n')
    jsonparse = None
    for line in lines:
        #print line
        if line.find('ObituaryNavigatorList:') > -1:
            jsonparse = line[24:-3]
            jsonparse = jsonparse.replace('\\"','"')
    obits = []
    if jsonparse != None:
        jsonresults = json.loads(jsonparse)
        for obitinfo in jsonresults:
            obit = Obituary()
            for attribute, value in obitinfo.iteritems():
                #print attribute, value
                if attribute == 'Url':
                    obit.Url = value
                elif attribute == 'ImageUrl':
                    obit.ImageUrl = value
                elif attribute == 'DisplayName':
                    obit.DisplayName = value
                elif attribute == 'PersonName':
                    obit.PersonName = value
                elif attribute == 'ObituaryId':
                    obit.ObitID = value
            obits.append(obit)
    Body = 'There are no obits.'
    anyObits = False
    for obit in obits:
        if not HasAlreadyRetrieved(obit.ObitID):
            obit.GetObit()
            anyObits = True
            #exit(0)
            #break
            JustRetrieved(obit.ObitID)
    if anyObits:
        Body = GenerateHtml(obits)
    Body = Body.encode('ascii','ignore')
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "New Obituaries"
    msg['From'] = 'noreply@gmail.com'
    recipients = []
    recipients.append(args['recipient'])
    msg['To'] = ", ".join(recipients)


    # Create the body of the message (a plain-text and an HTML version).
    text = Body
    html = Body
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    smtpserver = smtplib.SMTP(args['smtpserver'])
    # Send the message via local SMTP server.
    if args['smtpuser'] != "":
        print('Starting TTLS with user %s' % args['smtpuser'])
        smtpserver.starttls()
        smtpserver.login(args['smtpuser'], args['smtppassword'])
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    smtpserver.sendmail('noreply@gmail.com', recipients, msg.as_string())
    smtpserver.quit()
