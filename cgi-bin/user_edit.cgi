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



def print_user_form(id, details, group):
    """print html form to edit user details
    details: surname, forename, mobile, phone, mail, web, username, companies_id"""

    print """<input type=hidden name=id value="%s">""" % (id)
    print """<input type=hidden name=old_username value="%s">""" % (details[0][6])
    
    ### LEFT SIDE
    print """<div id="pos_left">"""
    print """<p>Surname *<br>"""
    print """<input type=text id="surname" name=surname size=33 class=b_eingabefeld maxlength=100 value="%s"></p>""" % (details[0][0])
    print """<p>Mobile<br>"""
    print """<input type=text id="mobile" name=mobile size=33 class=b_eingabefeld maxlength=40 value="%s"></p>""" % (details[0][2])
    print """<p>E mail *<br>"""
    print """<input type=text id="mail" name=mail size=33 class=b_eingabefeld maxlength=50 value="%s"></p>""" % (details[0][4])
    print """<p>Username *<br>"""
    print """<input type=text id="username" name=username size=33 class=b_eingabefeld maxlength=30 value="%s"></>""" % (details[0][6])
    print """</div>""" # left side

    ### RIGHT SIDE
    print """<div id="pos_right">"""
    print """<p>Forename *<br>"""
    print """<input type=text id="forename" name=forename size=33 class=b_eingabefeld maxlength=100 value="%s"></p>""" % (details[0][1])
    print """<p>Phone<br>"""
    print """<input type=text id="phone" name=phone size=33 class=b_eingabefeld maxlength=40 value="%s"></p>""" % (details[0][3])
    print """<p>Web<br>"""
    print """<input type=text id="web" name=web size=33 class=b_eingabefeld maxlength=50 value="%s"></p>""" % (details[0][5])
    print """<p>Password (6-32 characters) *<br>"""
    print """<input type=password id="password1" name=password1 size=33 class=b_eingabefeld maxlength=32></p>"""
    print """<p>Retype password *<br>"""
    print """<input type=password id="password2" name=password2 size=33 class=b_eingabefeld maxlength=32></p>"""
    print """</div>""" # left side

    print """<div id="pos_clear">"""
    if group == 1:
        print """<p>Company *<br>"""
        users_company = get_companies(details[0][7], group)
        print """</p>"""
    else:
        users_company = company_id
        print """<input type=hidden id="company" name=company value="%s">""" % (company_id)

    if group == 1 or rights[1] == 1 or rights[2] == 1:
        print """<p>Group<br>"""
        old_group = get_groups(details[0][6], group, users_company)
        print """</p>"""
        print """<input type=hidden id="old_group_id" name=old_group_id value="%s">""" % (old_group)
    print """<p><input type=submit id="save" name=save value=save class=button></p>"""
    print """</div>""" # clear
    

def get_groups(username, group, users_company):
    """print a dropdown box with groups"""
    
    if group == 1:
        sql_groups = """SELECT id, groupname FROM ipall_group WHERE companies_id = %u ORDER BY groupname""" % ( users_company )
    else:
        sql_groups = """SELECT id, groupname FROM ipall_group WHERE companies_id = %u 
            AND id != 1 ORDER BY groupname""" % ( users_company )
    groups = conn.get_data(sql_groups)
    #print groups

    sql_users_group = """SELECT g.group_id, gr.groupname FROM ipall_user_group g, persons p, ipall_group gr 
            WHERE g.username='%s' AND p.username='%s' AND g.group_id=gr.id """ % (username, username)
    users_group = conn.get_data(sql_users_group)

    if groups != () and groups != None:
        print """<select id="group_id" name=group_id class=b_eingabefeld>"""
        print """<option value="%s">%s</option>""" % (users_group[0][0], users_group[0][1])
        for g in groups:
            if g[0] != users_group[0][0]:
                print """<option value="%s">%s</option>""" % (str(g[0]), g[1])
        print """</select>"""
        return int(users_group[0][0])
    else:
        print """error!"""
        return 0


def get_companies(company, group):
    """print a dropdown box with all registered companies"""
    
    if company != 0:
        sql_users_company = """SELECT id, name FROM companies WHERE id = %u """ % int(company)
        users_company = conn.get_data(sql_users_company)
    else:
        users_company = ((0, 'none'),) 
    
    sql_companies = """SELECT id, name FROM companies WHERE id != %u ORDER BY name""" % int(company)
    companies = conn.get_data(sql_companies)
    
    print """<select id="company" onChange="fillGroup('%s');" name=company class=b_eingabefeld>""" % ( cgi_dir )
    print """<option value="%s">%s</option>""" % (str(users_company[0][0]), str(users_company[0][1]))
    if companies != () and companies != None:
        for c in companies:
            print """<option value="%s">%s</option>""" % (str(c[0]), c[1])
        
    if group == 1:
        print """<option value="0">none</option>"""
    print """</select>"""
    return int(users_company[0][0])


def main():
    """entry point for executing IP@LL - edit vrf details"""

    ### definitions of variables
    global company_id, id, conn, rights, cgi_dir
    surname = forename = mobile = phone = mail = web = "" 
    password = password1 = password2 = username = old_username = ""
    company = group_id = old_group_id = 0

    formdata = cgi.FieldStorage()

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 1:
            id = str(qs.split("&")[0])
        else:
            id = 0

    try:
        if formdata.has_key("id"):
            id = int(formdata['id'].value)
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
        if formdata.has_key("old_username"):
            old_username = str(formdata['old_username'].value)
        if formdata.has_key("group_id"):
            group_id = int(formdata['group_id'].value)
        if formdata.has_key("old_group_id"):
            old_group_id = int(formdata['old_group_id'].value)
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
 
        password = password1
        if group == 1 or rights[1] == 1:
            if group_id == 0:
                print """<script language="javascript">alert("Please select a group!"); history.back();</script> """; return;
        if company == 0 and group == 1:
            print """<script language="javascript">alert("Please select a company!"); history.back();</script> """; return;
   
        if username != old_username:
            sql_check = """SELECT persons_id FROM persons WHERE username='%s'""" \
                % (username)
            check = conn.get_data(sql_check)
        else:
            check = ()
        
        if check != ():
            print """<script language="javascript">alert("Username already exists!"); history.back();</script> """
            return
        else:
            if password != "":
                sql_person = """UPDATE persons SET
                    surname='%s' , forename='%s' , mobile='%s' , phone='%s' , mail='%s' , web='%s' , 
                    username='%s' , password=MD5('%s') , companies_id=%u WHERE persons_id=%u """ \
                    % (surname, forename, mobile, phone, mail, web, username, password, company, id)
            else:
                sql_person = """UPDATE persons SET
                    surname='%s' , forename='%s' , mobile='%s' , phone='%s' , mail='%s' , web='%s' , 
                    username='%s' , companies_id=%u WHERE persons_id=%u """ \
                    % (surname, forename, mobile, phone, mail, web, username, company, id)
            #print "<br>", sql_person
            user_id = conn.update_data(sql_person)
            
            if username != old_username:
                sql_user = """UPDATE ipall_user_group SET username='%s' WHERE username='%s' AND group_id=%u """ % (username, old_username, old_group_id)
                #print "<br>", sql_user
                user_ok = conn.update_data(sql_user)
            else:
                user_ok = 1
            if group_id != old_group_id:
                sql_group = """UPDATE ipall_user_group SET group_id=%u WHERE username='%s' """ % (group_id, username)
                #print "<br>", sql_group
                group_ok = conn.update_data(sql_group)
            else:
                group_ok = 1

        ### LOGGING
        log_string = re.sub( "MD5\('(.)*'\)", "PASSWORD", sql_person )
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'persons', "%s", %u)""" % (current_user, log_string, company)
        log = conn.insert_data(sql_log)
        
        if user_id != 0 and user_ok == 1 and group_ok == 1:
            HTML.notify_message("changes applied...")
        else:
            HTML.error_message("an error has occured...")
        linktext = """<a class=LinkPurpleBold href="%s/mgmt_user.cgi"> << back</a> """ % cgi_dir
        HTML.notify_message(linktext)
        
        HTML.close_body()
            
    else: ### SAVE key was not pressed
        query = """SELECT surname, forename, mobile, phone, mail, web, username, companies_id FROM persons WHERE persons_id=%u """ % (int(id))
        details = conn.get_data(query)

        if details == () or details == None:
            HTML.error_message("Nothing to display!")
            return
        else:
            if group != 1 and rights[1] != 1:
                if details[0][6] != current_user:
                    user_perm = 0
                else:
                    user_perm = 1
            else:
                user_perm = 1
                #print user_perm

            if user_perm != 1:
                HTML.restriction_message()
                return

            print """<div id="main">"""
            print """<div id="table_main">"""
            print """<div id="functionHead">Edit user details of <i>&quot;%s&quot;</i></div>""" % details[0][6]
            print """<form name="edit_user" method=POST action="user_edit.cgi"
                onSubmit="return check_user()">"""

            print_user_form(id, details, group)	

            print """</form>"""
            print """<div>&nbsp;</div>"""
            print """<div>* required field</div>"""
            print """</div>""" # table_main 
            print """</div>""" # main 

        HTML.popup_footer()

main()
