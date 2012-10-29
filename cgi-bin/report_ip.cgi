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
import re
import os
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie


def print_result(vrfs):
    """print doubled networks of selected views/vrfs"""

    if vrfs != []:
        for v in vrfs:
            print """<div class="table_main" style="border-bottom: dotted 1px #000000">&nbsp;</div>"""
    
            sql_networks = """SELECT id, label, net_name, path, vrf, companies_id FROM ipall_ip
                WHERE vrf="%s" ORDER BY address""" % (v)
            networks = conn.get_data(sql_networks)
            #print networks, "<br>"
            if networks != ():
                for n in networks:
                    #print n, "<br>"
                    more_nets = ()
                    for v2 in vrfs:
                        if v != v2: 
                            sql_more_nets = """SELECT id, label, net_name, path, vrf, companies_id FROM ipall_ip
                                WHERE vrf = "%s" AND label="%s" ORDER BY address""" % ( v2, n[1] )
                            more_nets += conn.get_data(sql_more_nets)
                            #print sql_more_nets
                    c_name = get_company(int(n[5]))
                    v_name1, v_name2 = get_vrf(n[4], int(n[5]))
                    if more_nets == ():
                        print """<div class="TextPurple" style="overflow:hidden;">
                            <span style="float: left; width: 250px;">%s</span>
                            <span style="float: left; width: 150px;"> %s / %s</span>
                            <span>(%s)</span></div>""" \
                            % ( n[1], v_name1, v_name2, c_name )
                    else:       
                        print """<div class="TextRed" style="overflow:hidden;">
                            <span style="float: left; width: 250px;">%s</span>
                            <span style="float: left; width: 150px;"> %s / %s</span>
                            <span>(%s)</span></div>""" \
                            % ( n[1], v_name1, v_name2, c_name )


def print_nets(n, c_name, v_name):
    """recursive function for displaying networks and subnets
    networks    ...     tuple of networks to display"""
                    
    ### definitions of variables
    depth = len(path.split(":"))
    p = int(path.split(":")[depth-1])
    childs = ()
            
    #print networks
    for n in networks:
        indent = len(n[3].split(":")) - 2
        for i in range(0, indent*2):
            print "&nbsp;"
        print "<font class=TextPurpleBold>" + n[1] + "</font>"
        print "<font class=TextPurple>" + " [" + n[2] + "]" + "</font><br>"

        print """</div>"""
        #print """</tr></table>"""

        child_query = """SELECT id, label, net_name, path, vrf, comanies_id FROM ipall_ip WHERE parent_id=%u ORDER BY address""" % (int(n[0]))
        childs = conn.get_data(child_query)
        tree_nodes(childs, rights)

        print """</td></tr>"""


def print_vrfs(group, company_id):
    """print a html form for searching in NMS database"""

    if group == 1:
        companies = get_companies()
        if companies != ():
            for c in companies:
                print """<div class="TextPurpleBold">%s</div>""" % ( c[1] )
                vrfs = get_vrfs(int(c[0]))
                if vrfs != ():
                    for v in vrfs:
                        print """<div class="TextPurple"><input type=checkbox name="vrfs" 
                            id="vrfs" value="%s"> %s</div>""" % ( v[0], v[1] )
    else:
        vrfs = get_vrfs(int(company_id))
        if vrfs != ():
            for v in vrfs:
                print """<div class="TextPurple"><input type=checkbox name="vrfs" 
                    id="vrfs" value="%s"> %s</div>""" % ( v[0], v[1] )
        


def get_companies():
    """return dropdown box <option> with network types"""

    sql_companies = """SELECT id, name FROM companies ORDER BY name"""
    companies = conn.get_data(sql_companies)
        
    return companies


def get_company(id):
    """return dropdown box <option> with network types"""

    sql_company = """SELECT name FROM companies WHERE id=%u ORDER BY name""" % ( id )
    company = conn.get_data(sql_company)
    
    if company != () and company != 0:
        return company[0][0]
    else:
        return "No Company"


def get_vrfs(company):
    """return dropdown box <option> with network types"""

    sql_vrfs = """SELECT vpn_rd, name FROM networks WHERE companies_id=%u ORDER BY name""" % ( company )
    vrfs = conn.get_data(sql_vrfs)
        
    return vrfs


def get_vrf(rd, company):
    """return dropdown box <option> with network types"""

    sql_vrf = """SELECT name, vpn_vrf_name FROM networks WHERE vpn_rd="%s" AND companies_id=%u """ % ( rd, company )
    vrf = conn.get_data(sql_vrf)
    
    if vrf != () and vrf != 0:
        return vrf[0][0], vrf[0][1]
    else:
        return "No View/VRF", "No View/VRF"


def main():
    """description"""

    global conn, vrf
    formdata = cgi.FieldStorage()
    search_type = search_text = ""
    vrfs = []
    net_type = 0

    try:
        if formdata.has_key("vrfs"):
            vrfs = formdata.getvalue("vrfs", "")
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

    print """<div id="main">"""
    print """<div id="table_main">"""

    ### HEADING
    print """<div id="functionHead">IP@LL doubled IP report</div>"""

    if group != 1 and int(rights[2]) == 0:
        HTML.restriction_message(1)
        HTML.close_body()
        return
    elif group != 1 and int(rights[2]) == 1:
        print """<form name="ipall_ip_report" id="ipall_ip_report" method=POST action="report_ip.cgi">"""

        if formdata.has_key("go"):
            found_nets = ()
            print_result(vrfs)            
        else: # "go" was not pressed
            print_vrfs(group, company_id)
            print """<div><br><input type=submit name=go id="go" value=go class=button></div>"""
        print """</form>"""
    else: # user is permitted
        print """<form name="ipall_ip_report" id="ipall_ip_report" method=POST action="report_ip.cgi">"""

        if formdata.has_key("go"):
            found_nets = ()
            print_result(vrfs)            
        else:
            print_vrfs(group, company_id)
            print """<div><br><input type=submit name=go id="go" value=go class=button></div>"""

        print """</form>"""

    print """</div>""" # table_main
    print """</div>""" # main
        
    HTML.popup_footer()

main()
