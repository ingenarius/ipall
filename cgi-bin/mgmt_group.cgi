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
from Cookie import SimpleCookie
from time import asctime


def main():
    """entry point for executing IPALL"""

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
    #company = s.check_cookie()
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
    ipall_dir = cfg['Server']['ipall_dir']
    
    if group == 0 and rights[1] != 1:
        HTML.restriction_message()
        return

    print """<div id="main">"""
    print """<div id="table_main">"""
    ### HEADING
    print """<div id="functionHead">"""
    print """<span>IP@LL group management</span>"""
    if rights[1] == 1 and group != 1:
        print """<span id="pos_right_inside" style="text-align: right">
            <a href="%s/new_group.cgi" class=linkPurpleBold>new group</a></span>""" % cgi_dir
    print """</div>"""
    if group == 1:
        sql_companies = """SELECT id, name FROM companies ORDER BY name"""
        companies = conn.get_data(sql_companies)
        for c in companies:
            print """<div id="pos_left" class=textPurpleBold>%s</div>""" % c[1]
            print """<div id="pos_right" style="text-align: right">
                [ <a href="%s/new_group.cgi?%s" class=linkPurpleBold>new group</a> ]</div>""" % (cgi_dir, c[0])
            print """<div id="pos_clear"></div>"""
            sql_groups = """SELECT id, groupname FROM ipall_group WHERE companies_id=%u ORDER BY groupname""" % int(c[0])
            groups = conn.get_data(sql_groups)
            for g in groups:
                print """<div id="pos_left_small" class=lineIndent style="margin-left: 20px">%s</div>""" % str(g[1])
                print """<div id="pos_right" style="text-align: right">"""
                print """<img src="%s/images/editOff.png" id="edit" onMouseOver="mouseoverImage(this, '%s');"  
                    onMouseOut="mouseoverImage(this, '%s');" onClick="redirect_to_url('%s/group_edit.cgi?%s&%s');" class=handlers />""" \
                        % ( ipall_dir, ipall_dir, ipall_dir, cgi_dir, str(g[0]), str(c[0]) )
                print """<img src="%s/images/deleteOff.png" id="delete" onMouseOver="mouseoverImage(this, '%s');"  
                    onMouseOut="mouseoverImage(this, '%s');" onClick="confirm_and_redirect('Do you really want to delete this group?', '%s/group_delete.cgi?%s');" class=handlers />""" \
                        % ( ipall_dir, ipall_dir, ipall_dir, cgi_dir, str(g[0]) )
                print """</div>"""
                print """<div id="pos_clear"></div>"""
    elif rights[1] == 1:
        sql_groups = """SELECT id, groupname FROM ipall_group WHERE companies_id=%u ORDER BY groupname""" % company_id
        groups = conn.get_data(sql_groups)
        for g in groups:
            print """<div id="pos_left_small" class=lineIndent>%s</div>""" % str(g[1])
            print """<div id="pos_right" style="text-align: right">"""
            print """<img src="%s/images/editOff.png" id="edit" onMouseOver="mouseoverImage(this, '%s');"  
                onMouseOut="mouseoverImage(this, '%s');" onClick="redirect_to_url('%s/group_edit.cgi?%s&%s');" class=handlers />""" \
                    % ( ipall_dir, ipall_dir, ipall_dir, cgi_dir, str(g[0]), company_id )
            print """<img src="%s/images/deleteOff.png" id="delete" onMouseOver="mouseoverImage(this, '%s');"  
                onMouseOut="mouseoverImage(this, '%s');" onClick="confirm_and_redirect('Do you really want to delete this group?', '%s/group_delete.cgi?%s');" class=handlers />""" \
                    % ( ipall_dir, ipall_dir, ipall_dir, cgi_dir, str(g[0]) )
            print """</div>"""
            print """<div id="pos_clear"></div>"""
    else:
        HTML.notify_message("You are not allowed to change group settings!")
    print """</div>""" #table_main
    print """</div>""" #main

    HTML.close_body()

main()
