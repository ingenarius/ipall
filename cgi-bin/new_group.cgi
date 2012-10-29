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
import IPy
import os
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj


def print_newgroup_form(company, group, rights):
    """print a HTML form for inserting a new group"""

    print """<form name="new_group" method=POST action="new_group.cgi"
        onSubmit="return check_group()">"""

    print """<input type=hidden name=company value="%s">""" % str(company)

    print """<div id="pos_left_small">"""
    print """<div class=lineHeight>Name *</div>"""
    print """<div class=lineHeight>Members are user admins</div>"""
    print """<div class=lineHeight>Members are company admins</div>"""
    print """</div>""" # left side


    print """<div id="pos_right_wide">"""
    print """<div class=lineHeight><input type=text id="groupname" name=groupname size=33 class=b_eingabefeld maxlength=50></div>"""
    print """<div class=lineHeight><input type=checkbox id="user_admin" name=user_admin></div>"""
    print """<div class=lineHeight><input type=checkbox id="company_admin" name=company_admin></div>"""
    print """</div>""" # left side

    print """<div id="pos_clear"></div>"""
    print """<div style="margin-top: 10px">* required field</div>"""
    print """<div style="margin-top: 10px"><input type=submit id="save" name=save value=save class=button></div>"""
    print """</form>"""



def main():
    """create a new group"""

    #global company, conn, cgi_dir
    formdata = cgi.FieldStorage()
    groupname = "" 
    user_admin = company_admin = "off"
    group_id = 0
    
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
    cgi_dir = cfg['Server']['cgi_dir']
    rights = user.get_rights()
    
    if group == 0 or rights[2] == 0:
        HTML.restriction_message()
        return
    else:
        if group == 1:
            if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
                qs = os.environ['QUERY_STRING']
                company = int(qs[0:])
            else:
                company = company_id
        else:
            company = company_id
            
        try:
            #if formdata.has_key("uri"):
                #uri = str(formdata['uri'].value)
            if formdata.has_key("groupname"):
                groupname = str(formdata['groupname'].value)
            if formdata.has_key("company_admin"):
                company_admin = str(formdata['company_admin'].value)
            if formdata.has_key("user_admin"):
                user_admin = str(formdata['user_admin'].value)
            if formdata.has_key("company"):
                company = int(formdata['company'].value)
        except:
            print """<script language="javascript">alert("data error!"); history.back();</script> """

    if group != 1 and rights[1] != 1 and rights[2] != 1: 
        HTML.restriction_message()
        return

    ### SAVE button has been pressed
    if formdata.has_key("save"):
        print "<br>"

        if company_admin == "on": company_admin = 1;
        else: company_admin = 0;
        if user_admin == "on": user_admin = 1;
        else: user_admin = 0;
   
        sql_check = """SELECT id FROM ipall_group WHERE groupname='%s' AND companies_id=%u """ \
            % (groupname, company)
        check = conn.get_data(sql_check)
        
        if check != ():
            HTML.error_message("Group already exists!")
            return
        else:
            sql_group = """INSERT INTO `ipall_group` 
                ( `id` , `groupname` , `user_admin` , `company_admin` , `companies_id` ) 
                VALUES ('', '%s', %u, %u, %u )""" \
                % ( groupname, user_admin, company_admin, company )
            group_ok = conn.update_data(sql_group)
            

        ### LOGGING
        log_string = sql_group
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_group', "%s", %u)""" % (current_user, log_string, company)
        log = conn.insert_data(sql_log)
        
        if group_ok != 0:
            HTML.notify_message("group created successfully...")
        else:
            HMTL.error_message("an error has occured...")
        msg = """<a href="%s/mgmt_group.cgi" class="linkPurpleBold"> << back</a>""" % cgi_dir
        HTML.notify_message(msg)
        
    ### SAVE button has not been pressed
    else:	
        print """<div id="main">"""
        print """<div id="table_main">"""

        ### HEADING
        print """<div id="functionHead">Insert a new group</div>"""

        print_newgroup_form(company, group, rights)

        print """</div>""" #table_main
        print """</div>""" #main

    HTML.close_body()

main()
