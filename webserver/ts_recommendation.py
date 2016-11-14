#!flask/bin/python
# This Python file uses the following encoding: utf-8
from rdflib import URIRef, BNode, Literal, Namespace, RDF, XSD
import rdflib
import sys
import copy
import os

import ts_search as search
reload(sys)
sys.setdefaultencoding('utf8')

ns = Namespace("http://www.w3.org/2002/07/wsont#")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")


def parseSearchString(keyword):
    print "[ts_recommendation] parseSearchString:", keyword

    whatToQuery = {}

    kw = []

    if keyword != None and keyword != '':
        kw = keyword.split(',')

    for key in kw:

        key2 = key.strip()

        result = search.keywordIsDate(key2)

        if result != -1:
            # Is a date! Make data query
            whatToQuery['date'] = result
            continue

        result = search.keywordIsPerson(key2)

        if result != -1:
            # Is a person! Make person query
            whatToQuery['person'] = result
            continue

        result = search.keywordIsKeyword(key2)

        if result != -1:
            # Is a keyword! Make keyword query
            whatToQuery['keyword'] = [result]
            continue


    if len(whatToQuery) == 0:
        whatToQuery['grade'] = 17

    return queryBuilder(whatToQuery)

def queryBuilder(whatToQuery):

    g = rdflib.Graph()
    g.parse("thesis_out.xml")

    keyword = False
    person = False
    date = False
    grade = False

    if 'grade' in whatToQuery:
        grade = True

    if 'date' in whatToQuery:
        date = True

    if 'person' in whatToQuery:
        person = True
        print "DEBUG", whatToQuery
        q = "SELECT ?b WHERE { ?a rdf:type ns:Person . ?a ns:hasName ?b . FILTER contains( LCASE(?b) , \"" + whatToQuery['person'] + "\" ) }"
        qres = g.query ( q, initNs = { "ns":ns} )
        print q
        peopleNames = []
        for k in qres:
            peopleNames += [str(k[0])]


        #print peopleNames,len(peopleNames)

    query = """ PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                SELECT ?title ?date ?authorName ?grade ?abstract ?deiarea ?advisers ?uri """

    #if 'keyword' in whatToQuery:
    #    keyword = True
    #    query += " ?keywords "

    # Get all thesis
    # Get all thesis
    query = query + """
            WHERE {
                ?a rdf:type ns:DoctorateThesis .
            """

    # Show broader date choice
    if date == True:
        if len(whatToQuery['date']) > 1:
            dateStart = int(    whatToQuery['date'][0]  ) - 2
            dateEnd =   int(    whatToQuery['date'][1]  ) + 2
            query = query + "?a ns:hasDateSubmitted ?date . \n"
            query = query + ''' FILTER ( ?date > "''' + str(dateStart) + '''") . '''
            query = query + ''' FILTER ( ?date < "''' + str(dateEnd) + '''") . '''
        else:
            date = int(str(whatToQuery['date'][0])) - 2
            query = query + "?a ns:hasDateSubmitted ?date . \n"
            query = query + ''' FILTER ( ?date > "''' + str(date) + '''") . '''

    else:
        query = query + ''' OPTIONAL { ?a ns:hasDateSubmitted ?date . } . '''


    # Filter by person
    if person == True:
        print "People Names:",peopleNames
        if len(peopleNames) > 1:
            query = query + """?a ns:hasAuthor ?author . \n"""
            for name in peopleNames:
                query = query + """{ ?author ns:hasName """+ "\"" + str(name) + "\" . } UNION"

            query = query[0:-5]
            query += " . \n"
        else:
            query = query + """?a ns:hasAuthor ?author . \n"""
            query = query + """?author ns:hasName """+ "\"" + peopleNames[0] + "\" . \n"
    else:
        query = query + '''OPTIONAL { ?a ns:hasAuthor ?author . ?author ns:hasName ?authorName} . \n'''

    # Filter by keywords || See if keyword is in abstract
    if keyword == True:
        query = query + '''?a ns:hasAbstract ?abstract . '''
        query = query + '''FILTER contains(?abstract,\"''' + str(whatToQuery['keyword'][0]) + '''\") . \n'''


    if grade == True:
        query += "?a ns:hasGrade ?grade . FILTER ( ?grade > \"17\") ."

    # OPTIONALS
    query += '''            ?a ns:hasTitle         ?title    .
                            ?a ns:hasGrade         ?grade    .
                            ?a ns:hasURI           ?uri      .
                OPTIONAL {  ?a ns:hasAbstract      ?abstract . } .
                            ?a ns:hasDeiArea       ?deiarea  .
                OPTIONAL {  ?a ns:hasAdvisor       ?advisers . } . '''

    # Close WHERE Query
    query = query + ''' } LIMIT 5 \n'''
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
        t['keywords'] = search.getAllKeywordsForThesis( t['title'] )
        t['advisors'] = search.getAllAdvisorForThesis( t['title'] )


        if 'person' in whatToQuery:
            t['author'] = peopleNames[i]

        i += 1

        # Recopy all keywords into one string
        q = ""
        for key in t['keywords']:
            q += str(key) + '\n'
        t['keywords'] = q

        #print "title:",t['title']," date:",t['date']," author:",t['author']," advisers:",t['advisers']

        if len(t['date'].split("-")) > 2 and int(t['date'].split("-")[1]) <= 1 and int(t['date'].split("-")[2]) <= 1:
            t['date'] = t['date'].split("-")[0]

        #print t
        if len(t['title']) > 1:
            thesis += [t]

    #print thesis

    print("[ts_recommendation] [queryBuilder] Found %d theses\n" % len(thesis))
    return thesis