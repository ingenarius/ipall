#!/usr/bin/python
"""
*****************************
IP@LL IP addressmanagement
Copyright 2009 Andreas Poiss
andreas@poiss.priv.at
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


def restriction_message():
    """print a restriction message"""

    print """<blockquote>"""
    print """<p class=textPurpleBold>You are not allowed to execute this</p>"""
    print """<a href="javascript:history.back();" class=linkPurpleBold> << back</a>"""
    print """</blockquote>"""


def main():
    """description"""

    #global 
    #formdata = cgi.FieldStorage()
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


#    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
#       qs = os.environ['QUERY_STRING']
#       if len(qs.split("&")) == 1:
#           view = int(qs[0:])
#           path = "0"
#       elif len(qs.split("&")) == 2:
#           view = int(qs.split("&")[0])
#           path = str(qs.split("&")[1])
#       else:
#           view = 1
#           path = "0"
#    else:
#       view = 1
#       path = "0"


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
    #rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    if group == 0:
        restriction_message()
        return

    if group != 1: # user is not member of group "admins"
        net_perm = conn.get_net_permissions(str(details[0][4]), group)
        if net_perm == () or net_perm == "":
            net_perm = 0
        else:
            net_perm = net_perm[3]
    else: # user is member of group "admins"
        net_perm = 1


    if net_perm != 1:
        restriction_message()
        return
    ### logged in user does have enough rights to 
    else:
        print """<br>"""
        print """<blockquote>"""
        print """<table width=550 border=0 cellspacing=5 cellpadding=0 class=TextPurple>"""
        print """<tr>"""
        print """<td>"""


        #print_newnet_form()

        print """</td>"""
	print """</tr>"""
        print """<tr><td>&nbsp;</td></tr>"""
        print """<tr><td align=right><a href="javascript:history.back();" class=LinkPurpleBold> << back </a></td></tr>"""
        print """</table>"""
        print """</blockquote>"""
	

    HTML.main_footer()

main()
