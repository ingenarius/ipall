#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
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

def get_net_names(service_id, vrf, parent_id):
    """get every single net name from the selected service type"""
    
    sql_names = """select DISTINCT(net_name), label FROM ipall_ip 
        WHERE service_id = %u AND allocated != 1 AND vrf='%s'
        AND parent_id=%u ORDER BY address DESC LIMIT 20""" % ( int(service_id), vrf, int(parent_id) )
    names = conn.get_data(sql_names)

    return names


def check_peering(service_id):
    """check if new network_type can have BGP peerings"""
    
    sql_peering = """SELECT is_peering FROM ipall_network_types WHERE id=%u""" % ( service_id )
    peering = conn.get_data(sql_peering)

    if peering != () and peering != 0:
        is_peering = int(peering[0][0])
        print "value:%s" % ( str(is_peering) )
    else:
        print "value:0"


def main():
    """description"""

    global conn

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 1:
            id = int(qs.split("&")[0])  ## service_id
            vrf = ""
            parent_id = 0
        if len(qs.split("&")) == 3:
            id = int(qs.split("&")[0])  ## service_id
            vrf = str(qs.split("&")[1])
            parent_id = int(qs.split("&")[2])
    else:
        id = parent_id = 0
        vrf = ""

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
    #company = s.check_cookie()

    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']

    if group == 0:
        HTML.restriction_message(1)
        return
    else:
        HTML.ajax_header()
    
    if int(id) != 0 and vrf != "":
        names = get_net_names(id, vrf, parent_id)
    elif int(id) != 0 and vrf == "":
        check_peering(id)
        names = ()
    else:
        check_peering(0)
        names = ()
    if names != ():
        print """<div class=TextPurple>"""
        print """<table border=0 cellspacing=4 cellpadding=0 width=100%>"""
        print """<tr class=lightPurple3>"""
        print """<td colspan=2 align=left class=TextPurpleBold>Network names in use (latest 20)</td>"""
        print """</tr>"""
        print """<tr><td colspan=2>"""
        print """<table border=0>"""

        for n in names:
            print """<tr class=TextPurple>"""
            print """<td>%s</td>""" % str(n[0])
            print """<td>(%s)</td>""" % str(n[1])
            print """</tr>"""

        print """</table>"""
        print """</td></tr>"""
        print """</table>"""
        print """</div>"""

main()
