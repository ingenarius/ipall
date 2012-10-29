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



def print_company_form(id, details, group):
    """print html form to edit company details
                  0     1            2        3             4            5     6        7      8
        details: name, description, street, street_number, postal_code, city, country, as_nr, as_set
         9            10            11             12          13            14           15           16
        ripe_header, ripe_trailer, ripe_password, ripe_mntby, ripe_admin_c, ripe_tech_c, ripe_notify, is_lir 
         17                18
        send_delete_mail, delete_mail"""

    print """<input type=hidden name=id value="%s">""" % (id)
    
    ## name ##
    print """<div>Name * <br>"""
    print """<input type=text id="name" name=name size=33 class=b_eingabefeld maxlength=100 value="%s"></div>""" % (details[0][0])
    ### LEFT SIDE ###
    print """<div id="pos_left">"""
    ## street ##
    print """<p>Street * <br>"""
    print """<input type=text id="street" name=street size=33 class=b_eingabefeld maxlength=50 value="%s"></p>""" % (details[0][2])
    ## postal code ##
    print """<p>Postal code * <br>"""
    print """<input type=text id="postal_code" name=postal_code size=33 class=b_eingabefeld maxlength=8 value="%s"></p>""" % (details[0][4])
    ## send mail checkbox ##
    print """<p>Send mail on deleting prefix? <br>"""
    if details[0][17] == 1:
        print """<input type=checkbox id="send_delete_mail" name=send_delete_mail checked></p>"""
    else:
        print """<input type=checkbox id="send_delete_mail" name=send_delete_mail></p>"""
    print """</div>""" # left side

    ### RIGHT SIDE ###
    print """<div id="pos_right">"""
    ## street nr ##
    print """<p>Nr * <br>"""
    print """<input type=text id="street_number" name=street_number size=33 class=b_eingabefeld maxlength=10 value="%s"></p>""" % (details[0][3])
    ## city ##
    print """<p>City * <br>"""
    print """<input type=text id="city" name=city size=33 class=b_eingabefeld maxlength=30 value="%s"></p>""" % (details[0][5])
    ## mail address for deletion ##
    print """<p>"delete prefix" notify email address ** <br>"""
    print """<input type=text id="delete_mail" name=delete_mail size=33 class=b_eingabefeld maxlength=250 value="%s"></p>""" % (details[0][18])
    print """</div>""" # right side

    ## description ##
    print """<div id="pos_clear">Description* <br>"""
    print """<textarea id="descr" name=descr class=code_eingabefeld rows=6>%s</textarea></div>""" % (details[0][1])

    ## rir member? ##
    print """<br><div>Company is RIR member? <br>"""
    if details[0][16] == 1:
        print """<input type=checkbox id="is_lir" name=is_lir checked></div>"""
    else:
        print """<input type=checkbox id="is_lir" name=is_lir></div>"""

    ### LEFT SIDE ###
    print """<div id="pos_left">"""
    ## RIR pw ##
    print """<p>RIR password ** <br>"""
    print """<input type=text id="ripe_password" name=ripe_password size=33 class=b_eingabefeld maxlength=200 value="%s"></p>""" % (details[0][11])
    ## AS nr ##
    print """<p>AS number * <br>"""
    print """<input type=text id="as_nr" name=as_nr size=33 class=b_eingabefeld maxlength=200 value="%s"></p>""" % (details[0][7])
    ## admin-c ##
    print """<p>RIR admin-c ** <br>"""
    print """<input type=text id="ripe_admin_c" name=ripe_admin_c size=33 class=b_eingabefeld maxlength=200 value="%s"></p>""" % (details[0][13])
    ## notify ##
    print """<p>RIR notify email address ** <br>"""
    print """<input type=text id="ripe_notify" name=ripe_notify size=33 class=b_eingabefeld maxlength=200 value="%s"></p>""" % (details[0][15])
    print """</div>""" # left side

    ### RIGHT SIDE ###
    print """<div id="pos_right">"""
    ## RIR mnt ##
    print """<p>RIR maintainer (mnt-by) ** <br>"""
    print """<input type=text id="ripe_mntby" name=ripe_mntby size=33 class=b_eingabefeld maxlength=200 value="%s"></p>""" % (details[0][12])
    ## AS set ##
    print """<p>AS set ** <br>"""
    print """<input type=text id="as_set" name=as_set size=33 class=b_eingabefeld maxlength=200 value="%s"></p>""" % (details[0][8])
    ## tech-c ##
    print """<p>RIR tech-c ** <br>"""
    print """<input type=text id="ripe_tech_c" name=ripe_tech_c size=33 class=b_eingabefeld maxlength=200 value="%s"></p>""" % (details[0][14])
    ## country code ##
    print """<p>Country code (2 letters) <br>"""
    print """<input type=text id="country" name=country size=33 class=b_eingabefeld maxlength=200 value="%s"></p>""" % (details[0][6])
    print """</div>""" # right side

    ## AS header ##
    print """<div id="pos_clear">RIR AS header (<b><a href="%s/documentation.cgi?de_3#companies" target="_blank">template</a></b>) <br>"""  % (cgi_dir)
    print """<textarea id="ripe_header" name=ripe_header class=code_eingabefeld rows=10>%s</textarea></div>""" % (details[0][9])
    ## AS trailer ##
    print """<div>RIR AS trailer <br>"""
    print """<textarea id="ripe_trailer" name=ripe_trailer class=code_eingabefeld rows=10>%s</textarea></div>""" % (details[0][10])


def main():
    """entry point for executing IP@LL - edit vrf details"""

    ### definitions of variables
    global id, conn, rights, cgi_dir
    name = descr = street = postal_code = city = country = as_set = ""
    ripe_header = ripe_trailer = ripe_password = ripe_mntby = ripe_admin_c = ripe_tech_c = ripe_notify = delete_mail = " "
    street_number = as_nr = 0
    is_lir = send_delete_mail = "off"
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
        if formdata.has_key("name"):
            name = str(formdata['name'].value)
        if formdata.has_key("descr"):
            descr = str(formdata['descr'].value)
        if formdata.has_key("street"):
            street = str(formdata['street'].value)
        if formdata.has_key("postal_code"):
            postal_code = str(formdata['postal_code'].value)
        if formdata.has_key("city"):
            city = str(formdata['city'].value)
        if formdata.has_key("country"):
            country = str(formdata['country'].value)
        if formdata.has_key("as_set"):
            as_set = str(formdata['as_set'].value)
        if formdata.has_key("ripe_header"):
            ripe_header = str(formdata['ripe_header'].value)
        if formdata.has_key("ripe_trailer"):
            ripe_trailer = str(formdata['ripe_trailer'].value)
        if formdata.has_key("ripe_password"):
            ripe_password = str(formdata['ripe_password'].value)
        if formdata.has_key("ripe_mntby"):
            ripe_mntby = str(formdata['ripe_mntby'].value)
        if formdata.has_key("ripe_admin_c"):
            ripe_admin_c = str(formdata['ripe_admin_c'].value)
        if formdata.has_key("ripe_tech_c"):
            ripe_tech_c = str(formdata['ripe_tech_c'].value)
        if formdata.has_key("ripe_notify"):
            ripe_notify = str(formdata['ripe_notify'].value)
        if formdata.has_key("street_number"):
            street_number = int(formdata['street_number'].value)
        if formdata.has_key("as_nr"):
            as_nr = int(formdata['as_nr'].value)
        if formdata.has_key("is_lir"):
            is_lir = str(formdata['is_lir'].value)
        if formdata.has_key("send_delete_mail"):
            send_delete_mail = str(formdata['send_delete_mail'].value)
        if formdata.has_key("delete_mail"):
            delete_mail = str(formdata['delete_mail'].value)
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
            
        if descr != "" and descr != "NULL": 
            descr = descr.rstrip()
        if send_delete_mail == "on":  send_delete_mail = 1;
        else:   send_delete_mail = 0;
        if delete_mail == "" or delete_mail != "NULL": 
            delete_mail = "'" + delete_mail + "'"
        if as_set == "" or as_set != "NULL": 
            as_set = "'" + as_set + "'"
        if ripe_header != "" and ripe_header != "NULL": 
            ripe_header = "'" + ripe_header.lstrip().rstrip() + "'"
        if ripe_trailer != "" and ripe_trailer != "NULL":
            ripe_trailer = "'" + ripe_trailer.lstrip().rstrip() + "'"
        if ripe_password != "" and ripe_password != "NULL": 
            ripe_password = "'" + ripe_password.lstrip().rstrip() + "'"
        if ripe_mntby != "" and ripe_mntby != "NULL": 
            ripe_mntby = "'" + ripe_mntby.lstrip().rstrip() + "'"
        if ripe_admin_c != "" and ripe_admin_c != "NULL": 
            ripe_admin_c = "'" + ripe_admin_c.lstrip().rstrip() + "'"
        if ripe_tech_c != "" and ripe_tech_c != "NULL": 
            ripe_tech_c = "'" + ripe_tech_c.lstrip().rstrip() + "'"
        if ripe_notify != "" and ripe_notify != "NULL": 
            ripe_notify = "'" + ripe_notify.lstrip().rstrip() + "'"
        if is_lir == "on":  is_lir = 1;
        else:   is_lir = 0;

            
        #print name, descr, street, postal_code, city, country, as_set,
        #print ripe_header, ripe_trailer, ripe_password, ripe_mntby, ripe_admin_c, ripe_tech_c, ripe_notify
        #print street_number, as_nr

        sql_company = """UPDATE companies SET name='%s', description='%s', street='%s', street_number=%u, postal_code='%s',
            city='%s', country='%s', as_nr=%u, as_set=%s, ripe_header=%s, ripe_trailer=%s, ripe_password=%s, ripe_mntby=%s,
            ripe_admin_c=%s, ripe_tech_c=%s, ripe_notify=%s, is_lir=%u, send_delete_mail=%u, delete_mail=%s WHERE id=%u """ \
            % (name, descr, street, street_number, postal_code, city, country, as_nr, as_set, ripe_header, ripe_trailer, \
                ripe_password, ripe_mntby, ripe_admin_c, ripe_tech_c, ripe_notify, is_lir, send_delete_mail, delete_mail, \
                int(id) )
        #print sql_company
        company_ok = conn.update_data(sql_company)

        ### LOGGING
        log_string = sql_company
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'companies', "%s", %u)""" % (current_user, log_string, int(id))
        log = conn.insert_data(sql_log)
        
        if company_ok == 1:
            HTML.notify_message("company update was successful...")
        else:
            HTML.error_message("an error has occured...")
        msg = """<a href="%s/mgmt_company.cgi" class="linkPurpleBold"> << back</a>""" % cgi_dir
        HTML.notify_message(msg)
            
    else: ### SAVE key was not pressed
        query = """SELECT name, description, street, street_number, postal_code, city, country, as_nr, as_set,
            ripe_header, ripe_trailer, ripe_password, ripe_mntby, ripe_admin_c, ripe_tech_c, ripe_notify, is_lir, 
            send_delete_mail, delete_mail FROM companies WHERE id=%u """ % (int(id))
        details = conn.get_data(query)

        if details == () or details == None:
            HTML.error_message("Nothing to display!")
            return
        else:
            if group != 1 and rights[1] != 1:
                company_perm = 0
            else:
                company_perm = 1
                #print company_perm

            if company_perm != 1:
                HTML.restriction_message()
                return

            print """<form name="edit_company" method=POST action="company_edit.cgi" 
                onSubmit="return check_company()">"""
            print """<div id="main">"""
            print """<div id="table_main">"""
            print """<br><div id="functionHead">Edit company <i>&quot;%s&quot;</i></div><br>""" % details[0][0]

            print_company_form(id, details, group)	

            print """</form>"""
            print """<p><div>* &nbsp; required field <br>"""
            print """** required when "Company is RIR" is checked. If there is more than 1 person please create a role object in your RIR database!</div>"""
            print """<div><input type=submit name=save value=save class=button></div></p>"""
            print """</div>""" # table_main
            print """</div>""" # main

    HTML.close_body()

main()
