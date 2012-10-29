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
import IPy
import os
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj


def print_newuser_form(group, rights):
    """print a HTML form for inserting a new vrf"""

    print """<form name="new_user" method=POST action="new_user.cgi" onSubmit="return check_user()">"""

    ### LEFT SIDE
    print """<div id="pos_left">"""
    print """<p>Surname *<br>"""
    print """<input type=text id="surname" name=surname size=33 class=b_eingabefeld maxlength=100></p>"""
    print """<p>Mobile<br>"""
    print """<input type=text id="mobile" name=mobile size=33 class=b_eingabefeld maxlength=40></p>"""
    print """<p>E mail *<br>"""
    print """<input type=text id="mail" name=mail size=33 class=b_eingabefeld maxlength=50></p>"""
    print """<p>Username *<br>"""
    print """<input type=text id="username" name=username size=33 class=b_eingabefeld maxlength=30></p>"""
    print """</div>""" #left side

    ### RIGHT SIDE
    print """<div id="pos_right">"""
    print """<p>Forename *<br>"""
    print """<input type=text id="forename" name=forename size=33 class=b_eingabefeld maxlength=100></p>"""
    print """<p>Phone<br>"""
    print """<input type=text id="phone" name=phone size=33 class=b_eingabefeld maxlength=40></p>"""
    print """<p>Web<br>"""
    print """<input type=text id="web" name=web size=33 class=b_eingabefeld maxlength=50 value="http://"></p>"""
    print """<p>Password (6-32 characters) *<br>"""
    print """<input type=password id="password1" name=password1 size=33 class=b_eingabefeld maxlength=32></p>"""
    print """<p>Retype password *<br>"""
    print """<input type=password id="password2" name=password2 size=33 class=b_eingabefeld maxlength=32></p>"""
    print """</div>""" #right side
        
    print """<div id="pos_clear"></div>"""
    if group == 1:
        print """<div>"""
        print """<p>Company *<br>"""
        get_companies()
        print """</p>"""
        print """</div>"""


    if group == 1 or rights[1] == 1:
        print """<div>"""
        print """<p>Group<br>"""
        get_groups(group)
        print """</p>"""
        print """</div>"""
    print """<input type=submit id="save" name=save value=save class=button>"""
    print """</div>"""
    
    print """<div id="info"></div>"""
    print """</form>"""


def get_companies():
    """print a dropdown box with all registered companies"""
    
    sql_companies = """SELECT id, name FROM companies ORDER BY name"""
    companies = conn.get_data(sql_companies)
    
    if companies != () and companies != None:
        print """<select id="company" name=company class=b_eingabefeld onChange="fillGroup('%s');">""" % ( cgi_dir  )
        print """<option value="0">select company</option>"""
        for c in companies:
            print """<option value="%s">%s</option>""" % (str(c[0]), c[1])
        print """</select>"""
    else:
        print """error!"""

def get_groups(group):
    """print a dropdown box with groups"""
    if group != 1:
        sql_groups = """SELECT id, groupname FROM ipall_group WHERE id != 1 AND companies_id=%u ORDER BY groupname""" % ( company_id )
        groups = conn.get_data(sql_groups)

    print """<select id="group_id" name=group_id class=b_eingabefeld>"""
    if group == 1:
        print """<option value="0">select company first...</option>"""
        print """<option value="1">Super Administrators</option>"""
    else:
        print """<option value="0">select group</option>"""
        if groups != () and groups != None:
            for g in groups:
                print """<option value="%s">%s</option>""" % (str(g[0]), g[1])
    print """</select>"""
          

def main():
    """create a new user object"""

    global company_id, vrf, conn, cgi_dir
    formdata = cgi.FieldStorage()
    surname = forename = mobile = phone = mail = web = "" 
    password = password1 = password2 = username = ""
    company = group_id = 0
    

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
    if group == 0:
        HTML.restriction_message()
        return
    ### logged in user does have enough rights to 
    else:
        try:
            #if formdata.has_key("uri"):
                #uri = str(formdata['uri'].value)
            if formdata.has_key("surname"):
                surname = str(formdata['surname'].value)
            if formdata.has_key("forename"):
                forename = str(formdata['forename'].value)
            if formdata.has_key("mobile"):
                mobile = str(formdata['mobile'].value)
            if formdata.has_key("phone"):
                phone = str(formdata['phone'].value)
            if formdata.has_key("mail"):
                mail = str(formdata['mail'].value)
            if formdata.has_key("web"):
                web = str(formdata['web'].value)
            if formdata.has_key("password1"):
                password1 = str(formdata['password1'].value)
            if formdata.has_key("password2"):
                password2 = str(formdata['password2'].value)
            if formdata.has_key("username"):
                username = str(formdata['username'].value)
            if formdata.has_key("group_id"):
                group_id = int(formdata['group_id'].value)
            if formdata.has_key("company"):
                company = int(formdata['company'].value)
            else:
                company = company_id
        except:
            print """<script language="javascript">alert("Please fill out all fields marked with asterisks!"); history.back();</script> """

    rights = user.get_rights()

    if group != 1 and rights[1] != 1 and rights[2] != 1: 
        HTML.restriction_message()
        return

    ### SAVE button has been pressed
    if formdata.has_key("save"):

        password = password1
        if group == 1 or rights[1] == 1:
            if group_id == 0:
                print """<script language="javascript">alert("Please select a group!"); history.back();</script> """; return;
#        if group == 1:
#            if company == 0:
#                print """<script language="javascript">alert("Please select a company!"); history.back();</script> """; return;
        else:
            company = company_id
   
        sql_check = """SELECT persons_id FROM persons WHERE username='%s'""" \
            % (username)
        check = conn.get_data(sql_check)
        
        if check != ():
            HTML.error_message("Username already exists!")
            return
        else:
            sql_person = """INSERT INTO `persons` 
                ( `persons_id` , `surname` , `forename` , `mobile` , `phone` , `mail` , `web` , `username` , `password` , `companies_id`) 
                VALUES ('', '%s', '%s', '%s' , '%s', '%s', '%s', '%s', MD5('%s'), %u)""" \
                % ( surname, forename, mobile, phone, mail, web, username, password, company )
            user_id = conn.insert_data(sql_person)
            sql_group = """INSERT INTO ipall_user_group ( `username` , `group_id` )
                VALUES ( '%s', %u )""" % ( username, group_id )
            group_ok = conn.update_data(sql_group)
            

        ### LOGGING
        log_string = re.sub( "MD5\('(.)*'\)", "PASSWORD", sql_person )
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'persons', "%s", %u)""" % (current_user, log_string, company)
        log = conn.insert_data(sql_log)
        
        if user_id != 0 and group_ok != 0:
            HTML.notify_message("changes applied...")
            linktext = """<a class=LinkPurpleBold href="%s/mgmt_user.cgi"> << back</a> """ % cgi_dir
            HTML.notify_message(linktext)
        else:
            HTML.error_message("An error has occured!")

        HTML.close_body()
    ### SAVE button has not been pressed
    else:
        print """<div id="main">"""
        print """<div id="table_main">"""

        ### HEADING
        print """<div id="functionHead">Insert a new user</div>"""

        print_newuser_form(group, rights)

        print """</div>""" # main
        print """</div>""" # table_main

        HTML.popup_footer()

main()
