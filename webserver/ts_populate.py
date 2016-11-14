#!flask/bin/python

from rdflib import URIRef, BNode, Literal, Namespace, RDF, XSD
import rdflib
import my_parser as dp
import pprint

ns = Namespace("http://www.w3.org/2002/07/wsont#")


def addThesis(g, t):

    # add the thesis itself
    tid = ''.join(e for e in t['title'] if e.isalnum())
    bob = URIRef(ns + tid)
    if   t['type'] == "Master Thesis":
        g.add((bob, RDF.type, ns.MasterThesis))
    elif t['type'] == "Doctoral Thesis":
        g.add((bob, RDF.type, ns.DoctorateThesis))
    else:
        # abort if unknown type
        return

    # add the author as individual

    #if len(t['author']) > 0:
    #   print t['author'][0]

    if len(t['author']) > 1:
        #print 'Author:',t['author'][0]
        author = URIRef(ns + ''.join(e for e in t['author'][0] if e.isalnum()))
        g.add((author, RDF.type,    ns.Person))
        g.set((author, ns.hasName,  Literal(t['author'][0])))

    # add advisers as individuals
    advisors = []
    if len(t['advisor']) > 1:
        for a in t['advisor']:
            print 'populate:',a
            ad = URIRef(ns + ''.join(e for e in a if e.isalnum() ))
            g.add((ad, RDF.type,    ns.Person))
            g.set((ad, ns.hasName,  Literal(a)))
            advisors += [ad]
        print 'end',advisors

    # add keywords as individuals
    keywords = []
    if len(t['keywords']) > 1:
        for k in t['keywords']:
            #print 'Keyword:',k
            kw = URIRef(ns + ''.join(e for e in k if e.isalnum()))
            g.add((kw, RDF.type,    ns.Keyword))
            g.set((kw, ns.hasName,  Literal(k)))
            keywords += [kw]

    # add deiArea as individual
    if len(t['deiarea']) > 1:
        #print 'Dei Area:',t['deiarea']
        deiarea = URIRef(ns + ''.join(e for e in t['deiarea'] if e.isalnum()))
        g.add((deiarea, RDF.type,    ns.DEIArea))
        g.set((deiarea, ns.hasName,  Literal(t['deiarea'])))


    # Data Properties TODO missing some: hasDateSubmittedm hasURI
    if len(t['abstract']) > 1:
        g.set((bob, ns.hasAbstract,      Literal(t['abstract'])))
    if len(t['grade']) > 1:
        #print 'Grade:',t['grade']
        g.set((bob, ns.hasGrade,         Literal(t['grade'])))
    if len(t['title']) > 1:
        #print 'Title:', t['title']
        g.set((bob, ns.hasTitle,         Literal(t['title'])))
    if len(t['uri']) > 1:
        g.set((bob, ns.hasURI,           Literal(t['uri'])))
    if len(t['date']) > 1:
        g.set((bob, ns.hasDateSubmitted, Literal(t['date'] )))#,datatype=XSD.date)))


    # Object Properties
    if len(t['author']) > 1:
        g.set((bob, ns.hasAuthor,   author))

    if len(t['deiarea']) > 1:
        g.set((bob, ns.hasDeiArea,  deiarea))

    for k in keywords:
        g.add((bob, ns.hasKeyword, k))

    for a in advisors:
        print "aaaa",a
        g.add((bob, ns.hasAdvisor, a))



thesis = dp.parse("thesis.txt")

print 'Populating...\nThesis\' found: ',len(thesis)

g = rdflib.Graph()
g.parse("thesis.rdf")

for t in thesis:
    addThesis(g, t)


#g.serialize(destination='thesis_out.turtle', format='turtle')
g.serialize(destination='thesis_out.xml', format='xml')
