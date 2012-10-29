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
import cgi
import re
import cgitb; cgitb.enable()
from Configobj import ConfigObj
from Cookie import SimpleCookie


def main():
    """update the aut-num object in the RIPE database where all the upstreams, 
    downstreams, and peerings are docuemted"""

    if os.environ.has_key('QUERY_STRING') and os.environ['QUERY_STRING'] != "":
        qs = os.environ['QUERY_STRING']
        if len(qs.split("&")) == 1:
            id = int(qs.split("&")[0])
        else:
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
    
    if group != 1 and rights[2] != 1: # user is not member of group "Super Administrators" or company admin
        net_perm = 0
    else: # user is member of group "admins"
        net_perm = 1

    if net_perm != 1:
        HTML.restriction_message()
        return

    ### logged in user does have enough rights to 
    if id != 0:
        sql_ripe_details = """SELECT ripe_header, ripe_trailer, ripe_password, ripe_mntby, ripe_admin_c, ripe_tech_c, ripe_notify, 
            as_nr, as_set, name, description FROM companies WHERE id=%u """ % int(id)
        ripe_details = conn.get_data(sql_ripe_details)
    else:
        ripe_details = ()
        
    if ripe_details == () or ripe_details == None:
        HTML.error_message("No Ripe details found!")
        return
    else:
        ripe_header = ripe_details[0][0]
        ripe_trailer = ripe_details[0][1]
        if ripe_details[0][2] != "":
            ripe_password = ripe_details[0][2]
        else:
            print """<script language="javascript">alert("RIPE password not set!"); history.back();</script> """; return;
        if ripe_details[0][3] != "" and ripe_details[0][3] != " ":
            ripe_mntby = ripe_details[0][3]
        else:
            print """<script language="javascript">alert("RIPE mnt-by not set!"); history.back();</script> """; return;
        if ripe_details[0][4] != "" and ripe_details[0][4] != " ":
            ripe_admin_c = ripe_details[0][4]
        else:
            print """<script language="javascript">alert("RIPE admin-c not set!"); history.back();</script> """; return;
        if ripe_details[0][5] != "" and ripe_details[0][5] != " ":
            ripe_tech_c = ripe_details[0][5]
        else:
            print """<script language="javascript">alert("RIPE tech-c not set!"); history.back();</script> """; return;
        if ripe_details[0][6] != "" and ripe_details[0][6] != " ":
            ripe_notify = ripe_details[0][6]
        else:
            print """<script language="javascript">alert("RIPE notify email address not set!"); history.back();</script> """; return;
        if ripe_details[0][7] != 0 and ripe_details[0][7] != " ":
            as_nr = ripe_details[0][7]
        else:
            print """<script language="javascript">alert("AS number not set!"); history.back();</script> """; return;
        if ripe_details[0][8] != "" and ripe_details[0][8] != " ":
            as_set = ripe_details[0][8]
        else:
            print """<script language="javascript">alert("AS-SET not set!"); history.back();</script> """; return;
        if ripe_details[0][9] != "" and ripe_details[0][9] != " ":
            name = ripe_details[0][9]
        else:
            print """<script language="javascript">alert("name not set!"); history.back();</script> """; return;
        descr = ripe_details[0][10]
        

    ripe_pw = """password:      """ + ripe_password
    body = ""
    w = Whois.whois()
    autnum = w.ip("-B -T aut-num -r AS" + str(as_nr))

    body = body + """password:     %s \n""" % ripe_password
    body = body + """aut-num:      AS%s \n""" % str(as_nr)
    body = body + """as-name:      %s \n""" % str(name)
    if descr != "":
        if len(descr.split("\n")) > 1:
            for d in descr.split("\n"):
                body = body + """descr:        %s \n""" % str(d)
        else:
            body = body + """descr:        %s \n""" % str(descr)
    
    if ripe_header != "":
        body = body + ripe_header + " \n"

    ## peerings
    sql_peerings = """SELECT id, net_name FROM ipall_ip WHERE service_id=11 and allocated=1 """
    peerings = conn.get_data(sql_peerings)
    
    if peerings != () and peerings != None:
        for p in peerings:
            body = body + """remarks:      ************************* \n"""
            body = body + """remarks:      %s \n""" % str(p[1]).upper()
            sql_childs = """SELECT peering_info_id FROM ipall_ip WHERE parent_id=%u """ % int(p[0])
            childs = conn.get_data(sql_childs)
            if childs != () and childs != None:
                body = body + """remarks:      ************************* \n"""
                for c in childs:
                    try:
                        p_id = int(c[0])
                    except:
                        continue
                    #sql_as_numbers = """SELECT DISTINCT(pi.as_nr), pi.as_set FROM ipall_peering_info pi, ipall_ip ip 
                    #    WHERE pi.id=ip.peering_info_id=%u """ % p_id
                    sql_as_numbers = """SELECT DISTINCT(pi.as_nr), pi.as_set FROM ipall_peering_info pi, ipall_ip ip 
                        WHERE pi.id=%u """ % p_id
                    as_numbers = conn.get_data(sql_as_numbers)
                    if as_numbers != () and as_numbers != None:
                        for a in as_numbers:
                            if a[1] != "" and a[1] != None and a[1] != "0":
                                body = body + """import:       from AS%s accept   %s \n""" % ( str(a[0]), str(a[1]) )
                                body = body + """export:       to   AS%s announce %s\n""" % ( str(a[0]), as_set )
                            else:
                                body = body + """import:       from AS%s accept   AS%s \n""" % ( str(a[0]), str(a[1]) )
                                body = body + """export:       to   AS%s announce %s\n""" % ( str(a[0]), as_set )
                            

    mail = user.get_mail_address()
    today = user.get_today()
    changed = ""

    c = autnum.count("changed:") - 1
    r = 0
    for a in autnum.split("\n"):
        if a.find("changed:") != -1: 
            r += 1
            if r > (c - 10):
                changed = changed + a + "\n"
            elif a.find("source:") != -1:
                break
            else:
                continue

    if ripe_trailer != "":
        body = body + ripe_trailer + " \n"

    body = body + """remarks:      *************************
admin-c:      %s
tech-c:       %s
mnt-by:       %s
%schanged:      %s %s
source:       RIPE\n""" % (ripe_admin_c, ripe_tech_c, ripe_mntby, changed, mail, today)


    if group == 1 or rights[2] == 1:
        if cfg['Server']['ripe_mail'] != "":
            ripe_mail = cfg['Server']['ripe_mail']
            sent = w.send_mail(mail, ripe_mail, "IP@LL auto register: AS" + str(as_nr), body)
            if sent != 0:
                show_body = re.sub('\n', "<br>", body)
                HTML.notify_message(show_body)
                success_text = """<br><br>Mail to "%s" was sent successfully""" % ripe_mail
                HTML.notify_message(success_text) 
            else:
                show_body = re.sub('\n', "<br>", body)
                HTML.notify_message(show_body)
                HTML.notify_message("<br><br>Mail was not sent")


    HTML.main_footer()

main()
