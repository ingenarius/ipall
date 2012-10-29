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
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie


def get_net_types():
    """return tuple with network types"""

    sql_net_types = """SELECT typename, description FROM ipall_network_types ORDER BY typename"""
    net_types = conn.get_data(sql_net_types)

    return net_types


def main():
    """description"""

    global conn

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
    #company = s.check_cookie()
    
    HTML = HtmlContent()
    print ""
    #HTML.simple_header()
    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()

    cgi_dir = cfg['Server']['cgi_dir']
    
    if group == 0: ### user is not logged in
        HTML.restriction_message(1)
        return


    net_types = get_net_types()
#    print """<div>"""
    for n in net_types:
        print """<div id="descriptions">"""
        print """<span class="left">%s</span>""" % str(n[0])
        if n[1]:
            print """<span class="right">%s</span>""" % str(n[1])
        print """</div>"""
#    print """</div>"""

main()
