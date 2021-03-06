"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
"""

from Html_new import HtmlContent
import os
from Configobj import ConfigObj
from Cookie import SimpleCookie
from string import zfill
from time import localtime

class Session:
    """helper class for handling session cookies and users"""
    def __init__(self, conn):
        self._cfg_ = ConfigObj("ipall.cfg")
        self._url_ = self._cfg_['Server']['web_dir']
        self._conn_ = conn

    def check_user(self):
        """check if a valid user is logged in and return the according company id"""
        if os.environ.has_key('HTTP_COOKIE') and os.environ['HTTP_COOKIE'] != "":
            C = SimpleCookie(os.environ['HTTP_COOKIE'])
            ### python2.4 related
            #phpsessid = str(C['PHPSESSID']).split("=")[1][:-1]
            ### python2.5+
            phpsessid = str(C['PHPSESSID']).split("=")[1]
            sql_session = """SELECT username, ip, starttime, endtime FROM php_session WHERE phpsessid='%s' """ % ( str(phpsessid) )
            session = self._conn_.get_data(sql_session)

            if session != ():
                user = session[0][0]
                user_ip = session[0][1]
                sess_start = session[0][2]
                sess_end = session[0][3]

                ### check the stored ip with the actual user ip
                if os.environ.has_key('REMOTE_ADDR') and os.environ['REMOTE_ADDR'] != user_ip:
                    return ""

                ### create date string for comparison
                y = zfill(str(localtime()[0]), 2)
                m = zfill(str(localtime()[1]), 2)
                d = zfill(str(localtime()[2]), 2)
                h = zfill(str(localtime()[3]), 2)
                i = zfill(str(localtime()[4]), 2)
                s = zfill(str(localtime()[5]), 2)
                now = y+m+d+h
                end = sess_end[0:10]
                if int(now) > int(end):
                    return ""
                else:
                    summe = int(i) + 60
                    min = summe % 60
                    uebertrag = summe / 60
                    std = int(h) + uebertrag
                    new_end = y+m+d+str(std)+str(min)+s
                    sql_upd_sess = """UPDATE php_session SET endtime='%s' WHERE phpsessid='%s' """ % ( new_end, phpsessid )
                    upd = self._conn_.update_data(sql_upd_sess)
            else:
                return "" 
            return user
        else:
            return ""

    def check_cookie(self):
        """check, if the cookie with the session variable is set"""
        HTML = HtmlContent()
        if os.environ.has_key('HTTP_COOKIE') and os.environ.has_key('HTTP_REFERER'):
            C = SimpleCookie(os.environ['HTTP_COOKIE'])
            if C.has_key('session') and C['session'].value != "":
                if C.has_key('company') and C['company'].value != "":
                    company = C['company'].value
                else:
                    company = -1
            else:
                HTML.simple_redirect_header(self._url_)
                return	
            return company
        else:
            HTML.simple_redirect_header(self._url_)
            return
