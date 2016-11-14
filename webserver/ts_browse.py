#!flask/bin/python
# This Python file uses the following encoding: utf-8
from rdflib import URIRef, BNode, Literal, Namespace, RDF, XSD
import rdflib
import sys
import copy
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

ns = Namespace("http://www.w3.org/2002/07/wsont#")


def init(path):
    g.parse(path)
    print("triplestore loaded")



def get_hasName_byResource(resource):
    qres = g.query(
        """ SELECT ?name
            WHERE { <""" + resource + """> ns:hasName ?name . }
           """, initNs = { "ns": ns })
    thename = ""
    for row in qres:
        thename = "%s" % row
    return thename


def allTheThesis(date="all", advisor="all", author="all", datestart=None, dateend=None, keywords=None):

    adviserfilter = ""
    if advisor != None and advisor != "all" and advisor != "":
        adviserfilter = "?a ns:hasAdvisor ?advisers .\n\
                        ?advisers ns:hasName ?advisorName \
                         FILTER contains(?advisorName , \"%s\")" \
                         % advisor

    datefilter = ""
    if date != None and date != "all" and date != "":
        datefilter = "?a ns:hasDateSubmitted ?date . \
                      FILTER regex(str(?date), \"%s\")" \
                      % date

    authorfilter = ""
    if author != None and author != "all" and author != "":
        authorfilter = "?a ns:hasAuthor ?author . \
                        ?author ns:hasName ?authorName \
                      FILTER contains(?authorName, \"%s\")" \
                      % date


    if adviserfilter != "":
        query = """ SELECT DISTINCT ?title ?date ?author ?grade ?abstract ?deiarea ?uri ?advisorName """
    else:
        query = """ SELECT DISTINCT ?title ?date ?author ?grade ?abstract ?deiarea ?uri ?advisers """

    query += """
            WHERE {
                ?a rdf:type ns:DoctorateThesis .
                OPTIONAL { ?a ns:hasTitle         ?title . } .
                OPTIONAL { ?a ns:hasDateSubmitted ?date . } .
                OPTIONAL { ?a ns:hasAuthor        ?author . } .
                OPTIONAL { ?a ns:hasGrade         ?grade . } .
                OPTIONAL { ?a ns:hasURI           ?uri . } .
                OPTIONAL { ?a ns:hasAbstract      ?abstract . } .
                OPTIONAL { ?a ns:hasDeiArea       ?deiarea . } . """

    if adviserfilter != "":
        query += adviserfilter

    query += datefilter + """
                } GROUP BY ?title ORDER BY ?date """

    qres = g.query(query, initNs = { "ns": ns })

    thesis = []

    for row in qres:
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

        # Recopy all keywords into one string
        q = ""
        for key in t['keywords']:
            #print str(key)
            q += str(key) + '\n'
        t['keywords'] = q

        if adviserfilter != "":
            print query
            print "DEBUIGGGG###",t

        if len(t['date'].split("-")) > 2 and int(t['date'].split("-")[1]) <= 1 and int(t['date'].split("-")[2]) <= 1:
            t['date'] = t['date'].split("-")[0]

        thesis += [t]

    print("[ts_browse] [allTheThesis] Found %d theses\n" % len(thesis))

    return thesis

def getAllKeywordsForThesis(title):
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

def getAllAdvisorForThesis(title):
    qres = g.query( ''' SELECT ?name
                        WHERE {
                            ?advisor rdf:type ns:Person .
                            ?a ns:hasTitle \"''' + title + '''\" .
                            ?a ns:hasAdvisor ?advisor .
                            ?advisor ns:hasName ?name .
                            }
                    ''', initNs = { "ns": ns })

    k = ""
    for key in qres:
        if key != '':
            k += str(key[0]) + ';\n'

    return k

def requeryObjectProperties(thesis):
    for t in thesis:
        t['author']   = get_hasName_byResource(t['author'])
        t['deiarea']  = get_hasName_byResource(t['deiarea']);
        #t['keywords'] = get_hasName_byResource(t['keywords']);
        #t['advisers'] = get_hasName_byResource(t['advisers']);

def browseDates(dateSpan, search):

    if dateSpan == None or dateSpan == 'all':
        dates = ['1970-1979','1980-1989','1990-1999','2000-2009','2010-2019']
        return (dates,search)

    if dateSpan == '1970-1979':
        dates = ['1970','1971','1972','1973','1974','1975','1976','1977','1978','1979']
        return (dates, '1970-1979')

    if dateSpan == '1980-1989':
        dates = ['1980','1981','1982','1983','1984','1985','1986','1987','1988','1989']
        return (dates,'1980-1989')

    if dateSpan == '1990-1999':
        dates = ['1990','1991','1992','1993','1994','1995','1996','1997','1998','1999']
        return (dates,'1990-1999')

    if dateSpan == '2000-2009':
        dates = ['2000','2001','2002','2003','2004','2005','2006','2007','2008','2009']
        return (dates,'2000-2009')

    if dateSpan == '2010-2019':
        dates = ['2010','2011','2012','2013','2014','2015','2016','2017','2018','2019']
        return (dates,'2010-2019')

    if int(dateSpan) > 1900 and int(dateSpan) < 2100:
        return ([dateSpan],dateSpan)
    print "###########################"

def browseNamesAuthor(nameSpace, search):

    if nameSpace == '' or nameSpace == None:
        nameSpace = ['A-E','F-J','K-O','P-T','U-Z']
        return (nameSpace,search)

    if nameSpace == 'A-E':
        nameSpace = ['A','B','C','D','E']
        return (nameSpace,'A-E')

    if nameSpace == 'F-J':
        nameSpace = ['F','G','H','I','J']
        return (nameSpace,'F-J')

    if nameSpace == 'K-O':
        nameSpace = ['K','L','M','N','O']
        return (nameSpace,'K-O')

    if nameSpace == 'P-T':
        nameSpace = ['P','Q','R','S','T']
        return (nameSpace,'P-T')

    if nameSpace == 'U-Z':
        nameSpace = ['U','V','W','X','Y','Z']
        return (nameSpace,'U-Z')

def browseNamesAdvisor(nameSpace, search):

    if nameSpace == '' or nameSpace == None:
        nameSpace = ['A-E','F-J','K-O','P-T','U-Z']
        return (nameSpace,search)

    if nameSpace == 'A-E':
        nameSpace = ['A','B','C','D','E']
        return (nameSpace,'A-E')

    if nameSpace == 'F-J':
        nameSpace = ['F','G','H','I','J']
        return (nameSpace,'F-J')

    if nameSpace == 'K-O':
        nameSpace = ['K','L','M','N','O']
        return (nameSpace,'K-O')

    if nameSpace == 'P-T':
        nameSpace = ['P','Q','R','S','T']
        return (nameSpace,'P-T')

    if nameSpace == 'U-Z':
        nameSpace = ['U','V','W','X','Y','Z']
        return (nameSpace,'U-Z')


# Deprecated: Used to show random Thesis dates
def queryDates():
    qres = g.query(
        """ SELECT DISTINCT ?date
            WHERE {
                ?a rdf:type ns:DoctorateThesis .
                ?a ns:hasDateSubmitted ?date .
            } LIMIT 5
            """, initNs = { "ns": ns })
    dates = []
    for row in qres:
        d = "%s" % row[:4]
        print "[ts_browse] DEBUG #",d
        dates += [d]
    return dates

def queryAdvisors():
    qres = g.query(
        """ SELECT DISTINCT ?name
            WHERE {
                ?a rdf:type ns:Person .
                ?a ns:hasName ?name .

                ?b rdf:type ns:DoctorateThesis .
                ?b ns:hasAdvisor       ?a .
            } LIMIT 5
            """, initNs = { "ns": ns })
    advisors = []
    for row in qres:
        advisors += [(str(row[0]))]

    return advisors

def queryAuthors():
    qres = g.query(
        """ SELECT DISTINCT ?name
            WHERE {
                ?a rdf:type ns:Person .
                ?a ns:hasName ?name .

                ?b rdf:type ns:DoctorateThesis .
                ?b ns:hasAuthor       ?a .
            } LIMIT 5
            """, initNs = { "ns": ns })
    authors = []
    for row in qres:
        authors += [(str(row[0]))]

    return authors


def getAllThesis(date="all", advisor="all", author="all"):
    if date == None:
        date = "all"
    if advisor == None:
        advisor = "all"
    if author == None:
        author = "all"

    allthesis = allTheThesis(date=date, advisor=advisor, author=author)
    requeryObjectProperties(allthesis)
    return allthesis

def getAllYears():
    dates = queryDates()
    dates = [d.split("-")[0] for d in dates]
    return dates

def getAllAdvisers():
    return queryAdvisors()

# globals

g = rdflib.Graph()

if __name__ == "__main__":
    init(sys.argv[1])
    getAllThesis(date="all", advisor="all")
else:
    # init everything
    pass



