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
    global conn

    ### create database connection object
    cfg = ConfigObj("ipall.cfg")
    db_host = cfg['Database']['db_host']
    db_user = cfg['Database']['db_user']
    db_pw = cfg['Database']['db_pw']
    db = cfg['Database']['db']
    conn = DBmy.db(db_host, db_user, db_pw, db)

    HTML = HtmlContent()

    s = Session(conn)
    current_user = s.check_user()
    #company = s.check_cookie()
    HTML.simple_header()
    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    else:
        HTML.body()

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']
    # smoothbox parameters
    sbox = cfg['Site']['smoothbox']

    if group == 0:
        HTML.restriction_message()
        return

    print """<p>""" # header
    print """<div id="divHead800">""" 
    print """<div class="TextPurpleBold" style="width: 100%; text-align: center;"><br>IP@LL Management</div>"""
    print """</div>"""
    print """</p>""" # header

    print """<p>""" # main text

    ### super user
    if group == 1 or rights[2] == 1:
        print """<div><span width=20px align=right> -</span>
            <span><a href="%s/report_ip.cgi%s" class="smoothbox">Doubled IP Report</a></span></div>""" % (cgi_dir, sbox)

        print """<div><span width=20px align=right> -</span>
            <span><a href="%s/mgmt_company.cgi%s" class="smoothbox">Companies</a></span></div>""" % (cgi_dir, sbox)
    ### user admin
    if group == 1 or rights[1] == 1:
        print """<div><span width=20px align=right> -</span>
            <span><a href="%s/mgmt_user.cgi%s" class="smoothbox">Users</a></span></div>""" % (cgi_dir, sbox)
        print """<div><span width=20px align=right> -</span>
            <span><a href="%s/mgmt_group.cgi%s" class="smoothbox">Groups</a></span></div>""" % (cgi_dir, sbox)
    ### company admin
    if group == 1 or rights[2] == 1:
        print """<div><span width=20px align=right> -</span>
            <span><a href="%s/mgmt_vrf.cgi%s" class="smoothbox">View/VRF group rights</a></span></div>""" % (cgi_dir, sbox)
        print """<div><span width=20px align=right> -</span>
            <span><a href="%s/mgmt_nettypes.cgi%s" class="smoothbox">Network types</a></span></div>""" % (cgi_dir, sbox)
    ### user admin or company admin
    if group == 1 or rights[1] == 1 or rights[2] == 1:
        print """<div><span width=20px align=right> -</span>
            <span><a href="%s/log_viewer.cgi%s" class="smoothbox">Logging</a></span></div>""" % (cgi_dir, sbox)
    ### no admin
    if group != 1 and rights[1] != 1 and rights[2] != 1:
        print """<div><span width=20px align=right> -</span>
            <span><a href="%s/mgmt_user.cgi%s" class="smoothbox">Users</a></span></div>""" % (cgi_dir, sbox)


    print """</p>""" # main text
#    print """<br><br>"""
    print """<p>""" # bottom
    print """<div style="margin-left: 25px;" class=TextPurple>"""
    print """If you find a bug in this software, please report this to 
        <a href="mailto:andi@poiss.priv.at?subject=IP@LL%20bug%20report" class=linkPurpleBold>Me</a>. Thank you!"""
    print """</div>"""
    print """</p>""" # bottom

    HTML.main_footer()

main()
