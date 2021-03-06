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
import IpallUser
from Sessionclass import Session
import os
import cgi
import IPy
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie
from time import asctime


def main():
    """entry point for executing IPALL"""

    ### definitions of variables
    global conn, depth, path, view
    formdata = cgi.FieldStorage()
    uri = label = path = vrf = ""
    companies_id = parent_id = 0
    has_peering = as_nr = max_prefix = routeserver = session_up = 0
    as_set = md5 = mail = peer_device = peer_descr = ""

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        #if len(qs.split("&")) == 1:
        try:
            id = int(qs.split("&")[0])
        except:
            HTML.restriction_message()
            return

    ### create database connection object
    cfg = ConfigObj("ipall.cfg")
    db_host = cfg['Database']['db_host']
    db_user = cfg['Database']['db_user']
    db_pw = cfg['Database']['db_pw']
    db = cfg['Database']['db']
    conn = DBmy.db(db_host, db_user, db_pw, db)

    HTML = HtmlContent()

    s = Session(conn)
    current_user = s.check_user()
    HTML.simple_header()
    if current_user == "":
        HTML.simple_redirect_header(cfg['Server']['web_dir'])
        return
    else:
        HTML.popup_body()

    ## User
    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    ipall_dir = cfg['Server']['ipall_dir']

    if group == 0:
        HTML.restriction_message()
        return

    if group == 1 or rights[2] == 1:
        net_perm = 1
    else:
        net_perm = conn.get_net_permissions(path, group)
        if net_perm == () or net_perm == "":
            net_perm = 0
        else:
            net_perm = net_perm[2]

    if net_perm != 1:
        HTML.restriction_message()
        return

    print """<br>"""
    print """<div id="main">"""
    print """<div id="table_main">"""
    print """<div id="functionHead">
        <span> Import child networks via CSV </span></div>"""

    if formdata.has_key("save"):
        try:
            if formdata.has_key("uri"):
                uri = str(formdata['uri'].value)
            if formdata.has_key("label"):
                label = str(formdata['label'].value)
            if formdata.has_key("path"):
                path = str(formdata['path'].value)
            if formdata.has_key("vrf"):
                vrf = str(formdata['vrf'].value)
            if formdata.has_key("parent_id"):
                parent_id = int(formdata['parent_id'].value)
            if formdata.has_key("companies_id"):
                companies_id = int(formdata['companies_id'].value)
            if formdata.has_key("filename"):
                item = formdata["filename"]
        except:
            print """<script language="javascript">alert("Value parse error, sorry!"); history.back();</script> """

        if item.file:
            error = 0
            line_nr = 0
            data = item.file.readlines()
            for d in data:
                line_nr += 1
                if len(d.split(";")) == 5 or len(d.split(";")) == 14:
                    if d.split(";")[0] != "":
                        network = d.split(";")[0]
                    else:
                        msg = "no network in line", line_nr,": ", d, " -> not imported"
                        HTML.notify_message(msg)
                        continue
                    if d.split(";")[1] != "":
                        name = d.split(";")[1]
                    else:
                        msg = "no name in line", line_nr,": ", d, " -> not imported"
                        HTML.notify_message(msg)
                        continue
                    if d.split(";")[2] != "":
                        descr = "'" + d.split(";")[2] + "'"
                    else:
                        descr = "NULL"
                    if d.split(";")[3] != "":
                        service_id = int(d.split(";")[3])
                    else:
                        service_id = 1
                    if d.split(";")[4] != "":
                        interface_name = "'" + d.split(";")[4] + "'"
                        interface_name = interface_name.lower().replace(" ", "")
                    else:
                        interface_name = "NULL"
                    if len(d.split(";")) == 14:
                        has_peering = 1
                        service_id = 11
                        if d.split(";")[5] != "":
                            as_nr = int(d.split(";")[5])
                        else:
                            msg = "no AS number specified -> not imported"
                            HTML.notify_message(msg)
                            continue
                        if d.split(";")[6] != "":
                            as_set = "'" + d.split(";")[6] + "'"
                        else:
                            as_set = "NULL"
                        if d.split(";")[7] != "":
                            max_prefix = int(d.split(";")[7])
                        else:
                            max_prefix = "NULL"
                        if d.split(";")[8] != "":
                            md5 = "'" + d.split(";")[8] + "'"
                        else:
                            md5 = "NULL"
                        if d.split(";")[9] != "":
                            mail = "'" + d.split(";")[9] + "'"
                        else:
                            mail = "NULL"
                        if d.split(";")[10] != "":
                            peer_device = "'" + d.split(";")[10] + "'"
                        else:
                            msg = "no peering device specified -> not imported"
                            HTML.notify_message(msg)
                            continue
                        if d.split(";")[11] != "":
                            routeserver = 1
                        else:
                            routeserver = 0
                        if d.split(";")[12] != "":
                            session_up = 1
                        else:
                            session_up = 0
                        if d.split(";")[13] != "":
                            peer_descr = "'" + d.split(";")[13] + "'"
                        else:
                            peer_descr = "NULL"

                    try:
                        net = IPy.IP(network)
                        parent = IPy.IP(label)
                    except:
                        message = """no valid network: %s ...""" % (network)
                        HTML.notify_message(message) 
                        continue

                    sql_check = """SELECT id FROM ipall_ip WHERE vrf="%s" AND parent_id=%u AND label="%s" 
                        AND address=%u """ % ( vrf, parent_id, network, int(net.strDec()) )
                    check = conn.get_data(sql_check)

                    if check != () and check != 0:
                        msg = "network <i>" + network + "</i> already exists -> not imported"
                        HTML.notify_message(msg)
                        continue

                    if parent.overlaps(net) == 0:
                        msg = "network <i>" + network + "</i> is not a subnet of " + label + " -> not imported"
                        HTML.notify_message(msg)
                        continue

                    if has_peering == 1:
                        sql_ins_peering = """INSERT INTO ipall_peering_info VALUES 
                            ('', %u, %s, %s, %u, %u, %s, %s, %s, %s)""" \
                            % (as_nr, as_set, md5, routeserver, session_up, mail, peer_descr, peer_device, max_prefix)
                        #print "peering: %s<br>" % sql_peering
                        peer_id = conn.insert_data(sql_ins_peering)
                    else:
                        peer_id = "NULL"

                    sql_ins = """INSERT INTO ipall_ip SET parent_id=%u, label='%s', address=%u, 
                        net_name='%s', description=%s, path='%s', vrf='%s', 
                        service_id=%u, interface_name=%s, companies_id=%u, peering_info_id=%s """ \
                        % ( parent_id, network, int(net.strDec()), name, descr, path, vrf, service_id, interface_name, companies_id, str(peer_id) ) 
                    message = """inserting %s ...""" % (network)
                    HTML.notify_message(message) 

                    net_id = conn.insert_data(sql_ins)

                    if net_id != 0:
                        new_path = path + ":" + str(net_id)

                        ### set the path field correctly
                        sql_update = """UPDATE ipall_ip SET path='%s' WHERE id=%u """ % (str(new_path), int(net_id))
                        error = conn.update_data(sql_update)
                    else:
                        message = """error while inserting %s ...""" % (network)
                        HTML.notify_message(message) 
                else:
                    msg = "error in line: ", d, "<br>"
                    HTML.notify_message(msg)
                    continue
                print "<br>"
        sql_check = """SELECT count(id) FROM ipall_ip WHERE parent_id=%u """ % parent_id    
        check = conn.get_data(sql_check)
        if check != ():
            sql_upd_parent = """UPDATE ipall_ip SET subnetted=1 WHERE id=%u """ % parent_id
            error = conn.update_data(sql_upd_parent)
        else:
            sql_upd_parent = """UPDATE ipall_ip SET subnetted=0 WHERE id=%u """ % parent_id
            error = conn.update_data(sql_upd_parent)
    else:   ## no "submit"
        sql_net = """SELECT label, path, vrf, service_id, companies_id FROM ipall_ip WHERE id=%u """ % int(id)
        parent_net = conn.get_data(sql_net)

        print """<form name="new_subnet_csv" method=POST action="network_upload_csv.cgi" enctype="multipart/form-data">"""
        print """<input type=hidden name=parent_id value="%s">""" % str(id)
        print """<input type=hidden id="label" name=label value="%s">""" % str(parent_net[0][0])
        print """<input type=hidden id="path" name=path value="%s">""" % str(parent_net[0][1])
        print """<input type=hidden id="vrf" name=vrf value="%s">""" % str(parent_net[0][2])
        print """<input type=hidden id="companies_id" name=companies_id value="%s">""" % str(parent_net[0][4])

        print """
            <div>The format of the CSV has to be (otherwise it will not work!):</div>
            <div class=textPurpleBold>
                network; name; description; nettype id; interface <br>
                -> 5 fields (4 semicolons)
            </div> 
            or
            <div class=textPurpleBold>
                network; name; description; nettype id; interface; as nr; as set; max prefix; md5; email; device; routeserver; session up; comment <br>
                -> 14 fields (13 semicolons)
            </div> 
            <p>
            <div>
            <span style="float: left; width: 100px;">1. network *</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 630px;">e.g. 192.168.1.0/24 </span>
            </div>
            <div>
            <span style="float: left; width: 100px;">2. name *</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 630px;">max. 35 characters (is displayed in "[]" next to the network</span>
            </div>
            <div>
            <span style="float: left; width: 100px;">3. description</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 630px;">anything else you want do document</span>
            </div>
            <div>
            <span style="float: left; width: 100px;">4. nettype_id</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 630px;">can be found under "management -> Network types" (will be "1" if empty)</span>
            </div>
            <div>
            <span style="float: left; width: 100px;">5. interface</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 630px;">e.g. fastethernet0/0</span>
            </div></p>"""
        print """<p><div class="TextPurpleBold">If the network is BGP Peering the following fields must be provided, too</div>"""
        print """
            <div>
            <span style="float: left; width: 120px;">6. AS nr *</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 610px;">Autonomous System number of the peering partner</span>
            </div>
            <div>
            <span style="float: left; width: 120px;">7. AS set</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 610px;">AS macro of the peering partner</span>
            </div>
            <div>
            <span style="float: left; width: 120px;">8. max prefix</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 610px;">the received prefixes exceed your default config</span>
            </div>
            <div>
            <span style="float: left; width: 120px;">9. MD5</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 610px;">BGP MD5 hash configured with this peer</span>
            </div>
            <div>
            <span style="float: left; width: 120px;">10. email</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 610px;">NOC or peering email address</span>
            </div>
            <div>
            <span style="float: left; width: 120px;">11. device *</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 610px;">your own peering device name</span>
            </div>
            <div>
            <span style="float: left; width: 120px;">12. routeserver</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 610px;">Peering is also available at routeserver [0 or 1]</span>
            </div>
            <div>
            <span style="float: left; width: 120px;">13. session up</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 610px;">the session came up? [0 or 1]</span>
            </div>
            <div>
            <span style="float: left; width: 120px;">14. comment</span>
            <span style="float: left; width: 50px;">...</span>
            <span style="float: left; width: 610px;">anything else you want to document</span>
            </div></p>
            """
        print """<div>&nbsp;</div>"""

        print """<div><input type=file id="filename" name=filename accept="text" class=b_eingabefeld></div>"""
        print """<div><br><input type=submit name=save value=submit class=button></div>"""
        print """<div><br>* required field</div>"""
        print """</form>"""

    print """<div id=message><a href="javascript:void(0);" onClick="parent.location.reload(1);" class="LinkPurpleBold">close and refresh</a></div>"""
    print """</div>""" # table_main
    print """</div>""" # main

    HTML.close_body()

main()
