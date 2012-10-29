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
    """delete a nettype"""

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        #if len(qs.split("&")) == 1:
        try:
            id = str(qs.split("&")[0])
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
        HTML.error_message("nettype not found")
        return

    if id <= 11:
        HTML.error_message("nettype could not be deleted")
        return

    if group != 1 and rights[2] == 0:
        HTML.restriction_message()
        return 

    ### logged in user does have enough rights to 
    sql_check = """SELECT count(id) FROM ipall_ip WHERE service_id=%u """ % int(id)
    check = conn.get_data(sql_check)
    if check[0][0] != 0:
        message = """nettype is in use by %s networks""" % str(check[0][0])
        HTML.error_message(message)
        return
    else:
        sql_delete_type = """DELETE FROM ipall_network_types WHERE id=%u """ % int(id)
        delete_type = conn.update_data(sql_delete_type)

        ### LOGGING
        log_string = sql_delete_type
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_network_types', "%s", 0)""" % (current_user, log_string)
        log = conn.update_data(sql_log)

        print """<br>"""
        print """<div id="main">"""
        print """<div id="table_main">"""

        if delete_type == 1:
            uri = "%s/mgmt_nettypes.cgi" % cgi_dir
            HTML.redirect(uri)
            HTML.close_body()
        else: 
            HTML.error_message("an error has occured...")
            HTML.popup_footer()
            
        print """</div>""" # table_main
        print """</div>""" # main


main()
