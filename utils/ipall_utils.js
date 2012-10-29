/*

*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
*/
                                                               
function showToolTip(id)
{
    var New_node = ".Node" + id;
    var Tip = new Tips($$(New_node), {
        fixed: true,
        initialize:function(){
            this.fx = new Fx.Style(this.toolTip, 'opacity', {duration: 500, wait: false}).set(0);
        },
        onShow: function(toolTip) {
            this.fx.start(1);
        },
        onHide: function(toolTip) {
            this.fx.start(0);
        }
    });
}

function mouseoverImage(image, ipall_dir)
{
    var s = image.id;
    var ssrc = image.src;
 
    if (ssrc.match(/[Oo]ff/))
    {
        image.src = ipall_dir + "/images/" + s + "On.png"
    }
    else
    {
        image.src = ipall_dir + "/images/" + s + "Off.png"
    }
} 

/*
 * Popup windows
 */
var subwindow = 0;

function ClosePopUp() {
    if (!subwindow)
        return;
    if (subwindow.closed)
        return;
    subwindow.close();
}

function popup(url, w, h) {
    var attribs = 'location=no,menubar=no,toolbar=no,statusbar=no';
    attribs += ',resizable=yes,scrollbars=yes,width='+ w +',height='+ h;
    execPopup(url, attribs);
}
function popup(url) {
    //window.location = url;
    var attribs = 'location=no,menubar=no,toolbar=no,statusbar=no';
    attribs += ',resizable=yes,scrollbars=yes,width=850,height=600';
    execPopup(url, attribs);
}

function execPopup(url, attribs) {
    ClosePopUp();  /* close existing popup */
    subwindow = window.open(url, 'popup', attribs);
    subwindow.moveTo(50,50);
}

function checkPopup() {
    if (window.opener) {
        $('foot').set('html', '<a href=\"javascript:this.close();\" class=linkPurpleBold>close</a>');
    }
    else {
        $('main').set('html', '');
        alert('Direct access is not allowed!');
        history.back();
    }
}

function checkTB() {
    if ( (this.document.referrer) ){
        if ( (this.document.referrer.search('networks\.cgi') == -1) && (this.document.referrer.search('index\.cgi') == -1) && (this.document.referrer.search('mgmt\.cgi') == -1) && ($('foot') != null) ) {
            $('foot').set('html', '<a href=\"javascript:history.back();\" class=linkPurpleBold> << back</a>');
        }
//        else {
//            $('foot').set('html', '');
//        }
    }
    else {
        $('main').set('html', 'Direct access is not allowed! Go away...');
    }
}


function redirect_to_url(url) {
        window.location = url;
}

function confirm_and_redirect(text, url) {
    var check = confirm(text);
    if(check) {
        window.location = url;
    }
}

function confirm_action_and_redirect(text, url) {
        var check = confirm(text);
        if(check) {
                window.location = url;
                //popup(url);
        }
}


function setFocus(el) {
    $(el).focus();
}

function toggle_msg(el, msg1, msg2) {
    if ( $(el).text == msg1 ) {
        $(el).set('html', msg2);
    }
    else if ( $(el).text == msg2 ) {
        $(el).set('html', msg1);
    }
    else {
        return false;
    }
}

function toggleVisibility(elId, linkId) {
    var slide = new Fx.Slide(elId).hide();
    $(linkId).addEvent('click', function(e){
        e = new Event(e);
        slide.toggle();
        e.stop();
    });
    //slide.hide();
}


/*
 * check input functions
 */

function errorField(el, msg) {
    alert(msg);
    $(el).style.background = "#FF0000"; //red
    $(el).style.color = "#FFFFFF";
    setFocus(el);
}

function check_apostrophe() {
    fs = document.forms;

    for( var i=0; i < fs.length; i++ ) {
        f = fs[i];
        for( var j=0; j < f.length; j++ ) {
            if ( f[j].value.indexOf("\'") != -1 ) {
                errorField(f[j], 'No apostrophes allowed!');
                return false;
            }
        }
    }
}

// global regex variables
var only_digits_as = new RegExp("^[0-9]{1,5}");
var only_digits = new RegExp("^[0-9]+");
var as_set_check = new RegExp("^(AS\-)([0-9]|[A-Z]|[a-z])+");
var rd_check = new RegExp("^[0-9]{1,5}:[0-9]{1,5}");
var mail_check = new RegExp("^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+\.(?:[A-Za-z]{2}|com|org|net|biz|info|name|aero|biz|info|jobs|museum|name)$");

function check_new_subnet(id, ipall_dir, cgi_dir, vrf, path) {
    if ( $('network').value == "None" ) {
        errorField('network', 'Please select network');
        return false;
    }
    if ( $('netmask').value == '0' ) {
        errorField('netmask', 'Please select netmask');
        return false;
    }
    if ( $('netname').value == "" || $('netname').value == "NULL" ) {
        errorField('netname', 'Please enter a network name');
        return false;
    }
    if ( ($('is_peering') != null) && ($('is_peering').checked == true) && ($('netmask').value == '32') ) {
        if ( $('as_nr').value.search(only_digits_as) == -1 ) {
            errorField('as_nr', 'Please enter only digits as AS number');
            return false;
        }
        if ( $('as_nr').value == '' || parseInt($('as_nr').value) > 65535 ) {
            errorField('as_nr', 'Please enter a correct AS number');
            return false;
        }
        if ( $('as_set').value != "" && $('as_set').value.search(as_set_check) == -1 ) {
            errorField('as_set', 'Please enter a correct AS MACRO');
            return false;
        }
        if ( $('max_prefix').value != "" && $('max_prefix').value.search(only_digits) == -1 ) {
            errorField('max_prefix', 'Please enter only digits in Max Prefix limit');
            return false;
        }
        if ( $('peering_device').value == "" || $('peering_device').value == "NULL" ) {
            errorField('peering_device', 'Please enter a peering device');
            return false;
        }
    }
    if ( $('is_peering') != null && $('is_peering').checked == true && $('netmask').value != '32') {
        errorField('is_peering', 'You can only add peering information to a single host');
        return false;
    }
    callNodeWindow('parent.window', id, ipall_dir, cgi_dir, vrf, path); 
//    callNode(id, ipall_dir, cgi_dir, vrf, path); 
    return check_apostrophe();
    // everything is OK
    return true;
}

function check_edit_subnet() {
    if ( $('net_name').value == "" || $('net_name').value == "NULL" ) {
        errorField('net_name', 'Please enter a network name');
        return false;
    }
    if ( $('as_nr') ) {
        if ( $('as_nr').value.search(only_digits_as) == -1 ) {
            errorField('as_nr', 'Please enter only digits as AS number');
            return false;
        }
        if ( $('as_nr').value == '' || parseInt($('as_nr').value) > 65535 ) {
            errorField('as_nr', 'Please enter an AS number');
            return false;
        }
        if ( $('as_set').value != "" && $('as_set').value.search(as_set_check) == -1 ) {
            errorField('as_set', 'Please enter a correct AS MACRO');
            return false;
        }
        if ( $('max_prefix').value != "" && $('max_prefix').value.search(only_digits) == -1 ) {
            errorField('max_prefix', 'Please enter only digits in Max Prefix limit');
            return false;
        }
        if ( $('peer_device').value == "" || $('peer_device').value == "NULL" ) {
            errorField('peer_device', 'Please enter a peering device');
            return false;
        }
    }
    return check_apostrophe();
    // everything is OK
    return true;
}

function check_new_net() {
    if ( $('network').value == "" || $('network').value == "NULL" ) {
        errorField('network', 'Please enter a network');
        return false;
    }
    if ( $('netname').value == "" || $('netname').value == "NULL" ) {
        errorField('netname', 'Please enter a network name');
        return false;
    }
    if ( $('allocated').checked == true && $('net_type').value == '1') {
        errorField('net_type', 'Please select network type');
        return false;
    }
    return check_apostrophe();
    // everything is OK
    return true;
}

function check_company() {
    if ( $('name').value == "" || $('name').value == "NULL" ) {
        errorField('name', 'Please enter a name');
        return false;
    }
    if ( $('street').value == "" || $('street').value == "NULL" ) {
        errorField('street', 'Please enter a street name');
        return false;
    }
    if ( $('street_number').value == "" || $('street_number').value == "NULL" ) {
        errorField('street_number', 'Please enter a street number');
        return false;
    }
    if ( $('postal_code').value == "" || $('postal_code').value == "NULL" ) {
        errorField('postal_code', 'Please enter a postal code');
        return false;
    }
    if ( $('city').value == "" || $('city').value == "NULL" ) {
        errorField('city', 'Please enter a city name');
        return false;
    }
    if ( $('send_delete_mail').checked == true ) {
        if ( $('delete_mail').value == "" || $('delete_mail').value.search(mail_check) == -1 ) {
            errorField('delete_mail', 'Please enter a valid email address');
            return false;
        }
    }
    if ( $('is_lir').checked == true ) {
        if ( $('ripe_password').value == '') {
            errorField('ripe_password', 'Please enter a RIR password');
            return false;
        }
        if ( $('ripe_mntby').value == '') {
            errorField('ripe_mntby', 'Please enter a RIR maintainer');
            return false;
        }
        if ( $('as_nr').value.search(only_digits_as) == -1 ) {
            errorField('as_nr', 'Please enter only digits as AS number');
            return false;
        }
        if ( $('as_nr').value == '' || parseInt($('as_nr').value) < 1 || parseInt($('as_nr').value) > 65535 ) {
            errorField('as_nr', 'Please enter a (correct) AS number [1-65535]');
            return false;
        }
        if ( $('as_set').value != "" && $('as_set').value.search(as_set_check) == -1 ) {
            errorField('as_set', 'Please enter a correct AS MACRO');
            return false;
        }
        if ( $('ripe_admin_c').value == '') {
            errorField('ripe_admin_c', 'Please enter an admin contact');
            return false;
        }
        if ( $('ripe_tech_c').value == '') {
            errorField('ripe_tech_c', 'Please enter a technical contact');
            return false;
        }
        if ( $('ripe_notify').value == "" || $('ripe_notify').value.search(mail_check) == -1 ) {
            errorField('ripe_notify', 'Please enter a valid email address');
            return false;
        }
        if ( $('country').value == '') {
            errorField('country', 'Please enter a country code');
            return false;
        }
    }
    return check_apostrophe();
    // everything is OK
    return true;
}

function check_user() {
    if ( $('surname').value == "" || $('surname').value == "NULL" ) {
        errorField('surname', 'Please enter a surname');
        return false;
    }
    if ( $('forename').value == "" || $('forename').value == "NULL" ) {
        errorField('forename', 'Please enter a forename');
        return false;
    }
    if ( $('mail').value == "" || $('mail').value.search(mail_check) == -1 ) {
        errorField('mail', 'Please enter a valid email address');
        return false;
    }
    if ( $('username').value == "" || $('username').value == "NULL" ) {
        errorField('username', 'Please enter a username');
        return false;
    }
    if ( $('password1').value != "" ) {
        if ( $('password1').value == "" || $('password1').value == "NULL" ) {
            errorField('password1', 'Please enter password');
            return false;
        }
        if ( $('password2').value == "" || $('password2').value == "NULL" ) {
            errorField('password2', 'Please re-enter password');
            return false;
        }
        if ( $('password1').value.length < 6 || $('password2').value.length < 6 ) {
            errorField('password1', 'Passwords must be at least 6 characters long');
            return false;
        }
        if ( $('password1').value != $('password2').value ) {
            errorField('password1', 'Passwords do not match');
            return false;
        }
    }
    if ( $('company') ) {
        if ( ($('company').value == "0") && ($('group_id').value != "1") ) {
            errorField('company', 'Please select company');
            return false;
        }
    }
    if ( $('group_id') ) {
        if ( $('group_id').value == "0" ) {
            errorField('group_id', 'Please select group');
            return false;
        }
    }
    return check_apostrophe();
    // everything is OK
    return true;
}

function check_group() {
    if ( $('groupname').value == "" || $('groupname').value == "NULL" ) {
        errorField('groupname', 'Please enter a name');
        return false;
    }
    if ( $('company') ) {
        if ( $('company').value == "0" ) {
            errorField('company', 'Please select company');
            return false;
        }
    }
    return check_apostrophe();
    // everything is OK
    return true;
}

function check_nettype() {
    if ( $('typename').value == "" || $('typename').value == "NULL" ) {
        errorField('typename', 'Please enter a title');
        return false;
    }
    return check_apostrophe();
    // everything is OK
    return true;
}

function check_vrf(as_nr) {
    var rd_as_check = new RegExp("^" + as_nr + ":[0-9]{1,5}");
    if ( $('company') ) {
        if ( $('company').value == "0" ) {
            errorField('company', 'Please select company');
            return false;
        }
    }
    if ( $('name').value == "" || $('name').value == "NULL" ) {
        errorField('name', 'Please enter a name');
        return false;
    }
    if ( $('vrf_name').value == "" || $('vrf_name').value == "NULL" ) {
        errorField('vrf_name', 'Please enter a configured vrf name');
        return false;
    }
    if ( $('rd').value == "" ) {
        errorField('rd', 'Please enter a route distinguisher');
        return false;
    }
    if ( $('rd').value != "" && $('rd').value.search(rd_check) == -1 ) {
        errorField('rd', 'Please enter a valid route distinguisher');
        return false;
    }
    if ( $('rd').value != "" && $('rd').value.search(rd_as_check) == -1 ) {
        errorField('rd', 'Please enter a valid route distinguisher [YOUR_AS:xxxxx]');
        return false;
    }
    return check_apostrophe();
    // everything is OK
    return true;
}

