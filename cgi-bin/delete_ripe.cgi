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
import Whois
import os
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie


def main():
    """description"""

    formdata = cgi.FieldStorage()
    id = companies_id = 0
    body = back = ""

    try:
        if formdata.has_key("id"):
            id = int(formdata['id'].value)
        if formdata.has_key("companies_id"):
            companies_id = int(formdata['companies_id'].value)
        if formdata.has_key("body"):
            body = str(formdata['body'].value)
        if formdata.has_key("back"):
            back = str(formdata['back'].value)
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

    HTML = HtmlContent()

    ### User
    s = Session(conn)
    current_user = s.check_user()
    #company = s.check_cookie()
    HTML.simple_header()

    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    else:
        HTML.popup_body()

    user = IpallUser.User(current_user)
    group = user.get_group_id()
    if group == 0:
        HTML.restriction_message()
        return

    if not formdata.has_key("send"):
        HTML.restriction_message()
        return
    else:
        if id == "" or id == 0: HTML.error_message("No network found<br>");
        if body == "" or body == None: HTML.error_message("No network found<br>");
        today = user.get_today()
        mail = user.get_mail_address()

#        ### delete objects of ripe db
#        body = ""
        sql_ripe = """SELECT ripe_password FROM companies WHERE id=%u""" % ( companies_id )
        ripe = conn.get_data(sql_ripe)
        if ripe != ():
            ripe_pw = "password:       %s\n" % (ripe[0][0])
        else:
            HTML.error_message("No RIPE password found! Mail not sent!", "javascript:this.close();")
            return
        w = Whois.whois()
#        body = body + "delete:          IP@LL auto delete\n"
        sent = w.send_mail(mail, cfg['Server']['ripe_mail'], "IP@LL auto delete", ripe_pw + body)
        ### 

        if sent != 0:
            msg = """<p>Mail to "%s" was sent successfully</p>""" % cfg['Server']['ripe_mail']
            HTML.notify_message(msg)
            print """<div id=message><a href="javascript:void(0);" onClick="parent.location.reload(1);" class="LinkPurpleBold">close and refresh</a></div>"""
        else:
            HTML.error_message("<p>Mail was not sent</p>")


    HTML.close_body()

main()
