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



def print_type_form(id, details):
    """print html form to edit nettype details
    details: typename, description"""

    print """<input type=hidden name=id value="%s">""" % (id)

    print """<div>"""
    print """<p>Title *<br>"""
    print """<input type=text id="typename" name=typename size=33 class=b_eingabefeld maxlength=50 value="%s"></p>""" % (details[0][0])
    print """<p>Description<br>"""
    print """<input type=text id="description" name=description size=33 class=b_eingabefeld maxlength=250 value="%s"></p>""" % (details[0][1])

    print """<p>Font color <span id="colorpicker301" class="colorpicker301"></span>
    <img src="%s/images/sel_color.gif" onclick="showColorGrid3('font','font_color');" border="0" style="cursor:pointer" 
    alt="select color" title="select color"><br>""" % ( ipall_dir )
    print """<input type=text name=font id="font" size=10 class=b_eingabefeld_100 maxlength=7 value="%s">
    <input type=text id="font_color" size=10 class=b_eingabefeld_color value="" style="background-color: %s;">
    </p>""" % ( details[0][3], details[0][3] )

    print """<p>Background color <span id="colorpicker301" class="colorpicker301"></span>
    <img src="%s/images/sel_color.gif" onclick="showColorGrid3('bg','bg_color');" border="0" style="cursor:pointer" 
    alt="select color" title="select color"><br>""" % ( ipall_dir )
    print """<input type=text name=bg id="bg" size=10 class=b_eingabefeld_100 maxlength=7 value="%s">
    <input type=text id="bg_color" size=10 class=b_eingabefeld_color value="" style="background-color: %s;">
    </p>""" % ( details[0][4], details[0][4] )
            
    if int(id) > 11:
        print """<p>Subnets could have BGP Peerings<br>"""
        if details[0][2] == 1:
            print """<input type=checkbox id="is_peering" name=is_peering checked></p>"""
        else:
            print """<input type=checkbox id="is_peering" name=is_peering></p>"""
    print """</div>"""


def main():
    """entry point for executing IP@LL - edit vrf details"""

    ### definitions of variables
    global id, conn, rights, cgi_dir, ipall_dir
    typename = description = "" 
    font = "#000000"
    bg = "#FFFFFF"
    is_peering = "off"
    id = 0

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
    HTML.simple_header(1)
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
        return

    if formdata.has_key("save"):
        print "<br>"

        if is_peering == "on":
            is_peering = 1
        else:
            is_peering = 0

        sql_update = """UPDATE ipall_network_types SET typename='%s', description='%s', is_peering=%u, 
            font_color='%s', bg_color='%s' WHERE id=%u """ \
            % ( typename, description, is_peering, font, bg, id )
        update = conn.update_data(sql_update)

        ### LOGGING
        log_string = sql_update
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_network_types', "%s", 0)""" % (current_user, log_string)
        log = conn.insert_data(sql_log)

        if update != 0:
            HTML.notify_message("type updated...")
            linktext = """<a href="%s/mgmt_nettypes.cgi" class=LinkPurpleBold> << back</a>""" % cgi_dir
            HTML.notify_message(linktext)
        else:
            HTML.error_message("an error has occured...")

        HTML.close_body()

    else: ### SAVE key was not pressed
        query = """SELECT typename, description, is_peering, font_color, bg_color FROM ipall_network_types WHERE id=%u """ % (int(id))
        details = conn.get_data(query)

        if details == () or details == None or details == 0:
            HTML.error_message("Nothing to display!")
            return
        else:
            if group != 1 and rights[2] != 1:
                    user_perm = 0
            else:
                user_perm = 1
                #print user_perm

            if user_perm != 1:
                HTML.restriction_message()
                return

            print """<div id="main">"""
            print """<div id="table_main">"""
            print """<div id="functionHead">Edit nettype details of <i>&quot;%s&quot;</i></div>"""  % details[0][0]
            print """<form name="edit_nettype" method=POST action="nettype_edit.cgi"
                onSubmit="return check_nettype()">"""

            print_type_form(id, details)

            print """<div><input type=submit id="save" name=save value=save class=button></div>"""
            print """</form>"""
            print """<div>&nbsp;</div>"""
            print """<div>* required field</div>"""
            print """</div>""" # table_main 
            print """</div>""" # main 

        HTML.popup_footer()

main()
