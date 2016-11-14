#!flask/bin/python
import sys
import os

# Function evaluates if string contains two valid years in correct order

def parseSearchString(keyword):
    #Antonio Figueiredo, 1997, nota 17,
    kw = keyword.split(',')

    print 'Search String:',kw

    for key in kw:

        result = keywordIsDate(key)

        if result != -1:
            # data query
            continue

        result = keywordIsPerson2(key)

        if result != -1:
            # Person query
            continue


        print 'Unknown keyword'

def keywordIsPerson2(keyword):

    if keyword in open('peopleNameFile.txt').read():
        print 'Found a person:', keyword
        return keyword

    #print 'Not a person'
    return -1

def keywordIsDate(keyword):

    check = keyword.split()
    #print 'Debug date:',check

    if len(check) == 1:                                             # Is Year > 1900
        if check[0].isdigit() and int(check[0]) > 1900:
            print 'Is year:',check[0]
            return check[0]+'-1-1'
        else:
            #print 'Is not year',check[0]
            return -1

    if len(check) > 1:
        countDates = []
        for key in check:
            if key.isdigit():       # Is numeric
                if key > 1900:      # Is a valid year
                    countDates += [key]

        if len(countDates) > 1:
            if (int(countDates[0]) < int(countDates[1])):
                print 'Found two coherent dates:',countDates[0]+'-1-1','and',countDates[1]+'-1-1'
                return countDates
            else:
                #print 'Incorrect date sequence:',countDates
                return -1
        else:
            #print 'Not a valid expression:',countDates
            return -1

if __name__ == "__main__":
    parseSearchString('de 2000 a 2005, Alberto')