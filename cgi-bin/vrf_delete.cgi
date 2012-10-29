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
import Whois
import IPy
import os
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj


def main():
    """delete a View/VRF if it is empty"""

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        #if len(qs.split("&")) == 1:
        try:
            rd = str(qs.split("&")[0])
        except:
            rd = "NULL"
    else:
        rd = "NULL"

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
    rights = user.get_rights()
    group, company_id  = user.get_group_id()
    cgi_dir = cfg['Server']['cgi_dir']
    if group == 0 or rights[2] == 0:
        HTML.restriction_message()
        return

    if rd == "NULL":
        HTML.error_message("No Prefix found to delete")
#        print """<br>"""
#        print """<blockquote>"""
#        print """<p class=TextPurpleBold>No Prefix found to delete </p>"""
#        print """<a href="javascript:history.back();" class=LinkPurpleBold> << back </a>"""
#        print """</blockquote>"""
        return

    if group != 1 and rights[2] != 1: # user is super administrator or company admin
        vrf_perm = conn.get_vrf_permissions(rd, group)
        if vrf_perm == ():
            vrf_perm = 0
        else:
            vrf_perm = vrf_perm[1]
    else:
        vrf_perm = 1 
        
    if vrf_perm != 1:
        HTML.restriction_message() 
        return 

    ### logged in user does have enough rights to 

    sql_nets = """SELECT id FROM ipall_ip WHERE vrf='%s' """ % rd
    nets = conn.get_data(sql_nets)
    #print nets

    print """<br>"""
    print """<div id="main">"""
    print """<div id="table_main">"""

    if nets == () or nets == None:

        sql_company = """SELECT companies_id FROM networks WHERE vpn_rd='%s' """ % ( rd )
        company = conn.get_data(sql_company)[0][0]

        ### NO child networks are present
        sql_rights_del = """DELETE FROM ipall_rights where path='%s'""" % str(rd)
        del_rights = conn.update_data(sql_rights_del)
        ### LOGGING
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_rights', "%s", %u)""" % (current_user, sql_rights_del, company)
        log = conn.update_data(sql_log)

        sql_del = """DELETE FROM networks WHERE vpn_rd='%s' """ % rd
        delete = conn.update_data(sql_del)

        ### LOGGING
        log_string = sql_del
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_ip', "%s", %u)""" % (current_user, log_string, company)
        log = conn.update_data(sql_log)
        #log = 1

        if delete != 0 and log != 0:
            HTML.notify_message("View/VRF successfully deleted...")
            print """<div id=message><a href="javascript:void(0);" onClick="parent.location.reload(1);" class="LinkPurpleBold">close and refresh</a></div>"""
        else:   ### delete != 1
            HTML.error_message("<br>An error has occured!")
    else:	### network has child networks
        HTML.error_message("<br>There are networks present. You can't delete this View/VRF")
        
    print """</div>""" #table_main
    print """</div>""" #main
    

    HTML.popup_footer()

main()
