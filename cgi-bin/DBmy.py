"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 Andreas Poiss
*****************************
"""

import MySQLdb
from time import localtime
from string import zfill

class db:
    'definitions to handle database operations'

    def __init__(self, host, user, passwd, dbname, port=3306):
        """initiates db connection"""
        self._host_ = host
        self._user_ = user
        self._passwd_ = passwd
        self._dbname_ = dbname
        self._port_ = port

    def open_connection(self):
        """creates database connection"""
        try:
            self._conn_ = MySQLdb.Connect(host=self._host_, port=self._port_, user=self._user_, passwd=self._passwd_, db=self._dbname_)
            #print self._host_, self._user_, self._passwd_, self._dbname_, self._port_
            self._cursor_ = self._conn_.cursor()
            #return self._conn_
        except MySQLdb.OperationalError, message:
            print "<br>Can't establish database connection to: %s<br>Error %d:<br>%s" % (self._dbname_, message[0], message[1])
        except: 
            print "<br>Can't establish database connection to: %s<br>Error %d:<br>%s" % (self._dbname_)
    
    def get_data(self, sql):
        """search in the database with a given sql statement
        return: set of entries"""
        try:
            self.open_connection()
            self._cursor_.execute(sql)
            result = self._cursor_.fetchall()
            self._conn_.commit()
            self._cursor_.close()
            self._conn_.close()
            return result
        except MySQLdb.Error, message:
            print "<br>SQL query was not successful: <i> %s </i><br>Error %s" % (sql, message)
            return 0

    
    def update_data(self, sql):
        """update or delete entries of the database"""
        try:
            self.open_connection()
            self._cursor_.execute(sql)
            self._conn_.commit()
            self._cursor_.close()
            self._conn_.close()
            return 1
        except MySQLdb.Error, message:
            print "<br>SQL query was not successful: <i> %s </i><br>Error %s" % (sql, message)
            return 0


    def insert_data(self, sql):
        """insert entries into the database"""
        try:
            self.open_connection()
            self._cursor_.execute(sql)
            last_id = int(self._cursor_.lastrowid)
            self._conn_.commit()
            self._cursor_.close()
            self._conn_.close()
            return last_id
        except MySQLdb.Error, message:
            print "<br>SQL query was not successful: <i> %s </i><br>Error %s" % (sql, message)
            return 0


    def get_username(self, md5):
        """returns the username in clear text"""
        try:
            # userformat: peter 3jd82h49d23u8d3u - 01%%02%%2006
            year = str(localtime()[0])
            mon = zfill(str(localtime()[1]), 2)
            day = zfill(str(localtime()[2]), 2)
            hash = "3jd82h49d23u8d3u" + "-" + mon + "%%" + day + "%%" + year
            #hash = "3jd82h49d23u8d3u" + "-" + "01" + "%%" + "01" + "%%" + "2006"

            self.open_connection()
            sql = """SELECT username FROM persons WHERE MD5(CONCAT(username,'%s'))='%s' """ % (hash, md5)
            self._cursor_.execute(sql)
            result = self._cursor_.fetchall()
            self._conn_.commit()
            self._cursor_.close()
            self._conn_.close()
            if result != ():
                return result[0][0]
            else:
                return ""
        except MySQLdb.Error, message:
            print "<br>SQL query was not successful: <i> %s </i><br>Error %s" % (sql, message)
            return 0


    def get_net_permissions(self, path, group):
        """return the permissions of users group to a dedicated network"""

        try:
            self.open_connection()
            sql = """SELECT delete_net, edit_net, subnet_net, view_net FROM ipall_rights 
                WHERE LOCATE(path, '%s') > 0 AND group_id=%u ORDER BY path DESC LIMIT 1""" % (path, group)
            self._cursor_.execute(sql)
            result = self._cursor_.fetchall()
            self._conn_.commit()
            self._cursor_.close()
            self._conn_.close()
            if result != ():
                return result[0]
            else:
                return ""
        except MySQLdb.Error, message:
            print "<br>SQL query was not successful: <i> %s </i><br>Error %s" % (sql, message)
            return 0

    def get_vrf_permissions(self, rd, group):
        """return the permissions of users group to a dedicated network"""

        try:
            self.open_connection()
            sql = """SELECT edit_vrf, delete_vrf FROM ipall_rights 
                WHERE LOCATE(path, '%s') > 0 AND group_id=%u ORDER BY path DESC LIMIT 1""" % (rd, group)
            self._cursor_.execute(sql)
            result = self._cursor_.fetchall()
            self._conn_.commit()
            self._cursor_.close()
            self._conn_.close()
            if result != ():
                return result[0]
            else:
                return ()
        except MySQLdb.Error, message:
            print "<br>SQL query was not successful: <i> %s </i><br>Error %s" % (sql, message)
            return 0
