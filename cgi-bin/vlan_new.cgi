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
import IPy
import os
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie


def print_new_form():
    """print a HTML form for inserting a new network"""

    print """<form name="new_vlan" method=POST action="vlan_new.cgi">"""

    print """<input type=hidden name=uri value="%s">""" % referer
    #print """</tr><tr>"""

    print """<td>New VLAN number *</td>"""
    print """</tr><tr>"""
    print """<td><input type=text name=vlan size=33 class=b_eingabefeld></td>"""
    print """</tr><tr>"""

    print """<td>VLAN name *</td>"""
    print """</tr><tr>"""
    print """<td><input type=text name=vlanname size=33 class=b_eingabefeld maxlength=30></td>"""
    print """</tr><tr>"""

    print """<td>Description</td>"""
    print """</tr><tr>"""
    print """<td><textarea name=description cols=40 rows=6 class=b_eingabefeld></textarea>"""
    print """</tr><tr>"""

    print """<td>&nbsp;</td>"""
    print """</tr><tr>"""
    print """<td><input type=submit name=save value=save class=button></td>"""
    print """</tr>"""



def main():
    """create a new superblock"""

    global vrf, referer, conn, cgi_dir
    formdata = cgi.FieldStorage()
    vlan = vlanname = description = "NULL"

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
    if group == 0:
	print """<blockquote>"""
	print """<p class=TextPurpleBold> You do not have enough rights to see this! </p>"""
	#print """<a href="javascript:history.back();" class=LinkPurpleBold> << back </a>"""
	print """<a href="%s/networks.cgi?%s" class=linkPurpleBold> << back </a>""" % (cgi_dir, str(vrf))
	print """</blockquote>"""
        return

    ### logged in user does have enough rights to 
    else:
	try:
	    if formdata.has_key("uri"):
		uri = str(formdata['uri'].value)
	    if formdata.has_key("vlan"):
		vlan = str(formdata['vlan'].value)
	    if formdata.has_key("vlanname"):
		vlanname = str(formdata['vlanname'].value)
	    if formdata.has_key("description"):
		description = str(formdata['description'].value)
	except:
	    print """<script language="javascript">alert("You should insert a network address"); history.back();</script> """
	
	rights = user.get_rights()
	if group != 1 and rights[0] != 1: 
	    print """<blockquote>"""
	    #print group
	    print """<p class=TextPurpleBold> You do not have enough rights to see this! </p>"""
	    #print """<a href="javascript:history.back();" class=LinkPurpleBold> << back </a>"""
	    print """<a href="%s/networks.cgi?%s" class=linkPurpleBold> << back </a>""" % (cgi_dir, str(vrf))
	    print """</blockquote>"""
	    return

	### SAVE button has been pressed
	if formdata.has_key("save"):
	    print "<br>"
            if vlan == "NULL" or vlan == None: print """<script language="javascript">alert("Please insert a VLAN"); history.back();</script> """; return;
            elif not re.search("^[0-9]{3,5}", vlan):
                print """<script language="javascript">alert("Please insert only digit characters for VLANs"); history.back();</script> """; return;
            else: vlan = int(vlan);
            if vlanname.find("'") != -1 or description.find("'") != -1:
                print """<script language="javascript">alert("You must not insert an apostrophe"); history.back();</script> """; return;
	    if vlanname == "NULL" or vlanname == None: print """<script language="javascript">alert("Please insert VLAN name"); history.back();</script> """; return;
	    ### a description has been typed
	    if description == "NULL" or description == "None": description = "NULL"
	    else: description = "'" + description + "'"

	    sql_insert = """INSERT INTO `ipall_vlan` ( `id` , `parent_id` , `path` , `is_vlan` , `is_group` , `is_device` , `vlan` , `name` , `has_childs` , `interfaces` , `comment` ) VALUES ('', '0', '%s', 1, 0, 0, %u, '%s', 0, NULL , NULL )""" \
		% ('', int(vlan), vlanname)

	    #print sql_insert + "<br>"
	    last_id = conn.insert_data(sql_insert)

	    ### LOGGING
            id_link = """<a href='%s/vlan_view.cgi?%s' class=LinkPurpleBold>id: %s</a> - """ % (cgi_dir, str(last_id), str(last_id))
            log_string = id_link + sql_insert
	    sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_vlan', "%s")""" % (current_user, log_string)
	    log = conn.insert_data(sql_log)
	    
	    #print str(check_ins) + "<br>"
	    if last_id != 0:
	        path = "0:" + str(last_id)
	        #print "path: %s<br>" % path
	    
	        ### set the path field correctly
	        sql_update = """UPDATE ipall_vlan SET path='%s' WHERE id=%u """ % (str(path), int(last_id))
	        print sql_update + "<br>"
	        update = conn.update_data(sql_update)
	        #print "update: %u" % update

#		if group != 1:
#		    sql_ins_rights = """INSERT INTO ipall_rights VALUES(%u, '%s', 1, 1, 1, 1)""" % (group, str(path))
#		    update = conn.update_data(sql_ins_rights)

	        #update = conn.update_path(path, last_id)
	        #print "update: %u" % update
	        if update != 0:
		    print """<blockquote>"""
		    print """<p class=TextPurpleBold>VLAN has been added successfully!</p>"""
		    print """<a href="%s/vlans.cgi" class=linkPurpleBold> << back </a>""" % cgi_dir
		else:
		    print """<blockquote>"""
		    print """<p class=TextPurpleBold>An error during "update path" has occured!</p>"""
		    print """<a href="%s/vlans.cgi" class=linkPurpleBold> << back </a>""" % cgi_dir
	    else:   ### check_ins = 0
		print """<blockquote>"""
		print """<p class=TextPurpleBold>An error during "insert VLAN" has occured!</p>"""
		print """<a href="%s" class=linkPurpleBold> << back </a>""" % uri

	### SAVE button has not been pressed
	else:	
	    referer = str(os.environ['HTTP_REFERER'])
	    print """<br>"""
	    print """<blockquote>"""
	    print """<table width=550 border=0 cellspacing=5 cellpadding=0 class=TextPurple><tr height=20>"""
	    print """<td class=TextPurpleBoldBig>Insert a new VLAN</td>""" 
	    print """</tr><tr height=20>"""
	
	    print_new_form()

	    print """<tr><td>&nbsp;</td>"""
	    print """</tr><tr>"""
            print """<td>* required field</td>"""
            print """</tr>"""
	    print """<tr><td align=right><a href="%s" class=LinkPurpleBold> << back </a></td></tr>""" % referer
	    print """</table>"""
	
    HTML.main_footer()

main()
