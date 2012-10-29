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
import Whois
import IPy
import os
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj


def main():
    """delete a user"""

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        #if len(qs.split("&")) == 1:
        try:
            id = int(qs.split("&")[0])
        except:
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

    if group == 0:
        HTML.restriction_message()
        return

    if id == 0:
        HTML.error_message("user not found: %s") % str(id)
        return

    if group != 1 and rights[1] != 1 and rights[2] != 1:
        HTML.restriction_message()
        return 

    ### logged in user does have enough rights to 
    
    if id == 1:
        HTML.error_message("Built-In Administrator can't be deleted!")
        return
    else:
        sql_user = """SELECT username, companies_id FROM persons WHERE persons_id=%u """ % int(id)
        user = conn.get_data(sql_user)

    if user == ():
        msg = "user not found: %s" % str(id)
        HTML.error_message(msg)
        return
    else:
        sql_delete_group = """DELETE FROM ipall_user_group WHERE username='%s' """ % user[0][0]
        delete_group = conn.update_data(sql_delete_group)

    sql_delete_user = """DELETE from persons WHERE persons_id=%u """ % int(id)
    delete_user = conn.update_data(sql_delete_user)

    ### LOGGING
    log_string = sql_delete_user + "<br>" + sql_delete_group
    sql_log_user = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'persons', "%s", %u)""" % (current_user, log_string, int(user[0][1]))
    log = conn.update_data(sql_log_user)
    #log = 0

    print """<br>"""
    print """<div id="main">"""
    print """<div id="table_main">"""

    if delete_user == 1 and delete_group == 1 and log > 0:
        HTML.notify_message("user deleted...")
        linktext = """<a href="%s/mgmt_user.cgi" class=LinkPurpleBold> << back</a>""" % cgi_dir
        HTML.notify_message(linktext)
    else: 
        HTML.error_message("An error has occured!")
        HTML.popup_footer()
        return
        
    print """</div>""" # table_main
    print """</div>""" # main

    HTML.close_body()

main()
