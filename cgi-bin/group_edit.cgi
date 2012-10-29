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
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie



def print_group_form(id, details, group):
    """print html form to edit group details
    details: groupname, user_admin, company_admin, companies_id"""

    print """<input type=hidden name=id value="%s">""" % (id)

    print """<div id="pos_left_small">"""
    print """<div class=lineHeight>Name *</div>"""
    print """<div class=lineHeight>Members are user admins</div>"""
    print """<div class=lineHeight>Members are company admins</div>"""
    if group == 1:
        print """<div class=lineHeight>Company *</div>"""
    print """</div>""" # left side

    print """<div id="pos_right_wide">"""
    print """<div class=lineHeight>
        <input type=text id="groupname" name=groupname size=33 class=b_eingabefeld maxlength=50 value="%s"></div>""" % (str(details[0][0]))
    if int(details[0][1]) == 1:
        print """<div class=lineHeight><input type=checkbox id="user_admin" name=user_admin checked></div>"""
    else:
        print """<div class=lineHeight><input type=checkbox id="user_admin" name=user_admin></div>"""
    if int(details[0][2]) == 1:
        print """<div class=lineHeight><input type=checkbox id="company_admin" name=company_admin checked></div>"""
    else:
        print """<div class=lineHeight><input type=checkbox id="company_admin" name=company_admin></div>"""
    if group == 1:
        print_companies( int(details[0][3]) )
    print """</div>""" # right side
    print """<div id="pos_clear"></div>"""
    

def print_companies(company):
    """print a dropdown box with all registered companies"""
    
    sql_groups_company = """SELECT id, name FROM companies WHERE id = %u """ % int(company)
    groups_company = conn.get_data(sql_groups_company)
    
    sql_companies = """SELECT id, name FROM companies WHERE id != %u ORDER BY name""" % int(company)
    companies = conn.get_data(sql_companies)
    
    print """<div class=lineHeight>"""
    print """<select id="company" name=company class=b_eingabefeld>"""
    print """<option value="%s">%s</option>""" % (str(groups_company[0][0]), str(groups_company[0][1]))
    if companies != () and companies != None:
        for c in companies:
            print """<option value="%s">%s</option>""" % (str(c[0]), c[1])
        print """</select>"""
    print """</div>"""


def main():
    """entry point for executing IP@LL - edit group details"""

    ### definitions of variables
    global company_id, id, conn, rights, cgi_dir
    groupname = "" 
    user_admin = company_admin = "off"
    company = 0

    formdata = cgi.FieldStorage()

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 2:
            id = str(qs.split("&")[0])
            companies_id = int(qs.split("&")[1])
        else:
            id = companies_id = 0            

    try:
        if formdata.has_key("id"):
            id = int(formdata['id'].value)
        if formdata.has_key("groupname"):
            groupname = str(formdata['groupname'].value)
        if formdata.has_key("user_admin"):
            user_admin = str(formdata['user_admin'].value)
        if formdata.has_key("company_admin"):
            company_admin = str(formdata['company_admin'].value)
        if formdata.has_key("company"):
            company = int(formdata['company'].value)
    except:
        print """<script language="javascript">alert("Please fill out all fields marked with asterisks!"); history.back();</script> """
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

    if formdata.has_key("save"):
        print "<br>"
        
        if user_admin == "on":
            user_admin = 1
        else:
            user_admin = 0
        if company_admin == "on":
            company_admin = 1
        else:
            company_admin = 0
        if group != 1:
            company = company_id
   
        sql_group = """UPDATE ipall_group SET
            groupname='%s' , user_admin=%u, company_admin=%u, companies_id=%u WHERE id=%u """ \
            % (groupname, user_admin, company_admin, company, id)
        group_ok = conn.update_data(sql_group)
            
        ### LOGGING
        log_string = sql_group
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_group', "%s", %u)""" % (current_user, log_string, company)
        log = conn.insert_data(sql_log)
        
        if group_ok == 1 and log >= 0:
            HTML.notify_message("changes applied...")
        else:
            HTML.error_message("an error has occured...")
        msg = """<a class=LinkPurpleBold href="%s/mgmt_group.cgi"> << back</a> """ % cgi_dir
        HTML.notify_message(msg)
        HTML.close_body()
        return
            
    else: ### SAVE key was not pressed
        if group == 1:
            query = """SELECT groupname, user_admin, company_admin, companies_id FROM ipall_group WHERE id=%u 
                AND companies_id=%u """ % ( int(id), int(companies_id) )
            details = conn.get_data(query)
        elif rights[2] == 1:
            if companies_id != company_id:
                print """<script language="javascript">alert("You are not allowed to change the company"); history.back();</script> """; return;
            query = """SELECT groupname, user_admin, company_admin, companies_id FROM ipall_group WHERE id=%u 
                AND companies_id=%u """ % ( int(id), int(company_id) )
            details = conn.get_data(query)
        else:
            if companies_id != company_id:
                print """<script language="javascript">alert("You are not allowed to change the company"); history.back();</script> """; return;
            details = ()

        if details == () or details == None:
            HTML.error_message("Nothing to display!")
            return
        else:
            if group != 1:
                if rights[2] != 1:
                    group_perm = 0
                else:
                    group_perm = 1
            else:
                group_perm = 1
                #print user_perm

            if group_perm != 1:
                HTML.restriction_message()
                return

            print """<div id="main">"""
            print """<div id="table_main">"""
            print """<div id="functionHead">Edit details of group <i>&quot;%s&quot;</i></div>""" % details[0][0]

            print """<form name="edit_group" method=POST action="group_edit.cgi"
                onSubmit="return check_group()">"""

            print_group_form(id, details, group)	

            print """<div>* required field</div>"""
            print """<div><input type=submit id="save" name=save value=save class=button></div>"""
            print """</form>"""
            print """</div>""" #table_main
            print """</div>""" #main

    HTML.popup_footer()

main()
