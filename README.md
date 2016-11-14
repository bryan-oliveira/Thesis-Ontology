# Thesis Recommender

This is a semantic web project that recommends theses. The theses were scraped from a public thesis repository (https://estudogeral.sib.uc.pt). An ontology is used to further enrich the search capabilities of the web application. The ontology was modeled using Protege (http://protege.stanford.edu/).

## Thesis Scraper

The repository contains the web scraper used to scrape the theses. The code is in Java and uses the jsoup HTML parser library.

## Web Server

Flask, a Python framework, was used for the web server. Run "./python run.py" to start server.