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
import os
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie



def print_network_form(details, f, group, cgi_dir):
    """print html form to edit network details"""

    print """<input type=hidden name=net_id value=%u>""" % int(details[0][0])
    print """<input type=hidden name=company value=%u>""" % int(details[0][11])

    ### LEFT SIDE
    print """<div id="pos_left_small">"""
    print """<div class="lineOdd">Network Name *</div>"""
    print """<div class="lineEven">Network Type</div>"""
    print """<div class="lineOdd">Interface</div>"""
    print """<div class="lineEven">Allocated</div>"""
    print """<div class="lineOdd">Aggregated</div>"""
    print """<div class="lineEven">Network Description</div>"""
    print """</div>""" # left side

    ### RIGHT SIDE
    print """<div id="pos_right_wide">"""
    print """<div class="lineOdd"><input type=text id="net_name" name=net_name 
        class=b_eingabefeld value="%s" maxlength=35></div>""" % details[0][2]
    print """<div class="lineEven"><select id="net_type" name=net_type class=b_eingabefeld 
        onChange="ajaxFunction('%s/a_network_names.cgi?'+document.getElementById('net_type').value,'peering_info','4');">""" % ( cgi_dir )
    if details[0][7] != 0 and details[0][7] != None:
        f.print_net_types(details[0][7])
    if group == 1 or rights[2] == 1:
        f.print_net_types()
    print """</select>"""
    print """<a href="javascript:void(0);" id="toggle_help">type definitions...</a>"""
    print """</div>""" # net_type
    if details[0][9] == "" or details[0][9] == None:
        print """<div class="lineOdd"><input type=text id="interface" name=interface class=b_eingabefeld value="" maxlength=250></div>"""
    else:
        print """<div class="lineOdd"><input type=text id="interface" name=interface class=b_eingabefeld value="%s" maxlength=250></div>""" % details[0][9]
    if group == 1 or rights[2] == 1:
        if details[0][8] == 1:
            print """<div class="lineEven"><input type=checkbox id="allocated" name=allocated checked></div>"""
        else:
            print """<div class="lineEven"><input type=checkbox id="allocated" name=allocated></div>"""
        if details[0][5] == 1:
            print """<div class="lineOdd"><input type=checkbox id="aggregated" name=aggregated checked></div>"""
        else:
            print """<div class="lineOdd"><input type=checkbox id="aggregated" name=aggregated></div>"""
    print """<div class="lineEven"><textarea id="net_description" name=net_description 
        class=b_eingabefeld>%s</textarea></div>""" % details[0][3]
    print """</div>""" #right side

    print """<div id="pos_clear">&nbsp;</div>"""

    print """<div id="info">test</div>"""


def print_peering_form(peering_info):
    """print html form for peering information"""

    print """<input type=hidden name=peering_info_id value=%u>""" % int(peering_info[0][0])
    ### LEFT SIDE
    print """<div id="pos_left_small">"""
    print """<div class="lineOdd">AS Number *</div>"""
    print """<div class="lineEven">AS SET</div>"""
    print """<div class="lineOdd">Max Prefix</div>"""
    print """<div class="lineEven">MD5 Password</div>"""
    print """<div class="lineOdd">Contact Email</div>"""
    print """<div class="lineEven">Peering Device *</div>"""
    print """<div class="lineOdd">Available at Routeserver</div>"""
    print """<div class="lineEven">Session is up</div>"""
    print """<div class="lineOdd">Comment</div>"""
    print """</div>""" # left side

    ### RIGHT SIDE
    print """<div id="pos_right_wide">"""
    print """<div class="lineOdd"><input type=text id="as_nr" name=as_nr class=b_eingabefeld_100 value=%u></div>""" % int(peering_info[0][1])
    if peering_info[0][2] == "" or peering_info[0][2] == None:
        print """<div class="lineEven"><input type=text id="as_set" name=as_set class=b_eingabefeld_100 value=""></div>"""
    else:
        print """<div class="lineEven"><input type=text id="as_set" name=as_set class=b_eingabefeld_100 value="%s"></div>""" % str(peering_info[0][2])
    if peering_info[0][9] == "" or peering_info[0][9] == None:
        print """<div class="lineOdd"><input type=text id="max_prefix" name=max_prefix class=b_eingabefeld_100 value=""></div>"""
    else:
        print """<div class="lineOdd"><input type=text id="max_prefix" name=max_prefix class=b_eingabefeld_100 value="%s"></div>""" % str(peering_info[0][9])
    if peering_info[0][3] == "" or peering_info[0][3] == None:
        print """<div class="lineEven"><input type=text id="md5" name=md5 class=b_eingabefeld_100 value=""></div>""" 
    else:
        print """<div class="lineEven"><input type=text id="md5" name=md5 class=b_eingabefeld_100 value="%s"></div>""" % str(peering_info[0][3])
    if peering_info[0][6] == "" or peering_info[0][6] == None:
        print """<div class="lineOdd"><input type=text id="contact_mail" name=contact_mail class=b_eingabefeld_100 value=""></div>"""
    else:
        print """<div class="lineOdd"><input type=text id="contact_mail" name=contact_mail class=b_eingabefeld_100 value="%s"></div>""" % str(peering_info[0][6])
    if peering_info[0][8] == "" or peering_info[0][8] == None:
        print """<div class="lineEven"><input type=text id="peer_device" name=peer_device class=b_eingabefeld_100 value=""></div>"""
    else:
        print """<div class="lineEven"><input type=text id="peer_device" name=peer_device class=b_eingabefeld_100 value="%s"></div>""" % str(peering_info[0][8])
    if peering_info[0][4] == 1:
        print """<div class="lineOdd"><input type=checkbox id="rs" name=rs checked></div>"""
    else:
        print """<div class="lineOdd"><input type=checkbox id="rs" name=rs></div>"""
    if peering_info[0][5] == 1:
        print """<div class="lineEven"><input type=checkbox id="session_up" name=session_up checked></div>"""
    else:
        print """<div class="lineEven"><input type=checkbox id="session_up" name=session_up></div>"""
    print """<div class="lineOdd"><textarea id="peer_comment" name=peer_comment class=b_eingabefeld>%s</textarea></div>""" % str(peering_info[0][7])
    print """</div>""" # right side

    print """<div id="pos_clear">&nbsp;</div>"""


def main():
    """entry point for executing IPALL - edit network details"""

    ### definitions of variables
    formdata = cgi.FieldStorage()
    as_nr = company = 0
    device_id = 1
    net_name = net_description = net_type = peering_info_id = interface = as_set = md5 = max_prefix = contact_mail = peer_comment = peer_device = "NULL"
    rs = session_up = allocated = aggregated = "off"

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        try:
            id = int(qs.split("&")[0])
        except:
            id = 0
    else:
        id = 0

    try:
        ### network info
        if formdata.has_key("uri"):
            uri = str(formdata['uri'].value)
        if formdata.has_key("net_id"):
            id = int(formdata['net_id'].value)
        if formdata.has_key("company"):
            company = int(formdata['company'].value)
        if formdata.has_key("net_name"):
            net_name = str(formdata['net_name'].value)
        if formdata.has_key("net_description"):
            net_description = str(formdata['net_description'].value)
        if formdata.has_key("interface"):
            interface = str(formdata['interface'].value)
        if formdata.has_key("net_type"):
            net_type = int(formdata['net_type'].value)
        if formdata.has_key("allocated"):
            allocated = str(formdata['allocated'].value)
        if formdata.has_key("aggregated"):
            aggregated = str(formdata['aggregated'].value)
        ### peering info
        if formdata.has_key("peering_info_id"):
            peering_info_id = int(formdata['peering_info_id'].value)
        if formdata.has_key("as_nr"):
            as_nr = str(formdata['as_nr'].value)
        if formdata.has_key("as_set"):
            as_set = str(formdata['as_set'].value)
        if formdata.has_key("md5"):
            md5 = str(formdata['md5'].value)
        if formdata.has_key("max_prefix"):
            max_prefix = str(formdata['max_prefix'].value)
        if formdata.has_key("contact_mail"):
            contact_mail = str(formdata['contact_mail'].value) 
        if formdata.has_key("peer_device"):
            peer_device = str(formdata['peer_device'].value) 
        if formdata.has_key("rs"): 
            rs = str(formdata['rs'].value)
        if formdata.has_key("session_up"):
            session_up = str(formdata['session_up'].value)
        if formdata.has_key("peer_comment"):
            peer_comment = str(formdata['peer_comment'].value)
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

    ### User
    s = Session(conn)
    current_user = s.check_user()
    HTML.simple_header()
    if current_user == "":
        HTML.error_message("nothing to display...")
        HTML.close_body()
        return
    else:
        HTML.popup_body()

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    cgi_dir = cfg['Server']['cgi_dir']

    if group == 0:
        HTML.restriction_message(1)
        HTML.popup_footer()
        return

    f = IpallFunctions(conn, current_user, group, company_id)

    if formdata.has_key("save"):
        if net_type == 0: net_type = "NULL";
        if net_description == "NULL" or net_description == "None": net_description = "NULL";
        else: net_description = "'" + net_description + "'"
        if interface == "NULL" or interface == "None": interface = "NULL";
        else: interface = "'" + interface.lower().replace(" ","") + "'"
        if allocated == "on": allocated = 1;
        else: allocated = 0
        if aggregated == "on": aggregated = 1;
        else: aggregated = 0

        #check if the selected network type could have BGP peerings
        chk_peer = f.check_is_peering(net_type, 2)
        #print chk_peer
        if chk_peer == 0 and peering_info_id != 0: 
            peering_info_id == "NULL"
            #print peering_info_id
            f.delete_peering(peering_info_id, id)

        if peering_info_id != "NULL":
            as_nr = int(as_nr);
            if as_set == "NULL" or as_set == "": as_set = "NULL";
            else: as_set = "'" + as_set + "'"
            if md5 == "NULL" or md5 == "None": md5 = "NULL";
            else: md5 = "'" + md5 + "'"
            if max_prefix == "NULL" or max_prefix == "None": max_prefix = "NULL";
            else: max_prefix = int(max_prefix);
            if contact_mail == "NULL" or contact_mail == "None": contact_mail = "NULL";
            else: contact_mail = "'" + contact_mail + "'"
            #print peer_comment.find("\""), peer_comment.find("'")
            if peer_comment == "NULL" or peer_comment == "None": peer_comment = "NULL";
            else: peer_comment = "'" + peer_comment + "'"
            if rs == "on": rs = 1;
            else: rs = 0
            if session_up == "on": session_up = 1;
            else: session_up = 0
            peer_device = "'" + peer_device + "'"

            if peering_info_id == 0:
                upd_peer = f.insert_peering(as_nr, as_set, md5, rs, session_up, contact_mail, peer_comment, peer_device, max_prefix, id)
            else:
                upd_peer = f.update_peering(as_nr, as_set, md5, rs, session_up, contact_mail, peer_comment, peer_device, max_prefix, peering_info_id)
            if upd_peer != 0:
                HTML.notify_message("Peering information has been updated successfully!")
            else:
                HTML.error_message("Peering information: An error has occured!")
        else:
            upd_peer = log_peer = 1 # no error can occur here

        update = f.update_network(net_name, net_description, aggregated, net_type, allocated, interface, id)
        if update != 0 and upd_peer != 0:
            HTML.notify_message("<div class=TextPurpleBold>changes applied...</div>")
        else:
            HTML.error_message("An error has occured!");

    else: ### SAVE key was not pressed
        details = f.get_net_info(2, id)
        rights = user.get_rights(details[0][10]) 
        if details == () or details == None:
            print """<p class=TextPurpleBold> Nothing to display</p>"""
            return
        else:
            if group != 1 and rights[2] != 1:
                net_perm = conn.get_net_permissions(str(details[0][6]), group)
                if net_perm == () or net_perm == "":
                    net_perm = 0
                else:
                    net_perm = net_perm[1]
            else:
                net_perm = 1

            if net_perm != 1:
                HTML.restriction_message(1)
                HTML.popup_footer()
                return

            peering_info_id = details[0][4]
            if peering_info_id != 0 and peering_info_id != None:
                peering_info = f.get_peering_info(peering_info_id)
            else:
                peering_info = ()
            
            print """<div id="main">"""
            print """<div id="table_main">"""

            print """<form name="edit_net" method=POST action="network_edit.cgi"
                onSubmit="return check_edit_subnet();">"""
            ### HEADING
            print """<div id="functionHead">"""
            print """<span>Network</span>""" # heading
            print """<span id="pos_right_wide">%s""" % details[0][1]
            print """</span>""" # right side
            print """</div>""" # functionHead

            print_network_form(details, f, group, cgi_dir) 
            if peering_info_id:
                print """<div id="peering_info" style="display: block">"""
            else:
                print """<div id="peering_info" style="display: none">"""
                peering_info = ((0,0,'','',0,0,'','','',0),)
            print_peering_form(peering_info)
            print """</div>"""
            print """<div>"""
            print """<span>* required field</span>"""
            print """<span id="pos_right_wide"><input type=submit name=save value=save class=button></span>"""
            print """</div>"""
            print """</form>"""
            print """</div>""" # table_main 
            print """</div>""" # main 
            print """<script language="javascript">
                window.addEvent('domready', function() {  
                    ajaxFunction('%s/help_nettypes.cgi','info','1');
                    toggleVisibility('info', 'toggle_help');
                });
                </script>""" % ( cgi_dir )

    
    HTML.popup_footer()


main()
