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
import os
from Configobj import ConfigObj
from Cookie import SimpleCookie


def main():
    """entry point for executing IPALL - view network details"""

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        try:
            id = int(qs.split("&")[0])
        except:
            id = 0
    else:
        current_user = ""
        id = 0

    ### create database connection object
    cfg = ConfigObj("ipall.cfg")
    ipall_dir = cfg['Server']['ipall_dir']
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
    if group == 0:
        HTML.restriction_message(1)
        HTML.popup_footer()
        return

    f = IpallFunctions(conn, current_user, group, company_id)
    details = ()

    if group != 1 and rights[2] != 1: # user is not member of group "Super Administrators" or is company admin
        details = f.get_net_info(3, id)
        net_perm = conn.get_net_permissions(str(details[0][3]), group)
        if net_perm == () or net_perm == "":
            net_perm = 0
        else:
            net_perm = net_perm[3]
    else: # user is member of group "admins"
        net_perm = 1
    
    if net_perm != 1:
        HTML.restriction_message(1)
        HTML.popup_footer()
        return
    else:
        if details == ():
            details = f.get_net_info(3, id)
        path = details[0][3]
    
        print """<div id="main">"""
        print """<div id="table_main">"""
        print """<div id="functionHead">Print screen &nbsp;&nbsp;&nbsp;
            <a href="javascript:print();"> <img src="%s/images/printOn.png" border=0> </a></div>""" % ( ipall_dir ) 

        f.print_tree_nodes(details, rights, path)

        print """</div>""" #table_main
        print """</div>""" #main
        
    
    HTML.popup_footer()


main()
