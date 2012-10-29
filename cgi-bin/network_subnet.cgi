#!/usr/bin/python

"""
*****************************
IP@LL IP address management
Copyright 2007 poiss.priv.at
andi@poiss.priv.at
*****************************
"""

from Html_new import HtmlContent
from Ipall import IpallFunctions
import DBmy
import IpallUser
from Sessionclass import Session
import Whois
import IP
import IPy
import re
import os
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie


def print_newnet_form(parent_net, mask, net_perm):
    """print a HTML form for inserting a new network
    parent_net ... i.label, i.path, i.vrf, i.service_id, i.companies_id, c.is_lir FROM ipall_ip i, companies c"""

    net = IPy.IP(parent_net[0][0])
    if parent_net[0][3] and parent_net[0][3] != 0:
        service_id = int(parent_net[0][3])
        sql_is_peering = """SELECT is_peering FROM ipall_network_types WHERE id=%u """ % service_id
        is_peering = int(conn.get_data(sql_is_peering)[0][0])
    else:
        service_id = is_peering = 0
        
    print """<form name="new_subnet" method=POST action="network_subnet.cgi" onSubmit="return check_new_subnet('%s', '%s', '%s', '%s', '%s')">""" \
        % (str(id), ipall_dir, cgi_dir, str(parent_net[0][2]), str(parent_net[0][1]))
    print """<input type=hidden name=parent_id value=%u>""" % id
    print """<input type=hidden name=company value=%u>""" % int(parent_net[0][4])
    print """<input type=hidden name=parent_vrf value="%s">""" % str(parent_net[0][2])
    print """<input type=hidden name=parent_path value="%s">""" % str(parent_net[0][1])
    print """<input type=hidden name=net_perm value="%s">""" % str(net_perm)

    ### LEFT SIDE ###
    print """<div id="pos_left">"""
    ### network 
    print """<p>Network * <span id="nw_page"></span> <br>"""
    print """<span id="network_container">"""
    print """<select id="network" name="network" class="b_eingabefeld">"""
    print """<option value="None">select netmask first...</option>"""
    print """</select>"""
    print """</span> </p>"""
    ### network name
    print """<p>Network name</a> [Cust. Name (Cust. Nr)] *</br>"""
    print """<input type=text id="netname" name=netname onFocus="netNames('%s/a_network_names.cgi?%s&%s&%s','netname','info');" 
            class=b_eingabefeld maxlength="35"></p>""" % ( cgi_dir, str(service_id), str(parent_net[0][2]), str(id) )
    ### interface
    print """<p>Interface</br>""" 
    print """<input type=text name=interface class=b_eingabefeld maxlength=250></p>"""
    ### description
    print """<p>Description</br>"""
    print """<textarea name=description rows=6 class=b_eingabefeld></textarea></p>"""
    print """</div>""" # pos_left

    ### RIGHT SIDE ###
    print """<div id="pos_right">"""
    ### netmask 
    print """<p>Netmask *<br>"""
    print """<select id="netmask" name=netmask onChange="fillNetworks('%s', '%s');" 
        class=b_eingabefeld><option value=0>select prefix length</option>""" % ( cgi_dir, str(id) )
    if net.version() == 4:
        for r in range(net.prefixlen()+1, 33):
            if r != 31:
                print """<option value="%s">/%s</option>""" % ( str(r), str(r) )
    elif net.version() == 6:
        for r in range(net.prefixlen()+1, 129):
            if r != 127:
                print """<option value="%s">/%s</option>""" % ( str(r), str(r) ) 
    print """</select></p>"""
    ### aggregation line
    if group == 1 or rights[2] == 1:
        ### only admins can create aggregated network blocks
        print """<p>Network is allocated / aggregated<br>"""
        print """<input type=checkbox name=allocated> / <input type=checkbox name=aggregated></p>"""
    ### network types
    print """<p>Network type (<a href="javascript:void(0);" class="linkPurpleBold"
        onClick="ajaxFunction('%s/help_nettypes.cgi','typeinfo','1');" 
        id="toggle_help">descriptions</a>)<br>""" % ( cgi_dir )
    print """<select name=net_type id="net_type" onChange="ajaxFunction('%s/a_network_names.cgi?'+document.getElementById('net_type').value+'&%s&%s','info','1');" 
        onBlur="ajaxFunction('%s/a_network_names.cgi?'+document.getElementById('net_type').value,'peering_info','4');" 
        class=b_eingabefeld>""" % ( cgi_dir, str(parent_net[0][2]), str(id), cgi_dir )
    print_net_types(service_id)
    print """</select></p>"""
    ### info field
    print """<div id="typeinfo"></div>"""
    print """<div id="info" style="display: none;"> <img src="%s/images/indicator.gif"> </div>"""  % ( ipall_dir )
    print """</div>""" # pos_right

    print """<div id="pos_clear"><br></div>"""


    ### peering info 
    if is_peering == 1:
        print """<div id="peering_info" style="display: block;">"""
        print """<div class=TextPurpleBold>Peering Information</div>"""
    else:
        print """<div id="peering_info" style="display: none;">"""
        print """<div class=TextPurpleBold>Peering Information</div>"""
    print_peering_info(int(parent_net[0][4]))
    print """</div>""" #  peering_info
    
    ### save button line
    print """<p>* required field</p>"""
    print """<div>"""
    if parent_net[0][5] == 1:
        print """<span><input type=submit name=save value=save class=button></span>""" 
        print """<span><input type=checkbox name=ripe> Register network at RIR </span>"""
    else:
        print """<input type=submit name=save value=save class=button>"""
    print """</div>"""
    
    print """</form>"""
    ### initialise function
#    print """<script language="javascript"> toggleVisibility('typeinfo', 'toggle_help'); </script>"""



def print_net_types(service_id):
    """return dropdown box <option> with network types"""

    if service_id != 0:
        sql_first_net_type = """SELECT * FROM ipall_network_types WHERE id=%u""" % service_id
        first_net_type = conn.get_data(sql_first_net_type)
        print """<option value=%u>%s</option>""" % (int(first_net_type[0][0]), first_net_type[0][1])
        sql_net_types = """SELECT * FROM ipall_network_types  WHERE id != %u ORDER BY typename""" % service_id
        net_types = conn.get_data(sql_net_types)
    else:
        sql_net_types = """SELECT * FROM ipall_network_types ORDER BY typename"""
        net_types = conn.get_data(sql_net_types)
        print """<option value=0>select type</option>"""
    
    if net_types != ():
        if group == 1 or rights[2] == 1:
            for t in net_types:
                print """<option value=%u>%s</option>""" % (int(t[0]), t[1])
    else:
        return


def print_peering_info(companies_id):
    """print html form for peering information"""

    ### LEFT SIDE ###
    print """<div id="pos_left">"""
    print """<p><input type=checkbox id="is_peering" name="is_peering">BGP Peering</p>"""
    ### LEFT INSIDE ###
    print """<div id="pos_left_inside">"""
    print """<p>AS Number *<br>"""
    print """<input type=text id="as_nr" name=as_nr onChange="document.new_subnet.is_peering.checked=true;" class=b_eingabefeld_100></p>"""
    print """<p>Max prefix limit<br>"""
    print """<input type=text id="max_prefix" name=max_prefix class=b_eingabefeld_100></p>"""
    print """<p>Contact email<br>"""
    print """<input type=text id="contact_mail" name=contact_mail class=b_eingabefeld_100></p>"""
    print """<p>Available at routeserver<br>"""
    print """<input type=checkbox id="rs" name=rs></p>"""
    print """</div>""" # pos_left_inside
    ### RIGHT INSIDE ###
    print """<div id="pos_right_inside">"""
    print """<p>AS set<br>"""
    print """<input type=text id="as_set" name=as_set class=b_eingabefeld_100></p>"""
    print """<p>MD5 password<br>"""
    print """<input type=text id="md5" name=md5 class=b_eingabefeld_100></p>"""
    print """<p>Peering device *<br>"""
    print """<input type=text id="peering_device" name=peering_device class=b_eingabefeld_100></p>"""
    print """<p>Session is up<br>"""
    print """<input type=checkbox id="session_up" name=session_up></p>"""
    print """</div>""" # pos_right_inside
    print """<p>Comment<br>"""
    print """<textarea id="peer_comment" name=peer_comment rows=3 class=b_eingabefeld></textarea></p>"""
    print """</div>""" # pos_left

    ### LEFT SIDE ###
    print """<div id="pos_right">"""
    if group != 1:
        companies_id = company_id
    print """ 
        <div id="private_as" onClick="ajaxFunction('%s/a_private_as_nr.cgi?%s','private_as','1');" 
        align=center style="border: solid 1px #CCCCCC;">
        Click <b>here</b> to see private AS numbers which are already in use</div>""" % ( cgi_dir, companies_id )
    print """</div>""" # pos_right        

    print """<div id="pos_clear"><br></div>"""


def main():
    """create a new subnet"""

    ### variables
    global current_user, rights, group, company_id, id, conn, network, mask, referer, cgi_dir, ipall_dir, ripe_mail
    formdata = cgi.FieldStorage()
    net_perm = [0,0,0,0]
    netname = description = interface = net_type = as_set = max_prefix = md5 = contact_mail = peering_device = peer_comment = "NULL"
    ripe = allocated = aggregated = is_peering = rs = session_up = "off"
    peer_id = send = company = 0


    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        #if len(qs.split("&")) == 1:
        try:
            id = int(qs.split("&")[0])
            mask = 0
            network = "None"
        #else:
        except:
            id = 0
            mask = 0
            network = "None"
    else:
        id = 0
        mask = 0
        network = "None"

    try:
        ### network info
        if formdata.has_key("uri"):
            uri = str(formdata['uri'].value)
        if formdata.has_key("net_perm"):
            net_perm = str(formdata['net_perm'].value)
        if formdata.has_key("company"):
            company = int(formdata['company'].value)
        if formdata.has_key("parent_id"):
            id = int(formdata['parent_id'].value)
        if formdata.has_key("parent_vrf"):
            parent_vrf = str(formdata['parent_vrf'].value)
        if formdata.has_key("parent_path"):
            parent_path = str(formdata['parent_path'].value)
        if formdata.has_key("network"):
            network = str(formdata['network'].value)
        if formdata.has_key("netname"):
            netname = str(formdata['netname'].value)
        if formdata.has_key("allocated"):
            allocated = str(formdata['allocated'].value)
        if formdata.has_key("aggregated"):
            aggregated = str(formdata['aggregated'].value)
        if formdata.has_key("description"):
            description = str(formdata['description'].value)
        if formdata.has_key("interface"):
            interface = str(formdata['interface'].value)
        if formdata.has_key("net_type"):
            net_type = int(formdata['net_type'].value)
        if formdata.has_key("ripe"):
            ripe = str(formdata['ripe'].value)
        ### device info
        if formdata.has_key("device_id"):
            device_id = int(formdata['device_id'].value)
        ### peering info
        if formdata.has_key("is_peering"):
            is_peering = str(formdata['is_peering'].value)
        if formdata.has_key("as_nr"):
            as_nr = str(formdata['as_nr'].value)
        if formdata.has_key("as_set"):
            as_set = str(formdata['as_set'].value)
        if formdata.has_key("max_prefix"):
            max_prefix = str(formdata['max_prefix'].value)
        if formdata.has_key("md5"):
            md5 = str(formdata['md5'].value)
        if formdata.has_key("contact_mail"):
            contact_mail = str(formdata['contact_mail'].value)
        if formdata.has_key("peering_device"):
            peering_device = str(formdata['peering_device'].value)
        if formdata.has_key("rs"):
            rs = str(formdata['rs'].value)
        if formdata.has_key("session_up"):
            session_up = str(formdata['session_up'].value)
        if formdata.has_key("peer_comment"):
            peer_comment = str(formdata['peer_comment'].value)
    except:
        print """<script language="javascript">alert("Value parse error, sorry!"); history.back();</script> """

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
    ripe_mail = cfg['Server']['ripe_mail']
    if group == 0:
        HTML.restriction_message(1)
        HTML.popup_footer()
        return

    if id == 0:   ### no network is selected
        HTML.error_message("No network selected!")
        HTML.close_body()
        return

    f = IpallFunctions(conn, current_user, group, company_id)
    ### SAVE button has been pressed
    if formdata.has_key("save"):
        try:
            net = IPy.IP(network)
        except:
            print """<script language="javascript">alert("No valid network!"); history.back();</script> """


        ### check if there is already such a network
        chk_net = f.check_new_subnet(network, parent_vrf)
#        sql_check = """SELECT id FROM ipall_ip WHERE label LIKE '%s' AND vrf='%s' """ % (network, parent_vrf)
#        chk_net = conn.get_data(sql_check)
        if chk_net != ():
            print """<script language="javascript">alert("This network already exists!"); history.back();</script> """
            return

        if is_peering == "on":
            ### parse peering info values
            as_nr = int(as_nr);
            if as_set == "NULL" or as_set == None:
                as_set = as_set
            else:
                as_set = "'" + as_set + "'"
            if max_prefix == "NULL" or max_prefix == None or max_prefix == 0:
                max_prefix = "NULL"
            if md5 != "NULL": md5 = "'" + md5 + "'";
            if contact_mail != "NULL": contact_mail = "'" + contact_mail + "'";
            if peering_device != "NULL": peering_device = "'" + peering_device + "'";
            if rs == "on": rs = 1;
            else: rs = 0;
            if session_up == "on": session_up = 1;
            else: session_up = 0;
            if peer_comment != "NULL": peer_comment = "'" + peer_comment + "'";

            ### insert peering info and get id
            sql_peering = """INSERT INTO ipall_peering_info VALUES ('', %u, %s, %s, %u, %u, %s, %s, %s, %s)""" \
                % (as_nr, as_set, md5, rs, session_up, contact_mail, peer_comment, peering_device, max_prefix)
            #print "peering: %s<br>" % sql_peering
            peer_id = conn.insert_data(sql_peering)
            #peer_id = 1

            ### LOGGING
            sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_peering_info', "%s", %u)""" % (current_user, sql_peering, company)
            log = conn.update_data(sql_log)
            #log = 1

        if description != "NULL": description = "'" + description + "'";
        if interface != "NULL": interface = "'" + interface.lower().replace(" ", "") + "'"
        ### only admins (group id = 1) can create aggregated networks
        if allocated == "on" and group == 1: allocated = 1;
        else: allocated = 0;
        if aggregated == "on" and group == 1: aggregated = 1;
        else: aggregated = 0;

        if allocated == 1 and net_type == "NULL": print """<script language="javascript">alert("You have to select a network type!"); history.back();</script> """; return;
        if net_type == 0: 
            HTML.error_message("Information: You did not select a network type!")
            net_type = "NULL"

        if peer_id == 0:
            sql_ins = """INSERT INTO ipall_ip VALUES ('', %u, '%s', %u, '%s', %s, '%s', 0, NULL, '%s', %u, NULL, NULL, %s, %s, %s, %u)""" \
                % (id, network, int(net.strDec()), netname, description, parent_path, parent_vrf, aggregated, net_type, allocated, interface, int(company)) 
        else:
            sql_ins = """INSERT INTO ipall_ip VALUES ('', %u, '%s', %u, '%s', %s, '%s', 0, %u, '%s', %u, NULL, NULL, %s, %s, %s, %u)""" \
                % (id, network, int(net.strDec()), netname, description, parent_path, peer_id, parent_vrf, aggregated, net_type, allocated, interface, int(company)) 
        last_id = conn.insert_data(sql_ins)

        ### LOGGING
        id_link = """<a href='javascript:void(0);' onClick=popup(\'%s/network_view.cgi?%s\') class=LinkPurpleBold>id: %s</a> - """ \
            % ( cgi_dir, str(last_id), str(last_id) )
        log_string = id_link + sql_ins
        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_ip', "%s", %u)""" % (current_user, log_string, company)
        log = conn.update_data(sql_log)

        if last_id != 0:
            path = parent_path + ":" + str(last_id)

            ### set the path field correctly
            sql_update = """UPDATE ipall_ip SET path='%s' WHERE id=%u """ % (str(path), int(last_id))
            update = conn.update_data(sql_update)
            sql_upd_parent = """UPDATE ipall_ip SET subnetted=1 WHERE id=%u """ % id
            update2 = conn.update_data(sql_upd_parent)

            ### create mail for register network at ripe.net
            if ripe == "on":
                uri = "javascript:parent.location.reload(1)"
                register = Whois.whois()
                register.print_form( company, net.net(), net.broadcast(), net.prefixlen(), netname, uri )

            if update != 0 and update2 != 0:
                if ripe != "on":
                    HTML.notify_message("subnet created...")
                else:
                    HTML.notify_message("Network has been added successfully!")
            else:
                HTML.error_message("""An error during "update path" has occured!""")
        else:   ### check_ins = 0
            HTML.error_message("""An error during "insert prefix" has occured!""")


    else:   ### "SAVE" has not been pressed
        # get information of the parent network
        parent_net = f.get_parent_net(id)

        ### get permissions of the group to the network
        if group == 1 or rights[2] == 1:
            net_perm = 1
        else:
            net_perm = conn.get_net_permissions(parent_net[0][1], group)
            if net_perm == () or net_perm == "":
                net_perm = 0
            else:
                net_perm = net_perm[2]

        if net_perm != 1:
            HTML.restriction_message(1)
            HTML.popup_footer()
            return
        
        print """<div id="main">"""
        print """<div id="table_main">"""
        print """<br><div id="functionHead">Create subnet of: %s</div>""" % parent_net[0][0]
        
        print_newnet_form(parent_net, mask, net_perm)

        print """</div>""" #table_main
        print """</div>""" #main
        print """<script language="javascript">
            window.addEvent('domready', function() {  
                ajaxFunction('%s/help_nettypes.cgi','typeinfo','1');
                toggleVisibility('typeinfo', 'toggle_help');
                $('foot').set('html', parent.window.getElementById('net247_247').text);
            });
            </script>""" % ( cgi_dir )

    
    HTML.popup_footer()

main()
