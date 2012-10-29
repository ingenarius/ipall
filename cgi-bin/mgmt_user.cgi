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
import os
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie
from time import asctime


def print_users(ipall_dir, cgi_dir, company):
    """print out all user who belong to given company"""

    sql_users = """SELECT persons_id, surname, forename, username FROM persons WHERE companies_id=%u ORDER BY surname""" % ( int(company))
    users = conn.get_data(sql_users)
    for u in users:
        print """<div id="pos_left_small" class="lineIndent">%s %s [%s]</div>""" % (u[1], u[2], u[3])
        print """<div id="pos_right" style="text-align: right">"""
        print """<img src="%s/images/editOff.png" id="edit" onMouseOver="mouseoverImage(this, '%s');"  
            onMouseOut="mouseoverImage(this, '%s');" onClick="redirect_to_url('%s/user_edit.cgi?%s');" class=handlers />""" \
                % ( ipall_dir, ipall_dir, ipall_dir, cgi_dir, str(u[0]) )
        print """<img src="%s/images/deleteOff.png" id="delete" onMouseOver="mouseoverImage(this, '%s');"  
            onMouseOut="mouseoverImage(this, '%s');" onClick="confirm_and_redirect('Do you really want to delete this user?', '%s/user_delete.cgi?%s');" 
            class=handlers />""" % ( ipall_dir, ipall_dir, ipall_dir, cgi_dir, str(u[0]) )
        print """</div>"""
        print """<div id="pos_clear"></div>"""



def main():
    """entry point for executing IPALL"""

    ### definitions of variables
    global conn

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
    print """<span>IP@LL user management<span>"""
    if rights[1] == 1 or rights[2] == 1:
        print """<span id="pos_right" style="text-align:right">
            <a href="%s/new_user.cgi" class=linkPurpleBold>new user</a></span>""" % cgi_dir
    else:
        print """<span id="pos_right"></span>"""
    print """</div>"""

    if group == 1:
        ### print Super Administrators (no company assigned)
        print """<div class=textPurpleBold>Super Administrators [no company]</div>"""
        print_users(ipall_dir, cgi_dir, 0)

        sql_companies = """SELECT id, name FROM companies ORDER BY name"""
        companies = conn.get_data(sql_companies)
        for c in companies:
            print """<div class=textPurpleBold>%s</div>""" % c[1]

            print_users(ipall_dir, cgi_dir, c[0])

    elif rights[1] == 1:
        print_users(ipall_dir, cgi_dir, company_id)

    else:
        sql_users = """SELECT persons_id, surname, forename FROM persons WHERE username='%s' """ % current_user
        user = conn.get_data(sql_users)[0]
        print """<div id="pos_left">%s %s [%s]</div>""" % (user[1], user[2], current_user)
        print """<div id="pos_right" style="text-align: right">"""
        print """<img src="%s/images/editOff.png" id="edit" onMouseOver="mouseoverImage(this, '%s');"  
            onMouseOut="mouseoverImage(this, '%s');" onClick="redirect_to_url('%s/user_edit.cgi?%s');" class=handlers /></div>""" \
                % ( ipall_dir, ipall_dir, ipall_dir, cgi_dir, str(user[0]) )
        print """</div>"""
        print """<div id="pos_clear"></div>"""
        

    print """</div>""" #table_main
    print """</div>""" #main

    HTML.close_body()

main()
