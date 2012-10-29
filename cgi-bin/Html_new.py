"""
*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
"""

import os
from Cookie import SimpleCookie
from Configobj import ConfigObj



#global self._cfg_, self._version_, self._company_name_, self._company_url_, self._ipall_dir_, self._cgi_dir_, self._web_dir_, self._doc_prefer_

class HtmlContent:
    """Display HTML content which is used very often within IP@LL
       init variables:
       self._cfg_ = ConfigObj("ipall.cfg")
       self._version_ = self._cfg_['General']['version']
       self._company_name_ = self._cfg_['General']['company_name']
       self._company_url_ = self._cfg_['General']['company_url']
       self._ipall_dir_ = self._cfg_['Server']['ipall_dir']
       self._cgi_dir_ = self._cfg_['Server']['cgi_dir']
       self._web_dir_ = self._cfg_['Server']['web_dir']
       self._doc_prefer_ = self._cfg_['Server']['doc_prefer']
    """

    def __init__(self):
        self._cfg_ = ConfigObj("ipall.cfg")
        self._version_ = self._cfg_['General']['version']
        self._company_name_ = self._cfg_['General']['company_name']
        self._company_url_ = self._cfg_['General']['company_url']
        self._ipall_dir_ = self._cfg_['Server']['ipall_dir']
        self._cgi_dir_ = self._cfg_['Server']['cgi_dir']
        self._web_dir_ = self._cfg_['Server']['web_dir']
        self._doc_prefer_ = self._cfg_['Server']['doc_prefer']


    def restriction_message(self, popup=0):
        """print a restriction message"""

        print """<div id="message">"""
        print """<span class=textPurpleBold>You are not allowed to execute this</span>"""
        if popup == 0:
            print """<div><a href="javascript:history.back();" class=linkPurpleBold> << back</a></div>"""
        print """</div>"""

    
    def error_message(self, text, url="javascript:history.back();"):
        """print an error message with a special text"""

        print """<div id="message">%s</div>""" % str(text)
        print """<div><a href="%s" class=linkPurpleBold> << back</a></div>""" % url 


    def notify_message(self, text):
        """print a message with a special text"""

        print """<div id="message">%s</div>""" % str(text)


    def redirect(self, url):
        """redirect to url"""
        #print cookie
        print """<html><head><title>IP@LL</title>"""
        print """<meta http-equiv="refresh" content="0; url=%s" />""" % url
        print """</head>"""


    def simple_redirect_header(self, url):
        """redirect to another site"""
        print "Content-type: text/html\n\n"
        print """<html><head><title>IP@LL</title>"""
        print """<meta http-equiv="refresh" content="0; url=%s" />""" % url
        print """</head>"""

    def ajax_header(self):
        print "Content-type: text/html\n\n"

    def simple_header(self, sel_color=0, cmenu=0):
        """only print HTML header without any navigation bar"""
        
        print "Content-type: text/html\n\n"
        print """<html><head><title>IP@LL</title>"""
        print """<link href="%s/ipall_style_new.css" rel="stylesheet" type="text/css">""" % self._ipall_dir_
        print """<link href="%s/smoothbox.css" rel="stylesheet" type="text/css">""" % self._ipall_dir_
        print """<script type="text/javascript" src="%s/utils/mootools1.2.js"></script>""" % self._ipall_dir_
        print """<script type="text/javascript" src="%s/utils/mootools1.2.4.4-more.js"></script>""" % self._ipall_dir_
        print """<script type="text/javascript" src="%s/utils/ajax.js"></script>""" % self._ipall_dir_
        print """<script type="text/javascript" src="%s/utils/smoothbox.js"></script>""" % self._ipall_dir_
        if cmenu == 1:
            print """<script type="text/javascript" src="%s/utils/contextmenu.js"></script>""" % self._ipall_dir_
        print """<script type="text/javascript" src="%s/utils/ipall_utils.js"></script>""" % self._ipall_dir_
        if sel_color == 1:
            print """<script type="text/javascript" src="%s/utils/301a.js"></script>""" % self._ipall_dir_
        print """</head>"""


    def popup_body(self):
        """initialize popup window"""
        print """<body onLoad="checkTB();">"""


    def body(self):
        """print top navigation and logo of IP@LL"""

        print """<body bgcolor="#FFFFFF">"""
        print """<div id="table_index">
        <span class="headlineLogo"><a href="%s"><img src="%simages/logo0.gif" width=120 border=0></a></span>
        <span class="headlineText">IP@LL <span class="headlineVersion">v%s</span> </span>
        <div style="text-align: right;" class="TextBlackSmall">&copy; 2007 
            <a href="%s" target="_blank">%s</a>
        </div>
    </div>
    <div id="main_links">
      <span class="left">
        <a class="LinkPurpleBold" href="%slogout.php">logout</a>
      </span>
      <span class="right">
      <!-- <a class="LinkPurpleBold" href="%s">home</a>&nbsp; &nbsp; -->
      <a class="LinkPurpleBold" href="%s/index.cgi">view/vrf</a>&nbsp; &nbsp;
<!--
      <a class="LinkPurpleBold" href="%s/search.cgi">search</a>&nbsp; &nbsp;
      <a class="LinkPurpleBold" href="%s/register_as.cgi">register AS</a>&nbsp; &nbsp;
      <a class="LinkPurpleBold" href="%s/peering_stats.cgi">peering statistics</a>&nbsp; &nbsp;
-->
      <a class="LinkPurpleBold" href="%s/mgmt.cgi">management</a>&nbsp; &nbsp;
<!--      <a class="LinkPurpleBold" href="%s/documentation.cgi?%s_index" target="_blank">documentation</a> -->
      </span>
    </div>
    <div id="main_body">""" %(self._web_dir_, self._web_dir_, self._version_, self._company_url_, self._company_name_, self._web_dir_, self._web_dir_, self._cgi_dir_, self._cgi_dir_, self._cgi_dir_, self._cgi_dir_, self._cgi_dir_, self._cgi_dir_, self._doc_prefer_)



    def main_footer(self):
        """close HTML site"""
        
        print """</div>""" # main_body
        print """<div id="foot"></div>"""
        print """</body>"""
        print """</html>"""


    def popup_footer(self):
        """close HTML site in popup / thickbox"""

        print """<div id="foot" align=right></div>"""
        print """</body>"""
        print """</html>"""


    def close_body(self):
        """close HTML site without footer"""

        print """</body>"""
        print """</html>"""
