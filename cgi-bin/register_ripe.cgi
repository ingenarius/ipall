#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
"""

from Html_new import HtmlContent()
import DBmy
import IpallUser
from Sessionclass import Session
import Whois
import IPy
import os
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie


def main():
    """create an inetnum and optional also a route object of a subnet stored in IP@LL"""

    formdata = cgi.FieldStorage()
    back = inetnum = netname = descr = country = adminc = status = ""
    person = address1 = address2 = address3 = address4 = phone = nichdl = ""
    create_person = create_route_obj = "off"
    workflow = company = 0

    try:
        if formdata.has_key("inetnum"):
            inetnum = str(formdata['inetnum'].value).lower()
        if formdata.has_key("netname"):
            netname = str(formdata['netname'].value)
        if formdata.has_key("descr"):
            descr = str(formdata['descr'].value)
        if formdata.has_key("country"):
            country = str(formdata['country'].value)
        if formdata.has_key("adminc"):
            adminc = str(formdata['adminc'].value)
        if formdata.has_key("status"):
            status = str(formdata['status'].value)
        if formdata.has_key("create_person"):
            create_person = str(formdata['create_person'].value)
        if formdata.has_key("person"):
            person = str(formdata['person'].value)
        if formdata.has_key("address1"):
            address1 = str(formdata['address1'].value)
        if formdata.has_key("address2"):
            address2 = str(formdata['address2'].value)
        if formdata.has_key("address3"):
            address3 = str(formdata['address3'].value)
        if formdata.has_key("address4"):
            address4  = str(formdata['address4'].value)
        if formdata.has_key("phone"):
            phone = str(formdata['phone'].value)
        if formdata.has_key("nichdl"):
            nichdl = str(formdata['nichdl'].value)
        if formdata.has_key("back"):
            back = str(formdata['back'].value)
        if formdata.has_key("workflow"):
            workflow = int(formdata['workflow'].value)
        if formdata.has_key("company"):
            company = int(formdata['company'].value)
        if formdata.has_key("create_route_obj"):
            create_route_obj = str(formdata['create_route_obj'].value)
        if formdata.has_key("route"):
            route = str(formdata['route'].value)
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
    HTML.simple_header()

    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    else:
        HTML.popup_body()

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    if group == 0:
        HTML.restriction_message()
        return

    if not formdata.has_key("send"):
        HTML.restriction_message()
        return
    elif cfg['Server']['ripe_mail'] == "":
        HMTL.error_message("You didn't configure an email address for this function!")
        return 
    else:
        if inetnum == "": print """<script language="javascript">alert("Please insert inetnum"); history.back();</script> """; return;
        if netname == "": print """<script language="javascript">alert("Please insert netname"); history.back();</script> """; return;
        if descr == "": print """<script language="javascript">alert("Please insert descr"); history.back();</script> """; return;
        if country == "": print """<script language="javascript">alert("Please insert country"); history.back();</script> """; return;
        if adminc == "": print """<script language="javascript">alert("Please insert admin-c"); history.back();</script> """; return;
        if status == "": print """<script language="javascript">alert("Please insert status"); history.back();</script> """; return;
        if create_person == "on":
            if person == "": print """<script language="javascript">alert("Please insert person"); history.back();</script> """; return;
            if address1 == "": print """<script language="javascript">alert("Please insert address1"); history.back();</script> """; return;
            if address2 == "": print """<script language="javascript">alert("Please insert address2"); history.back();</script> """; return;
            if address3 == "": print """<script language="javascript">alert("Please insert address3"); history.back();</script> """; return;
            if address4 == "": print """<script language="javascript">alert("Please insert address4"); history.back();</script> """; return;
            if phone == "": print """<script language="javascript">alert("Please insert phone"); history.back();</script> """; return;
            if nichdl == "": print """<script language="javascript">alert("Please insert nic-hdl"); history.back();</script> """; return;
        today = user.get_today()
        mail = user.get_mail_address()
        sql_ripe_details = """SELECT ripe_header, ripe_trailer, ripe_password, ripe_mntby, ripe_admin_c, ripe_tech_c, ripe_notify, as_nr 
            FROM companies WHERE id=%u """ % company
        ripe_details = conn.get_data(sql_ripe_details)
        if ripe_details == () or ripe_details == None:
            HTML.error_message("No Ripe details found!")
            return
        else:
            ripe_header = ripe_details[0][0]
            ripe_trailer = ripe_details[0][1]
            ripe_password = ripe_details[0][2]
            ripe_mntby = ripe_details[0][3]
            ripe_admin_c = ripe_details[0][4]
            ripe_tech_c = ripe_details[0][5]
            ripe_notify = ripe_details[0][6]
            as_nr = ripe_details[0][7]

        w = Whois.whois()
##        create_person, password, inetnum, netname, descr, country, adminc, techc, status, notify, mntby, \
##        person, address1, address2, address3, address4, phone, nichdl, mail, today, create_route_obj, route, as_nr
        body = w.create_mail(create_person, ripe_password, inetnum, netname, descr, country, adminc, ripe_tech_c, status, ripe_notify, ripe_mntby, \
            person, address1, address2, address3, address4, phone, nichdl, mail, today, create_route_obj, route, as_nr)
        #print body

        sent = w.send_mail(mail, cfg['Server']['ripe_mail'], "IP@LL auto register: " + inetnum, body)
        if sent != 0 and workflow == 0:
            msg = """Mail to "%s" was sent successfully""" % cfg['Server']['ripe_mail']
            HTML.notify_message(msg)
        elif sent != 0 and workflow == 1:
            msg = """Mail to "%s" was sent successfully""" % cfg['Server']['ripe_mail']
            HTML.notify_message(msg)
        else:
            msg = """Mail was <b>not</b> sent!"""
            HTML.notify_message(msg)

    HTML.main_footer()

main()
