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
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj


def main():
    """delete a group"""

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
    if group == 0:
        HTML.restriction_message()
        return

    if id == 0:
        HTML.error_message("user not found")
        return

    if group != 1 and rights[2] != 1:
        HTML.restriction_message()
        return 

    ### logged in user does have enough rights to 

    sql_user = """SELECT username FROM ipall_user_group WHERE group_id=%u """ % int(id)
    user = conn.get_data(sql_user)

    if user != ():
        HTML.error_message("You can't delete this group!<br>There are users assigned to the group.")
        return
    else:
        sql_company = """SELECT companies_id FROM ipall_group WHERE id=%u""" % ( int(id) )
        company = conn.get_data(sql_company)[0][0]

        sql_delete_group = """DELETE FROM ipall_group WHERE id=%u """ % int(id)
        delete_group = conn.update_data(sql_delete_group)

        ### LOGGING
        log_string = sql_delete_group
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_group', "%s", %u)""" % ( current_user, log_string, int(company) )
        log = conn.update_data(sql_log)
        #log = 1

    if delete_group == 1 and log == 1:
        HTML.notify_message("group deleted successfully...")
    else: 
        HMTL.error_message("an error has occured...")
    msg = """<a href="%s/mgmt_group.cgi" class="linkPurpleBold"> << back</a>""" % cgi_dir
    HTML.notify_message(msg)        

    HTML.close_body()

main()
