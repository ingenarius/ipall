"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
"""

from Configobj import ConfigObj
from IPy import IP


class IpallFunctions:
    """init variables:
        self._cfg_ = ConfigObj("ipall.cfg")
        self._version_ = self._cfg_['General']['version']
        self._company_name_ = self._cfg_['General']['company_name']
        self._company_url_ = self._cfg_['General']['company_url']
        self._ipall_dir_ = self._cfg_['Server']['ipall_dir']
        self._cgi_dir_ = self._cfg_['Server']['cgi_dir']
        self._web_dir_ = self._cfg_['Server']['web_dir']
        self._doc_prefer_ = self._cfg_['Server']['doc_prefer']
        self._sbox_ = self._cfg_['Site']['smoothbox']
        self._conn_ = conn
        self._user_ = user # logged in user
        self._group_ = group # logged in users group
        self._company_ = company
    """

    def __init__(self, conn, user, group, company):
        self._cfg_ = ConfigObj("ipall.cfg")
        self._version_ = self._cfg_['General']['version']
        self._company_name_ = self._cfg_['General']['company_name']
        self._company_url_ = self._cfg_['General']['company_url']
        self._ipall_dir_ = self._cfg_['Server']['ipall_dir']
        self._cgi_dir_ = self._cfg_['Server']['cgi_dir']
        self._web_dir_ = self._cfg_['Server']['web_dir']
        self._doc_prefer_ = self._cfg_['Server']['doc_prefer']
        self._sbox_ = self._cfg_['Site']['smoothbox']
        self._conn_ = conn # db connection object
        self._user_ = user # logged in user
        self._group_ = group # logged in users group
        self._company_ = company # company of logged in user


    def get_table_names(self):
        """get db table names used in nms_log"""

        if self._group_ == 1:
            sql_table_names = """SELECT DISTINCT(table_name) FROM nms_log ORDER BY table_name"""
        else:
            sql_table_names = """SELECT DISTINCT(table_name) FROM nms_log WHERE companies_id=%u
                ORDER BY table_name""" % int(self._company_)
        table_names = self._conn_.get_data(sql_table_names)
        return table_names


    def get_user_names(self):
        """get all users who has done some changes in NMS"""

        if self._group_ == 1:
            sql_user_names = """SELECT DISTINCT(user) FROM nms_log ORDER BY user"""
        else:
            sql_user_names = """SELECT DISTINCT(user) FROM nms_log WHERE companies_id=%u
                ORDER BY user""" % int(self._company_)
        user_names = self._conn_.get_data(sql_user_names)
        return user_names


    def get_groups(self, company_id):
        """network_permissions: get groups of selected company"""

        sql_groups = """SELECT id, groupname FROM ipall_group 
            WHERE companies_id=%u AND id != 1 """ % ( int(company_id) )
        groups = self._conn_.get_data(sql_groups)
        return groups

    
    def get_sel_group(self, id):
        """network_permissions: get group info of selected group id"""
        
        sql_group = """SELECT groupname FROM ipall_group WHERE id=%u""" % id
        group = self._conn_.get_data(sql_group)
        return group[0]


    def get_companies(self):
        """get all companies from the db"""

        sql_companies = """SELECT id, name FROM companies ORDER BY name"""
        companies = self._conn_.get_data(sql_companies)
        return companies


    def get_years(self):
        """get all years where log entries are in the database table"""

        if self._group_ == 1:
            sql_years = """SELECT DISTINCT(YEAR(time)) FROM nms_log ORDER BY YEAR(time)"""
        else:
            sql_years = """SELECT DISTINCT(YEAR(time)) FROM nms_log WHERE companies_id=%u
                ORDER BY YEAR(time)""" % int(self._company_)
        years = self._conn_.get_data(sql_years)
        return years


    def get_vrf_count(self, id):
        """company_delete: get number of vrfs/views assigned to specific company"""

        sql_nets = """SELECT COUNT(networks_id) FROM networks WHERE companies_id=%u """ % int(id)
        nets = self._conn_.get_data(sql_nets)
        return nets


    def get_user_count(self, id):
        """company_delete: get number of users assigned to specific company"""

        sql_users = """SELECT COUNT(persons_id) FROM persons WHERE companies_id=%u """ % int(id)
        users = self._conn_.get_data(sql_users)
        return users


    def get_log_results(self, table_name, pattern, user_name, year_from, month_from, day_from, company):
        """get the result according to search patterns"""

        sql_search = """SELECT time, user, table_name, sql_statement FROM nms_log WHERE 
                (table_name %s) AND 
                (sql_statement LIKE '%s%s%s') AND 
                (user %s) AND
                (YEAR(time) %s AND MONTH(time) %s AND DAY(time) %s) AND
                (companies_id %s)
                ORDER BY time DESC""" \
                % (table_name, "%", pattern, "%", user_name, year_from, month_from, day_from, company)
        result = self._conn_.get_data(sql_search)
        return result


    def get_parent_net(self, id):
        """get parent network of the new subnet"""

        sql_net = """SELECT i.label, i.path, i.vrf, i.service_id, i.companies_id, c.is_lir
            FROM ipall_ip i, companies c
            WHERE i.id=%u AND i.companies_id=c.id""" % int(id)
        net = self._conn_.get_data(sql_net)    
        return net


    def get_net_info(self, fct, id):
        """ get information about subnet: 
            fct=1 -> network_view
            tcf=2 -> network_edit, network_permission
            tcf=3 -> network_print
        """
        if fct == 1:
            query = """SELECT i.label, i.net_name, i.description, i.peering_info_id, i.path,
                i.service_id, i.interface_name, i.vrf, i.companies_id, c.is_lir
                FROM ipall_ip i, companies c
                WHERE i.id=%u AND i.companies_id=c.id """ % (id)
        if fct == 2:
            query = """SELECT id, label, net_name, description, peering_info_id, aggregated, 
                path, service_id, allocated, interface_name, vrf, companies_id
                FROM ipall_ip WHERE id=%u """ % (id)
        if fct == 3:
            query = """SELECT id, label, net_name, path FROM ipall_ip WHERE id=%u """ % (id)
        info = self._conn_.get_data(query)
        return info

    
    def get_net_rights(self, sel_group, path):
        """network_permissions: get permission information of selected network """

        sql_perm = """SELECT delete_net, edit_net, subnet_net, view_net, edit_vrf, delete_vrf
            FROM ipall_rights WHERE group_id=%u AND path='%s' """ % (sel_group, path)
        perm = self._conn_.get_data(sql_perm)
        if perm != ():
            return perm[0]
        else:
            return perm


    def get_peering_info(self, id):
        """network_view: get information about BGP peering"""

        sql_peering = """SELECT id, as_nr, as_set, md5, rs, session_up, contact, 
            comment, device, max_prefix FROM ipall_peering_info where id=%u""" % id
        info = self._conn_.get_data(sql_peering)
        return info

    def get_service_name(self, id):
        """network_view: get name of network type"""

        sql_net_type = """SELECT id, typename, description 
            FROM ipall_network_types where id=%u""" % id
        net_type = self._conn_.get_data(sql_net_type)
        return net_type


    def print_net_types(self, id=0):
        """return dropdown box <option> with network types"""
    
        if id == 0:
            sql_net_types = """SELECT id, typename FROM ipall_network_types 
                WHERE id != 1 ORDER BY typename"""
        else:
            sql_net_types = """SELECT id, typename FROM ipall_network_types 
                WHERE id=%u""" % id
        net_types = self._conn_.get_data(sql_net_types)

        if net_types != ():
            for t in net_types:
                print """<option value=%u>%s</option>""" % (int(t[0]), t[1])
        else:
            return


    def print_tree_nodes(self, networks, rights, path):
        """recursive function for displaying networks and subnets
        networks    ...     tuple of networks to display"""

        if path != 0:
            ### definitions of variables
            depth = len(path.split(":"))
            p = int(path.split(":")[depth-1])
            childs = ()

        for n in networks:
                #id_found = 0
                ### permissions of the network(s)
                if self._group_ == 1 or rights[2] == 1:
                    net_perm = ([1,1,1,1],)
                else:
                    sql_perm = """SELECT delete_net, edit_net, subnet_net, view_net 
                    FROM ipall_rights WHERE LOCATE(path, '%s') > 0 AND group_id=%u 
                    ORDER BY path DESC LIMIT 1""" % (n[3], self._group_)
                    net_perm = self._conn_.get_data(sql_perm)
                if net_perm == ():
                    net_perm = [0,0,0,0]
                else:
                    net_perm = net_perm[0]
                if net_perm[3] != 1:
                    continue
                else:
                    print """<div>"""
                    if net_perm[3] == 1:
                        indent = len(n[3].split(":")) - 2
                        for i in range(0, indent*2):
                            print "&nbsp;"
                        print "<span class=TextPurpleBold>" + n[1] + "</span>"
                        print "<span class=TextPurple>" + " [" + n[2] + "]" + "</span><br>"
                    print """</div>"""
    
                    child_query = """SELECT id, label, net_name, path FROM ipall_ip 
                        WHERE parent_id=%u ORDER BY address""" % (int(n[0]))
                    childs = self._conn_.get_data(child_query)
                    self.print_tree_nodes(childs, rights, path)


    def check_new_network(self, net, vrf):
        """check if new network could be created or if it overlaps 
           with an existing one"""
        sql_networks = """SELECT id, label FROM ipall_ip WHERE parent_id=0 AND vrf='%s' """ \
            % (vrf)
        networks = self._conn_.get_data(sql_networks)

        if networks != ():
            chk = 0
            for n in networks:
                ip = IP(n[1])
                nw = ip.strDec()
                bc = ip.broadcast().strDec()
                if net >= nw and net <= bc:
                    chk = 1
                else:
                    continue

            return chk
        else:
            return -1


    def check_new_subnet(self, net, vrf):
        """check if the subnet already exists"""

        sql_check = """SELECT id FROM ipall_ip WHERE label LIKE '%s' AND vrf='%s' """ \
            % (net, vrf)
        chk_net = self._conn_.get_data(sql_check)
        return chk_net


    def check_is_peering(self, service_id, fct):
        """check if selected nettype is allowed to have BGP peerings
        fct = 1 ... a_network_names
        fct = 2 ... network_edit"""

        sql_peering = """SELECT is_peering FROM ipall_network_types WHERE id=%u""" % ( service_id )
        peering = self._conn_.get_data(sql_peering)

        if fct == 1:
            if peering != () and peering != 0:
                is_peering = int(peering[0][0])
                print "value:%s" % ( str(is_peering) )
            else:
                print "value:0"
        if fct == 2:
            if peering != () and peering != 0:
                return 1
            else:
                return 0
                    

    def insert_new_net(self, net, vrf, netname, description, aggregated, net_type, allocated):
        """inserts a new subnet into the database"""

        if net.version() == 4:
            sql_insert = """INSERT INTO `ipall_ip` ( `id` , `parent_id` , `label` , `address` , `net_name` , `description` , `path` , `subnetted` , `peering_info_id` , `vrf` , `aggregated` , `product_id` , `interface_id` , `service_id`, `allocated`, `companies_id`) VALUES ('', '0', '%s', %u, '%s', %s , '0', '0', NULL, '%s', %s, NULL , NULL , %s, %s, %u)""" % (net.strNormal(), int(net.strDec()), netname, description, str(vrf), aggregated, net_type, allocated, self._company_)
        if net.version() == 6:
            sql_insert = """INSERT INTO `ipall_ip` ( `id` , `parent_id` , `label` , `address` , `net_name` , `description` , `path` , `subnetted` , `peering_info_id` , `vrf` , `aggregated` , `product_id` , `interface_id` , `service_id`, `allocated`, `companies_id`) VALUES ('', '0', '%s', %u, '%s', %s , '0', '0', NULL, '%s', %s, NULL , NULL , %s, %s, %u)""" % (net.strCompressed(), int(net.strDec()), netname, description, str(vrf), aggregated, net_type, allocated, self._company_)
        last_id = self._conn_.insert_data(sql_insert)

        log = self.insert_log(last_id, sql_insert, "ipall_ip")

        if last_id != 0:
            path = "0:" + str(last_id)

            ### set the path field correctly
            sql_update = """UPDATE ipall_ip SET path='%s' WHERE id=%u """ % (str(path), int(last_id))
            update = self._conn_.update_data(sql_update)

            if self._group_ != 1:
                sql_ins_rights = """INSERT INTO ipall_rights VALUES(%u, '%s', 1, 1, 1, 1, 0, 0, %u)""" \
                    % ( self._group_, str(path), int(self._company_) )
                update = self._conn_.update_data(sql_ins_rights)

        if last_id != 0 and log != 0:
            update = 1
        else:
            update = 0

        return update


    def insert_peering(self, as_nr, as_set, md5, rs, session_up, contact_mail, peer_comment, peering_device, max_prefix, net_id):
        """insert bgp peering information"""

        sql_peering = """INSERT INTO ipall_peering_info VALUES ('', %u, %s, %s, %u, %u, %s, %s, %s, %s)""" \
            % (as_nr, as_set, md5, rs, session_up, contact_mail, peer_comment, peering_device, max_prefix)
        peer_id = self._conn_.insert_data(sql_peering)
        upd_net = 0
        if net_id != 0:
            sql_upd_net = """UPDATE ipall_ip SET peering_info_id=%u WHERE id=%u""" % ( int(peer_id), int(net_id) )
            upd_net = self._conn_.update_data(sql_upd_net)
        ### LOGGING
        log = self.insert_log(0, sql_peering, 'ipall_peering_info')
        if upd_net != 0 and log != 0:
            return 1
        else:
            return 0


    def update_peering(self, as_nr, as_set, md5, rs, session_up, contact_mail, peer_comment, peer_device, max_prefix, peering_info_id):
        """network_edit: update BGP peering info in db"""

        sql_peer_upd = """UPDATE ipall_peering_info SET as_nr=%u, as_set=%s, 
            md5=%s, rs='%s', session_up='%s', contact=%s, comment=%s, device=%s, 
            max_prefix=%s WHERE id=%u """ \
            % (as_nr, as_set, md5, rs, session_up, contact_mail, peer_comment, peer_device, max_prefix, peering_info_id)
        update = self._conn_.update_data(sql_peer_upd)
        if update != 0:
            log = self.insert_log(0, sql_peer_upd, "ipall_peering_info")
        if update != 0 and log != 0:
            return 1
        else:
            return 0


    def update_network(self, net_name, net_description, aggregated, net_type, allocated, interface, id):
        """network_edit: update ip information"""

        sql_net_upd = """UPDATE ipall_ip SET net_name='%s', description=%s, 
            aggregated=%u, service_id=%s, allocated=%u, interface_name=%s 
            WHERE id=%u """ \
            % (net_name, net_description, aggregated, net_type, allocated, interface, id)
        update = self._conn_.update_data(sql_net_upd)
        if update != 0:
            log = self.insert_log(id, sql_net_upd, "ipall_ip")
        if update != 0 and log != 0:
            return 1
        else:
            return 0


    def insert_log(self, last_id, sql, table):
        """insert log string into database"""

        if last_id != 0:
            id_link = """<a href=%s/network_view.cgi?%s class=LinkPurpleBold>id: %s</a> - """ \
                % ( self._cgi_dir_, str(last_id), str(last_id) )
            log_string = id_link + sql.replace("'", "&quot;")
        else:
            log_string = sql.replace("'", "&quot;")

        sql_log = """INSERT INTO nms_log VALUES ('', '%s', SYSDATE(), '%s', "%s", %u)""" \
            % (self._user_, table, log_string, self._company_)
        log = self._conn_.insert_data(sql_log)

        return log


    def delete_company(self, id):
        """company_delete: delete it"""

        sql_delete_company = """DELETE FROM companies WHERE id=%u """ % int(id)
        del_c = self._conn_.update_data(sql_delete_company)
        
        if del_c == 1:
            log = self.insert_log(0, sql_delete_company, "companies")
            if log > 0:
                return 1
        return 0


    def delete_peering(self, peering_id, net_id):
        """network_edit: delete entry in peering_info database"""

        sql_del_p = """DELETE FROM ipall_peering_info WHERE id=%u""" % int(peering_id)
        del_p = self._conn_.update_data(sql_del_p)
        if del_p == 1:
            log_p = self.insert_log(0, sql_del_p, 'ipall_peering_info')
            sql_upd_net = """UPDATE ipall_ip SET peering_info_id=NULL WHERE id=%u""" \
                % ( int(net_id) )
            upd_net = self._conn_.update_data(sql_upd_net)
            log_n = self.insert_log(0, sql_upd_net, 'ipall_ip')
            if upd_net != 0 and log_p > 0 and log_n > 0:
                return 1
        return 0
