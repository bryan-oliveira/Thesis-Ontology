#!flask/bin/python
# This Python file uses the following encoding: utf-8
from flask import render_template, send_from_directory, request
from app import app
import sys

sys.path.append("../")
import ts_browse
import ts_search
import ts_recommendation

ts_browse.init("thesis_out.xml")

# TODO
# add link in the resitem


# the main file
@app.route('/')
@app.route('/index')
def index():
    title = 'The perfect thesis finder'
#    resitems = [
#        {
#            'title'    : 'A beautiful title for a thesis',
#            'date'     : 'Jan/2069',
#            'grade'    : '20',
#            'author'   : 'Manel, Zé',
#            'advisers' : 'Alice, Maria',
#            'keywords' : 'The, Best',
#            'abstract' : 'Perfect description',
#        }, ]
    date    = request.args.get('date')
    advisor = request.args.get('advisor')
    author = request.args.get('author')
    search = request.args.get('searchbox')

    print 'Received req: ', search

    # Browse Date Section
    date,search = ts_browse.browseDates(date,search)

    #tmp ,search = ts_browse.browseNamesAuthor(author,search)
    #tmp2,search = ts_browse.browseNamesAdvisor(advisor,search)

    print "[views] search:",search

    if search != None:
        return render_template('index.html',
                           title    = title,
                           resitems = ts_search.parseSearchString(search),
                           recitems = ts_recommendation.parseSearchString(search),
                           advisors = ts_browse.queryAdvisors(),
                           dates    = date,
                           authors  = ts_browse.queryAuthors(),
                           debug    = 'yes' if request.args.get('debug') != None else None,
                           )
    else:
        return render_template('index.html',
                           title    = title,
                           resitems = ts_browse.getAllThesis(date=date, advisor=advisor, author=author),
                           recitems = ts_recommendation.parseSearchString(None),
                           advisors = ts_browse.queryAdvisors(),
                           dates    = date,
                           authors  = ts_browse.queryAuthors(),
                           debug    = 'yes' if request.args.get('debug') != None else None,
                           )

# the css files
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(app.static_folder + '/css', path)

# the js files
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(app.static_folder + '/js', path)

# the rest of static files, if needed
#@app.route('/<path:path>')
#def send_file(path):
#    return send_from_directory(app.static_folder, path)
