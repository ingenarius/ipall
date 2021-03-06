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
from Cookie import SimpleCookie



def print_vrf_form(vrf, details):
    """print html form to edit group details
    details: group_id, groupname"""

    print """<input type=hidden name=vrf value="%s">""" % str(vrf)

    print """<div id="pos_left_260">Select group"""
    print_groups()
    print """</div>"""
    print """<div id="pos_left_30" style="margin-top:50px">"""
    print """<span class=button id="add" onClick="moveOptions('groups', 'in_groups', '%s', '%s');" 
        title="set permission to selected group(s) on the left"><img src="%s/images/forward.gif"></span><br>""" \
        % ( cgi_dir, vrf, ipall_dir )
    print """<span class=button id="del" onClick="moveOptions('in_groups', 'groups', '%s', '%s');" 
        title="delete permissions of selected group(s) on the right"><img src="%s/images/back.gif"></span>""" \
        % ( cgi_dir, vrf, ipall_dir )
    print """</div>"""

    print """<div id="pos_left_260">"""
    print """Groups with permission"""
    print_in_groups(details)
    print """</div>""" # right side
    print """<div id="pos_clear"></div>"""
    print """<div id="info" class=textPurpleItalic"></div>
        <div id="info2" class=textPurpleItalic"></div>
        <div id="info3" class=textPurpleItalic"></div>"""
    


def print_groups():
    """print a dropdown box with groups"""
    
    sql_groups = """SELECT g.id, g.groupname, g.companies_id FROM
        ipall_group g, networks n WHERE
        ( g.id != 1 AND g.company_admin != 1 AND
        n.vpn_rd='%s' AND
        n.companies_id=g.companies_id ) AND
        g.id NOT IN ( SELECT group_id FROM ipall_rights_vrf WHERE vrf='%s' )
        ORDER BY g.groupname""" % ( vrf, vrf )
    groups = conn.get_data(sql_groups)
    if groups != () and groups != None:
        print """<select name="groups" id="groups" size=7 class=b_eingabefeld multiple="multiple">"""
        for g in groups:
            print """<option value="%s;%s">%s</option>""" % ( str(g[0]), str(g[2]), g[1] )
        print """</select>"""
    else:
        print """<select name="groups" id="groups" size=7 class=b_eingabefeld>"""
        print """</select>"""


def print_in_groups(in_groups):
    """print a dropdown box with groups"""
    
    if in_groups != () and in_groups != None:
        print """<select name="in_groups" id="in_groups" size=7 class=b_eingabefeld multiple="multiple">"""
        for g in in_groups:
            print """<option value="%s;%s">%s</option>""" % ( str(g[0]), str(g[2]), g[1] )
        print """</select>"""
    else:
        print """<select name="in_groups" id="in_groups" size=7 class=b_eingabefeld>"""
        print """</select>"""

def main():
    """entry point for executing IP@LL - edit vrf group permissions"""

    ### definitions of variables
    global current_user, cgi_dir, ipall_dir, vrf, conn, rights
    group_id = () 

    formdata = cgi.FieldStorage()

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 1:
            vrf = str(qs.split("&")[0])
            add_id = del_id = companies_id = 0
        elif len(qs.split("&")) == 2:
            vrf = str(qs.split("&")[0])
            if str(qs.split("&")[1]).find("add") != -1:
                add_id = int( qs.split("&")[1].split("=")[1].split(";")[0] )
                del_id = 0
                companies_id = int( qs.split("&")[1].split("=")[1].split(";")[1] )
            elif str(qs.split("&")[1]).find("del") != -1:
                add_id = 0
                del_id = int( qs.split("&")[1].split("=")[1].split(";")[0] )
                companies_id = int( qs.split("&")[1].split("=")[1].split(";")[1] )
            else:
                add_id = del_id = companies_id = 0
        else:
            vrf = "0"
            add_id = del_id = companies_id = 0
            

    try:
        if formdata.has_key("vrf"):
            vrf = str(formdata['vrf'].value)
        if formdata.has_key("group_id"):
            group_id = formdata['group_id']
    except:
        HTML.simple_header()
        print """<script language="javascript">alert("Value error"); history.back();</script> """
        return

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
        if add_id == 0 and del_id == 0:
            HTML.popup_body()

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']

    if group == 0:
        HTML.restriction_message()
        return
    
    if vrf == 0:
        HTML.error_message("Nothing to display!")
        return

    if del_id != 0:
        sql_delete = """DELETE FROM ipall_rights_vrf WHERE vrf='%s' AND group_id=%u AND companies_id=%u """ % ( vrf, int(del_id), companies_id )
        delete = conn.update_data(sql_delete)
        
        if delete == 1:
            HTML.notify_message("Group permissions deleted")
        else:
            HTML.notify_message("Error!")
        return
        
    if add_id != 0:
        sql_add = """INSERT ipall_rights_vrf SET group_id=%u, vrf='%s', create_net=1, companies_id=%u """ % ( int(add_id), vrf, companies_id )
        add = conn.update_data(sql_add)

        if add == 1:
            HTML.notify_message("Group permissions added")
        else:
            HTML.notify_message("Error!")
        return
            
##    else: ### SAVE key was not pressed
    if group != 1:
        sql_check = """SELECT count(networks_id) FROM networks WHERE vpn_rd='%s' AND companies_id=%u """ % ( vrf, int(company_id) )
        check = conn.get_data(sql_check)
        if check[0][0] == 0:
            HTML.restriction_message()
            return                

    query = """SELECT r.group_id, g.groupname, g.companies_id FROM ipall_rights_vrf r, ipall_group g
        WHERE vrf='%s' AND create_net=1 AND r.group_id=g.id ORDER BY g.groupname""" % ( vrf )
    details = conn.get_data(query)

    if group != 1:
        if rights[2] != 1:
            group_perm = 0
        else:
            group_perm = 1
    else:
        group_perm = 1
        #print user_perm

    if group_perm != 1:
        HTML.restriction_message()
        return
    else:
        print """<div id="main">"""
        print """<div id="table_main">"""
        ### HEADING
        print """<div id="functionHead">Allow to add "new network" to groups in View/VRF %s</div> """ % vrf

        print """<form name="vrf_edit_group" method=GET action="vrf_group_edit.cgi">"""
        
        print_vrf_form(vrf, details)	                

        #print """<td colspan=2><input type=submit name=refresh value="check" onClick="window.location.reload( false );" class=button></td>"""
#        print """<div align=center class=button id=refresh title="click to check entries" style="width: 50px;">
#            <img src="%s/images/checkbox.gif" onClick="window.location.reload( false );"></div></td>""" % ( ipall_dir )
        #print """<td>&nbsp;</td>"""
        #print """<a href="%s/mgmt_vrf.cgi" class=LinkPurpleBold> << back </a>""" % (cgi_dir)
        print """</form>"""
        print """</div>""" #table_main
        print """</div>""" #main

    HTML.popup_footer()

main()
