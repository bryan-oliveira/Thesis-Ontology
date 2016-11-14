#!flask/bin/python
# This Python file uses the following encoding: utf-8
import sys
import copy
import os
from random import randint

deiareas = ['NA',
            'Comunicações, Serviços e Infraestrturas',
            'Engenharia de Software',
            'Sistemas Inteligentes',
            'Sistemas de Informação']

debug = 'off'

def cleanName(name, spl = ", "):
    if name == None or name == '':
        return None
    tmp = name.split(spl)
    if len(tmp) > 1:
        return tmp[1] + " " + tmp[0]
    return name

def cleanDate(date):

    if  date == None or \
        date == 'None' or \
        date == '':
        return 0
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dec']

    yyyy = 0
    mm   = 1
    dd   = 1

    if any(m in date.lower() for m in months):
        dateparts = date.lower().split("-")
        yyyy = int(dateparts[2])
        mm   = months.index(dateparts[1]) + 1
        dd   = int(dateparts[0])
    else:
        yyyy = int(date)

    return "%04d-%02d-%02d" % (yyyy, mm, dd)


def parse(path):

    with open(path, 'r') as f:
        thesis = []

        fileInfo = os.stat(path)
        fileSize = fileInfo.st_size

        thesisRead = 0

        while f.tell() < fileSize:

            t = {}

            t['grade']    = ''
            t['deiarea']  = ''

            t['title'] = f.readline().rstrip('\n')
            t['author'] = f.readline().rstrip('\n')
            t['advisor'] = f.readline().rstrip('\n')
            t['keywords'] = f.readline().rstrip('\n')
            t['date'] = f.readline().rstrip('\n')
            t['abstract'] = f.readline().rstrip('\n')
            t['type'] = f.readline().rstrip('\n')
            t['uri'] = f.readline().rstrip('\n')

            # the random grade
            #if randint(0,10) > 7:
            t['grade'] = str(randint(10,19))


            # listify the author names {name : website, ...}
            authors = []
            author = t['author']
            index = author.find('[')
            name = author[:index]
            website = author[index+1:-1]
            authors += [name]
            authors += [website]
            t['author'] = authors

            if not os.path.isfile('peopleNameFile.txt'):
                open('peopleNameFile.txt', 'a').close()

            if name not in open('peopleNameFile.txt').read():
                with open("peopleNameFile.txt", "a") as myfile:
                    myfile.write(name.lower()+'\n')


            # listify the adviser names {name : website, ...}
            ads = t['advisor'].split(";")
            advisors = []
            for ad in ads:
                index = ad.find('[')
                name = ad[:index]
                website = ad[index+1:-1]
                #print 'name:',name#, '\n', website, '\n'
                if name != '':
                    advisors += [name]
            #print 'PARSER :',advisors

            t['advisor'] = advisors

            # listify the keywords
            t['keywords'] = t['keywords'].split(";")

            if not os.path.isfile('keywordsFile.txt'):
                open('keywordsFile.txt', 'a').close()

            for x in t['keywords']:
                if x.lower() not in open('keywordsFile.txt').read():
                    with open('keywordsFile.txt', 'a') as myfile:
                        print x.lower()
                        myfile.write(x.lower()+'\n')

            if len(t['keywords']) == 1 and t['keywords'][0] == ' ':
                t['keywords'] = []

            # dummy deiarea
            t['deiarea'] = deiareas[randint(0, len(deiareas) - 1)]

            # date
            t['date'] = cleanDate(t['date'])

            if debug == 'on':
                #print thesis
                print "Title: ", t['title']
                print "Author: ",t['author']

                for key in advisers:
                    print "Adviser: ",key, " - ", advisers[key]

                print "Keywords: ", t['keywords']
                print "Date: ", t['date']
                #print t['abstract']
                print "Thesis Type: ", t['thesisType']
                print "URI: ", t['uri']
                print

            thesisRead += 1

            # add to the list
            thesis += [t]

    # print and return them
    if __name__ == "__main__":
        #for t in thesis:
            #print(t)
        print 'Read: ', thesisRead
        print 'Send: ',len(thesis)

    return thesis

if __name__ == "__main__":
    parse(sys.argv[1])


