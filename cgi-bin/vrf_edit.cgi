#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 racyAPz
http://www.racyapz.at
*****************************
"""

from Html_new import HtmlContent
import DBmy
import IpallUser
from Sessionclass import Session
import os
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie



def print_vrf_form(details):
    """print html form to edit network details"""

    print """<div id="vrf_edit">"""
    print """<input type=hidden name=company value="%s">""" % company
    
    ### LEFT SIDE
    print """<div id="pos_left_small">"""
    print """<div class="lineOdd">View ID / VRF RD</div>"""
    print """<div class="lineEven">View/VRF Name (displayed) *</div>"""
    print """<div class="lineOdd">View/VRF Name (configured) *</div>"""
    print """<div class="lineEven">Network description</div>"""
    print """</div>""" # left side

    ### RIGHT SIDE
    print """<div id="pos_right_wide">"""
    print """<div class="lineOdd"><input type=text id="rd" name=rd class=b_eingabefeld value="%s" maxlength=35 readonly></div>""" % str(rd)
    ### vrf name
    print """<div class="lineEven"><input type=text id="name" name=name class=b_eingabefeld value="%s" maxlength=35></div>""" % details[0][0]
    ### vrf name configured
    print """<div class="lineOdd"><input type=text id="vrf_name" name=vrf_name class=b_eingabefeld value="%s" maxlength=35></div>""" % details[0][2]
    ### vrf description
    print """<div class="lineEven"><textarea id="vrf_description" name=vrf_description class=b_eingabefeld>%s</textarea></div>""" % details[0][1]
    print """</div>""" # right side

    print """<div id="pos_clear"><input type=submit id="save" name=save value=save class=button></div>"""


def main():
    """entry point for executing IP@LL - edit vrf details"""

    ### definitions of variables
    global rd, company, conn, group, cgi_dir
    vrf_description = "NULL"
    formdata = cgi.FieldStorage()

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        #if len(qs.split("&")) == 2:
        try:
            rd = str(qs.split("&")[0])
            company = int(qs.split("&")[1])
        except:
        #else:
            rd = company = 0

    try:
        ### network info
        if formdata.has_key("company"):
            company = int(formdata['company'].value)
        if formdata.has_key("rd"):
            rd = str(formdata['rd'].value)
        if formdata.has_key("name"):
            name = str(formdata['name'].value)
        if formdata.has_key("vrf_name"):
            vrf_name = str(formdata['vrf_name'].value)
        if formdata.has_key("vrf_description"):
            vrf_description = str(formdata['vrf_description'].value)
    except ValueError, e:
        #print "Error: %s" % e
        print """<script language="javascript">alert("Value parse error!"); history.back();</script> """
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
        #HTML.body()

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights(rd)
    cgi_dir = cfg['Server']['cgi_dir']

    if group == 0:
        HTML.restriction_message()
        return

    if formdata.has_key("save"):
        if vrf_description == "NULL" or vrf_description == "None": vrf_description = "NULL";
        else: vrf_description = "'" + vrf_description + "'"

        sql_check = """SELECT networks_id FROM networks WHERE
            companies_id=%u AND vpn_rd!='%s' AND (name LIKE '%s%s%s' OR vpn_vrf_name LIKE '%s%s%s') """ \
            % ( company, str(rd), "%", str(name), "%", "%", (vrf_name), "%" )
        check = conn.get_data(sql_check)
        if check != ():
            print """<script language="javascript">alert('View/VRF already exists!'); history.back();</script> """
            return
        
        sql_vrf_upd = """UPDATE networks SET name='%s', description=%s, vpn_vrf_name='%s' WHERE vpn_rd='%s' """ \
            % (name, vrf_description, vrf_name, rd)
        #print "<br>", sql_vrf_upd
        update = conn.update_data(sql_vrf_upd)
        
        ### LOGGING
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'networks', "%s", %u)""" % (current_user, sql_vrf_upd, company)
        log = conn.update_data(sql_log)
        #print log

        print """<div id="main">"""
        print """<div id="table_main">"""

        ### HEADING
        print """<div id="functionHead">Edit VRF/View</div>""" 

        if update != 0 and log != 0:
            HTML.notify_message("changes applied...")
        else:
            HTML.error_message("An error has occured!")
            return
 
        print """</div>""" #table_main
        print """</div>""" #main
    
           
    else: ### SAVE key was not pressed
        query = """SELECT name, description, vpn_vrf_name FROM networks WHERE vpn_rd='%s' AND companies_id=%u """ % (rd, company)
        details = conn.get_data(query)

        #rights = user.get_rights(rd) 

        if details == () or details == None:
            HTML.error_message("Nothing to display!")
            return
        else:
            if group != 1 and rights[2] != 1:
                net_perm = conn.get_vrf_permissions(str(rd), group)
                if vrf_perm == () or vrf_perm == "":
                    net_perm = 0
                else:
                    vrf_perm = vrf_perm[0]
            else:
                net_perm = 1
                #print net_perm

            if net_perm != 1:
                HTML.restriction_message()
                return

            print """<form name="edit_vrf" method=POST action="vrf_edit.cgi"
                onSubmit="return check_vrf(%s)">""" % ( rd )
            print """<div id="main">"""
            print """<div id="table_main">"""

            ### HEADING
            print """<div id="functionHead">Edit VRF/View <i>"%s"</i></div>""" % details[0][0]

            print_vrf_form(details)	

            print """</div>""" # main
            print """</div>""" # table_main


    HTML.main_footer()

main()
