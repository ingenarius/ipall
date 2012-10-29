#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 racyAPz
http://www.racyapz.at
*****************************
"""

from Html_new import HtmlContent
import DBmy
import IpallUser
from Sessionclass import Session
import IPy
import os
import cgi
from Configobj import ConfigObj
from Cookie import SimpleCookie


def get_as_number():
    """return tuple with AS number of the selected company"""

    sql_as_nr = """SELECT as_nr FROM companies WHERE id=%u """ % ( companies_id ) 
    as_nr = conn.get_data(sql_as_nr)

    return as_nr


def main():
    """description"""

    global companies_id, conn

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 1:
            companies_id = int(qs.split("&")[0])
        else:
            companies_id = 0
    else:
        companies_id = 0
    ### create database connection object
    cfg = ConfigObj("ipall.cfg")
    db_host = cfg['Database']['db_host']
    db_user = cfg['Database']['db_user']
    db_pw = cfg['Database']['db_pw']
    db = cfg['Database']['db']
    conn = DBmy.db(db_host, db_user, db_pw, db)


    ### User
    s = Session(conn)
    current_user = s.check_user()
    HTML = HtmlContent()

    #company = s.check_cookie()
    
    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']

    HTML.ajax_header()

    if group == 0 or not os.environ.has_key('HTTP_REFERER'):
        HTML.restriction_message()
        return

    if group != 1 and company_id != companies_id:
        return

    print """<div id="main">"""

    as_nr = get_as_number()
    if as_nr != ():
        print "result:" + str(as_nr[0][0]) + ":;"
    else:
        print "result:0:;"
    
    print """</div>"""
        
main()
