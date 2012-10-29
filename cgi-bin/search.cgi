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


def print_search_form():
    """print a html form for searching in NMS database"""

    print """<form name="ipall_search" method=POST action="search.cgi">"""
    
    print """<input type=hidden name=vrf value="%s">""" % str(vrf)
    #print """</tr><tr>"""
    
    ### LEFT SIDE
    print """<div id="pos_left">"""
    print """<div class="lineOdd">1. Network address or Network description</div>"""
    print """<div class="lineEven">2. Peering information</div>"""
    print """<div class="lineOdd">3. Network type</div>"""
    print """</div>""" # left side

    ### RIGHT SIDE
    print """<div id="pos_right">"""
    print """<div class="lineOdd"><input type=radio name=search_type value="network" checked></div>"""
    print """<div class="lineEven"><input type=radio name=search_type value="peering">"""
    print """<input type=text name=search_text onKeyUp="document.ipall_search.search_type[2].checked=false;" 
        class=b_eingabefeld_226 value="choose 1. or 2." onFocus="this.value='';"></div>"""
    print """<div class="lineOdd"><input type=radio id="search_type" name=search_type value="service">"""
    print """<select name=net_type onChange="document.ipall_search.search_type[2].checked=true;" class=b_eingabefeld_226>"""
    print """<option value=0>&nbsp;</option>"""
    all_types = get_net_types()
    for t in all_types:
        print """<option value=%u>%s</option>""" % (t[0], t[1])
    print """</select>"""
    print """<input type=checkbox id="allocated" name=allocated> allocated"""
    print """</div>""" 
    print """</div>""" #right side
    
    print """<div id="pos_clear"><br><input type=submit name=search value=search class=button></div>"""

    print """<p><a href="javascript:void(0);" id="toggle_help" title="helpful instructions" 
        onClick="toggle_msg(this, 'need some help?', 'do not need help!');">need some help?</a>
        <div id=info>
        <p>To search for IP addresses / networks please select the radiobutton next to point 1. <br>
        and enter the search string into the text field in the <i>second line</i>!</p>
        <p>To search for Peering Partner information (AS nr, AS-set, etc.) please select the radiobutton next to point 2. <br>
        and enter the search string into the text field in the <i>second line</i>!</p>
        <p>To search for all IP addresses / networks of a specific type please choose the type in the dropdown box at point 3.<br>
        The "allocated" checkbox excludes all IPs which do not have this flag set (You can set this when creating a (sub-)network or when you edit one).
        </div></p>"""
    print """</form>"""


def get_net_types(id=0):
    """return dropdown box <option> with network types"""

    if id == 0:
        sql_net_types = """SELECT * FROM ipall_network_types ORDER BY typename"""
    else:
        sql_net_types = """SELECT * FROM ipall_network_types WHERE id=%u""" % id
    net_types = conn.get_data(sql_net_types)
        
    return net_types


def main():
    """description"""

    global conn, vrf
    formdata = cgi.FieldStorage()
    search_type = search_text = ""
    vrf = ""
    net_type = 0
    allocated = "off"

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        try:
            vrf = str(qs.split("&")[0])
        except:
            vrf = ""
    else:
        vrf = ""

    try:
        if formdata.has_key("vrf"):
            vrf = str(formdata['vrf'].value)
        if formdata.has_key("search_type"):
            search_type = str(formdata['search_type'].value).lower()
        if formdata.has_key("search_text"):
            search_text = str(formdata['search_text'].value)
        if formdata.has_key("net_type"):
            net_type = str(formdata['net_type'].value)
        if formdata.has_key("allocated"):
            allocated = str(formdata['allocated'].value)
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
    if group == 0:
        HTML.restriction_message(1)
        HTML.popup_footer()
        return

    if vrf == "":
        HTML.notify_message("No View/VRF seleced for search!")
        HTML.popup_footer()
        return

    if formdata.has_key("search"):
        #print search_type, "<br>"
        #print search_text, "<br>"
        if allocated == "on": allocated = 1;
        else: allocated = 0

        if re.search("^as[0-9]", search_text, re.I):
            search_text = search_text.lower().replace("as", "")

        if search_type == "network":
            sql_search = """SELECT id, label, path, vrf, net_name FROM ipall_ip WHERE 
                (label LIKE '%s%s' OR net_name LIKE '%s%s%s') AND vrf='%s'
                ORDER BY address, label""" \
                    % ( search_text, "%", "%", search_text, "%", vrf )
        elif search_type == "peering":
            sql_search = """SELECT i.id, i.label, i.path, i.vrf, i.net_name FROM ipall_ip i, ipall_peering_info p WHERE 
                (i.peering_info_id=p.id AND p.as_nr LIKE '%s' OR p.as_set LIKE '%s' OR p.contact LIKE '%s' OR p.device LIKE '%s') 
                AND i.vrf='%s' ORDER BY i.address, i.label""" % (search_text, search_text, search_text, search_text, vrf)
        elif search_type == "service":
            if allocated == 1:
                sql_search = """SELECT id, label, path, vrf, net_name FROM ipall_ip WHERE 
                    service_id=%u AND allocated=1 AND vrf='%s'
                    ORDER BY address, label""" % (int(net_type), vrf)
            else:
                sql_search = """SELECT id, label, path, vrf, net_name FROM ipall_ip WHERE 
                    service_id=%u AND vrf='%s'
                    ORDER BY address, label""" % (int(net_type), vrf)
        else:   
            HTML.error_message("Error<br>")
            return

        print sql_search, "<br>"
        result = conn.get_data(sql_search)
        #print result[0]

        print """<div id="main">"""
        print """<div id="table_main">"""

        ### HEADING
        print """<div id="functionHead">IP@LL network search</div>"""

        for r in result:
            print """<div id="pos_left"><a href="%s/network_view.cgi?%s">%s (%s)</a></div>""" % (cgi_dir, r[0], r[1], r[4])
            print """<div id="pos_rigth">"""
            print """<img src="%s/images/editOff.png" id="edit"  onMouseOver="mouseoverImage(this, '%s');"  
                    onMouseOut="mouseoverImage(this, '%s');" onClick="redirect_to_url('%s/network_edit.cgi?%s');" 
                    class=handlers title="edit details"></a>""" % ( ipall_dir, ipall_dir, ipall_dir, cgi_dir, str(r[0]) )
            print """</div>"""
            print """<div id="pos_clear"></div>"""

    else:
        print """<div id="main">"""
        print """<div id="table_main">"""

        ### HEADING
        print """<div id="functionHead">IP@LL network search</div>"""

        print_search_form()

        print """</div>""" # main
        print """</div>""" # table_main
        print """<script language="javascript">
            window.addEvent('domready', function() {  
                toggleVisibility('info', 'toggle_help');
            });
            </script>"""

        
    HTML.popup_footer()

main()
