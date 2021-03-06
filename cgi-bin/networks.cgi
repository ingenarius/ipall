#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 racyAPz
http://www.racyapz.at
*****************************
"""

from Html_new import HtmlContent
import DBmy
from Sessionclass import Session
import Tree
import IpallUser
import os
import sys
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie

def tree_nodes(networks, rights, path):
    """recursive function for displaying networks and subnets
    networks	...	tuple of networks to display"""

    ### definitions of variables
    depth = len(path.split(":"))
    p = int(path.split(":")[depth-1])
    childs = ()

    for n in networks:
        id_found = 0
        ### permissions of the network(s)
        if group == 1 or rights[2] == 1:
            net_perm = ([1,1,1,1],)
        else:
            sql_perm = """SELECT delete_net, edit_net, subnet_net, view_net FROM ipall_rights 
                WHERE LOCATE(path, '%s') > 0 AND group_id=%u ORDER BY path DESC LIMIT 1""" % (n[6], group)
            net_perm = conn.get_data(sql_perm)
        if net_perm == ():
            net_perm = [0,0,0,0]
        else:
            net_perm = net_perm[0]

        net = Tree.Node(rights, net_perm, len(n[6].split(":")), n[6], vrf, "0", n[17], n[18])
        for i in path.split(":"):
            if int(i) == n[0]:
                id_found = 1


        if net_perm[3] != 1:
            continue
        else:
            print """<div id="net%s">""" % str(n[0])

        print """<div id="table_networks">"""

        ### build tree of networks with plus and minus symbols
        if net_perm[3] == 1:
            net.print_plus(n[7], n[0])
            net.print_node(n)
        print """</div></div>"""

        print """<div>"""
        print """<div style="display:none" id="net%s_%s"><img src="%s/images/indicator.gif"></div>""" % ( str(n[0]), str(n[0]), ipall_dir )
        print """</div>"""
        

def main():
    """entry point for executing IPALL - networks"""

    ### definitions of variables
    global ipall_dir, cgi_dir, current_user, group, rights, conn, depth, path, vrf
    nodes = ()

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 1:
            vrf = str(qs.split("&")[0])
            path = "0"
        elif len(qs.split("&")) == 2:
            vrf = str(qs.split("&")[0])
            path = str(qs.split("&")[1])
        else:
            vrf = "None"
            path = "0"  
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

    ### User
    s = Session(conn)
    current_user = s.check_user()
    #company = s.check_cookie()
    HTML = HtmlContent()
    HTML.simple_header(0,1)

    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    else:
        HTML.body()

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights(vrf)
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']
    sbox = cfg['Site']['smoothbox'].replace("?", "&")

    if group == 0:
        HTML.restriction_message()
        return

    sql_vrf_name = """SELECT vpn_vrf_name FROM networks WHERE vpn_rd='%s' """ % vrf
    vrf_name = conn.get_data(sql_vrf_name)
    if vrf_name != ():
        vrf_name = vrf_name[0]
    else:
        vrf_name = ""

    ### print the network table
    print """<br>"""
    print """<div id="divHead800">""" #3
    print """<span class=left>networks of <i>'%s'</i></span>""" % ( vrf_name )
    print """<span class=right>you are logged in as: <i>%s</i></span>""" % ( current_user )
    print """<span class=left></span>"""
    print """<span class=right>"""
#    if rights[1] == 1:
#        print """<span class=linkPurpleBold>"""
#        print """<a href="%s/nettype_permissions.cgi?%s%s");" 
#            class="smoothbox">type permission</a>&nbsp; |&nbsp;""" % ( cgi_dir, str(vrf), sbox )
#        print """</span>"""
    if group == 1 or rights[0] == 1 or rights[2] == 1:
        print """<a href="%s/new_network.cgi?%s%s" 
            class="smoothbox">new network</a>&nbsp; |&nbsp;""" % (cgi_dir, str(vrf), sbox)
    if rights[0] == 0 and rights[1] == 0:
        print """&nbsp;"""
    print """<a href="%s/search.cgi?%s%s" class="smoothbox">search</a>""" % ( cgi_dir, str(vrf), sbox )
    print """</span>""" 
    print """</div>""" #3

    if vrf != "None":
        roots_query = """SELECT ip.*, nt.font_color, nt.bg_color FROM ipall_ip ip, ipall_network_types nt 
            WHERE ip.service_id=nt.id AND (ip.parent_id=0 AND ip.vrf='%s') ORDER BY ip.address""" % vrf
        nodes = conn.get_data(roots_query)
 
    if nodes == () or nodes == 0:
        HTML.error_message("No networks found!")
    else:
        print """<div id="table_main">"""

        tree_nodes(nodes, rights, path)

        print """</div>"""

    HTML.main_footer()

main()
