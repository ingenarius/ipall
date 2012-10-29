#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
"""

from Html_new import HtmlContent
import DBmy
import IpallUser
from Sessionclass import Session
import os
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj


def main():
    """display documentation and help files"""

    ### definitions of variables
    formdata = cgi.FieldStorage()
    uri = path = vrf = ""
    companies_id = parent_id = 0

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 1:
            doc = str(qs.split("&")[0])
        else:
            HTML.error_message("no document selected")
            return

    ### create database connection object
    cfg = ConfigObj("ipall.cfg")
    db_host = cfg['Database']['db_host']
    db_user = cfg['Database']['db_user']
    db_pw = cfg['Database']['db_pw']
    db = cfg['Database']['db']
    conn = DBmy.db(db_host, db_user, db_pw, db)

    HTML = HtmlContent()

    s = Session(conn)
    current_user = s.check_user()
    HTML.simple_header()
    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    else:
        HTML.body()

    ## User
    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']
    doc_dir = cfg['Server']['doc_dir']

    if group == 0:
        HTML.restriction_message()
        return

    print """<br>"""
    print """<div id="divHead800">""" #1
    print """<span class=left>Documentation</span>"""
    print """<span class=right>you are logged in as: <i>%s</i></span>""" % ( current_user )
    print """<span class=left></span>"""
    print """<span class=right></span>"""
    print """</div>""" #1
    print """<div id="main">"""
    print """<div id="table_main">"""

    filename = doc_dir + "/" + doc

    try:
        file = open(filename, 'r')
    except:
        HTML.error_message("Document not available!")
        return
            
    data = file.readlines()
    for d in data:
        d = d.replace("cgi_dir", cgi_dir)
        d = d.replace("ipall_dir", ipall_dir)
        d = d.replace("doc_dir", doc_dir)
        print d

    print """</div>""" #table_main
    print """</div>""" #main

    HTML.main_footer()

main()
