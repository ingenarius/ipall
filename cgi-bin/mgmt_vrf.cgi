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
    
    if group == 0 and rights[2] != 1:
        HTML.restriction_message()
        return

    print """<div id="main">"""
    print """<div id="table_main">"""
    ### HEADING
    print """<div id="functionHead">IP@LL VRF group management</div>"""

    if group == 1:
        sql_companies = """SELECT id, name FROM companies ORDER BY name"""
        companies = conn.get_data(sql_companies)
        for c in companies:
            print """<div class=textPurpleBold>%s</div>""" % c[1]
            sql_vrfs = """SELECT networks_id, name, vpn_rd, vpn_vrf_name FROM networks WHERE companies_id=%u ORDER BY name""" % int(c[0])
            vrfs = conn.get_data(sql_vrfs)
            for v in vrfs:
                print """<div id="pos_left_small" class=lineIndent>%s (%s)</div>""" % ( str(v[1]), str(v[3]) )
                print """<div id="pos_right" style="text-align: right">"""
                print """<img src="%s/images/editOff.png" id="edit" onMouseOver="mouseoverImage(this, '%s');"  
                    onMouseOut="mouseoverImage(this, '%s');" onClick="redirect_to_url('%s/vrf_group_edit.cgi?%s');" class=handlers />""" \
                        % ( ipall_dir, ipall_dir, ipall_dir, cgi_dir, str(v[2]) )
                print """</div>"""
                print """<div id="pos_clear"></div>"""
    elif rights[1] == 1:
        sql_vrfs = """SELECT networks_id, name, vpn_rd, vpn_vrf_name FROM networks WHERE companies_id=%u ORDER BY name""" % company_id
        vrfs = conn.get_data(sql_vrfs)
        for v in vrfs:
            print """<div id="pos_left_small" class=lineIndent>%s (%s)</td>""" % ( str(v[1]), str(v[3]) )
            print """<div id="pos_right" style="text-align: right">"""
            print """<img src="%s/images/editOff.png" id="edit" onMouseOver="mouseoverImage(this, '%s');"  
                onMouseOut="mouseoverImage(this, '%s');" onClick="redirect_to_url('%s/vrf_group_edit.cgi?%s');" class=handlers />""" \
                    % ( ipall_dir, ipall_dir, ipall_dir, cgi_dir, str(v[2]) )
            print """</div>"""
            print """<div id="pos_clear"></div>"""
    else:
        HTML.notify_message("You are not allowed to change VRF group settings!")

    print """</div>""" #table_main
    print """</div>""" #main
    HTML.popup_footer()

main()
