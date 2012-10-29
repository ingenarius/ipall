"""
perform a whois query and send mail to ripe
"""
import socket
import os
from Configobj import ConfigObj

global cfg
cfg = ConfigObj("ipall.cfg")

class whois:
    pass

    def ip(self, adresse):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((cfg['Server']['whois_server'], 43))
        self.s.send("%s \n\n" % adresse)
        self.page = ''
        while True:
            self.data = self.s.recv(8196)
            if not self.data:
                break  # data will be empty when the socket is closed
            self.page = self.page + self.data
        return self.page


    def print_form(self, company_id, netaddr, broadcast, prefixlen, netname, back, workflow=0, version=4):
        """print a html form where all missing data should be filled out"""

        print """<form name="ripe_update" method=POST action="register_ripe.cgi">"""
        print """<input type=hidden name=company value="%s">""" % company_id
        print """<input type=hidden name=back value="%s">""" % back
        print """<input type=hidden name=workflow value="%s">""" % workflow
        print """<input type=hidden name=route value="%s/%s">""" % (netaddr, prefixlen)

        ### LEFT SIDE
        print """<div id="pos_left_small"><p>"""
        print """<div class="lineOdd">inetnum</div>"""
        print """<div class="lineEven">netname</div>"""
        print """<div class="lineOdd">descr</div>"""
        print """<div class="lineEven">country</div>"""
        print """<div class="lineOdd">admin-c</div>"""
        print """<div class="lineEven">status</div>"""
        print """</p><p>"""
        print """<div class="lineOdd"><input type=checkbox name=create_person></div>"""
        print """<div class="lineEven">person</div>"""
        print """<div class="lineOdd">address line 1</div>"""
        print """<div class="lineEven">address line 2</div>"""
        print """<div class="lineOdd">address line 3</div>"""
        print """<div class="lineEven">address line 4</div>"""
        print """<div class="lineOdd">phone</div>"""
        print """<div class="lineEven">nic-hdl</div>"""
        print """<div class="lineOdd"><input type=checkbox name=create_route_obj></div>"""
        print """</p></div>""" # left side

        ### RIGHT SIDE
        print """<div id="pos_right_wide"><p>"""
        if version == 4:
            print """<div class="lineOdd"><input type=text name=inetnum value="%s" class=b_eingabefeld readonly></div>""" % (str(netaddr) + " - " + str(broadcast))
        if version == 6:
            print """<div class="lineOdd"><input type=text name=inetnum value="%s" class=b_eingabefeld readonly></div>""" % (str(netaddr))
        print """<div class="lineEven"><input type=text name=netname value="%s" class=b_eingabefeld></div>""" % netname
        print """<div class="lineOdd"><input type=text name=descr class=b_eingabefeld></div>"""
        print """<div class="lineEven"><input type=text name=country value="AT" class=b_eingabefeld></div>"""
        print """<div class="lineOdd"><input type=text name=adminc value="AUTO-1" class=b_eingabefeld></div>"""
        print """<div class="lineEven"><input type=text name=status value="ASSIGNED PA" class=b_eingabefeld></div>"""
        print """</p><p>""" 
        print """<div class="lineOdd">create person object</div>"""
        print """<div class="lineEven"><input type=text name=person class=b_eingabefeld></div>"""
        print """<div class="lineOdd"><input type=text name=address1 value="company name" class=b_eingabefeld></div>"""
        print """<div class="lineEven"><input type=text name=address2 value="street" class=b_eingabefeld></div>"""
        print """<div class="lineOdd"><input type=text name=address3 value="city" class=b_eingabefeld></div>"""
        print """<div class="lineEven"><input type=text name=address4 value="Austria" class=b_eingabefeld></div>"""
        print """<div class="lineOdd"><input type=text name=phone class=b_eingabefeld></div>"""
        print """<div class="lineEven"><input type=text name=nichdl value="AUTO-1" class=b_eingabefeld></div>"""
        print """<div class="lineOdd">create route object (use carefully)</div>"""
        print """</p></div>""" # right side

        print """<div id="pos_clear"><input type=submit name=send value=send class=button></div>"""
        print """</form>"""



    def create_mail(self, create_person, password, inetnum, netname, descr, country, adminc, techc, status, notify, mntby, \
        person, address1, address2, address3, address4, phone, nichdl, mail, today, create_route_obj, route, as_nr):
        """create mail body text for register network at ripe DB"""

        self._body_ = """password:     %s
inetnum:      %s
netname:      %s
descr:        %s
country:      %s
admin-c:      %s
tech-c:       %s
status:       %s
notify:       %s
mnt-by:       %s
changed:      %s %s
source:       RIPE""" % (password, inetnum, netname, descr, country, adminc, techc, status, notify, mntby, mail, today)

        if create_person == "on":
            self._body_ = self._body_ + """\n\nperson:       %s
address:      %s
address:      %s
address:      %s
address:      %s
phone:        %s
nic-hdl:      %s
mnt-by:       %s
notify:       %s
changed:      %s %s
source:       RIPE""" % (person, address1, address2, address3, address4, phone, nichdl, mntby, notify, mail, today)
        
        if create_route_obj == "on":
            self._body_ = self._body_ + """\n\nroute:      %s
descr:      %s
origin:     AS%s
mnt-by:     %s
changed:    %s %s
source:     RIPE""" % (route, descr, as_nr, mntby, mail, today)

        return self._body_


    def send_mail(self, sender, receipient, subj, body):
        """send a mail to someone
        receipient  ...     mail is sent to
        sender      ...     mail is sent from
        subj        ...     mail subject
        body        ...     mail text"""

        self._sendmail_ = cfg['Server']['sendmail'] # sendmail location
        self._p_ = os.popen("%s -t" % self._sendmail_, "w")
        self._sender_ = """From: %s\n""" % str(sender)
        self._p_.write(self._sender_)
        self._receipient_ = """To: %s\n""" % str(receipient)
        self._p_.write(self._receipient_)
        #self._bcc_ = """Bcc: ripe-test@ipall.net\n"""
        #self._p_.write(self._bcc_)
        self._subj_ = """Subject: %s\n""" % str(subj)
        self._p_.write(self._subj_)
        self._p_.write("\n") # blank line separating headers from body
        self._body_ = """%s\n""" % str(body)
        self._p_.write(self._body_)
        self._sts_ = self._p_.close()
        if self._sts_ != 0 and self._sts_ != None:
            print "Sendmail exit status", self._sts_
            return 0
        else:
            return 1

