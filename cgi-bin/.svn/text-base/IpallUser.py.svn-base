"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 racyAPz
http://www.racyapz.at
*****************************
"""

import DBmy
from time import localtime
from string import zfill
from Configobj import ConfigObj


class User:
    
    def __init__(self, username):
        """IpallUser 
        username    ...	    must be unique in database"""

        self._username_ = username
        self._cfg_ = ConfigObj("ipall.cfg")
        self._db_host_ = self._cfg_['Database']['db_host']
        self._db_user_ = self._cfg_['Database']['db_user']
        self._db_pw_ = self._cfg_['Database']['db_pw']
        self._db_ = self._cfg_['Database']['db']
        self._conn_ = DBmy.db(self._db_host_, self._db_user_, self._db_pw_, self._db_)


    def get_group_id(self):
        """read the group_id from current user
        return: group_id -> success
        return: -1	-> error"""

        query = """SELECT g.group_id, p.companies_id FROM ipall_user_group g, persons p 
            WHERE g.username='%s' AND p.username='%s' """ % (self._username_, self._username_)
        tmp = self._conn_.get_data(query)
        if tmp != () and tmp != None:
            self._group_id_ = tmp[0][0]
            self._company_id_ = tmp[0][1]
        else:
            self._group_id_ = self._company_id_ = 0

        return [self._group_id_, self._company_id_]

    def get_rights(self, vrf="NULL"):
        """reads the boolean values for the users rights
        group_id    ...	    id of users group membership
        return: list of rights bits"""

        self.get_group_id()
        if vrf != "NULL":
            query = """SELECT create_net FROM ipall_rights_vrf WHERE group_id=%u AND vrf='%s' """ % (self._group_id_, vrf)
            tmp1 = self._conn_.get_data(query)
            if tmp1 != () and tmp1 != None:
                create = tmp1[0][0]
            else:
                create = 0
        else:
            create = 0

        query = """SELECT user_admin, company_admin FROM ipall_group WHERE id=%u """ % self._group_id_
        tmp2 = self._conn_.get_data(query)
        if tmp2 != () and tmp2 != None:
            user_admin = tmp2[0][0]
            company_admin = tmp2[0][1]
        else:
            user_admin = 0
            company_admin = 0

        return [create, user_admin, company_admin]


    def get_mail_address(self):
        """search for the email address of the logged in user"""

        sql_mail = """SELECT mail FROM persons WHERE username='%s' """ % self._username_
        mail = self._conn_.get_data(sql_mail)

        if mail != () and mail != None:
            mail_address = mail[0][0]
        else:
            mail_address = ""

        return mail_address


    def get_today(self):
        """return the current date"""

        year = str(localtime()[0])
        mon = zfill(str(localtime()[1]), 2)
        day = zfill(str(localtime()[2]), 2)
        today = year + mon + day

        return today

