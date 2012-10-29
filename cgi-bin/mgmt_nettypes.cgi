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
    print """<p><div id="functionHead">"""
    print """<span class="TextPurpleBold">IP@LL nettype management</span>"""
    if rights[2] == 1 or group != 1:
        print """<span id="pos_right_inside" style="text-align: right"><a href="%s/new_nettype.cgi" 
            class=linkPurpleBold>new nettype</a></span>""" % cgi_dir
    print """</div></p>"""
    print """<div style="text-align: center;">Note: Built in nettypes (id 1-11) can't be deleted!</div>"""
#    print """<div style="border-bottom: 1px dotted;">"""

    if group == 1 or rights[2] == 1:
        sql_types = """SELECT id, typename FROM ipall_network_types ORDER BY typename"""
        types = conn.get_data(sql_types)
        for t in types:
            print """<div id="pos_left" class=lineHeight>%s [id: %s]</div>""" % ( str(t[1]), str(t[0]) )
            print """<div id="pos_right" class=lineHeight style="text-align: right">"""
            print """<img src="%s/images/editOff.png" id="edit" onMouseOver="mouseoverImage(this, '%s');"  
                onMouseOut="mouseoverImage(this, '%s');" onClick="redirect_to_url('%s/nettype_edit.cgi?%s');" class=handlers />""" \
                    % ( ipall_dir, ipall_dir, ipall_dir, cgi_dir, str(t[0]) )
            if int(t[0]) > 11:
                print """<img src="%s/images/deleteOff.png" id="delete" onMouseOver="mouseoverImage(this, '%s');"  
                    onMouseOut="mouseoverImage(this, '%s');" onClick="confirm_and_redirect('Do you really want to delete this network type?', '%s/nettype_delete.cgi?%s');" class=handlers />""" \
                        % ( ipall_dir, ipall_dir, ipall_dir, cgi_dir, str(t[0]) )
            print """</div>"""
            print """<div id="pos_clear"></div>"""
    else:
        HTML.notify_message("You are not allowed to execute this!")

    HTML.close_body()

main()
