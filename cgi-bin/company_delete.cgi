#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
"""

from Html_new import HtmlContent
from Ipall import IpallFunctions
import DBmy
import IpallUser
from Sessionclass import Session
import Whois
import IPy
import os
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj


def main():
    """delete a company"""

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 1:
            id = str(qs.split("&")[0])
        else:
            id = 0
    else:
        id = 0

    ### create database connection object
    cfg = ConfigObj("ipall.cfg")
    db_host = cfg['Database']['db_host']
    db_user = cfg['Database']['db_user']
    db_pw = cfg['Database']['db_pw']
    db = cfg['Database']['db']
    conn = DBmy.db(db_host, db_user, db_pw, db)

    HTML = HtmlContent()

    ### User
    s = Session(conn)
    current_user = s.check_user()
    HTML.simple_header()
    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    else:
        HTML.popup_body()

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    if group == 0 and group != 1:
        HTML.restriction_message()
        return

    if id == 0:
        HTML.error_message("user not found")
        return

    ### logged in user does have enough rights to 
    f = IpallFunctions(conn, current_user, group, company_id)
    nets = f.get_vrf_count(int(id))
    if nets[0][0] != 0:
        HTML.error_message("There are VRFs/Views assigned. This company cannot be deleted!")
        return
    if nets[0][0] == 0:
        users = f.get_user_count(int(id))
        if users[0][0] != 0:
            HTML.error_message("There are users assigned. This company cannot be deleted!")
            return

    delete_company = f.delete_company(int(id))

    print """<br>"""
    print """<div id="main">"""
    print """<div id="table_main">"""

    if delete_company == 1:
        HTML.notify_message("company deleted successfully...")
    else: 
        HMTL.error_message("an error has occured...")
    msg = """<a href="%s/mgmt_company.cgi" class="linkPurpleBold"> << back</a>""" % cgi_dir
    HTML.notify_message(msg)
    print """</div>""" #table_main
    print """</div>""" #main

    HTML.close_body()

main()
