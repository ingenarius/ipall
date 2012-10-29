"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
"""

import IPy
from Configobj import ConfigObj


def calc_networks(id, parent, mask, index, conn):
    """calculate available subnetworks
        input:	id of the parent network, parent network, subnetmask for new networks, database connection object
        return:	tuple of networks"""
                
    sql_childs = """SELECT id, label FROM ipall_ip WHERE parent_id=%u ORDER BY label""" % id
    childs = conn.get_data(sql_childs)
    new_nets = []
    if mask != 32 and mask != 128:
        start_net = parent.strNormal(0) + "/" + str(mask)
    else:
        start_net = str(int(parent.strDec()) + 1) + "/" + str(mask)
    start_net = IPy.IP(start_net)
    net_len = int(start_net.len())
    new_nets = get_subnets(parent, start_net, mask, index)
##    if mask == 32:
##        print str(parent.broadcast())
        #new_nets = new_nets.remove( str(parent.broadcast() ) )
    
    if childs != () and childs != None:
        for child in childs:
            new_nets = check_net(new_nets, child)
    #else:
        #new_nets = get_subnets(parent, start_net, mask)
    
    return new_nets, len(childs), net_len


def get_subnets(parent, start_net, mask, index):
    """calculate all possible subnets
        input:	parent network, first subnet (CIDR), subnetmask
        return:	list object of all net subnets"""
    
    cfg = ConfigObj("ipall.cfg")
    nw = int(cfg['Site']['networks'])
    ### start index
    i = (int(index) - 1) * nw
    ### end index
    j = (int(index) * nw) - 1
    ### iterating number
    k = 1
    new_nets = []
    ### IPv4 addresses are displayed in dotted quad notation: e.g. 127.0.0.1
    if int(index) == 1 and int(parent.version()) == 4:
        new_nets = new_nets.__add__([start_net.strNormal(1)])
    ### IPv6 addresses are displayed in compressed form: e.g. 2001:affe::/48
    if int(index) == 1 and int(parent.version()) == 6:
        new_nets = new_nets.__add__([start_net.strCompressed()])
    next_net = IPy.IP(int(start_net.strDec()) + start_net.len())
    next_net = IPy.IP(next_net.strNormal(0) + "/" + str(mask)) 
    ### IPv4 addresses are displayed in dotted quad notation: e.g. 127.0.0.1
    if int(index) == 1 and int(parent.version()) == 4:
        new_nets = new_nets.__add__([next_net.strNormal(1)])
    ### IPv6 addresses are displayed in compressed form: e.g. 2001:affe::/48
    if int(index) == 1 and int(parent.version()) == 6:
        new_nets = new_nets.__add__([next_net.strCompressed()])
    
    while parent.overlaps(next_net.strNormal()) > 0:
        next_net = IPy.IP(int(next_net.strDec()) + start_net.len())
        next_net = IPy.IP(next_net.strNormal(0) + "/" + str(mask))
        if int(parent.version()) == 4:
            ### don't add the broadcast address
            if mask == 32 and int(IPy.IP(str(next_net.net())).strDec()) < int(IPy.IP(str(parent.broadcast())).strDec()):
                new_nets = new_nets.__add__([next_net.strNormal(1)])
            elif mask != 32 and int(IPy.IP(str(next_net.broadcast())).strDec()) <= int(IPy.IP(str(parent.broadcast())).strDec()):
                new_nets = new_nets.__add__([next_net.strNormal(1)])
        elif int(parent.version()) == 6:
            if mask == 128 and int(IPy.IP(str(next_net.net())).strDec()) < int(IPy.IP(str(parent.broadcast())).strDec()):
                k += 1
                ### k is within the index range 
                if k >= i and k <= j:
                    new_nets = new_nets.__add__([next_net.strCompressed()])
                ### k is below the index range
                elif k < j:
                    continue
                ### k is higher than the index range
                else:
                    break
            elif mask != 128 and int(IPy.IP(str(next_net.broadcast())).strDec()) <= int(IPy.IP(str(parent.broadcast())).strDec()):
                k += 1
                ### k is within the index range 
                if k >= i and k <= j:
                    new_nets = new_nets.__add__([next_net.strCompressed()])
                ### k is below the index range
                elif k < j:
                    continue
                ### k is higher than the index range
                else:
                    break 
            else:
                break
    
        else:
            break
    return new_nets


def check_net(netlist, child):
    """check if one network is overlapping another
        input:	list object of networks, current already used network
        return:	new list object of networks"""
        
    child = IPy.IP(child[1])
    to_del = []
    for n in netlist:
        net = IPy.IP(n)
        if child.overlaps(n) == 1 or child.overlaps(n) == int('-1'):
            to_del = to_del.__add__([n])
            #netlist.remove(n)
   
    for d in to_del: 
        netlist.remove(d)
            
    return netlist


