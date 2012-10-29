#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
"""

from Html_new import HtmlContent
from Ipall import IpallFunctions
import DBmy
import IpallUser
from Sessionclass import Session
import IPy
import os
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie
from string import zfill



def print_from_date(f):
    """print table with dropdown boxes for day-month-year"""

    print """<div id="pos_left_small">date</div>"""
    print """<div id="pos_right_wide">"""
    print """<select name=day_from class=b_eingabefeld_50>"""
    print """<option value="%">day</option>"""
    for r in range(1, 32):
        print """<option value=%s>%s</option>""" % (zfill(str(r),2), zfill(str(r),2))
    print """</select>"""
    print """<select name=month_from class=b_eingabefeld_50>"""
    print """<option value="%">mon</option>"""
    for r in range(1, 13):
        print """<option value=%s>%s</option>""" % (zfill(str(r),2), zfill(str(r),2))
    print """</select>"""
    print """<select name=year_from class=b_eingabefeld_50>"""   
    print """<option value="%">year</option>"""
    years = f.get_years()
    for y in years:
        print """<option value=%s>%s</option>""" % (str(y[0]), str(y[0]))
    print """</select>"""
    print """</div>""" # right side
    print """<div id="pos_clear"></div>"""

def print_pattern():
    """print text field for user input"""

    print """<div id="pos_left_small">search</div>"""
    print """<div id="pos_right_wide">"""
    print """<input type=text name=pattern class=b_eingabefeld>"""
    print """</div>""" # right side
    print """<div id="pos_clear"></div>"""



def print_tables(f):
    """print html table with sql table name entries in a dropdownbox"""

    print """<div id="pos_left_small">table</div>"""
    print """<div id="pos_right_wide">"""
    print """<select name=table_name class=b_eingabefeld>"""
    print """<option value="%">all tables</option>"""
    tables = f.get_table_names()
    if tables != ():
        for t in tables:
            print """<option value="%s">%s</option>""" % (str(t[0]), str(t[0]))
    print """</select>"""
    print """</div>""" # right side
    print """<div id="pos_clear"></div>"""
    

def print_users(f):
    """print html table with all users who did changes in NMS"""
    
    print """<div id="pos_left_small">user</div>"""
    print """<div id="pos_right_wide">"""
    print """<select name=user_name class=b_eingabefeld>"""
    print """<option value="%">any user</option>"""
    users = f.get_user_names()
    if users != ():
        for u in users:
            print """<option value="%s">%s</option>""" % (str(u[0]), str(u[0]))
    print """</select>"""
    print """</div>""" # right side
    print """<div id="pos_clear"></div>"""


def print_companies(f):
    """print html table with all companies"""

    print """<div id="pos_left_small">user</div>"""
    print """<div id="pos_right_wide">"""
    print """<select name=company class=b_eingabefeld>"""
    print """<option value="%">any company</option>"""
    companies = f.get_companies()
    if companies != ():
        for c in companies:
            print """<option value="%s">%s</option>""" % (str(c[0]), str(c[1]))
    print """</select>"""
    print """</div>""" # right side
    print """<div id="pos_clear"></div>"""



def main():
    """LOG viewer"""

    global conn
    formdata = cgi.FieldStorage()
    day_from = month_from = year_from = day_to = month_to = year_to = company = table_name = user_name = pattern = ""

    try:
        if formdata.has_key("day_from"):
            day_from = str(formdata['day_from'].value)
        if formdata.has_key("month_from"):
            month_from = str(formdata['month_from'].value)
        if formdata.has_key("year_from"):
            year_from = str(formdata['year_from'].value)
        if formdata.has_key("company"):
            company = str(formdata['company'].value)
        if formdata.has_key("table_name"):
            table_name = str(formdata['table_name'].value)
        if formdata.has_key("user_name"):
            user_name = str(formdata['user_name'].value)
        if formdata.has_key("pattern"):
            pattern = str(formdata['pattern'].value)
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

    ### user
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
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']
    
    if group == 0:
        HTML.restriction_message()
        HTML.main_footer()
        return

    elif group != 1 and rights[1] != 1 and rights[2] != 1:
        HTML.restriction_message()
        HTML.main_footer()
        return
    else: 
        ### logged in user does have enough rights to 
        f = IpallFunctions(conn, current_user, group, company_id)

        print """<div id="main">"""
        print """<div id="table_main">"""
        print """<div id="functionHead">View Logs</div>"""

        print """<form name="view_logs" method=POST action="log_viewer.cgi">"""
        
        print_from_date(f)
        if group == 1:
            print_companies(f)
        print_tables(f)
        print_users(f)
        print_pattern()
        print """<div><input type=submit name=send value=send class=button></div>"""

        print """</form>"""
        
        if formdata.has_key("send"):
            if user_name == "%": user_name = " LIKE '%'";
            else: user_name = "= '" + user_name + "'"
            if group != 1:
                company = "= '" + str(company_id) + "'"
            else:
                if company == "%": company = " LIKE '%'";
                else: company = "= '" + str(company) + "'";
            if table_name == "%": table_name = " LIKE '%'";
            else: table_name = "= '" + table_name + "'"
            if day_from == "%": day_from = " LIKE '%'";
            else: day_from = "= '" + day_from + "'"
            if month_from == "%": month_from = " LIKE '%'";
            else: month_from = "= '" + month_from + "'"
            if year_from == "%": year_from = " LIKE '%'";
            else: year_from = "= '" + year_from + "'"
            if pattern.find("'") != -1 or pattern.find("\"") != -1 or pattern.find("%") != -1:  
                print """<script language="javascript">alert("Do not use single or double quotes!"); history.back();</script> """
                return

            result = f.get_log_results(table_name, pattern, user_name, year_from, month_from, day_from, company)

            if result != () and result != None:
                print """<div class=TextPurpleBold style="border-bottom: 1px solid;">"""
                print """<div id="pos_left_100">date</div>"""
                print """<div id="pos_left_100">user</div>"""
                print """<div id="pos_left_130">table</div>"""
                print """<div id="pos_left">sql statement</div>"""
                print """<div id="pos_clear"></div>"""
                print """</div>"""
                for r in result:
                    print """<div style="border-bottom: 1px dotted;">"""
                    print """<div id="pos_left_100">%s</div>""" % str(r[0])
                    print """<div id="pos_left_100">%s</div>""" % str(r[1])
                    print """<div id="pos_left_130">%s</div>""" % str(r[2])
                    print """<div id="pos_left">%s</div>""" % re.sub( "MD5\('(.)*'\)", "PASSWORD", str(r[3]) )
                    print """<div id="pos_clear"></div>"""
                    print """</div>"""
            else:
                HTML.notify_message("Sorry, no matches found!")

        print """</div>""" # table_main
        print """</div>""" # main

    HTML.main_footer()

main()
