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


def print_newtype_form():
    """print a HTML form for inserting a new nettype"""

    print """<form name="new_type" method=POST action="new_nettype.cgi"
        onSubmit="return check_nettype()">"""

    ### LEFT SIDE
    print """<div>"""
    print """<p>Title *<br>"""
    print """<input type=text id="typename" name=typename size=33 class=b_eingabefeld maxlength=50></p>"""

    print """<p>Description<br>"""
    print """<input type=text id="description" name=description size=33 class=b_eingabefeld maxlength=250></p>"""

    print """<p>Font color <span id="colorpicker301" class="colorpicker301"></span>
    <img src="%s/images/sel_color.gif" onclick="showColorGrid3('font','font_color');" border="0" style="cursor:pointer" 
    alt="select color" title="select color"><br>""" % ( ipall_dir )
    print """<input type=text name=font id="font" size=10 class=b_eingabefeld_100 maxlength=7 value="%s">
    <input type=text id="font_color" size=10 class=b_eingabefeld_color value="" style="background-color: #000000;">
    </p>""" % ( "#000000" )

    print """<p>Background color <span id="colorpicker301" class="colorpicker301"></span>
    <img src="%s/images/sel_color.gif" onclick="showColorGrid3('bg','bg_color');" border="0" style="cursor:pointer" 
    alt="select color" title="select color"><br>""" % ( ipall_dir )
    print """<input type=text name=bg id="bg" size=10 class=b_eingabefeld_100 maxlength=7 value="%s">
    <input type=text id="bg_color" size=10 class=b_eingabefeld_color value="" style="background-color: #FFFFFF;">
    </p>""" % ( "#FFFFFF" )

    print """<p>Subnets could have BGP Peerings <br>"""
    print """<input type=checkbox id="is_peering" name=is_peering></p>"""

    print """<p><input type=submit id="save" name=save value=save class=button></p>"""
    print """</div>"""
    print """</form>"""
            

def main():
    """create a new nettype"""

    global vrf, conn, cgi_dir, ipall_dir
    formdata = cgi.FieldStorage()
    typename = description = "" 
    font = "#000000"
    bg = "#FFFFFF"
    is_peering = "off"
    
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
    HTML.simple_header(1, 0)

    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    else:
        HTML.popup_body()

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']
    rights = user.get_rights()
    
    if group == 0 or rights[2] == 0:
        HTML.restriction_message()
        return
    else:
        try:
            if formdata.has_key("typename"):
                typename = str(formdata['typename'].value)
            if formdata.has_key("description"):
                description = str(formdata['description'].value)
            if formdata.has_key("font"):
                font = str(formdata['font'].value)
            if formdata.has_key("bg"):
                bg = str(formdata['bg'].value)
            if formdata.has_key("is_peering"):
                is_peering = str(formdata['is_peering'].value)
        except:
            print """<script language="javascript">alert("Please fill out all fields marked with asterisks!"); history.back();</script> """

    if group != 1 and rights[1] != 1 and rights[2] != 1: 
        HTML.restriction_message()
        return

    ### SAVE button has been pressed
    if formdata.has_key("save"):
        print "<br>"

        if is_peering == "on":
            is_peering = 1
        else:
            is_peering = 0

        sql_check = """SELECT id FROM ipall_network_types WHERE typename='%s' """ \
            % (typename)
        check = conn.get_data(sql_check)
        
        if check != ():
            HTML.error_message("Nettype already exists!")
            return
        else:
            sql_type = """INSERT INTO `ipall_network_types` 
                ( `id` , `typename` , `description`, `is_peering`, `font_color`, `bg_color` ) 
                VALUES ('', '%s', '%s', %u, '%s', '%s' )""" \
                % ( typename, description, int(is_peering), font, bg )
            type_ok = conn.update_data(sql_type)
            

        ### LOGGING
        log_string = sql_type
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_network_types', "%s", 0)""" % (current_user, log_string)
        log = conn.insert_data(sql_log)
        
        if type_ok != 0:
            HTML.notify_message("network type created...")
            linktext = """<a href="%s/mgmt_nettypes.cgi" class=LinkPurpleBold> << back</a>""" % cgi_dir
            HTML.notify_message(linktext)
        else:
            HTML.error_message("An error has occured!")
        
        HTML.close_body()
        
    ### SAVE button has not been pressed
    else:	
        print """<br>"""
        print """<div id="main">"""
        print """<div id="table_main">"""
        print """<div id="functionHead">Insert a new nettype</div>""" 

        print_newtype_form()

        print """<div>&nbsp;</div>"""
        print """<div>* required field</div>"""
        print """</div>""" # table_main 
        print """</div>""" # main 

        HTML.popup_footer()

main()
