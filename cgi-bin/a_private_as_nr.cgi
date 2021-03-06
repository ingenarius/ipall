#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 racyAPz
http://www.racyapz.at
*****************************
"""

import DBmy
import IpallUser
from Html_new import HtmlContent
from Sessionclass import Session
import IPy
import os
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie


def get_as_numbers():
    """return tuple with private AS numbers"""

    sql_as_nrs = """SELECT DISTINCT(pi.as_nr), ip.net_name FROM ipall_peering_info pi, ipall_ip ip 
                        WHERE pi.id=ip.peering_info_id AND pi.as_nr >= 64512 
                        AND ip.companies_id=%u ORDER BY pi.as_nr """ % ( companies_id ) 
    as_nrs = conn.get_data(sql_as_nrs)

    return as_nrs


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

    if group == 0 or not os.environ.has_key('HTTP_REFERER'):
        HTML.restriction_message()
        return

    HTML.ajax_header()

    print """<div class=TextPurple>"""
    print """<table width="100%" border=0 cellspacing=4 cellpadding=0>"""
    print """<tr>"""
    print """<td colspan=2 align=center class=TextPurpleBold>Private AS numbers in use</td>"""
    print """</tr>"""
    print """<tr><td colspan=2>"""

    as_nrs = get_as_numbers()
    
    print """<table border=0>"""
    for a in as_nrs:
        print """<tr class=TextPurple>"""
        print """<td><b>%s</b></td>""" % str(a[0])
        print """<td>... %s</td>""" % str(a[1])
        print """</tr>"""
    print """</table>"""

    print """</td></tr>"""
    print """</table>"""
    print """</div>"""
        
main()
