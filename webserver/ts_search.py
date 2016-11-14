#!flask/bin/python
# This Python file uses the following encoding: utf-8
from rdflib import URIRef, BNode, Literal, Namespace, RDF, XSD
import rdflib
import sys
import copy
import os

reload(sys)
sys.setdefaultencoding('utf8')

ns = Namespace("http://www.w3.org/2002/07/wsont#")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")

initState = False
g = None

def init():
    global g
    global initState
    g = rdflib.Graph()
    g.parse("thesis_out.xml")
    initState = True

def parseSearchString(keyword):
    print "[ts_search] parseSearchString:", keyword
    if keyword == None or keyword == '':
        return []

    kw = keyword.split(',')

    whatToQuery = {}

    for key in kw:

        key2 = key.strip()

        result = keywordIsDate(key2)

        if result != -1:
            # Is a date! Make data query
            whatToQuery['date'] = result
            continue

        result = keywordIsPerson(key2)

        if result != -1:
            # Is a person! Make person query
            whatToQuery['person'] = result
            continue

        result = keywordIsKeyword(key2)

        if result != -1:
            # Is a keyword! Make keyword query
            whatToQuery['keyword'] = [result]
            continue

        #result = keywordIsLetterRange(key2)

        #if result != -1:
            # Is a range of Letters from browse selection
        #    whatToQuery['letterRange'] = key2


        #whatToQuery['other'] = key2
    #print "[ts_search] parseSearchString FINAL whatToQuery:",whatToQuery

    if len(whatToQuery) == 0:
        return []

    return queryBuilder(whatToQuery)


def keywordIsLetterRange(range):
    if range == 'A-E':
        return ['A','B','C','D','E']

    if range == 'F-J':
        return ['F','G','H','I','J']

    if range == 'K-O':
        return ['K','L','M','N','O']

    if range == 'P-T':
        return ['P','Q','R','S','T']

    if range == 'U-Z':
        return ['U','V','W','X','Y','Z']

    if len(range) == 1 and range.isalpha() == True:
        print 'Found letter',range
        return range

    return -1


def queryBuilder(whatToQuery):

    print "[ts_search] QueryBuilder - whatToQuery:", whatToQuery

    if initState == False:
        init()

    keyword = False
    person = False
    date = False
    #other = False #not date or person or keyword

    if 'date' in whatToQuery:
        date = True

    if 'person' in whatToQuery:
        person = True
        q = "SELECT ?b WHERE { ?a rdf:type ns:Person . ?a ns:hasName ?b . FILTER contains( LCASE(?b) , \"" + whatToQuery['person'] + "\" ) }"
        qres = g.query ( q, initNs = { "ns":ns} )
        print q
        peopleNames = []
        for k in qres:
            peopleNames += [str(k[0])]

        #print peopleNames,len(peopleNames)

    if 'other' in whatToQuery:
        other = True

    query = """ PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                SELECT ?title ?date ?authorName ?grade ?abstract ?deiarea ?advisorName ?uri """

    if 'keyword' in whatToQuery:
        keyword = True
        query += " ?keywords "

    # Get all thesis
    query = query + """
            WHERE {
                ?a rdf:type ns:DoctorateThesis .
            """

    # Filter by date
    if date == True:
        if len(whatToQuery['date']) > 1:
            query = query + "?a ns:hasDateSubmitted ?date . \n"
            query = query + ''' FILTER ( ?date >= "''' + str(whatToQuery['date'][0]) + '''") . '''
            query = query + ''' FILTER ( ?date <= "''' + str(whatToQuery['date'][1]) + '''") . '''
        else:
            query = query + "?a ns:hasDateSubmitted ?date . \n"
            query = query + ''' FILTER ( ?date >= "''' + str(whatToQuery['date'][0]) + '''") . '''
    else:
        query = query + ''' ?a ns:hasDateSubmitted ?date . '''


    # Filter by person
    if person == True:
        #print "People Names:",peopleNames
        if len(peopleNames) > 1:
            query = query + """?a ns:hasAuthor ?author . \n"""
            query = query + """?a ns:hasAdvisor ?advisers . \n"""

            for name in peopleNames:
                query = query + """{ ?author ns:hasName """+ "\"" + str(name) + "\" . } UNION"
                query = query + """{ ?advisers ns:hasName """+ "\"" + str(name) + "\" . } UNION"

            # Strip "UNION" from last author query
            query = query[0:-5]
            query += " . \n"
        else:
            query = query + """?a ns:hasAuthor ?author . \n"""
            query = query + """?author ns:hasName """+ "\"" + peopleNames[0] + "\" . \n"

            query = query + """?a ns:hasAdvisor ?advisers . \n"""
            query = query + """?advisers ns:hasName """+ "\"" + peopleNames[0] + "\" . \n"
    else:
        query = query + '''?a ns:hasAuthor ?author . ?author ns:hasName ?authorName . \n'''
        query = query + '''?a ns:hasAdvisor ?advisers . ?advisers ns:hasName ?advisorName . \n'''

    # Filter by keywords
    if keyword == True:
        query = query + '''?a ns:hasKeyword ?keyword . '''
        query = query + '''?keyword ns:hasName ?keyName . \n'''
        query = query + '''FILTER contains(?keyName,\"''' + str(whatToQuery['keyword'][0]) + '''\") . \n'''

    # Not tested yet - New function of Letter drill down
    #if len( whatToQuery['letterRange'] ) > 0:
    #    for letter in whatToQuery['letterRange']:
    #        query += """?a ns:hasAuthor ?author .   \n """
    #        query += """?author ns:hasName ?b .     \n """
    #        query += '''FILTER regex(?b, \"''' + letter + '''\") . '''

    print "DEBUG ###", whatToQuery


    # OPTIONALS
    query += '''?a ns:hasTitle         ?title    . '''
    #if other == True:
    #    query = query + '''FILTER contains(?title,\"''' + whatToQuery['other'] + '''\") . \n'''

    query +='''
                ?a ns:hasGrade         ?grade    .
                ?a ns:hasURI           ?uri      .
                OPTIONAL { ?a ns:hasAbstract      ?abstract . } .
                ?a ns:hasDeiArea       ?deiarea  .
                OPTIONAL { ?a ns:hasAdvisor       ?advisers . } . '''

    # Close WHERE Query
    query = query + ''' } ORDER BY ?date \n'''
    print query
    fullQuery = g.query( query, initNs = { "ns": ns}) #, "xsd":xsd } )

    thesis = []
    i = 0

    for row in fullQuery:
        t = {}
        t['title']    = str(row[0])
        t['date']     = str(row[1])
        t['author']   = str(row[2])
        t['grade']    = str(row[3])
        t['abstract'] = str(row[4])
        t['deiarea']  = str(row[5])
        t['uri']      = str(row[6])
        t['keywords'] = getAllKeywordsForThesis( t['title'] )
        t['advisors'] = getAllAdvisorForThesis( t['title'] )


        if 'person' in whatToQuery:
            t['author'] = peopleNames[i]

        i += 1

        # Recopy all keywords into one string
        q = ""
        for key in t['keywords']:
            q += str(key) + '\n'
        t['keywords'] = q

        if len(t['date'].split("-")) > 2 and int(t['date'].split("-")[1]) <= 1 and int(t['date'].split("-")[2]) <= 1:
            t['date'] = t['date'].split("-")[0]

        # Solves no match empty return response case.
        if len(t['title']) > 1:
            thesis += [t]

    #print thesis

    print("[ts_search] [queryBuilder] Found %d theses\n" % len(thesis))
    return thesis

def getAllAdvisorForThesis(title):
    global initState
    if initState == False:
        init()

    qres = g.query( ''' SELECT ?name
                        WHERE {
                            ?a ns:hasTitle \"''' + title + '''\" .
                            ?a ns:hasAdvisor ?advisor .
                            ?advisor ns:hasName ?name .
                            } ''', initNs = { "ns": ns })

    k = ""
    for key in qres:
        if key != '':
            k += str(key[0]) + ';\n'


    if len(k) < 1:
        return None

    return k

def getAllKeywordsForThesis(title):

    global initState
    if initState == False:
        init()

    qres = g.query( ''' SELECT ?name
                        WHERE {
                            ?keywords rdf:type ns:Keyword .
                            ?a ns:hasTitle \"''' + title + '''\" .
                            ?a ns:hasKeyword ?keywords .
                            ?keywords ns:hasName ?name .
                            }
                    ''', initNs = { "ns": ns })

    k = []
    for key in qres:
        k += [str(key[0])]

    return k

def keywordIsKeyword(keyword):
    if keyword.lower() in open('keywordsFile.txt').read():
        print '[keywordIsKeyword] Found a keyword:', keyword
        return keyword.lower()

    return -1

def keywordIsPerson(keyword):

    if keyword.lower() in open('peopleNameFile.txt').read():
        print '[keywordIsPerson] Found a person:', keyword
        return keyword.lower()

    #print 'Not a person'
    return -1


def keywordIsDate(keyword):
    print keyword

    if len( keyword.split() ) > len ( keyword.split('-') ):
        check = keyword.split()
    else:
        check = keyword.split('-')

    if len( keyword.split(' ') ) > len( check ):
        check = keyword.split(' ')

    print check

    print '[keywordIsDate] ### Got:',check

    if len(check) == 1:                                             # Is Year > 1900
        if check[0].isdigit() and int(check[0]) > 1900:
            print '[keywordIsDate] Is year:',check[0]
            return [check[0]]#+'-1-1'#T00:00:00Z'
        else:
            #print 'Is not year',check[0]
            return -1

    elif len(check) > 1:
        countDates = []
        for key in check:
            if key.isdigit():       # Is numeric
                if key > 1900:      # Is a valid year
                    countDates += [key]

        if len(countDates) == 2:
            if (int(countDates[0]) < int(countDates[1])):
                print '[keywordIsDate] Found two coherent dates:',countDates[0]+'-1-1','and',countDates[1]+'-1-1'
                return countDates
            else:
                #print 'Incorrect date sequence:',countDates
                return -1
        else:
            #print 'Not a valid expression:',countDates
            return -1

def search(path, keyword):

    global initState
    if initState == False:
        init()

    qres = g.query (
        """ SELECT DISTINCT ?title ?date ?author ?grade ?abstract ?deiarea ?keywords ?advisers ?uri
            WHERE {
                ?a rdf:type ns:DoctorateThesis .
                ?a ns:hasTitle         ?title . } .
                OPTIONAL { ?a ns:hasDateSubmitted ?date . } .
                OPTIONAL { ?a ns:hasAuthor        ?author . } .
                OPTIONAL { ?a ns:hasGrade         ?grade . } .
                OPTIONAL { ?a ns:hasURI           ?uri . } .
                OPTIONAL { ?a ns:hasAbstract      ?abstract . } .
                OPTIONAL { ?a ns:hasDeiArea       ?deiarea . } .
                OPTIONAL { ?a ns:hasKeyword       ?keywords . } .
            }
            ORDER BY ?date
        """, initNs = { "ns": ns }, initBindings={'keywords': keyword})

    thesis = []
    for row in qres:
        t = {}
        t['title']    = str(row[0])
        t['date']     = str(row[1])
        t['author']   = str(row[2])
        t['grade']    = str(row[3])
        t['abstract'] = str(row[4])
        t['deiarea']  = str(row[5])
        t['keywords'] = str(row[6])
        t['advisers'] = str(row[7])
        t['uri']      = str(row[8])

        if len(t['date'].split("-")) > 2 and int(t['date'].split("-")[1]) <= 1 and int(t['date'].split("-")[2]) <= 1:
            t['date'] = t['date'].split("-")[0]
        print t['title'],t['author'],t['advisers']
        thesis += [t]

    return thesis

