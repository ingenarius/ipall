#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
"""

from Html_new import HtmlContent
from Ipall import IpallFunctions
import DBmy
import IpallUser
from Sessionclass import Session
import IPy
import os
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie


def print_form(cgi_dir, net, f, sel_group):
    """print form to edit permissions"""

    print """<form name="edit_permissions" method=POST action="network_permissions.cgi">"""

    ### hidden values
    print """<input type=hidden name=net_id value=%u>""" % net[0]
    print """<input type=hidden name=net_path value="%s">""" % net[6]
    print """<input type=hidden name=company value="%s">""" % net[11]

    print """<div id="pos_left_small">"""
    print """<div class="lineHeight">Network</div>"""
    print """<div class="lineHeight">Group</div>"""
    print """</div>""" # left side

    print """<div id="pos_right_wide">"""
    print """<div class="lineHeight">%s</div>""" % net[1]
    print """<div class="lineHeight">"""
#    print """<select name=group onChange="location = this.options[this.selectedIndex].value;" class=b_eingabefeld>"""
    print """<select name=group onChange="ajaxFunction('%s/a_net_permissions.cgi?%s&'+this.options[this.selectedIndex].value, 'perm_info', 1)" class=b_eingabefeld>""" % ( cgi_dir, str(net[6]) )
    groups = f.get_groups(net[11])
    if sel_group == 0:
        print """<option value="%s">select group ...</option>""" % ( "0")
    else:
        group = f.get_sel_group(sel_group)
        print """<option value="%s">%s</option>""" % ( sel_group, group[0] )
        print """<option value="%s">select group</option>""" % ("0")
    for g in groups:
        if g[0] != sel_group:
            print """<option value="%s">%s</option>""" % ( str(g[0]), str(g[1]) )
    print """</select></div>"""
    print """</div>""" # right side
    print """<div id="pos_clear"></div>"""
    print """<div id="perm_info"></div>"""
    print """<div><input type=submit name=save value=save class=button></div>"""
    print """</form>"""


def main():
    """edit permissions of groups to networks"""

    #global id, sel_group, conn, cgi_dir
    formdata = cgi.FieldStorage()
    id = group = sel_group = company = 0
    delete_net = edit_net = subnet_net = view_net = edit_vrf = delete_vrf = "off"


    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if qs.split("&")[1].find("keep") == 0:
            id = int(qs.split("&")[0]) # network id
            sel_group = 0
        if qs.split("&")[2].find("keep") == 0:
            id = int(qs.split("&")[0]) # network id
            sel_group = int(qs.split("&")[1])
    else:
        id = 0

    try:
        ### network info
        if formdata.has_key("net_id"):
            id = int(formdata['net_id'].value)
        if formdata.has_key("net_path"):
            path = str(formdata['net_path'].value)
        if formdata.has_key("sel_group"):
            sel_group = int(formdata['sel_group'].value)
        if formdata.has_key("company"):
            company = int(formdata['company'].value)
        ### group rigths
        if formdata.has_key("delete_net"):
            delete_net = str(formdata['delete_net'].value)
        if formdata.has_key("edit_net"):
            edit_net = str(formdata['edit_net'].value)
        if formdata.has_key("subnet_net"):
            subnet_net = str(formdata['subnet_net'].value)
        if formdata.has_key("view_net"):
            view_net = str(formdata['view_net'].value)
    except ValueError, e:
        print "Error: %s" % e
        print """<script language="javascript">alert("Value parse error, sorry!"); history.back();</script> """
        return

    ### create database connection object
    cfg = ConfigObj("ipall.cfg")
    cgi_dir = cfg['Server']['cgi_dir']
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

    if group != 1 and rights[1] == 0:
        HTML.restriction_message(1)
        HTML.close_body()
        return

    ### logged in user does not have enough rights to edit permissions
    if id == 0:
        HTML.restriction_message(1)
        HTML.close_body()
        return

    ### logged in user does have enough rights to edit permissions
    else:
        f = IpallFunctions(conn, current_user, group, company_id)
        if formdata.has_key("save"):
            if delete_net == "on": delete_net = 1;
            else: delete_net = 0; 
            if edit_net == "on": edit_net = 1;
            else: edit_net = 0; 
            if subnet_net == "on": subnet_net = 1;
            else: subnet_net = 0; 
            if view_net == "on": view_net = 1;
            else: view_net = 0; 
            if edit_vrf == "on": edit_vrf = 1;
            else: edit_vrf = 0; 
            if delete_vrf == "on": delete_vrf = 1;
            else: delete_vrf = 0; 

            sql_check = """SELECT group_id, path FROM ipall_rights WHERE group_id=%u AND path='%s' """ % (sel_group, path)
            chk = conn.get_data(sql_check)

            if chk == ():
                sql_ins_rights = """INSERT INTO ipall_rights VALUES(%u, '%s', %u, %u, %u, %u, 0, 0, %u)""" \
                    % (sel_group, path, delete_net, edit_net, subnet_net, view_net, company)
                print sql_ins_rights
                insert_rights = conn.update_data(sql_ins_rights)

            else:
                sql_upd_rights = """UPDATE ipall_rights SET delete_net=%u, edit_net=%u, subnet_net=%u, view_net=%u 
                    WHERE group_id=%u AND path='%s' """ \
                    % (delete_net, edit_net, subnet_net, view_net, sel_group, path)
                print sql_upd_rights
                insert_rights = conn.update_data(sql_upd_rights)

            if insert_rights == 0: 
                HTML.error_message("An error has occured! Sorry!")
                HTML.close_body()
                return
            else:
                HTML.notify_message("changes applied ...")
                HTML.popup_footer()
                return


        network = f.get_net_info(2, id)

    print """<div id="main">"""
    print """<div id="table_main">"""
    print """<div id="functionHead">Permissions of network %s and <i>all</i> subnets</div>""" \
        % network[0][2]

    print_form(cgi_dir, network[0], f, sel_group)

    print """</div>""" #table_main
    print """</div>""" #main

    HTML.close_body()

main()
