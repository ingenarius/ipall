#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
"""

import os
import IP
import IPy
import DBmy
import IpallUser
from Html_new import HtmlContent
from Sessionclass import Session
from Configobj import ConfigObj


def main():
    """return companies"""
    
    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 1:
            id = int(qs.split("&")[0])
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

    ### user
    s = Session(conn)
    current_user = s.check_user()
    #company = s.check_cookie()
    HTML = HtmlContent()

    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']
    if group == 0:
        return

    HTML.ajax_header()

    if group == 1 or rights[2] == 1:
        net_perm = 1
    else:
        net_perm = 0
    if net_perm != 1:
        return
    
    sql_groups = """SELECT id, groupname FROM ipall_group WHERE companies_id=%u """ % int(id)
    groups = conn.get_data(sql_groups)
    return_value = ""

    if groups != ():
        for g in groups:
            if return_value == "":
                return_value = str(g[0]) + "," + str(g[1]) + ";"
            else:
                return_value = return_value + str(g[0]) + "," + str(g[1]) + ";"
        print return_value[0:-1]
    else:
        print "no groups found..."


main()
