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



def print_interfaces(interfaces):
    """print out a list of interfaces with (documented) connected customers"""

    for i in interfaces:
        print """<tr>"""
        print """<td valign=top style="border-bottom: 1px dotted #C0C0C0">%s</td>""" % i
        print """<td style="border-bottom: 1px dotted #C0C0C0">"""

        sql_netname = """SELECT DISTINCT net_name FROM ipall_ip WHERE interface_name LIKE '%s' """ % str(i)
        netname = conn.get_data(sql_netname)
        if netname == ():
            print """&nbsp;"""
            continue
        else:
#       for n in netname:
            print """%s<br>""" % (netname[0][0])
#           print """%s - %s<br>""" % (n[0], n[1])
        print """</td>"""
        print """</tr>"""


def main():
    """description"""

    global conn
    formdata = cgi.FieldStorage()
    #network = netname = description = ""

    try:
        if formdata.has_key("username"):
            username = str(formdata['username'].value).lower()
        if formdata.has_key("passwd"):
            passwd = str(formdata['passwd'].value)
    except ValueError, e:
        print "Error: %s" % e
        print """<script language="javascript">alert("Value parse error, sorry!"); history.back();</script> """
        return

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
        HTML.simple_redirect_header("/")
        return
    else:
        HTML.simple_header()
    user = IpallUser.User(current_user)
    group = user.get_group_id()

    if group == 0: ### user is not logged in
        HTML.restriction_message()
        return
    else: ### user is logged in
	### create list of all cannalized STM-1 interfaces
	r4_interfaces = r5_interfaces = channy1s = channy2s = channy3s = ()
	p_channy1 = "Serial4/0/0.1/"
	p_channy2 = "Serial4/1/0.1/"
	p_channy3 = "Serial3/0.1/"
	tug3 = ("1/", "2/", "3/")
	tug2 = ("1/", "2/", "3/", "4/", "5/", "6/", "7/",)
	intf = ("1", "2", "3")
	suffix = ":0"
	for r in range(0,3):	    
	    for s in range(0,7):
		for t in range(0,3):
		    channy1s = channy1s.__add__((p_channy1 + tug3[r] + tug2[s] + intf[t] + suffix,) )
		    channy2s = channy2s.__add__((p_channy2 + tug3[r] + tug2[s] + intf[t] + suffix,) )
	r4_interfaces = r4_interfaces.__add__(channy1s)
	r4_interfaces = r4_interfaces.__add__(channy2s)

        for r in range(0,3):    
            for s in range(0,7):
                for t in range(0,3):
		    channy3s = channy3s.__add__((p_channy3 + tug3[r] + tug2[s] + intf[t] + suffix,) )
	r5_interfaces = r5_interfaces.__add__(channy3s)

        print """<br>"""
        print """<blockquote>"""
        print """<table width=550 border=0 cellspacing=5 cellpadding=0 class=TextPurple>"""
        print """<tr>"""
        print """<td colspan=2 class=TextPurpleBold>Interface listing for customer networks</td>"""
	print """</tr>"""
        print """<tr>"""
        print """<td colspan=2>Please copy and paste the interface name you want to use</td>"""
	print """</tr>"""
        print """<tr><td colspan=2>&nbsp;</td></tr>"""
        print """<tr><td colspan=2 class=TextPurpleBold>r4-hayd1-vie</td></tr>"""

	print_interfaces(r4_interfaces)

        print """<tr><td colspan=2>&nbsp;</td></tr>"""
        print """<tr><td colspan=2 class=TextPurpleBold>r5-hayd1-vie</td></tr>"""

	print_interfaces(r5_interfaces)

#	for i in r4_interfaces:
#	    print """<tr>"""
#	    print """<td valign=top style="border-bottom: 1px dotted #C0C0C0">%s</td>""" % i
#	    print """<td style="border-bottom: 1px dotted #C0C0C0">"""
#
#	    sql_netname = """SELECT DISTINCT net_name FROM ipall_ip WHERE interface_name LIKE '%s' """ % str(i)
#	    netname = conn.get_data(sql_netname)
#	    if netname == ():
#		print """&nbsp;"""
#		continue
#	    else:
#	    for n in netname:
#		print """%s<br>""" % (netname[0][0])
#		print """%s - %s<br>""" % (n[0], n[1])
#	    print """</td>"""
#	    print """</tr>"""

#        print """</td>"""
#	print """</tr>"""
        print """<tr><td colspan=2>&nbsp;</td></tr>"""
        print """<tr><td colspan=2 align=right><a href="javascript:history.back();" class=LinkPurpleBold> << back </a></td></tr>"""
        print """</table>"""
        print """</blockquote>"""
	

    HTML.main_footer()

main()
