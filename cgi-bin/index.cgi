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

    ### definitions of variables
    global conn, depth, path, view
    formdata = cgi.FieldStorage()

    HTML = HtmlContent()
    HTML.simple_header()
    ### create database connection object
    cfg = ConfigObj("ipall.cfg")
    db_host = cfg['Database']['db_host']
    db_user = cfg['Database']['db_user']
    db_pw = cfg['Database']['db_pw']
    db = cfg['Database']['db']
    conn = DBmy.db(db_host, db_user, db_pw, db)

    s = Session(conn)
    current_user = s.check_user()
    #company = s.check_cookie()
    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    else:
        HTML.body()

    ## User
    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']
    ripe_mail = cfg['Server']['ripe_mail']
    # smoothbox parameters
    sbox = cfg['Site']['smoothbox'].replace("?", "&")

    
    if group == 0:
        HTML.restriction_message()
        return

    print """<br>"""
    print """<div id="divHead800">""" #1
    print """<span class=left>select view/VRF</span>"""
    print """<span class=right>you are logged in as: <i>%s</i></span>""" % ( current_user )
    print """<span class=left></span>"""
    print """<span class=right></span>"""
    print """</div>""" #1
    print """<div id="table_main">"""


    if group == 1:
        sql_companies = """SELECT id, name, is_lir FROM companies ORDER BY name"""
        companies = conn.get_data(sql_companies)
        
        if companies != ():
            for c in companies:
                sql_vpns = """SELECT vpn_rd, name, vpn_vrf_name, description FROM networks WHERE vpn_rd != "" AND companies_id=%u ORDER BY name""" % int(c[0])
                vpns = conn.get_data(sql_vpns)
                print """<div id="company_name">"""
                print """<span class=left>%s</span>""" % ( c[1] )
                print """<span class=right>[ """
                if c[2] == 1:
                    print """<a href="javascript:void(0)" onClick="confirm_and_redirect('send mail to %s', '%s/register_as.cgi?%s');" class=linkPurpleBold>register AS @ RIR</a> | """ % ( ripe_mail, cgi_dir, c[0] )
                print """<a href="%s/new_vrf.cgi?%s%s" class="smoothbox">new View/VRF</a>""" % ( cgi_dir, c[0], sbox )
                print """ ]</span>"""
                print """</div>""" #company
                if vpns == () or vpns == None:
                    HTML.notify_message("No views or VRFs found!")
                else:
                    for v in vpns:
                        print """
                            <div id="vpn">
                            <span class="left">-</span>
                            <span class="middle"> <a href="%s/networks.cgi?%s" class=LinkPurple title="%s"> %s [%s]</a>""" \
                                % ( cgi_dir, str(v[0]), str(v[3]), str(v[1]), str(v[2]) )
                        print """</span>"""
                        print """<span class="right"><a class="smoothbox" href="%s/vrf_edit.cgi?%s&%s%s">
                            <img src="%s/images/editOff.png" id="edit" title="edit" onMouseOver="mouseoverImage(this, '%s');"  
                            onMouseOut="mouseoverImage(this, '%s');" class=handlers /></a>""" \
                                % ( cgi_dir, str(v[0]), str(c[0]), sbox, ipall_dir, ipall_dir, ipall_dir )
                        print """<a class="smoothbox" href="%s/vrf_delete.cgi?%s%s">
                            <img src="%s/images/deleteOff.png" id="delete" title="delete" onMouseOver="mouseoverImage(this, '%s');"  
                            onMouseOut="mouseoverImage(this, '%s');" onClick="confirm('Do you really want to delete this vrf?');" 
                            class=handlers /></a>""" % ( cgi_dir, str(v[0]), sbox, ipall_dir, ipall_dir, ipall_dir )
                        print """</span></div>"""
    else: # group != 1
        sql_companies = """SELECT id, name, is_lir FROM companies WHERE id=%u """ % int(company_id)
        companies = conn.get_data(sql_companies)
        sql_vpns = """SELECT vpn_rd, name, vpn_vrf_name, description FROM networks WHERE vpn_rd != "" AND companies_id=%u ORDER BY name""" % int(companies[0][0])
        vpns = conn.get_data(sql_vpns)
        if vpns == () or vpns == None:
            HTML.notify_message("No views or VRFs found!")
            return
        if rights[2] == 1:
            print """<div id="company_name">"""
            print """<span class="left" style="font-weight: bold; margin-bottom: 5px;">%s</span>""" % companies[0][1]
            print """<span class="right">[ """
            if companies[0][2] == 1:
                print """<a href="javascript:void(0)" onClick="confirm_and_redirect('send mail to %s', '%s/register_as.cgi?%s');" class=linkPurpleBold>register AS @ RIR | </a>""" \
                    % ( ripe_mail, cgi_dir, company_id )
            print """<a href="%s/new_vrf.cgi?%s%s" class=smoothbox>new View/VRF</a>""" % ( cgi_dir, companies[0][0], sbox )
            print """ ]</span>"""
            print """</div>""" # company
        else:
            print """<span class=left style="font-weight: bold;">%s</span>""" % companies[0][1]
        for v in vpns:
            if v[0] != "" or v[1] != "":
                if group != 1 and rights[2] != 1:
                    vrf_perm = conn.get_vrf_permissions(str(v[0]), group)
                    if vrf_perm == ():
                        vrf_perm = [0,0]
                else:
                    vrf_perm = [1,1]
                print """
                    <div id="vpn">
                    <span class="left">-</span>
                    <span class="middle"> <a href="%s/networks.cgi?%s" class=LinkPurple title="%s"> %s [%s]</a> """ \
                        % ( cgi_dir, str(v[0]), str(v[3]), str(v[1]), str(v[2]) )
#                print """<span class=TextGrey>&nbsp;/&nbsp;</span> <a href="%s/networks1.cgi?%s" title="non AJAX version - discontinued" class=LinkGrey>
#                    %s [%s]</a>""" % ( cgi_dir, str(v[0]), str(v[1]), str(v[2]) )
                print """</span>"""
                print """<span class="right">"""
                if vrf_perm[0] == 1:
                    print"""<a class="smoothbox" href="%s/vrf_edit.cgi?%s&%s%s">
                        <img src="%s/images/editOff.png" id="edit" title="edit" onMouseOver="mouseoverImage(this, '%s');"  
                        onMouseOut="mouseoverImage(this, '%s');" class=handlers /></a>""" \
                            % ( cgi_dir, str(v[0]), str(companies[0][0]), sbox, ipall_dir, ipall_dir, ipall_dir )
                if vrf_perm[1] == 1:
                    print """<a class="smoothbox" href="%s/vrf_delete.cgi?%s%s">
                        <img src="%s/images/deleteOff.png" id="delete" title="delete" onMouseOver="mouseoverImage(this, '%s');"  
                        onMouseOut="mouseoverImage(this, '%s');" onClick="confirm('Do you really want to delete this vrf?');" 
                        class=handlers /></a>""" % ( cgi_dir, str(v[0]), sbox, ipall_dir, ipall_dir, ipall_dir )
                print """</span></div>""" #vpn
        print """</div>""" # table_main

    HTML.main_footer()

main()
