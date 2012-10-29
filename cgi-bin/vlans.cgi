#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 racyAPz
http://www.racyapz.at
*****************************
"""

import Html as HTML
import DBmy
from Sessionclass import Session
import Tree
import IpallUser
import os
import sys
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie

def tree_nodes(vlans, rights):
    """recursive function for displaying networks and subnets
    networks	...	tuple of networks to display"""

    ### definitions of variables
    #depth = len(path.split(":"))
    #p = int(path.split(":")[depth-1])
    #childs = ()

    for n in vlans:
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

        net = Tree.Node(rights, net_perm, 1, 1, "vrf")
        #for i in path.split(":"):
            #if int(i) == n[0]:
                #id_found = 1


        if net_perm[3] != 1:
            continue
        else:
            print """<div id="net%s">""" % str(n[0])
            print """<tr><td align=center>"""
        
        print """<table class="table_networks" border=0><tr height=20>"""

        ### build tree of networks with plus and minus symbols
        if net_perm[3] == 1:
            net.print_plus(1, n[0])
            net.print_node(n)
        print """</tr></table></div>"""

        print """</td></tr>"""
        print """<tr><td>"""
        print """<div style="display:none" id="net%s_%s"><img src="%s/images/indicator.gif"></div>""" % ( str(n[0]), str(n[0]), ipall_dir )
        print """</td></tr>"""
        
##        if path != "0":
##            depth = len(path.split(":"))
##            for r in range(1, (depth)):
##                q = int(path.split(":")[r])
##                if q == int(n[0]):
##                    #print q, "- "
##                    print """<script language="javascript">callNode('%s', '%s', '%s', '%s', '%s');</script>""" \
##                        % ( q, ipall_dir, cgi_dir, vrf, path )



def main():
    """entry point for executing IPALL - networks"""

    ### definitions of variables
    global ipall_dir, cgi_dir, current_user, group, rights, conn, depth, path, company
    nodes = ()

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 1:
            company = int(qs.split("&")[0])
        else:
            company = 0 
    else:
        company = 0

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
    HTML.simple_header()

    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    else:
        HTML.body()
    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']
    if group == 0:
        HTML.restriction_message()
        HTML.main_footer()
        return

    if group != 1:
        company = company_id

    if company == 0:
        HTML.error_message("No company selected")
        HTML.main_footer()
        return


    sql_vlans = """SELECT * FROM ipall_vlan WHERE companies_id=%u ORDER BY id""" % ( int(company) )
    nodes = conn.get_data(sql_vlans)


    print """<div id="main" style="position: absolute; top: 140px;">""" ### main
    print """   <div class="table_main">""" ### table_main
    print """       <div style="background-color: rgb(237, 237, 237);height:19px;">""" ### colored
    print """           <div style="display:inline; width: 400px;" class="textPurpleBold">vlan database</div>""" ### line 1
    print """           <div align=right class=TextPurple style="display:inline; width: 400px; position: absolute; left: 400;">
                            you are logged in as: <i>%s</i></div>""" % ( current_user ) ### line 1
    print """       </div>""" ### colored
    print """       <div align=right class=TextPurple style="background-color: rgb(237, 237, 237);height:19px;">""" ### line 2
    if group == 1 or rights[0] == 1 or rights[2] == 1:
        print """       <a href="javascript:void(0);" onClick="popup('%s/new_vlan?%s');" 
                           class="LinkPurpleBold">new vlan</a>&nbsp; |&nbsp;""" % (cgi_dir, str(company))
    print """           <a href="javascript:void(0);" onClick="popup('%s/search_vlan.cgi?%s');" 
                            class=linkPurpleBold>search</a>""" % ( cgi_dir, str(company) )
    print """       </div>""" ### line 2
    print """   </div>"""### table_main
    print """   <div class="textPurple">""" ### body

    if nodes == () or nodes == 0:
        print """<br>No vlans found"""
    else:
        #print """<br><table class=table_main>"""

        print nodes
        #tree_nodes(nodes, rights)

        #print """</table>"""

    print """</div>""" ### body
    print """</div>""" ### main

    HTML.main_footer()

main()
