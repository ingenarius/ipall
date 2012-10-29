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
import IPy
import Whois
from Sessionclass import Session
import os
import re
from Configobj import ConfigObj
from Cookie import SimpleCookie


def print_configs(peering_info, network, netname, dev):
    """shows the neighbor config for cisco and juniper routers"""

    print """<div>&nbsp;</div>"""

    ### cisco neighbor config
    print """<div class="TextPurpleBold">Cisco neighbor config</div>"""
    print """<div>neighbor %s remote-as %s</div>""" % (network, peering_info[0][1])
    print """<div>neighbor %s description %s</div>""" % (network, netname)
    if peering_info[0][3] != "NULL" and peering_info[0][3] != "None":
        print """<div>neighbor %s password %s</div>""" % (network, peering_info[0][3])
    print """<div>neighbor %s peer-group YOUR-PEER-GROUP</div>""" % (network)
    if peering_info[0][9] != "NULL" and peering_info[0][9] != None and peering_info[0][9] != 0:
        print """<div>neighbor %s maximum-prefix %s restart 30</div>""" % (network, peering_info[0][9])

    print """<div>&nbsp;</div>"""

    ### juniper neighbor config
    print """<div class="TextPurpleBold">Juniper neighbor config (edit within bgp group)</div>"""
    print """<div>set neighbor %s peer-as %s </div>""" % (network, peering_info[0][1])
    if peering_info[0][3] != "NULL" and peering_info[0][3] != "None":
        print """<div>set neighbor %s authentication-key "%s" </div>""" % (network, peering_info[0][3])
    print """<div>set neighbor %s description "%s" </div>""" % (network, netname)
    if peering_info[0][9] != "NULL" and peering_info[0][9] != None and peering_info[0][9] != 0:
        print """<div>set neighbor %s family inet unicast prefix-limit maximum %s</div>""" % (network, peering_info[0][9])
        print """<div>set neighbor %s family inet unicast prefix-limit teardown 90</div>""" % (network)
        print """<div>set neighbor %s family inet unicast prefix-limit teardown idle-timeout 30</div>""" % (network) 
    print """<div>insert neighbor %s after neighbor [PREVIOUS NEIGHBOR IP] </div>""" % (network)

    


def print_peering_info(peering_info, network, device):
    """If the selected network is a peering parner - print infos"""
    
    print """<p> </p>"""
    ### LEFT SIDE
    print """<div id="pos_left_small">"""
    print """<div class="lineOdd">AS</div>"""
    print """<div class="lineEven">AS-SET</div>"""
    print """<div class="lineOdd">max prefix</div>"""
    print """<div class="lineEven">MD5 password</div>"""
    print """<div class="lineOdd">routeserver</div>"""
    print """<div class="lineEven">session</div>"""
    print """<div class="lineOdd">contact</div>"""
    print """<div class="lineEven">device</div>"""
    print """<div class="lineOdd">comment</div>"""
    print """</div>""" # left side

    ### RIGHT SIDE
    print """<div id="pos_right_wide">"""
    print """<div class="lineOdd">%s</div>""" % peering_info[0][1] # as
    if peering_info[0][2] != None and peering_info[0][2] != "NULL":
        print """<div class="lineEven">%s</div>""" % peering_info[0][2] # as-set
    else:
        print """<div class="lineEven"><i>none</i></div>""" 
    if peering_info[0][9] != None and peering_info[0][9] != "NULL":
        print """<div class="lineOdd">%s</div>""" % peering_info[0][9] # max prefix
    else:
        print """<div class="lineOdd"><i>none</i></div>""" 
    if peering_info[0][3] != None and peering_info[0][3] != "NULL":
        print """<div class="lineEven">%s</div>""" % peering_info[0][3] # MD5 password
    else:
        print """<div class="lineEven"><i>none</i></div>""" 
    if peering_info[0][4] == 1:
        print """<div class="lineOdd">yes</div>""" 
    else:
        print """<div class="lineOdd">no</div>""" 
    if peering_info[0][5] == 1:
        print """<div class="lineEven">UP</div>""" 
    else:
        print """<div class="lineEven">DOWN</div>""" 
    if peering_info[0][6] != None and peering_info[0][6] != "NULL":
        print """<div class="lineOdd"><a href="mailto:%s" class=LinkPurpleBold>%s</a></div>""" % (peering_info[0][6], peering_info[0][6])
    else:
        print """<div class="lineOdd"><i>none</i></div>""" 
    print """<div class="lineEven">%s</div>""" % peering_info[0][8].lower() # device
    print """<div class="lineOdd"><textarea class=b_eingabefeld_white readonly>%s</textarea></div>""" % peering_info[0][7] # comment
    print """</div>""" # right side

    print """<div id="pos_clear"> </div>"""


def main():
    """entry point for executing IPALL - view network details"""

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        try:
            id = int(qs.split("&")[0])
        except:
            id = 0
    else:
        current_user = ""
        id = 0

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
        #print ""
        HTML.popup_body()

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']
    if group == 0:
        HTML.restriction_message(1)
        HTML.popup_footer()
        return

    f = IpallFunctions(conn, current_user, group, company_id)

    referer = "javascript:this.close();"

    details = f.get_net_info(1, id)
    if details == () or details == None:
        HTML.error_message("Nothing to display!")
        return
    else:
        if group != 1 and rights[2] != 1:
            net_perm = conn.get_net_permissions(str(details[0][4]), group)
            if net_perm == () or net_perm == "":
                net_perm = 0
                edit_perm = 0
            else:
                edit_perm = net_perm[1]
                net_perm = net_perm[3]
        else:
            net_perm = 1
            edit_perm = 1

        if net_perm != 1:
            HTML.restriction_message(1)
            HTML.popup_footer()
            return

        peering_info_id = details[0][3]
        if peering_info_id != 0 and peering_info_id != None:
            peering_info = f.get_peering_info(peering_info_id)
        else:
            peering_info = ()
            
        service_id = details[0][5]
        if service_id != 0 and service_id != None:
            net_type = f.get_service_name(service_id)
        else:
            net_type = ()

        print """<div id="main">"""
        print """<div id="table_main">"""
        
        ### HEADING
        print """<div id="functionHead">""" 
        print """<span>Network</span>""" # heading
        print """<span id="pos_right_wide">%s""" % details[0][0]
        if group == 1 or rights[2] == 1:
            if peering_info != () and peering_info != None:
                print """&nbsp;&nbsp; | &nbsp;&nbsp;<a href="javascript:void(0);" id="toggle_config" 
                onClick="toggle_msg(this, 'config on', 'config off');" title="show router configs">config on</a>"""
            if details[0][9] == 1:
                print """&nbsp;&nbsp; | &nbsp;&nbsp;<a href="javascript:void(0);" title="show ripe mail form" class=LinkPurpleBold id="toggle_ripe" onClick="toggle_msg(this, 'show ripe', 'hide ripe');">show ripe</a>"""
            else:
                print """&nbsp;&nbsp;"""
            #print """</td>"""
            if edit_perm == 1:
                print """&nbsp;&nbsp; | &nbsp;&nbsp;<img src="%s/images/editOff.png" id="edit" onMouseOver="mouseoverImage(this, '%s');"  
                    onMouseOut="mouseoverImage(this, '%s');" onClick="window.location = '%s/network_edit.cgi?%s';" class=handlers />""" \
                        % ( ipall_dir, ipall_dir, ipall_dir, cgi_dir, id )
        print """</span>""" # right side
        print """</div>""" # functionHead

        ### LEFT SIDE
        print """<div id="pos_left_small">"""
        print """<div class="lineOdd">Name</div>"""
        print """<div class="lineEven">Network Type</div>"""
        print """<div class="lineOdd">Interface</div>"""
        print """<div class="lineEven">Description</div>"""
        print """</div>""" # left side

        ### RIGHT SIDE
        print """<div id="pos_right_wide">"""

        print """<div class="lineOdd">%s</div>"""  % details[0][1]  # name

        if net_type != () and net_type != None:
            print """<div class="lineEven">%s</div>"""  % net_type[0][1]  # network type
        else:
            print """<div class="lineEven"></div>""" 

        if details[0][6] != "NULL" and details[0][6] != None: 
            print """<div class="lineOdd">%s</div>"""  % details[0][6]  # interface
        else:
            print """<div class="lineOdd"><i>none</i></div>"""
        print """<div class="lineEven"><textarea class=b_eingabefeld_white readonly>%s</textarea></div>"""  % details[0][2]  # description
        print """</div>""" # right side

        print """<div id="pos_clear"> </div>"""

        if peering_info != () and peering_info != None:
            if peering_info[0][8].find("_"):
                dev = re.sub("_", "-", peering_info[0][8].lower())
            else:
                dev = peering_info[0][8].lower()
            print_peering_info(peering_info, details[0][0], dev)
            print """<div id="config">"""
            print_configs(peering_info, details[0][0], details[0][1], dev)
            print """</div>"""
            print """<script language="javascript">toggleVisibility('config', 'toggle_config');</script>"""

        if details[0][9] == 1:
            print """<div id="ripe"><hr>"""
            net = IPy.IP(details[0][0])
            register = Whois.whois()
            if int(net.version()) == 4:
                register.print_form(details[0][8], net.net(), net.broadcast(), net.prefixlen(), details[0][1], referer)
            if int(net.version()) == 6:
                register.print_form(details[0][8], net.strCompressed(), "", net.prefixlen(), details[0][1], referer, 0, 6)
            print """</div>"""
            print """<script language="javascript">toggleVisibility('ripe', 'toggle_ripe');</script>"""

        print """</div>""" # table_main
        print """</div>""" # main


    HTML.popup_footer()


main()
