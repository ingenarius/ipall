"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
*****************************
"""

import string
import DBmy
from Configobj import ConfigObj


class Node:
    """Netrork-tree node"""

    def __init__(self, rights, net_perm, depth, path, vrf, urlpath="0", cfont="#000000", cbg="#FFFFFF"):

        self._cfg_ = ConfigObj("ipall.cfg")
        (self._create_, self._user_admin_, self._company_admin_) = rights
        ### rights of the logged in user(group)
        (self._delete_, self._edit_, self._subnet_, self._view_net_) = net_perm
        ### URL path of a selected network
        self._urlpath_ = urlpath
        ### path of the network, stored in database
        self._path_ = path
        self._vrf_ = str(vrf)
        ### how many parents a subnet has
        self._depth_ = 	depth
        ### the last id in the path -> direct parent id of selected node
        self._selected_ = int(self._urlpath_.split(":")[len(self._urlpath_.split(":"))-1])
        self._font_color_ = cfont
        self._bg_color_ = cbg
        self._sbox_ = self._cfg_['Site']['smoothbox'].replace("?", "&")
        self._cgi_dir_ = self._cfg_['Server']['cgi_dir']
        self._ipall_dir_ = self._cfg_['Server']['ipall_dir']
        self._db_host_ = self._cfg_['Database']['db_host']
        self._db_user_ = self._cfg_['Database']['db_user']
        self._db_pw_ = self._cfg_['Database']['db_pw']
        self._db_ = self._cfg_['Database']['db']
        self._conn_ = DBmy.db(self._db_host_, self._db_user_, self._db_pw_, self._db_)


    def print_plus(self, subnetted, id):
        """prints a plus sign before a tree node if there are available subnets
        subnetted   ...     1: a node has childs; 0: a node has no childs
        id          ...     id of the current network"""
        for r in range(0, (self._depth_ - 1) ):
            if subnetted == 1 and r == (self._depth_ - 2):
                print """<span onClick="callNode('%s', '%s', '%s', '%s', '%s');"><img src=%s/images/ftv2pnode.gif border=0 id="img_of_%s"></span>""" \
                    % ( str(id), self._ipall_dir_, self._cgi_dir_, self._vrf_, self._path_, self._ipall_dir_, str(id) )
            else:
                print """<span class="empty">&nbsp;</span>"""


    def print_node(self, n, selected=0, bold=0):
        """print the label of the network node
        n   ...	    network node (only one)"""

        if n[7] == 1:  ### network has subnets
            if bold == 0 and n[14] == 1:
                css = "italic"
            else:
                css = "normal"

            print """<span id="prefix" class="prefix" style="color: %s; background-color: %s;">""" % \
                ( str(self._font_color_), str(self._bg_color_) )
            print """<span id="%s" onClick="callNode('%s', '%s', '%s', '%s', '%s');" """ % \
                ( str(n[0]), str(n[0]), self._ipall_dir_, self._cgi_dir_, self._vrf_, self._path_ )
            print """class="Text" style="font-style: %s;">%s</span>""" % ( css, str(n[2]) ) 
            print """<a name="%s" style="color: %s; background-color: %s; text-decoration: none;" class="Node%s" title="%s">""" % \
                ( str(n[0]),  str(self._font_color_), str(self._bg_color_), str(n[0]), str(n[5]).replace("\n", "<br>") )
            print """[%s]</a></span> """ % ( str(n[4]) )
            print """<ul id="cmenu" class="SimpleContextMenu"></ul>""" 
            print """<img src="%s/images/menu_icon_32.png" border=0 title="menu - click for options" class="menubutton" """ % ( self._ipall_dir_ )
            print """onClick="SimpleContextMenu.click(event,'prefix','%s;%s;%s;%s;%s;%s');"> """ % \
                ( self._ipall_dir_, self._cgi_dir_, str(n[0]), self._vrf_, self._path_, self._sbox_ ) 


        else: ### network has no subnets
            if bold == 0 and n[14] == 1:
                css = "italic"
            else:
                css = "normal"

            print """<span class="prefix" style="color: %s; background-color: %s;">""" % ( self._font_color_, self._bg_color_ )
            print """<span id=prefix class="Text" style="font-style: %s;">%s</span>""" % ( css, str(n[2]) ) 
            print """<a name="%s" style="color: %s; background-color: %s; text-decoration: none;" class="Node%s" title="%s">""" %\
                ( str(n[0]), str(self._font_color_), str(self._bg_color_), str(n[0]), str(n[5]).replace("\n", "<br>") )
            print """[%s]</a></span>""" % ( str(n[4]) )
            print """<ul id="cmenu" class="SimpleContextMenu"></ul>""" 
            print """<img src="%s/images/menu_icon_32.png" border=0 title="menu - click for options" class="menubutton" """ % ( self._ipall_dir_ )
            print """onClick="SimpleContextMenu.click(event,'prefix','%s;%s;%s;%s;%s;%s');"> """ % \
                ( self._ipall_dir_, self._cgi_dir_, str(n[0]), self._vrf_, self._path_, self._sbox_ ) 
