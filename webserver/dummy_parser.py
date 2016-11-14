#!flask/bin/python
# coding: latin-1
import sys
import copy
import os
from random import randint

deiareas = ['NA',
            'Comunicações, Serviços e Infraestrturas',
            'Engenharia de Software',
            'Sistemas Inteligentes',
            'Sistemas de Informação']

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
    months = ['jan', 'fev', 'mar', 'abrl', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

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
    #String thesisStr = year + "|||" + title + "|||" + advisor + "|||" + author + "|||" + keywords + "|||" + abstract_ + "|||" + type + "|||" + uri + "\n";

    with open(path, 'r') as f:
        thesis = []
        idmap = {}
        idmap['date']     = 0
        idmap['title']    = 1
        idmap['adviser']  = 2
        idmap['author']   = 3
        idmap['keywords'] = 4
        idmap['abstract'] = 5
        idmap['type']     = 6
        idmap['uri']      = 7
        idmap['grade']    = -1
        idmap['deiarea']  = -1

        for line in f:
            t = {}
            t['type']     = ''
            t['title']    = ''
            t['date']     = ''
            t['author']   = ''
            t['adviser']  = ''
            t['grade']    = ''
            t['keywords'] = ''
            t['abstract'] = ''
            t['deiarea']  = ''
            t['uri']      = ''

            if len(line) <= 1:
                continue

            # clean and separate
            parts = [p.strip() for p in line.split('\n')]

            #print parts

            # copy each part to the dic
            for key in idmap:
                if idmap[key] >= 0:
                    t[key] = parts[idmap[key]]

            # # # # CORRECTIONS # # # #
            # the random grade
            if randint(0,10) > 7:
                t['grade'] = str(randint(10,19))

            # the author name
            t['author'] = cleanName(t['author'])

            # listify the adviser names
            ads = t['adviser'].split(";")
            advisers = []
            for ad in ads:
                a = cleanName(ad)
                if a != None:
                    advisers += [a]
            t['adviser'] = advisers

            # listify the keywords
            t['keywords'] = t['keywords'].split(";")
            if len(t['keywords']) == 1 and t['keywords'][0] == '':
                t['keywords'] = []

            # dummy deiarea
            t['deiarea'] = deiareas[randint(0, len(deiareas) - 1)]

            # date
            t['date'] = cleanDate(t['date'])

            # add to the list
            thesis += [t]

        # print and return them
        if __name__ == "__main__":
            for t in thesis:
                print(t)
        return thesis


if __name__ == "__main__":
    parse(sys.argv[1])


