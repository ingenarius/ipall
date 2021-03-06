#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
"""

import Html as HTML
import DBmy
import IpallUser
from Sessionclass import Session
import IPy
import os
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie


def print_form():
    """print form to edit permissions"""

#    print "type_id: %u<br>" % type_id
#    print "sel_group: %u<br>" % sel_group
    print """<form name="edit_permissions" method=POST action="nettype_permissions.cgi">"""

    ### hidden values
    print """<input type=hidden name=vrf value="%s">""" % vrf
    print """<input type=hidden name=type_id value=%u>""" % type_id
    print """<input type=hidden name=sel_group value=%u>""" % sel_group
    print """<input type=hidden name=company value=%u>""" % company
    print """<table width=100% border=0 class=TextPurple>"""
    print """<tr height=25>"""
    print """<td width=200px>Network type</td>"""
    print """<td>"""
    print """<select name=group onChange="location = this.options[this.selectedIndex].value;" class=b_eingabefeld>"""
    nettypes = get_net_types()
    if type_id == 0:
        print """<option value="%s/nettype_permissions.cgi?%s&%s">select network type</option>""" % (cgi_dir, str(vrf), "0")
    else:
        type = get_sel_type()
        print """<option value="%s/nettype_permissions.cgi?%s&%s">%s</option>""" % (cgi_dir, str(vrf), str(type_id), type[0])
        print """<option value="%s/nettype_permissions.cgi?%s&%s">select network type</option>""" % (cgi_dir, str(vrf), "0")
    for t in nettypes:
        if t[0] != type_id:
            print """<option value="%s/nettype_permissions.cgi?%s&%s">%s</option>""" % (cgi_dir, str(vrf), str(t[0]), str(t[1]))
    print """</select>"""
    print """</td>"""
#    print """<td>%s</td>""" % net[2]
    print """</tr>"""

    print """<tr height=25>"""
    print """<td width=200px>Group</td>"""
    print """<td>"""
    print """<select name=group onChange="location = this.options[this.selectedIndex].value;" class=b_eingabefeld>"""
    groups = get_groups()
    if sel_group == 0:
        print """<option value="%s/nettype_permissions.cgi?%s&%s&%s">select group</option>""" % (cgi_dir, str(vrf), str(type_id), "0")
    else:
        group = get_sel_group()
        print """<option value="%s/nettype_permissions.cgi?%s&%s&%s">%s</option>""" % (cgi_dir, str(vrf), str(type_id), sel_group, group[0])
        print """<option value="%s/nettype_permissions.cgi?%s&%s&%s">select group</option>""" % (cgi_dir, str(vrf), str(type_id), "0")
    for g in groups:
        if g[0] != sel_group:
            print """<option value="%s/nettype_permissions.cgi?%s&%s&%s">%s</option>""" % (cgi_dir, str(vrf), str(type_id), str(g[0]), str(g[1]))
    print """</select>"""
    print """</td>"""
    print """</tr>"""
#    if sel_group != 0:
#       rights = get_rights(net[6])
#       if rights != ():
#           print_checkboxes(rights)
#       else:
    print_checkboxes()
    print """<tr>"""
    print """<td colspan=2><input type=submit name=save value=save class=button></td>"""
    print """</tr>"""

    print """</table>"""
    print """</form>"""


def print_checkboxes( rights=(0,0,0,0) ):
    ### checkboxes for the rights
    print """<tr>"""
    print """<td width=200px>Delete network</td>"""
    if rights[0] == 1:
        print """<td><input type=checkbox name=delete_net checked></td>"""
    else:
        print """<td><input type=checkbox name=delete_net></td>"""
    print """</tr>"""
    print """<tr>"""
    print """<td width=200px>Edit network</td>"""
    
    if rights[1] == 1:
        print """<td><input type=checkbox name=edit_net checked></td>"""
    else:
        print """<td><input type=checkbox name=edit_net></td>"""
    print """</tr>"""
    print """<tr>"""
    print """<td width=200px>Subnet network</td>"""
    if rights[2] == 1:
        print """<td><input type=checkbox name=subnet_net checked></td>"""
    else:
        print """<td><input type=checkbox name=subnet_net></td>"""
    print """</tr>"""
    print """<tr>"""
    print """<td width=200px>View network</td>"""
    if rights[3] == 1:
        print """<td><input type=checkbox name=view_net checked></td>"""
    else:
        print """<td><input type=checkbox name=view_net></td>"""
    print """</tr>"""


def get_rights(path):
    """fetch rights of selected group"""

    sql_perm = """SELECT delete_net, edit_net, subnet_net, view_net FROM ipall_rights WHERE group_id=%u AND path='%s' """ % (sel_group, path)
    perm = conn.get_data(sql_perm)
    
    if perm != ():
        return perm[0]
    else:
        return perm

def get_sel_group():
    """fetch the selected group info"""

    sql_group = """SELECT groupname FROM ipall_group WHERE id=%u""" % sel_group
    group = conn.get_data(sql_group)

    return group[0]

def get_groups():
    """fetches all groups and makes a dropdown box"""

    sql_groups = """SELECT id, groupname FROM ipall_group WHERE id != 1 AND companies_id=%u""" % ( company )
    groups = conn.get_data(sql_groups)

    return groups


def get_sel_type():
    """fetch the selected type name"""

    sql_type = """SELECT typename FROM ipall_network_types WHERE id=%u""" % type_id
    type = conn.get_data(sql_type)

    return type[0]


def get_net_types(id=0):
    """return dropdown box <option> with network types"""

    if id == 0:
        sql_net_types = """SELECT id, typename FROM ipall_network_types ORDER BY typename"""
    else:
        sql_net_types = """SELECT id, typename FROM ipall_network_types WHERE id=%u""" % id
    net_types = conn.get_data(sql_net_types)

    return net_types


def main():
    """edit permissions of groups to networks"""

    global company, group, vrf, type_id, sel_group, conn, cgi_dir
    formdata = cgi.FieldStorage()
    vrf = ""
    company = type_id = group = sel_group = 0
    delete_net = edit_net = subnet_net = view_net = "off"


    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
#        if len(qs.split("&")) == 1:
#            vrf = str(qs[0:])
#            type_id = 0
#            sel_group = 0
#        if len(qs.split("&")) == 2:
#            vrf = str(qs.split("&")[0])
#            type_id = int(qs.split("&")[1])
#            sel_group = 0
#        if len(qs.split("&")) == 3:
    try:
         vrf = str(qs.split("&")[0])
         type_id = int(qs.split("&")[1])
         sel_group = int(qs.split("&")[2])
    except:
        vrf = ""
        type_id = sel_group = 0


    try:
        ### network info
        if formdata.has_key("vrf"):
            vrf = str(formdata['vrf'].value)
        if formdata.has_key("type_id"):
            type_id = int(formdata['type_id'].value)
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
    db_host = cfg['Database']['db_host']
    db_user = cfg['Database']['db_user']
    db_pw = cfg['Database']['db_pw']
    db = cfg['Database']['db']
    conn = DBmy.db(db_host, db_user, db_pw, db)

    ### User
    s = Session(conn)
    current_user = s.check_user()
    #company = s.check_cookie()
    HTML.simple_header()

    if current_user == "":
        return
    else:
        print ""
        #HTML.popup_body()

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']

    if group == 0:
        HTML.restriction_message(1)
        HTML.popup_footer()
        return

    ### logged in user does not have enough rights to edit permissions
    elif rights[1] != 1 and rights[2] != 1:
        HTML.restriction_message(1)
        HTML.popup_footer()
        return

    ### logged in user does have enough rights to edit permissions
    else:
        if formdata.has_key("save"):
            if type_id == 0 or type_id == None: print """<script language="javascript">alert("Please choose network type"); history.back();</script> """; return
            if sel_group == 0 or sel_group == None: print """<script language="javascript">alert("Please choose group"); history.back();</script> """; return
            if delete_net == "on": delete_net = 1;
            else: delete_net = 0; 
            if edit_net == "on": edit_net = 1;
            else: edit_net = 0; 
            if subnet_net == "on": subnet_net = 1;
            else: subnet_net = 0; 
            if view_net == "on": view_net = 1;
            else: view_net = 0; 
            insert_rights = 0

            sql_networks = """SELECT id, path, label FROM ipall_ip WHERE service_id=%s AND vrf='%s' 
                AND allocated=1 ORDER BY address""" % ( str(type_id), str(vrf) )
            networks = conn.get_data(sql_networks)

            if networks == () or networks == 0:
                HTML.notify_message("There are no networks assigned to this type")
                HTML.popup_footer()
                return

            print """Networks: <br>"""
            for n in networks:
                path = n[1]
                sql_check = """SELECT group_id, path FROM ipall_rights WHERE group_id=%u AND path='%s' """ % (sel_group, path)
                chk = conn.get_data(sql_check)

                if chk == ():
                    sql_ins_rights = """INSERT INTO ipall_rights VALUES(%u, '%s', %u, %u, %u, %u, 0, 0, %u)""" \
                        % (sel_group, path, delete_net, edit_net, subnet_net, view_net, company)
                    #print sql_ins_rights, "<br>"
                    insert_rights = conn.update_data(sql_ins_rights)
                else:
                    sql_upd_rights = """UPDATE ipall_rights SET delete_net=%u, edit_net=%u, subnet_net=%u, view_net=%u WHERE group_id=%u AND path='%s' """ \
                        % (delete_net, edit_net, subnet_net, view_net, sel_group, path)
                    #print sql_upd_rights, "<br>"
                    insert_rights = conn.update_data(sql_upd_rights)

                print n[2], "<br>"

            if insert_rights == 0: 
                HTML.notify_message("An error has occured! Sorry!")
                HTML.popup_footer()
                return
            else:
                HTML.notify_message("Network permissions successfully changed")
                HTML.popup_footer()
                return
                            
        if group == 1:
            print "vrf: %s" % vrf
            sql_company = """SELECT companies_id FROM networks WHERE vpn_rd='%s' """ % ( vrf )
            company = conn.get_data(sql_company)
            if company != ():
                company = company[0][0]
            else:
                HTML.notify_message("View/VRF error")
                HTML.popup_footer()
                return
        else:
            company = company_id

        print """<br>"""
        print """<div id="main">"""
        print """<table class=table_main border=0 cellspacing=5 cellpadding=0 class=TextPurple>"""
        print """<tr height=20 class=lightPurple3>"""
        print """<td class=textPurpleBold>Change permissions of all allocated networks of the selected type - !!! Use with care !!!</td>"""
        print """</tr>"""
        print """<tr>"""
        print """<td>"""

        print_form()
#        print_form(network[0])

        print """</td>"""
        print """<tr><td colspan=2 align=right><div id="info"></div></td></tr>"""
        print """</table>"""
        print """</div>"""

    HTML.popup_footer()

main()
