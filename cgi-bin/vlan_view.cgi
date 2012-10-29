#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 racyAPz
http://www.racyapz.at
*****************************
"""

import HTML
import DBmy
import IpallUser
import IPy
import Whois
import Session
import os
import re
from Configobj import ConfigObj
from Cookie import SimpleCookie


def print_configs(peering_info, network, netname, dev):
    """shows the neighbor config for cisco and juniper routers"""

    print """<table border=0 cellspacing=0 cellpadding=0 class=TextPurple>"""
    ### cisco neighbor config
    print """<tr> <th align=left>Cisco neighbor config</th> </tr>"""
    print """<tr>"""
    print """<td>neighbor %s remote-as %s</td>""" % (network, peering_info[0][1])
    print """</tr>"""
    print """<tr>"""
    print """<td>neighbor %s description %s</td>""" % (network, netname)
    print """</tr>"""
    if peering_info[0][3] != "NULL" and peering_info[0][3] != "None":
	print """<tr>"""
	print """<td>neighbor %s password %s</td>""" % (network, peering_info[0][3])
	print """</tr>"""
    print """<tr>"""
    if dev == "at-v-vix" or dev == "at-v-inx" or dev == "at-v-vix;at-v-inx" or dev == "at-v-inx;at-v-vix":
	print """<td>neighbor %s peer-group VIX-PEER</td>""" % (network)
    elif dev == "r1-intx1-fra":
	print """<td>neighbor %s peer-group DECIX-PEER</td>""" % (network)
    elif dev == "uk-l-inx" and network.find("224") != -1:
	print """<td>neighbor %s peer-group LINX-PEER-224</td>""" % (network)
    elif dev == "uk-l-inx" and network.find("225") != -1:
	print """<td>neighbor %s peer-group LINX-PEER-224</td>""" % (network)
    elif dev == "uk-l-inx" and network.find("226") != -1:
	print """<td>neighbor %s peer-group LINX-PEER-226</td>""" % (network)
    elif dev == "uk-l-inx" and network.find("227") != -1:
	print """<td>neighbor %s peer-group LINX-PEER-226</td>""" % (network)
    else:
	print """<td>peer-group not desireable</td>"""
    print """</tr>"""
    if peering_info[0][9] != "NULL" and peering_info[0][9] != None and peering_info[0][9] != 0:
	print """<tr>"""
	print """<td>neighbor %s maximum-prefix %s restart 30</td>""" % (network, peering_info[0][9])
	print """</tr>"""

    print """<tr><td>&nbsp;</td></tr>"""

    ### juniper neighbor config
    print """<tr> <th align=left>Juniper neighbor config (edit within bgp group)</th> </tr>"""
    print """<tr><td>set neighbor %s peer-as %s </td></tr>""" % (network, peering_info[0][1])
    if peering_info[0][3] != "NULL" and peering_info[0][3] != "None":
	print """<tr><td>set neighbor %s authentication-key "%s" </td></tr>""" % (network, peering_info[0][3])
    print """<tr><td>set neighbor %s description "%s" </td></tr>""" % (network, netname)
    if peering_info[0][9] != "NULL" and peering_info[0][9] != None and peering_info[0][9] != 0:
	print """<tr><td>set neighbor %s family inet unicast prefix-limit maximum %s</td></tr>""" % (network, peering_info[0][9])
	print """<tr><td>set neighbor %s family inet unicast prefix-limit teardown 90</td></tr>""" % (network)
	print """<tr><td>set neighbor %s family inet unicast prefix-limit teardown idle-timeout 30</td></tr>""" % (network)
    #print """<tr><td>Please use the insert [after|before] command to keep the config clean!</td></tr>""" 
    print """<tr><td>insert neighbor %s after neighbor [previous neighbor IP] </td></tr>""" % (network)

    print """</table>"""
    


def restriction_message():
    """print a restriction message"""

    print """<blockquote>"""
    print """<p class=textPurpleBold>You are not allowed to execute this</p>"""
    print """<a href="javascript:history.back();" class=linkPurpleBold> << back</a>"""
    print """</blockquote>"""


def main():
    """entry point for executing IPALL - view network details"""

    ### definitions of variables
    global rights, conn, group, cgi_dir
    configs = ripe = "no"

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 1:
            id = int(qs.split("&")[0])
	    configs = "no"
        if len(qs.split("&")) == 2:
            id = int(qs.split("&")[0])
	    configs = str(qs.split("&")[1])
        if len(qs.split("&")) == 3:
            id = int(qs.split("&")[0])
	    configs = str(qs.split("&")[1])
	    ripe = str(qs.split("&")[2])
    else:
        current_user = ""
        id = 0
	configs = ripe = "no"

    user_md5 = Session.check_cookie()

    ### create database connection object
    cfg = ConfigObj("ipall.cfg")
    db_host = cfg['Database']['db_host']
    db_user = cfg['Database']['db_user']
    db_pw = cfg['Database']['db_pw']
    db = cfg['Database']['db']
    conn = DBmy.db(db_host, db_user, db_pw, db)

    ### User
    current_user = conn.get_username(user_md5)
    if current_user == "":
	HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    else:
        HTML.main_header()
    user = IpallUser.User(current_user)
    group = user.get_group_id()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']
    if group == 0:
        restriction_message()
        return

    referer = str(os.environ['HTTP_REFERER'])

    query = """SELECT is_vlan, is_group, is_device, path, vlan, name, interfaces, description FROM ipall_vlan WHERE id=%u """ % (id)
    details = conn.get_data(query)

    if details == () or details == None:
	print """<p class=TextPurpleBold> Nothing to display</p>"""
	return
    else:
        if group != 1:
	    net_perm = conn.get_net_permissions(str(details[0][4]), group)
            if net_perm == () or net_perm == "":
                net_perm = 0
                edit_perm = 0
            else:
		edit_perm = net_perm[1]
                net_perm = net_perm[3]
        else:
            net_perm = 1
	    edit_perm = 1
            #print net_perm

        if net_perm != 1:
            restriction_message()
            return

	print """<br><blockquote>"""
	print """<table width=550 border=0 cellspacing=0 cellpadding=0 class=TextPurple><tr class=lightPurple3 height=20><td colspan=2>"""
	### header table ###
	print """<table width=550 border=0 cellspacing=0 cellpadding=0 class=TextPurple>"""
	print """<tr>"""
	print """<td width=210 class=TextPurpleBold>VLAN"""
	print """</td>"""
	print """<td class=TextPurpleBold valign="middle">%s""" % details[0][4]
	if edit_perm == 1:
	    print """<td align=right> <a href="%s/vlan_edit.cgi?%s" title="edit details">
		<img src="%s/images/editOff.png" id="edit" onmouseover="javascript:mouseoverImage(this)" 
		onmouseout="javascript:mouseoverImage(this)" class=handlers></a></td>""" % (cgi_dir, id, ipall_dir)
	print """</tr>"""
	print """</table>""" ### header table

	print """</td>""" 
	print """</tr><tr>"""
	print """<td width=210>Name</td>"""
	print """<td>%s</td>""" % details[0][5]
	print """</tr>"""

	if details[0][6]:
	    print """<tr>"""
	    print """<td>Interfaces</td>"""
	    print """<td>"""
	    for i in details[0][6].split(";"):
		print """%s<br>""" % i
	    print """</td>"""
	    print """</tr>"""

	print """<tr>"""
	print """<td valign=top>Description</td>"""
	print """<td><textarea class=b_eingabefeld_white readonly>%s</textarea></td>""" % details[0][7]
	print """</tr>"""
	
	print """<tr><td colspan=2>&nbsp;</td></tr>"""
	print """<td colspan=2 align=right>"""
	print """<a href="%s/vlans.cgi?%s#%s" class=LinkPurpleBold> << back </a>""" % (cgi_dir, details[0][3], id)
	print """</td></tr>""" 

	print """</table>"""
	print """</blockquote>"""
	
    
    HTML.main_footer()


main()
