#!flask/bin/python
# This Python file uses the following encoding: utf-8

#encoding = utf8
import sys

reload(sys)
sys.setdefaultencoding('utf8')

from app import app
app.run(debug=True)

