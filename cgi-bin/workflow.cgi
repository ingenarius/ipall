#!/usr/bin/python

import HTML
import DBmy
import IpallUser
import Session
import IP
import IPy
import os
import cgi
import Whois
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie


def get_sel_type(service_id): 
    """fetch the selected type name"""
    
    sql_type = """SELECT typename FROM ipall_network_types WHERE id=%u""" % int(service_id)
    type = conn.get_data(sql_type)
    
    return type[0]


def print_net_types(vrf, service_id):
    """return dropdown box <option> with network types"""

    sql_net_types = """SELECT id, typename FROM ipall_network_types ORDER BY typename"""
    nettypes = conn.get_data(sql_net_types)

    print """<form name="edit_permissions" method=POST action="workflow.cgi">"""
    print """<table width=100% border=0 cellspacing=5 cellpadding=0 class=TextPurple>"""
    print """<tr height=25>"""
    print """<td>"""
    print """<select name=group ONCHANGE="location = this.options[this.selectedIndex].value;" class=b_eingabefeld>"""
    #nettypes = get_net_types()
    if service_id == 0:
        print """<option value="%s/workflow.cgi?%s&%s&%s&%s">select network type</option>""" % (cgi_dir, user_md5, vrf, "0", "0")
    else:
        type = get_sel_type(service_id)
        print """<option value="%s/workflow.cgi?%s&%s&%s&%s">%s</option>""" % (cgi_dir, user_md5, vrf, str(service_id), "0", type[0])
        print """<option value="%s/workflow.cgi?%s&%s&%s&%s">select network type</option>""" % (cgi_dir, user_md5, vrf, "0", "0")
    for t in nettypes:
        if t[0] != service_id:
            print """<option value="%s/workflow.cgi?%s&%s&%s&%s">%s</option>""" % (cgi_dir, user_md5, vrf, str(t[0]), "0", str(t[1]))
    print """</select>"""
    print """<a href="%s/help_nettypes.cgi" title="descriptions for net types">help</a>""" % cgi_dir
    print """</td>"""
#    print """<td>%s</td>""" % net[2]
    print """</tr>"""
    print """</table>"""
    print """</form>"""


def get_networks(service_id):
    """search for networks assigned to certain net types"""

    sql_nets = """SELECT id, label, net_name FROM ipall_ip WHERE service_id=%u AND allocated=1 ORDER BY address""" % (int(service_id))
    nets = conn.get_data(sql_nets)

    return nets


def print_nets_of_type(vrf, service_id, product_id, if_id):
    """print a HTML form with the networks of the selected type"""

    print """<form name="new_subnet" method=POST action="workflow.cgi">"""
    print """<table width=550 border=0 cellspacing=5 cellpadding=0 class=TextPurple>"""
    print """<tr>"""
    print """<td><select ONCHANGE="location = this.options[this.selectedIndex].value;" class=b_eingabefeld_400>"""
    print """<option value="%s/workflow.cgi?%s&%s&%s&%s&%s&%s">select network</option>""" \
	% (cgi_dir, user_md5, vrf, str(service_id), str(product_id), str(if_id), "0")

    nets = get_networks(service_id)
    for n in nets:
	print """<option value="%s/workflow.cgi?%s&%s&%s&%s&%s&%s">%s (%s)</option>""" \
	    % (cgi_dir, user_md5, vrf, str(service_id), str(product_id), str(if_id), n[0], n[1], n[2])

    print """</select></td>"""
    print """</tr>"""
    print """</table>"""
    print """</form>"""


def print_newnet_form(parent_net, id, mask, network, vrf, service_id, product_id, if_id):
    """print a HTML form for inserting a new network"""
    
    net = IPy.IP(parent_net[0][0])
    print """<form name="new_subnet" method=POST action="workflow.cgi">"""
    print """<table width=550 border=0 cellspacing=5 cellpadding=0 class=TextPurple>"""
    print """<tr>"""
    
    ### hidden values
    #print """<input type=hidden name=current_user value="%s">""" % current_user
    print """<input type=hidden name=parent_id value=%u>""" % id
    print """<input type=hidden name=parent_vrf value="%s">""" % str(parent_net[0][2])
    print """<input type=hidden name=parent_path value="%s">""" % str(parent_net[0][1])
    print """<input type=hidden name=service_id value=%u>""" % int(service_id)
    print """<input type=hidden name=product_id value=%u>""" % int(product_id)
    print """<input type=hidden name=if_id value=%u>""" % int(if_id)
    
    ### network dropdown box or text box (if no netmask or a network is selected)
    print """<td width=50%>Network</td>"""
    print """<td>Netmask</td>"""
    print """</tr><tr>"""
    if mask == 0:
        print """<td><input type=text name=network class=b_eingabefeld readonly></td>"""
    elif mask != 0 and network == "None":
        print """<td><select ONCHANGE="location = this.options[this.selectedIndex].value;" class=b_eingabefeld>"""
        print """<option value="%s/workflow.cgi?%s&%s&%s&%s&%s&%s&%s&%s">select network</option>""" \
	    % (cgi_dir, user_md5, vrf, service_id, product_id, if_id, id, mask, "None")
        new_nets = IP.calc_networks(id, net, mask, conn)
	for n in new_nets:
	    print """<option value="%s/workflow.cgi?%s&%s&%s&%s&%s&%s&%s&%s">%s</option>""" \
		% (cgi_dir, user_md5, vrf, service_id, product_id, if_id, id, mask, n, n)
        print """</select>"""
    else:
        print """<td><input type=text name=network value="%s" readonly class=b_eingabefeld>""" % network
    print """</td>"""
    
    ### netmask dropdown box
    if mask == 0: 
        print """<td><select name=netmask ONCHANGE="location = this.options[this.selectedIndex].value;" class=b_eingabefeld><option value=0>select prefix length</option>"""
    else:
        print """<td><select name=netmask ONCHANGE="location = this.options[this.selectedIndex].value;" class=b_eingabefeld><option value=%u>/%s</option>""" % (mask, str(mask))
    if net.version() == 4:
        for r in range(net.prefixlen()+1, 33):
            if r != 31:
                print """<option value="%s/workflow.cgi?%s&%s&%s&%s&%s&%s&%s">/%s</option>""" \
		    % (cgi_dir, user_md5, vrf, service_id, product_id, if_id, id, str(r), str(r))
    elif net.version() == 6:
        for r in range(net.prefixlen()+1, 129):
            if r != 127:
                print """<option value="%s/workflow.cgi?%s&%s&%s&%s&%s&%s&%s">/%s</option>""" \
		    % (cgi_dir, user_md5, vrf, service_id, product_id, if_id, id, str(r), str(r))
    if mask != 0:
        print """<option value="%s/workflow.cgi?%s&%s&%s&%s&%s&%s&%s">select prefix length</option>""" \
	    % (cgi_dir, user_md5, vrf, service_id, product_id, if_id, id, "0")
    print """</select>"""
    print """</td>"""
    print """</tr>"""
    
    ### network name and aggregation line
    print """<tr>"""
    ### only admins (group id = 1) can create aggregated networks
    if group == 1:
        print """<td>Network name [Cust. Name (Cust. Nr)] *</td>"""
        print """<td>Network is aggregated</td>"""
        print """</tr><tr>"""
        print """<td><input type=text name=netname class=b_eingabefeld></td>"""
        print """<td><input type=checkbox name=aggregated></td>"""
    else:
        print """<td colspan=2>Network name [Cust. Name (Cust. Nr)] *</td>"""
        print """</tr><tr>"""
        print """<td colspan=2><input type=text name=netname class=b_eingabefeld></td>"""
    print """</tr>"""
    
    ### interface line
    print """<tr>"""
    print """<td colspan=2>Interface -> <a href="%s/search_interface.cgi" title="list all channalized interfaces" class=LinkPurpleBold>list</a></td>""" % cgi_dir
    print """</tr><tr>"""
    print """<td colspan=2><input type=text name=interface class=b_eingabefeld maxlength=250></td>"""
    print """</tr>"""

    ### description area 
    print """<tr>"""
    print """<td colspan=2>Description</td>"""
    print """</tr><tr>"""
    print """<td colspan=2 valign=top><textarea name=description rows=6 class=b_eingabefeld></textarea></td>"""
    print """</td>"""
    print """</tr>"""

    ### save button line
    print """<tr>"""
    print """<td colspan=2>* required field</td>"""
    print """</tr><tr>"""
    print """<td colspan=2>&nbsp;</td>"""
    print """</tr><tr>"""
    if ripe_mail == "":
        print """<td colspan=2><input type=submit name=save value=save class=button></td>"""
    else:
        print """<td><input type=submit name=save value=save class=button></td>"""
        print """<td><input type=checkbox name=ripe> Register network at ripe.net </td>"""
#    print """<td><input type=submit name=save value=save class=button></td>"""
#    print """<td><input type=checkbox name=ripe> Register network at ripe.net </td>"""
#    print """<td colspan=2><input type=submit name=save value=save class=button></td>"""
    print """</tr>"""

    print """</table>"""
    print """</form>"""


def print_footer():
    """footer of the whole site with "back" button and "close window" button"""

    print """<tr><td>&nbsp;</td></tr>"""
    print """<table width=550 border=0 cellspacing=0 cellpadding=0 class=TextPurple>"""
    print """<tr>"""
    print """<td width=50%><a href="javascript:opener.location.reload();this.close();" class=LinkPurpleBold> close window </a></td>"""
    print """<td align=right><a href="javascript:history.back();" class=LinkPurpleBold> << back </a></td>"""
    print """</tr>"""
    print """</table>"""


def main():
    """description"""

    global conn, group, user_md5, cgi_dir, ripe_mail
    formdata = cgi.FieldStorage()
    referer = ""
    vrf = service_id = product_id = if_id = netname = description = interface = "NULL"
    network = "None"
    id = mask = aggregated = netmask = send = 0
    ripe = allocated = aggregated = "off"

    user_md5 = Session.check_cookie()

    try:
        if formdata.has_key("parent_id"):
            parent_id = str(formdata['parent_id'].value)
        if formdata.has_key("parent_vrf"):
            parent_vrf = str(formdata['parent_vrf'].value)
        if formdata.has_key("parent_path"):
            parent_path = str(formdata['parent_path'].value)
        if formdata.has_key("service_id"):
            service_id = str(formdata['service_id'].value)
        if formdata.has_key("product_id"):
            product_id = str(formdata['product_id'].value)
        if formdata.has_key("if_id"):
            if_id = str(formdata['if_id'].value)
        if formdata.has_key("network"):
            network = str(formdata['network'].value)
        if formdata.has_key("netmask"):
            netmask = str(formdata['netmask'].value)
        if formdata.has_key("netname"):
            netname = str(formdata['netname'].value)
        if formdata.has_key("aggregated"):
                aggregated = str(formdata['aggregated'].value)
        if formdata.has_key("description"):
            description = str(formdata['description'].value)
        if formdata.has_key("interface"):
            interface = str(formdata['interface'].value)
        if formdata.has_key("ripe"):
                ripe = str(formdata['ripe'].value)
    except ValueError, e:
        print "Error: %s" % e
        print """<script language="javascript">alert("Value parse error, sorry!"); history.back();</script> """
        return


    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 2:
            user_md5 = str(qs.split("&")[0])
            vrf = str(qs.split("&")[1])
            service_id = 0
            product_id = 0
            if_id = 0
        elif len(qs.split("&")) == 3:
            user_md5 = str(qs.split("&")[0])
            vrf = str(qs.split("&")[1])
            service_id = int(qs.split("&")[2])
            product_id = 0
            if_id = 0
        elif len(qs.split("&")) == 4:
            user_md5 = str(qs.split("&")[0])
            vrf = str(qs.split("&")[1])
            service_id = int(qs.split("&")[2])
            product_id = str(qs.split("&")[3])
            if_id = 0
        elif len(qs.split("&")) == 5:
            user_md5 = str(qs.split("&")[0])
            vrf = str(qs.split("&")[1])
            service_id = int(qs.split("&")[2])
            product_id = str(qs.split("&")[3])
            if_id = str(qs.split("&")[4])
        elif len(qs.split("&")) == 6:
            user_md5 = str(qs.split("&")[0])
            vrf = str(qs.split("&")[1])
            service_id = int(qs.split("&")[2])
            product_id = str(qs.split("&")[3])
            if_id = str(qs.split("&")[4])
            id = int(qs.split("&")[5])
        elif len(qs.split("&")) == 7:
            user_md5 = str(qs.split("&")[0])
            vrf = str(qs.split("&")[1])
            service_id = int(qs.split("&")[2])
            product_id = str(qs.split("&")[3])
            if_id = str(qs.split("&")[4])
            id = int(qs.split("&")[5])
            mask = int(qs.split("&")[6])
        elif len(qs.split("&")) == 8:
            user_md5 = str(qs.split("&")[0])
            vrf = str(qs.split("&")[1])
            service_id = int(qs.split("&")[2])
            product_id = str(qs.split("&")[3])
            if_id = str(qs.split("&")[4])
            id = int(qs.split("&")[5])
            mask = int(qs.split("&")[6])
            network = str(qs.split("&")[7])
        else:
            vrf = service_id = product_id = if_id = "NULL"
            network = "None"
            user_md5 = ""
            id = mask = 0
    else:
        if_id = "NULL"

    ### create database connection object
    cfg = ConfigObj("ipall.cfg")
    db_host = cfg['Database']['db_host']
    db_user = cfg['Database']['db_user']
    db_pw = cfg['Database']['db_pw']
    db = cfg['Database']['db']
    conn = DBmy.db(db_host, db_user, db_pw, db)

    ### User
    current_user = conn.get_username(user_md5)
    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    else:
        HTML.simple_header()
    user = IpallUser.User(current_user)
    group = user.get_group_id()
    cgi_dir = cfg['Server']['cgi_dir']
    ripe_mail = cfg['Server']['ripe_mail']
    if group == 0:
        HTML.restriction_message()
        return
    

    if vrf == "NULL" and not formdata.has_key("save"):
        HTML.restriction_message()
        return
    elif service_id == "NULL" and not formdata.has_key("save"):
        HTML.restriction_message()
        return 	
    elif product_id == "NULL" and not formdata.has_key("save"):
        HTML.restriction_message()
        return 	
    else:
        print """<br>"""
        print """<blockquote>"""
        print """<table width=550 border=0 cellspacing=5 cellpadding=0 class=TextPurple>"""

	if formdata.has_key("save"):
	    ### check if the network is valid
            try:
                net = IPy.IP(network)
            except:
                print """<script language="javascript">alert("No valid network!"); history.back();</script> """

            ### check if there is already such a network
            sql_check = """SELECT id FROM ipall_ip WHERE label LIKE '%s' AND vrf='%s' """ % (network, parent_vrf)
            chk_net = conn.get_data(sql_check)
            #print sql_check
            #print chk_net
            if chk_net != ():
                print """<script language="javascript">alert("This network already exists!"); history.back();</script> """
                return

            if netname.find("'") != -1 or interface.find("'") != -1 or description.find("'") != -1:
                print """<script language="javascript">alert("You must not insert an apostrophe"); history.back();</script> """; return;
	    if network == "None" or network == "select network": print """<script language="javascript">alert("Please select network"); history.back();</script> """; return;
	    if netname == "NULL" or netname == None: print """<script language="javascript">alert("Please insert network name"); history.back();</script> """; return;
	    if netname != "NULL": netname = "'" + netname + "'"
	    ### only admins (group id = 1) can create aggregated networks
	    if aggregated == "on" and group == 1: aggregated = 1;
            else: aggregated = 0;
	    if parent_vrf != "NULL": parent_vrf = "'" + parent_vrf + "'"
	    #if parent_path != "NULL": parent_path = "'" + parent_path + "'"
	    if description != "NULL": description = "'" + description + "'"
	    if interface != "NULL": interface = "'" + interface + "'"
	    try:
		net = IPy.IP(network)
	    except:
		print """<script language="javascript">alert("Error: invalid network address"); history.back();</script> """
		return
	    if network != "None": network = "'" + network + "'"

	    sql_ins = """INSERT INTO ipall_ip VALUES('', %s, %s, %u, %s, %s, '%s', 0, NULL, %s, %u, %s, %s, %s, 0, %s)""" \
		% (parent_id, network, int(net.strDec()), netname, description, parent_path, parent_vrf, aggregated, product_id, if_id, service_id, interface) 
	    #print sql_ins, "<br>"
	    ins_id = conn.insert_data(sql_ins)

	    ### LOGGING
	    sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_ip', "%s")""" % (current_user, sql_ins)
	    log = conn.update_data(sql_log)

            if ripe == "on":
                referer = """%s/networks.cgi?%s&%s#%s"""  % (cgi_dir, str(parent_vrf), parent_path, str(id))
                register = Whois.whois()
                register.print_form(net.net(), net.broadcast(), netname.replace("'", ""), referer, 1)

	    if ins_id != 0:
		new_path = parent_path + ":" + str(ins_id)
		sql_upd = """UPDATE ipall_ip SET path='%s' WHERE id=%u""" % (new_path, ins_id)
		#print sql_upd, "<br>"
		update = conn.update_data(sql_upd)

                sql_upd_parent = """UPDATE ipall_ip SET subnetted=1 WHERE id=%u """ % int(parent_id)
                #print sql_upd_parent + "<br>"
                update2 = conn.update_data(sql_upd_parent)

                if send != 0 and ripe == "on":
                    print """<blockquote>"""
                    print """<p class=TextPurpleBold>Mail to %s was sent successfully</p>""" % ripe_mail
                    print """</blockquote>"""
                else:
                    print """<blockquote>"""
                    print """<p class=TextPurpleBold>Mail was not sent</p>"""
                    print """</blockquote>"""

                if update != 0 and update2 != 0:
                    print """<blockquote>"""
                    print """<p class=TextPurpleBold>Network has been added successfully!</p>"""
                    print """</blockquote>"""
                else:
                    print """<blockquote>"""
                    print """<p class=TextPurpleBold>An error during "update path" has occured!</p>"""
                    print """</blockquote>"""
	    else: ### insert_id == 0 --> error!
                print """<blockquote>"""
                print """<p class=TextPurpleBold>An error during "insert prefix" has occured!</p>"""
                print """</blockquote>"""

	else:	# SAVE has not been pressed
	    print """<tr>"""
	    if service_id != 0:
		sql_type = """SELECT typename FROM ipall_network_types WHERE id=%s ORDER BY typename""" % service_id
		typename = conn.get_data(sql_type)[0][0]
		print """<td colspan=2 class=lightPurple3><font class=TextPurpleBoldBig>Create %s</font></td>""" % typename
	    else:
		print """<td colspan=2 class=lightPurple3><font class=TextPurpleBoldBig>Choose network type</font></td>"""
	    print """</tr>"""
	    print """<tr><td>"""
	    print_net_types(vrf, service_id)
	    print """</td></tr>"""
	    
	    if len(qs.split("&")) == 4 or id == 0:
#		print """<tr><td colspan=2>given values:<br>vrf: %s<br>service id: %s<br>product id: %s<br>interface id: %s<br><br></td></tr>""" % (vrf, service_id, product_id, if_id)
		print """<tr><td>"""
		if service_id != "NULL" and service_id != 0:
		    print_nets_of_type(vrf, service_id, product_id, if_id)
		else:
		    print """&nbsp;"""
		print """</td></tr>"""
		print_footer()
		print """</table>"""
		return

	    sql_net = """SELECT label, path, vrf FROM ipall_ip WHERE id=%u """ % int(id)
            parent_net = conn.get_data(sql_net)

            if group == 1:
                net_perm = (1,1,1,1)
            else:
                net_perm = conn.get_net_permissions(parent_net[0][1], group)
                #print net_perm
            if net_perm == () or net_perm == "":
                net_perm = 0
            else:
                net_perm = net_perm[2]
            
            if net_perm != 1:
                HTML.restriction_message()
                return
	    else:
		print """<tr><td>"""
		print_newnet_form(parent_net, id, mask, network, vrf, service_id, product_id, if_id)
		print """</td></tr>"""


	print """<tr><td>"""
	print_footer()
	print """</td></tr>"""
	print """</table>"""
	print """</blockquote>"""
	

    HTML.main_footer()

main()
