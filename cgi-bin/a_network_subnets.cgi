#!/usr/bin/python

"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
"""

import os
import IP
import IPy
import DBmy
import IpallUser
from Html_new import HtmlContent
from Sessionclass import Session
from Configobj import ConfigObj
from math import ceil


def main():
    """return subnets"""
    
    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 2:
            id = int(qs.split("&")[0])
            mask = int(qs.split("&")[1])
            index = 1
        elif len(qs.split("&")) == 3:
            id = int(qs.split("&")[0])
            mask = int(qs.split("&")[1])
            index = int(qs.split("&")[2])
        else:
            id = mask = 0
            index = 1
    else:
        id = mask = 0
        index = 1

    ### create database connection object
    cfg = ConfigObj("ipall.cfg")
    db_host = cfg['Database']['db_host']
    db_user = cfg['Database']['db_user']
    db_pw = cfg['Database']['db_pw']
    db = cfg['Database']['db']
    nw = int(cfg['Site']['networks'])
    conn = DBmy.db(db_host, db_user, db_pw, db)

    ### user
    s = Session(conn)
    current_user = s.check_user()
    HTML = HtmlContent()
    #company = s.check_cookie()

    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']
    if group == 0:
        return

    HTML.ajax_header()

    sql_parent_net = """SELECT label, path, vrf, id FROM ipall_ip WHERE id=%u """ % int(id)
    parent_net = conn.get_data(sql_parent_net)
    parent = IPy.IP(parent_net[0][0])

    if group == 1 or rights[2] == 1:
        net_perm = 1
    else:
        net_perm = conn.get_net_permissions(parent_net[0][1], group)
        #print net_perm
        if net_perm == () or net_perm == "":
            net_perm = 0
        else:
            net_perm = net_perm[2]

    if net_perm != 1:
        return

    if parent_net != ():
        ### calculate the pages of subnets for the index 
        if int(parent.version()) == 6:
            pages_len = 2 ** (mask - int(parent.prefixlen())) 
            pages = pages_len / nw  
        else:
            pages = 1

        ### get the subnets
        new_nets, childs_len, net_len = IP.calc_networks(id, parent, mask, index, conn)
        return_value = ""
        if new_nets != ():
            for n in new_nets:
                if return_value == "":
                    return_value = n
                else:
                    return_value = return_value + "," + n

        ### separate networks, index, and amount of pages by semicolons
        print return_value + ";" + str(index) + ";" + str(pages)


main()
