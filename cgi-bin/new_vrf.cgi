#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
andi@poiss.priv.at
*****************************
"""

from Html_new import HtmlContent
import DBmy
import IpallUser
from Sessionclass import Session
import IPy
import os
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj


def print_newnet_form(group, company, as_nr):
    """print a HTML form for inserting a new vrf"""

    print """<form name="new_vrf" method=POST action="new_vrf.cgi"
        onSubmit="return check_vrf(%s)">""" % ( as_nr )

    print """<div id="new_vrf">"""
    print """<input type=hidden id="company" name=company value="%s">""" % ( company )

    print """<p>VRF Name (displayed) *<br>"""
    print """<input type=text id="name" name=name size=33 class=b_eingabefeld></p>"""

    print """VRF Name (configured) *<br>"""
    print """<input type=text id="vrf_name" name=vrf_name size=33 class=b_eingabefeld></p>"""

    print """<p>Route Distiguisher *<br>"""
    if group == 1:
        print """<input type=text id="rd" name=rd size=33 class=b_eingabefeld maxlength=30
            onFocus="ajaxFunction('%s/a_as_number.cgi?'+document.getElementById('company').value, 'rd', '5');"></p>""" % ( cgi_dir )
    else:
        print """<input type=text id="rd" name=rd size=33 class=b_eingabefeld maxlength=30
            onFocus="ajaxFunction('%s/a_as_number.cgi?%s', 'rd', '5');"></p>""" % ( cgi_dir, str(company_id) )

    print """<p>Description<br>"""
    print """<textarea id="description" name=description cols=40 rows=6 class=b_eingabefeld></textarea></p>"""

    print """<p><input type=submit name=save value=save class=button></p>"""
    print """</div>""" # new_vrf



def main():
    """create a new view/vrf"""

    global company_id, vrf, conn, cgi_dir
    formdata = cgi.FieldStorage()
    name = vrf_name = vrf = description = rd = "NULL"
    company = 0

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
        print ""
        #HTML.body()

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    cgi_dir = cfg['Server']['cgi_dir']
    if group == 0:
        HTML.restriction_message()
        return
    ### logged in user does have enough rights to 
    else:
        try:
            if formdata.has_key("uri"):
                uri = str(formdata['uri'].value)
            if formdata.has_key("name"):
                name = str(formdata['name'].value)
            if formdata.has_key("vrf_name"):
                vrf_name = str(formdata['vrf_name'].value)
            if formdata.has_key("rd"):
                rd = str(formdata['rd'].value)
            if formdata.has_key("description"):
                description = str(formdata['description'].value)
            if formdata.has_key("company"):
                company = int(formdata['company'].value)
        except:
            print """<script language="javascript">alert("value parse error!"); history.back();</script> """

    rights = user.get_rights(vrf)

    if group == 0 or rights[2] == 0:
        HTML.restriction_message()
        return
    else:
        if group == 1:
            if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
                qs = os.environ['QUERY_STRING']
                try:
                    company = int(qs.split("&")[0])
                except:
                    company = 0
        else:
            company = company_id

    ### SAVE button has been pressed
    if formdata.has_key("save"):
        print "<br>"

        ### a description has been typed
        if description == "NULL" or description == "None": description = "NULL"
        else: description = "'" + description + "'"
        if group != 1 and company == 0:
            company = company_id

        sql_check = """SELECT networks_id FROM networks WHERE
            companies_id=%u AND (vpn_rd='%s' OR name LIKE '%s%s%s' OR vpn_vrf_name LIKE '%s%s%s') """ \
            % ( company, str(rd), "%", str(name), "%", "%", (vrf_name), "%" )
        check = conn.get_data(sql_check)
        
        if check != ():
            HTML.error_message("VRF/View already exists!")
            return
        else:
            sql_insert = """INSERT INTO `networks` ( `networks_id` , `name` , `description` , `companies_id` , `vpn_vrf_name` , `vpn_rd`) 
                VALUES ('', '%s', %s, %u , '%s', '%s')""" \
                % (name, description, int(company), vrf_name, rd)
            last_id = conn.insert_data(sql_insert)

        ### LOGGING
        log_string = sql_insert
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'networks', "%s", %u)""" % (current_user, log_string, company)
        log = conn.insert_data(sql_log)
        
        if last_id != 0:
            #uri = "%s/index.cgi" % (cgi_dir)
            #HTML.redirect(uri)
            HTML.notify_message("View/VRF created successfully!")
            print """<div id=message><a href="javascript:void(0);" onClick="parent.location.reload(1);" class="LinkPurpleBold">close and refresh</a></div>"""
            return
        else:
            HTML.error_message("An error has occured!")
            return
        
    ### SAVE button has not been pressed
    else:
        sql_comp = """SELECT as_nr, name FROM companies WHERE id=%u""" % ( company )
        comp = conn.get_data(sql_comp)
        if comp != ():
            as_nr = str(comp[0][0])
            c_name = str(comp[0][1])
        else:
            as_nr = "0"
            c_name = ""

        print """<div id="main">"""
        print """<div id="table_main">"""

        ### HEADING
        print """<div id="functionHead">Insert a new vrf/view for "%s"</div>""" % ( c_name )

        print_newnet_form(group, company, as_nr)

        print """</div>""" # main
        print """</div>""" # table_main

    HTML.main_footer()

main()
