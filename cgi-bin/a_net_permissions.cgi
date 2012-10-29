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
from Ipall import IpallFunctions
from Sessionclass import Session
from Configobj import ConfigObj


def main():
    """print permission info of selected netword and group"""
    
    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 2:
            path = str(qs.split("&")[0])
            sel_group = int(qs.split("&")[1])
        else:
            id = 0
            path = ""
    else:
        id = 0
        path = ""

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
    
    f = IpallFunctions(conn, current_user, group, company_id)

    rights = f.get_net_rights(sel_group, path)
    if rights == ():
        rights = (0,0,0,0,0,0)

    if sel_group != 0:
        print """<input type=hidden name=sel_group value=%u>""" % sel_group
        print """<div id="pos_left_small">"""
        print """<div class="lineHeight">Delete network</div>"""
        print """<div class="lineHeight">Edit network</div>"""
        print """<div class="lineHeight">Subnet network</div>"""
        print """<div class="lineHeight">View network</div>"""
        print """</div>""" #left side

        print """<div id="pos_right_wide">"""
        if rights[0] == 1:
            print """<div class="lineHeight"><input type=checkbox name=delete_net checked></div>"""
        else:
            print """<div class="lineHeight"><input type=checkbox name=delete_net></div>"""
        if rights[1] == 1:
            print """<div class="lineHeight"><input type=checkbox name=edit_net checked></div>"""
        else:
            print """<div class="lineHeight"><input type=checkbox name=edit_net></div>"""

        if rights[2] == 1:
            print """<div class="lineHeight"><input type=checkbox name=subnet_net checked></div>"""
        else:
            print """<div class="lineHeight"><input type=checkbox name=subnet_net></div>"""

        if rights[3] == 1:
            print """<div class="lineHeight"><input type=checkbox name=view_net checked></div>"""
        else:
            print """<div class="lineHeight"><input type=checkbox name=view_net></div>"""
        print """</div>""" #right side
        print """<div id="pos_clear"></div>"""


main()
