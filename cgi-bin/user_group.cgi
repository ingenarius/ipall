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
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie



def print_usergroup_form(sel_group):
    """print html form for setting users group membership"""

    print """<form name="group_membership" method=POST action="user_group.cgi">"""
    print """<input type=hidden name=group_id value=%u>""" % sel_group

    print """<table width=100% border=0 class=TextPurple>"""

    ### GROUP dropdown box
    print """<tr>"""
    print """<td colspan=3 align=center>"""
    print """<select name=group ONCHANGE="location = this.options[this.selectedIndex].value;" class=b_eingabefeld>"""
    groups = get_groups()
    if sel_group == 0:
        print """<option value="%s/user_group.cgi?%s">no group</option>""" % (cgi_dir, "0")
    else:
        group = get_sel_group(sel_group)
        print """<option value="%s/user_group.cgi?%s">%s</option>""" % (cgi_dir, sel_group, group[0])
        print """<option value="%s/user_group.cgi?%s">select group</option>""" % (cgi_dir, "0")
    for g in groups:
        if g[0] != sel_group:
            print """<option value="%s/user_group.cgi?%s">%s</option>""" % (cgi_dir, str(g[0]), str(g[1]))
    print """</select>"""
    print """</td>"""
    print """</tr>"""

    print """<tr><td colspan=3>&nbsp;</td></tr>"""
    print """<tr class=TextPurpleBold><td>no members</td><td>&nbsp;</td><td>members</td></tr>"""
    print """<tr>"""

    ### non members list box
    print """<td width=200px>"""
    print """<select name=non_member size=15 class=b_eingabefeld>"""
    non_members = get_non_members(sel_group)
    if non_members != () and non_members != 0:
        for n in non_members:
            print """<option value="%s">%s (%s %s)</option>""" % (str(n[0]), str(n[0]), str(n[1]), str(n[2]))
    else:
        print """<option value="">no users</option>"""
    print """<option value="">&nbsp;</option>"""
    print """</select>"""
    print """</td>"""

    ### add button
    print """<td valign=middle align=center>"""
    print """<input type=submit name=add value=">>" class=button title="add user to selected group">"""
    print """<br><br><input type=submit name=delete value="delete" class=button title="delete user from IP@LL">"""
    print """</td>"""

    ### members list box
    print """<td width=200px>"""
    print """<select name=member size=15 class=b_eingabefeld>"""
    if sel_group == 0:
        print """<option value="">no group selected</option>"""
    else:
        members = get_members(sel_group)
        if members != () and members != 0:
            for n in members:
                print """<option value="%s">%s (%s %s)</option>""" % (str(n[0]), str(n[0]), str(n[1]), str(n[2]))
        else:
            print """<option value="">no members</option>"""
    print """<option value="">&nbsp;</option>"""
    print """</select>"""
    print """</td>"""

    print """</tr>"""
    print """</table>"""
    print """</form>"""


def get_non_members(sel_group):
    """fetches all groups and makes a dropdown box"""

    sql_non_members = """SELECT DISTINCT(p.username), p.surname, p.lastname FROM 
        persons p, persons_rights r, persons_rights_groups g, ipall_user_group i WHERE 
        ((p.persons_id=r.persons_id AND r.persons_rights_ip_all=1) OR
        (p.persons_id=r.persons_id AND r.persons_rights_group_id=g.persons_rights_groups_id AND g.persons_rights_ip_all=1)) AND
        (p.username = i.username AND i.group_id != %s)
        ORDER BY p.username""" % sel_group
    non_members = conn.get_data(sql_non_members)

    return non_members


def get_members(sel_group):
    """fetches all groups and makes a dropdown box"""

    sql_members = """SELECT DISTINCT(p.username), p.surname, p.lastname FROM
        persons p, ipall_user_group i WHERE
        (p.username=i.username AND i.group_id = %s)
        ORDER BY p.username""" % sel_group
    members = conn.get_data(sql_members)

    return members


def get_groups():
    """fetches all groups and makes a dropdown box"""

    sql_groups = """SELECT id, groupname FROM ipall_group ORDER BY groupname"""
    groups = conn.get_data(sql_groups)

    return groups
 

def get_sel_group(sel_group):
    """fetch the selected group info"""
    
    sql_group = """SELECT groupname FROM ipall_group WHERE id=%u""" % sel_group
    group = conn.get_data(sql_group)

    return group[0]


def main():
    """description"""

    global conn, cgi_dir
    formdata = cgi.FieldStorage()
    group_id = 0
    member = non_member = username = ""

    try:
        if formdata.has_key("group_id"):
            group_id = int(formdata['group_id'].value)
        if formdata.has_key("member"):
            member = str(formdata['member'].value).lower()
        if formdata.has_key("non_member"):
            non_member = str(formdata['non_member'].value).lower()
    except ValueError, e:
        print "Error: %s" % e
        print """<script language="javascript">alert("Value parse error, sorry!"); history.back();</script> """
        return


    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
       qs = os.environ['QUERY_STRING']
       if len(qs.split("&")) == 1:
           group_id = int(qs[0:])
           #username = ""
#       elif len(qs.split("&")) == 2:
#           group_id = int(qs.split("&")[0])
#           username = str(qs.split("&")[1])
       else:
           group_id = 0
#           username = ""
    else:
       group_id = group_id
#       username = ""


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
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    if group == 0:
        HTML.restriction_message()
        return

    if rights[1] != 1: # user does not have the permission to edit other users
        HTML.restriction_message()
        return
    else:   ### logged in user does have enough rights to 
        print """<br>"""
        print """<blockquote>"""
        print """<table width=550 border=0 cellspacing=5 cellpadding=0 class=TextPurple>"""
	print """<tr class=lightPurple3>"""
	print """<td class=TextPurpleBoldBig>Change group membership of IP@LL users</td>"""
	print """</tr>"""
	print """<tr><td>&nbsp;</td></tr>"""
        print """<tr>"""
        print """<td>"""

	if formdata.has_key("add"):
	    if non_member == 0 or non_member == "": print """<script language="javascript">alert("Please choose a 'no member' user"); history.back();</script> """; return
	    if member != "": print """<script language="javascript">alert("Please do not choose a 'member' user"); history.back();</script> """; return
	    sql_check_user = """SELECT group_id FROM ipall_user_group WHERE username='%s' """ % non_member
	    user = conn.get_data(sql_check_user)
	    if user == ():
		sql_add_user = """INSERT ipall_user_group SET username='%s', group_id=%s""" % (non_member, str(group_id))
	    else:
		sql_add_user = """UPDATE ipall_user_group SET group_id=%s WHERE username='%s' """ % (str(group_id), non_member)
	    #print sql_add_user, "<br>"
	    upd = conn.update_data(sql_add_user)

	if formdata.has_key("delete"):
	    if member == 0 or member == "": print """<script language="javascript">alert("Please choose a 'member' user"); history.back();</script> """; return
	    if non_member != "": print """<script language="javascript">alert("Please do not choose a 'no member' user"); history.back();</script> """; return
	    sql_del_user = """DELETE FROM ipall_user_group WHERE username='%s' """ % (member)
	    #print sql_del_user, "<br>"
	    upd = conn.update_data(sql_del_user)

        print_usergroup_form(group_id)

        print """</td>"""
	print """</tr>"""
        print """<tr><td>&nbsp;</td></tr>"""
	print """<tr><td align=right><a href="%s/users.html" class=LinkPurpleBold> << back </a></td></tr>""" % cfg['Server']['ipall_dir']
        print """</table>"""
        print """</blockquote>"""
	

    HTML.main_footer()

main()
