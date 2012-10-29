#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 racyAPz
http://www.racyapz.at
*****************************
"""

import sys
import os
import DBmy
import Tree
from Html_new import HtmlContent
from Sessionclass import Session
import IpallUser
import cgitb; cgitb.enable()
from Configobj import ConfigObj


def main():
    
    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 3:
            vrf = str(qs.split("&")[0])
            parent_id = int(qs.split("&")[1])
            path = str(qs.split("&")[2])
        else:
            vrf = "None"
            parent_id = 0  
            path = "0"
    else:
        vrf = "None"
        parent_id = 0
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
    HTML = HtmlContent()

    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights(vrf)
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']
    if group == 0:
        HTML.restriction_message()
        return

    HTML.ajax_header()

    child_query = """SELECT * FROM ipall_ip WHERE parent_id=%u AND vrf='%s' ORDER BY address""" % (parent_id, str(vrf))
    childs = conn.get_data(child_query)

##    depth = len(path.split(":"))
##    p = int(path.split(":")[depth-1])

    for n in childs:
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

        net = Tree.Node(rights, net_perm, len(n[6].split(":")), n[6], vrf)
        for i in n[6].split(":"):
            if int(i) == n[0]:
                id_found = 1


        if net_perm[3] != 1:
            continue
        else:
            print """<div id="net%s">""" % str(n[0])
            print """<tr><td align=center>"""

        print """<table class="table_networks"><tr height=20>"""

        ### build tree of networks with plus and minus symbols
        if net_perm[3] == 1:
            net.print_plus(n[7], n[0])
            net.print_node(n)
            #net.print_actions(n[0], n[14])
        print """</tr></table></div>"""

        print """</td></tr>"""        
        print """<tr><td>"""
        print """<div style="display:none" id="net%s_%s"><img src="%s/images/indicator.gif"></div>""" % ( str(n[0]), str(n[0]), ipall_dir )
        print """</td></tr>"""

##        if path != "0":
##            depth = len(path.split(":"))
##            for r in range(1, (depth)):
##                q = int(path.split(":")[r])
##                #print q, "-", n[0]
##                if q == int(n[0]):
##                    # callNode(id, ipall_dir, cgi_dir, vrf, path)
##                    #print q, "-", n[0], " - "
##                    print """callNode('%s', '%s', '%s', '%s', '%s')""" % ( q, ipall_dir, cgi_dir, vrf, path )
##                    print """<script language="javascript">callNode('%s', '%s', '%s', '%s', '%s');</script>""" \
##                        % ( q, ipall_dir, cgi_dir, vrf, n[6] )


main()
