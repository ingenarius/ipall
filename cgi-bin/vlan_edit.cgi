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
import Session
import os
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie



def print_form(details):
    """print html form to edit network details"""

    print """<input type=hidden name=vlan_id value=%u>""" % int(details[0][0])
    print """<table width=100% border=0 class=TextPurple>"""
    ### VLAN name
    print """<tr>"""
    print """<td width=200px>VLAN name *</td>"""
    print """<td><input type=text name=vlanname class=b_eingabefeld value="%s" maxlength=35></td>""" % details[0][5]
    print """</tr>"""
    ### interfaces
    if details[0][2] == 1:
	print """<tr>"""
	print """<td valign=top>Interfaces<br>(separated with ";"<br>e.g. gi1/0/27;gi1/0/28)</td>"""
	print """<td><textarea name=description class=b_eingabefeld>%s</textarea></td>""" % details[0][6]
	print """</tr>"""
    ### VLAN description
    print """<tr>"""
    print """<td valign=top>VLAN description</td>"""
    print """<td><textarea name=description class=b_eingabefeld>%s</textarea></td>""" % details[0][7]
    print """</tr>"""

    print """</table>"""


def restriction_message():
    """print a restriction message"""
        
    print """<blockquote>"""
    print """<p class=textPurpleBold>You are not allowed to execute this</p>"""
    print """<a href="javascript:history.back();" class=linkPurpleBold> << back</a>"""
    print """</blockquote>"""


def main():
    """entry point for executing IPALL - edit network details"""

    ### definitions of variables
    global rights, conn, group, cgi_dir
    formdata = cgi.FieldStorage()
    vlanname = description = interfaces = "NULL"

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
	if len(qs.split("&")) == 1:
	    id = int(qs.split("&")[0])
    else:
        id = 0

    user_md5 = Session.check_cookie()

    try:
        ### network info
        if formdata.has_key("uri"):
            uri = str(formdata['uri'].value)
        if formdata.has_key("vlan_id"):
            id = int(formdata['vlan_id'].value)
        if formdata.has_key("vlanname"):
            vlanname = str(formdata['vlanname'].value)
        if formdata.has_key("description"):
            description = str(formdata['description'].value)
        if formdata.has_key("interfaces"):
            interfaces = str(formdata['interfaces'].value)
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
    current_user = conn.get_username(user_md5)
    if current_user == "":
	HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    else:
        HTML.main_header()
    user = IpallUser.User(current_user)
    group = user.get_group_id()
    cgi_dir = cfg['Server']['cgi_dir']
    if group == 0:
        restriction_message()
        return


    if formdata.has_key("save"):
	#print "id, net_name, net_description, device_id, peering_info_id, as_nr, as_set, md5, contact_mail, rs, session_up, peer_comment<br>"
	#print id, net_name, net_description, device_id, peering_info_id, as_nr, as_set, md5, contact_mail, rs, session_up, peer_comment
        if vlanname.find("'") != -1 or interface.find("'") != -1 or description.find("'") != -1:
            print """<script language="javascript">alert("You must not insert a quote"); history.back();</script> """; return;
	if vlanname == "NULL" or vlanname == None: print """<script language="javascript">alert("Please insert VLAN name"); history.back();</script> """; return;
	if description == "NULL" or description == "None": description = "NULL";
	else: description = "'" + description + "'"
	if interfaces == "NULL" or interfaces == "None": interfaces = "NULL";
	else: interfaces = "'" + interfaces + "'"


#	sql_net_upd = """UPDATE ipall_ip SET net_name='%s', description=%s, aggregated=%u, service_id=%s, allocated=%u WHERE id=%u """ \
#	    % (net_name, net_description, aggregated, net_type, allocated, id)
	#print "<br>", sql_net_upd
#	update = conn.update_data(sql_net_upd)
	
	### LOGGING    
#	sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_ip', "%s")""" % (current_user, sql_net_upd)
#        log = conn.update_data(sql_log)
	#print log

        if update != 0 and log != 0:
            print """<blockquote>"""
            print """<p class=TextPurpleBold>Network has been updated successfully!</p>"""
            print """<a href="%s#%s" class=linkPurpleBold> << back </a>""" % (uri, id)
            print """</blockquote>"""
        else:
            print """<blockquote>"""
            print """<p class=TextPurpleBold>An error has occured!</p>"""
            print """<a href="%s#%s" class=linkPurpleBold> << back </a>""" % (uri, id)
            print """</blockquote>"""

    else: ### SAVE key was not pressed
	referer = str(os.environ['HTTP_REFERER'])
	query = """SELECT is_vlan, is_group, is_device, path, vlan, name, interfaces, description FROM ipall_vlan WHERE id=%u """ % (id)
	details = conn.get_data(query)

	rights = user.get_rights() 

	if details == () or details == None:
	    print """<p class=TextPurpleBold> Nothing to display</p>"""
	    print """<a href="%s" class=LinkPurpleBold> << back </a>""" % referer
	    return
	else:
	    if group != 1:
		net_perm = conn.get_net_permissions(str(details[0][6]), group)
		if net_perm == () or net_perm == "":
		    net_perm = 0
		else:
		    net_perm = net_perm[1]
	    else:
		net_perm = 1
            #print net_perm

            if net_perm != 1:
                restriction_message()
                return

	    print """<blockquote>"""
	    print """<form name="edit_net" method=POST action="network_edit.cgi">"""
	    print """<input type=hidden name=uri value="%s">""" % referer
#	    print """<input type=hidden name=current_user value="%s">""" % current_user
	    print """<table width=550 border=0 cellspacing=0 cellpadding=0 class=TextPurple>"""
	    print """<tr>"""
	    print """<td colspan=2 class=TextPurpleBoldBig>Edit VLAN details<br>&nbsp;</td>"""
	    print """</tr>"""
	    print """<tr class=lightPurple3 height=20>"""
	    print """<td width=200px class=TextPurpleBold>VLAN</td>"""
	    print """<td class=TextPurpleBold>%s</td>""" % details[0][4]
	    print """</tr><tr>"""
	    print """<td colspan=2>"""

	    print_form(details)	

	    print """</td></tr>"""	
	    print """<tr>"""
	    print """<td colspan=2>* required field</td>"""
	    print """</tr><tr>"""
	    print """<td colspan=2>&nbsp;</td>"""
	    print """</tr><tr>"""
	    print """<td colspan=2><input type=submit name=save value=save class=button></td>"""
	    print """</tr>"""
	    print """<tr>"""
	    print """<td colspan=2 align=right>"""
	    print """<a href="%s#%s" class=LinkPurpleBold> << back </a>""" % (referer, id)
	    print """</td></tr>""" 
	    print """</table>"""
	    print """</form>"""
	    print """</blockquote>"""
	
    
    HTML.main_footer()


main()
