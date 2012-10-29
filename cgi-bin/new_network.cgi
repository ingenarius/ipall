#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
andi@poiss.priv.at
*****************************
"""

from Html_new import HtmlContent
from Ipall import IpallFunctions
import DBmy
import IpallUser
from Sessionclass import Session
import IPy
import os
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie


def print_newnet_form(company, vrf, f):
    """print a HTML form for inserting a new network"""

    print """<div id="new_net">"""
    print """<input type=hidden name=vrf value="%s">""" % str(vrf)
    print """<input type=hidden name=company value="%s">""" % company

    print """<p>Network (in CIDR format, e.g. 10.0.0.0/8) *<br>"""
    print """<input type=text id="network" name=network size=33 class=b_eingabefeld></p>"""

    print """<p>Network name *<br>"""
    print """<input type=text id="netname" name=netname size=33 class=b_eingabefeld maxlength=30></p>"""

    print """<p>Network type (<b><a href="javascript:void(0);" id="toggle_help">type definitinos</a></b>)<br>"""
    print """<select id="net_type" name=net_type class=b_eingabefeld><option value="1">Default</option>"""
    f.print_net_types()
    print """</select></p>"""

    print """<p>Network is allocated / aggregated<br>"""
    print """<input type=checkbox id="allocated" name=allocated> / <input type=checkbox id="aggregated" name=aggregated></p>"""

    print """<p>Description<br>"""
    print """<textarea id="description" name=description cols=40 rows=6 class="b_eingabefeld"></textarea></p>"""

    print """<p><input type=submit id="save" name=save value=save class=button></p>"""
    print """</div>""" # new_net

    print """<div id="info_newnet"></div>"""

    print """<div id="pos_clear"></div>"""


def main():
        """create a new superblock"""

        formdata = cgi.FieldStorage()
        network = netname = description = net_type = "NULL"
        device_id = 1
        company = 0
        allocated = aggregated = "off"

        if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
            qs = os.environ['QUERY_STRING']
            try:
                vrf = str(qs.split("&")[0])
            except:
                vrf = "None"
        else:
                vrf = "None"
                path = "0"

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
        #company = s.check_cookie()
        HTML.simple_header()
        if current_user == "":
            HTML.simple_redirect_header(cfg['Server']['web_dir'])
            return
        else:
            HTML.popup_body()

        user = IpallUser.User(current_user)
        group, company_id  = user.get_group_id()
        cgi_dir = cfg['Server']['cgi_dir']
        ipall_dir = cfg['Server']['ipall_dir']
        sbox = cfg['Site']['smoothbox']

        if group == 0:
            HTML.restriction_message(1)
            return

        if vrf == "None" and not formdata.has_key("save"):
            HTML.error_message("No vrf selected!")
            return
        ### logged in user does have enough rights to 
        else:
            try:
                if formdata.has_key("uri"):
                        uri = str(formdata['uri'].value)
                if formdata.has_key("company"):
                        company = int(formdata['company'].value)
                if formdata.has_key("vrf"):
                        vrf = str(formdata['vrf'].value)
                if formdata.has_key("network"):
                        network = str(formdata['network'].value)
                if formdata.has_key("netname"):
                        netname = str(formdata['netname'].value)
                if formdata.has_key("description"):
                        description = str(formdata['description'].value)
                if formdata.has_key("net_type"):
                        net_type = str(formdata['net_type'].value)
                if formdata.has_key("allocated"):
                        allocated = str(formdata['allocated'].value)
                if formdata.has_key("aggregated"):
                        aggregated = str(formdata['aggregated'].value)
            except:
                print """<script language="javascript">alert("value parse error!"); history.back();</script> """

        rights = user.get_rights(vrf)
        if group != 1 and rights[0] != 1 and rights[2] != 1: 
            HTML.restriction_message(1)
            HTML.popup_footer()
            return

        ### SAVE button has been pressed
        if formdata.has_key("save"):
            try:
                net = IPy.IP(network)
            except:
                print """<script language="javascript">alert("You should insert a valid network address"); history.back();</script> """ 
                return

            print "<br>"

            ### a description has been typed
            if description == "NULL" or description == "None": description = "NULL"
            else: description = "'" + description + "'"
            if allocated == "on" and group == 1: allocated = 1;
            else: allocated = 0;
            if aggregated == "on" and group == 1: aggregated = 1;
            else: aggregated = 0;

            if net_type == 0:
                HTML.notify_message("Information: You did not select a network type!")
                net_type = "NULL"

            f = IpallFunctions(conn, current_user, group, company_id)
            chk = f.check_new_network(net.strDec(), vrf) 

            # 0 ... network does not overlap
            # 1 ... network does overlap -> not inserted
            # -1 .. no other networks exist
            if chk != 1: 
                update = f.insert_new_net(net, vrf, netname, description, aggregated, net_type, allocated)
            else:
                print """<script language="javascript">alert("network already exists..."); history.back();</script> """ 
                return

            if update != 0:
                msg = """Network successfully created!"""
                HTML.notify_message(msg)
                print """<div id=message><a href="javascript:void(0);" onClick="parent.location.reload(1);" class="LinkPurpleBold">close and refresh</a></div>"""
            else:
                msg = """An error during "update path" has occured!"""
                HTML.notify_message(msg)
            HTML.popup_footer()

        ### SAVE button has not been pressed
        else:   
            f = IpallFunctions(conn, current_user, group, company_id)
            sql_net = """SELECT companies_id FROM networks WHERE vpn_rd='%s' """ % vrf
            company = conn.get_data(sql_net)
            if company != ():
                company = company[0][0]
            else:
                company = company_id

            print """<div id="main">"""
            print """<div id="table_main">"""
            print """<form name="new_network" method=POST action="new_network.cgi" onSubmit="return check_new_net()">"""

            ### HEADING
            print """<div id="functionHead">Insert a new network superblock</div>""" # heading

            print_newnet_form(company, vrf, f)

            print """<div>&nbsp;</div>"""
            print """<div>* required field</div>"""
            print """</form>"""
            print """</div>""" # table_main 
            print """</div>""" # main 
            print """<script language="javascript">
                window.addEvent('domready', function() {  
                    ajaxFunction('%s/help_nettypes.cgi','info_newnet','1');
                    toggleVisibility('info_newnet', 'toggle_help');
                });
                </script>""" % ( cgi_dir )

        HTML.close_body()

main()
