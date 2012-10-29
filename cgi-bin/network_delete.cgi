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
import Whois
import IPy
import os
import re
import cgi
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie


def main():
    """delete a network"""

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        try:
            vrf = str(qs.split("&")[0])
            path = str(qs.split("&")[1])
            id = int(qs.split("&")[2])
        except:
            current_user = path = ""
            vrf = "NULL"
            id = 0
    else:
        current_user = path = ""
        view = "NULL"
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
        HTML.popup_body()

    user = IpallUser.User(current_user)
    group, company_id  = user.get_group_id()
    rights = user.get_rights()
    cgi_dir = cfg['Server']['cgi_dir']
    if group == 0:
        HTML.restriction_message(1)
        HTML.main_footer()
        return

    if id == 0:
        HTML.error_message("No Prefix found to delete ", "parent.location.reload(1);")
        return
    else:
        sql_path = """SELECT parent_id, path, label, net_name, companies_id FROM ipall_ip WHERE id=%u""" % id
        path = conn.get_data(sql_path)
        if path != ():
            parent_id = path[0][0]
            label = path[0][2]
            netname = path[0][3]
            companies_id = path[0][4]
            path = path[0][1]
        else:
            parent_id = companies_id = 0
            path = "0"
            label = netname = ""

    if group != 1 and rights[2] != 1:
        net_perm = conn.get_net_permissions(path, group)
        if net_perm == ():
            net_perm = 0
        else:
            net_perm = net_perm[0]
    else:
        net_perm = 1 
        
    if net_perm != 1:
        HTML.restriction_message(1) 
        HTML.main_footer()
        return 

    ### logged in user does have enough rights to 
    else:
        try:
            parent_id = path.split(":")[-2]
        except:
            HTML.error_message("operation is not possible...")
            return
        childs_query = """SELECT id FROM ipall_ip WHERE parent_id=%u """ % id
        childs = conn.get_data(childs_query)

        print """<br>"""
        print """<div id="main">"""
        print """<div id="table_main">"""

        back = """parent.location.reload(1);"""

        if childs == () or childs == None:
            ### NO child networks are present
            sql_net = """SELECT peering_info_id, label, net_name FROM ipall_ip where id=%u""" % id
            net = conn.get_data(sql_net)
            if net[0][0] != None:
                sql_peer_del = """DELETE FROM ipall_peering_info where id=%u""" % int(net[0][0])
                del_peer = conn.update_data(sql_peer_del)

                ### LOGGING
                sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_peering_info', "%s", %u)""" \
                    % (current_user, sql_peer_del, companies_id)
                log = conn.update_data(sql_log)

                sql_rights_del = """DELETE FROM ipall_rights where path='%s'""" % str(path)
                del_rights = conn.update_data(sql_rights_del)

                ### LOGGING
                sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_rights', "%s", %u)""" % (current_user, sql_rights_del, int(companies_id) )
                log = conn.insert_data(sql_log)

                if del_peer == 1 and del_rights == 1 and log != 0:
                    HTML.notify_message("Peering info has been successfully deleted!")
                else:
                    HTML.error_message("An error has occured!", back)

            sql_del = """DELETE FROM ipall_ip WHERE id=%u """ % id
            delete = conn.update_data(sql_del)

            ### LOGGING
            log_string = sql_del + "; " + net[0][1] + "; " + net[0][2]
            sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), 'ipall_ip', "%s", %u)""" % (current_user, log_string, companies_id)
            log = conn.insert_data(sql_log)

            if delete == 1:
                ripe = Whois.whois()
                HTML.notify_message("Network has been successfully deleted!")
                if len(path.split(":")) == 2:
                    print """<div id=message><a href="javascript:void(0);" onClick="parent.location.reload(1);" class="LinkPurpleBold">close and refresh</a></div>"""
                else:
                    print """<div id=message><a href="javascript:void(0);" onClick="parent.location.reload(1);" class="LinkPurpleBold">close and refresh</a></div>"""
                    #print """<div id=message><a href="javascript:void(0);" onClick="callNodeWindow('parent', );" class="LinkPurpleBold">close and refresh</a></div>"""
                sql_notify = """SELECT send_delete_mail, delete_mail FROM companies WHERE id=%u """ % ( int(companies_id) )
                notify = conn.get_data(sql_notify)
                if notify != () and notify != 0:
                    send_mail = notify[0][0]
                    notify_mail = notify[0][1]
                    ### mail should be sent when a network was deleted
                    if send_mail == 1:
                        body = ""
                        body = body + """The following network has been deleted by %s\n""" % ( current_user )
                        body = body + """IP:     %s\n""" % ( label )
                        body = body + """Name:   %s\n""" % ( netname )
                        ripe.send_mail( user.get_mail_address(), notify_mail, "IP@LL: network deleted", body  )


                sql_chk = """SELECT id FROM ipall_ip WHERE parent_id=%u """ % int(parent_id)
                another_nets = conn.get_data(sql_chk)
                if another_nets == ():
                    sql_upd_parent = """UPDATE ipall_ip SET subnetted=0 WHERE id=%u """ % int (parent_id)
                    upd_parent = conn.update_data(sql_upd_parent)
                    #print sql_upd_parent, "<br>"

                ### delete objects of ripe db
                body = inetnum = ""

                #back = """%s/networks.cgi?%s&%s#%s"""  % (cgi_dir, str(vrf), path, str(id))
                if net != ():
                    net = net[0][1]
                    try:
                        #return ### no connection possible to external port 43
                        inetnum = ripe.ip("-T inetnum -B " + net)
                    except:
                        print "whois query was not possible"
                        return
                    for l in inetnum.split("\n"):
                        #print l, "<br>"
                        if l.find("%") != -1 or len(l) == 0:
                            continue
                        elif l.find("source:") == -1:
                            if l.find("inetnum:") != -1:
                                inetnum = l[10:].replace(" ", "")
                                body = body + l + "\n"
                        else:
                            break

                net_obj = IPy.IP(net)

                if inetnum == net_obj.strNormal(3):
                    body = body + "source:         RIPE\n"
                    body = body + "delete:          IP@LL auto delete\n"
                    print """<div class=TextPurpleBold>Ripe object</div>"""
                    print """<div id=table_main><div class=TextPurple>"""
                    print re.sub('\n', '<br>', body)
                    print """</div></div>"""
                    print """<div class=TextPurpleBold><p>Send mail to "%s" to delete the network from database?</p></div>""" \
                        % cfg['Server']['ripe_mail']
                    print """<form name="ripe_delete" method=POST action="delete_ripe.cgi">"""
                    print """<input type=hidden name=id value="%s">""" % id
                    print """<input type=hidden name=companies_id value="%s">""" % companies_id
                    print """<input type=hidden name=body value="%s">""" % body
                    print """<input type=hidden name=back value="%s">""" % back
                    print """<div><input type=submit name=send value=send class=button></div>"""
                    print """</form>"""
            else:   ### delete != 1
                HTML.notify_message("An error has occured!")
        else:	### network has child networks
            HTML.notify_message("There are child networks present. You can't delete this network")

        print """</div>""" #table_main
        print """</div>""" #main


    HTML.popup_footer()

main()
