/*

*****************************
IP@LL IP addressmanagement
Copyright 2007 poiss.priv.at
mailto:andi@poiss.priv.at
*****************************
*/

function ajaxFunction(scripturl, elId, type) {
    var xmlHttp;
    //Creating object of XMLHTTP in IE
    try {
        xmlHttp = new ActiveXObject("Msxml2.XMLHTTP");
    }
    catch(e) {
        try {
            xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
        }
        catch(e) {
            xmlHttp = null;
        }
    }
    //Creating object of XMLHTTP in Mozilla and Safari
    if(!xmlHttp && typeof XMLHttpRequest != "undefined") {
        xmlHttp = new XMLHttpRequest();
    }
    xmlHttp.open('GET',scripturl,true);

    xmlHttp.onreadystatechange=function() {
        if(xmlHttp.readyState==4) {
            // type 1 = fill <div> or <span> tag with responseText
            if(type == '1') {
                $(elId).set('html',xmlHttp.responseText);
                return false;
            }
            //type 2 = fill network dropdown box
            else if(type == '2') {
                var elem = $('netmask')
                var mask = elem.options[elem.selectedIndex].value
                var response = xmlHttp.responseText;
                var networks = response.split(';')[0];
                var index = parseInt(response.split(';')[1]);
                var pages = parseInt(response.split(';')[2]);

                while (networks.indexOf("\n") > -1) {
                    networks = networks.replace("\n",'');
                }
                if (pages > 1) {
                    if (parseInt(scripturl.split('&').length) == 3) {
                            scripturl = scripturl.split('&')[0] + "&" + scripturl.split('&')[1];
                        }
                    var next_index = index + 1
                    if (index < pages) {
                        var next_page = '<a href="javascript:void(0);" title="next set of subnets" onClick="fillMoreNetworks(\''+scripturl+'\','+next_index+');"> <img src="/images/go-next.png" border=0> </a>';
                        }
                    else {
                        var next_page = '';
                        }
                    if (index > 1) {
                        var prev_index = index - 1
                        var prev_page = '<a href="javascript:void(0);" title="previous set of subnets" onClick="fillMoreNetworks(\''+scripturl+'\','+prev_index+');"> <img src="/images/go-previous.png" border=0> </a>';
                        }
                    else {
                        var prev_page = '';
                        }
                    var pages_link = prev_page + "&nbsp;" + next_page;
                    $('nw_page').set('html', pages_link);
                    }
                if (networks != '') {
                    var net = networks.split(',');
                    var i;
                    clearBox('network');
                    fillBox('network','None','select network...');
                    for (i=0; i<net.length; i++) {
                        fillBox('network', net[i], net[i]);
                    }
                    /*
                    if (mask == '32' && $('peering_info').style.display == 'block') {
                        $('peering_info').style.display = 'block';
                    }
                    else {
                        $('peering_info').style.display = 'none';
                    }
                    */
                }
                else {
                    clearBox('network');
                    fillBox('network','None','none available!');
                    $('peering_info').style.display = 'none';
                }
                return false;
            }
            // type 3 = fill dropdownbox (elId) with return value/text pairs
            else if(type == '3') {
                var values = xmlHttp.responseText;
                while (values.indexOf("\n") > -1) {
                    values = values.replace("\n",'');
                }
                if(values != '') {
                    var valuePairs = values.split(';');
                    var i;
                    clearBox(elId);
                    fillBox(elId, '0', 'select...');
                    for(i=0; i<valuePairs.length; i++) {
                        //$('info').set('html', valuePairs[i]);
                        id = valuePairs[i].split(',')[0]
                        name = valuePairs[i].split(',')[1]
                        fillBox(elId, id, name);
                    }
                }
                else {
                    $('info').set('html', '<br><b>no return value</b>');
                }
            }
            // type 4 = toggle visible/unvisible
            else if(type == '4') {
                visible = xmlHttp.responseText;
                if (visible.indexOf("value:0") > -1) {
                    $(elId).style.display='none';
                }
                else {
                    $(elId).style.display='block';
                }
            }
            // type 5 = fill value (only 1!) into elId field
            else if(type == '5') {
                var value = xmlHttp.responseText;
                while (value.indexOf("\n") > -1) {
                    value = value.replace("\n",'');
                }
                var start = value.indexOf("result:") + 7;
                var end = value.indexOf(";", start); 
                value = value.substring(start, end);
                $(elId).value = value;
            }
        }
    }

    xmlHttp.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
    xmlHttp.send(null);
}

/*
 * tree helper functions
 */

function callNode(id, ipall_dir, cgi_dir, vrf, path) {
        elId = 'net'+id+'_'+id;
        //menuName = 'contextmenu'+id;
        if ($(elId).style.display=='block') {
                $('img_of_'+id).src = ipall_dir+'/images/ftv2pnode.gif';
                $(elId).style.display='none'; 
        }
        else {
                $(elId).style.display='block';
                scriptUrl = cgi_dir+'/a_network_childs.cgi?'+vrf+'&'+id+'&'+path;
                $(elId).onclick = ajaxFunction(scriptUrl, elId, '1'); 
                $('img_of_'+id).src = ipall_dir+'/images/ftv2mnode.gif';
        }
}

function callNodeWindow(windowname, id, ipall_dir, cgi_dir, vrf, path) {
        elId = windowname+'.net'+id+'_'+id;
        //menuName = 'contextmenu'+id;
        if ($(elId).style.display=='block') {
                $('img_of_'+id).src = ipall_dir+'/images/ftv2pnode.gif';
                $(elId).style.display='none';
        }
        else {
                $(elId).style.display='block';
                scriptUrl = cgi_dir+'/a_network_childs.cgi?'+vrf+'&'+id+'&'+path;
                $(elId).onclick = ajaxFunction(scriptUrl, elId, '1');
                $('img_of_'+id).src = ipall_dir+'/images/ftv2mnode.gif';
        }
}

/*
 * list functions
 */

var NS4 = (navigator.appName == "Netscape" && parseInt(navigator.appVersion) < 5);
function addOption(theSel, theText, theValue) {
        var newOpt = new Option(theText, theValue);
        var selLength = theSel.length;
        theSel.options[selLength] = newOpt;
}

function deleteOption(theSel, theIndex) { 
        var selLength = theSel.length;
        if(selLength>0) {
                theSel.options[theIndex] = null;
        }
}

function moveOptions(from, to, cgi_dir, vrf) {
        var selFrom = $(from);
        var selTo = $(to);
        var selLength = selFrom.length;
        var selectedText = new Array();
        var selectedValues = new Array();
        var selectedCount = 0;
        
        var i;
        
        // Find the selected Options in reverse order
        // and delete them from the 'from' Select.
        for(i=selLength-1; i>=0; i--) {
                if(selFrom.options[i].selected) {
                        selectedText[selectedCount] = selFrom.options[i].text;
                        selectedValues[selectedCount] = selFrom.options[i].value;
                        deleteOption(selFrom, i);
                        if (from == 'in_groups') {
                                $('del').onclick == ajaxFunction(cgi_dir+'/vrf_group_edit.cgi?'+vrf+'&del='+selectedValues[selectedCount], 'info', '1');
                        }
                        selectedCount++;
                }
        }
        
        // Add the selected text/values in reverse order.
        // This will add the Options to the 'to' Select
        // in the same order as they were in the 'from' Select.
        for(i=selectedCount-1; i>=0; i--) {
                addOption(selTo, selectedText[i], selectedValues[i]);
                if (to == 'in_groups') {
                        $('add').onclick = ajaxFunction(cgi_dir+'/vrf_group_edit.cgi?'+vrf+'&add='+selectedValues[i], 'info', '1');
                }
        }
        
        if(NS4) history.go(0);
}

function fillBox(elId, value, text) {
        var elem = $(elId);
        var len = elem.length;
        var newOpt = new Option(text, value);

        elem.options[len] = newOpt;     
}

function clearBox(elId) {
        $(elId).options.length = 0;
}

/*
 * misc
 */

function netNames(scripturl, srcElId, destElId) {
    if ($(destElId).style.display=='block') {
        $(destElId).style.display='none'; 
    }
    else {
        $(destElId).style.display='block';
        $(srcElId).onfocus = ajaxFunction(scripturl, destElId, '1'); 
    }
}


function fillNetworks(cgi_dir, parentId) {
        var elem = $('netmask')
        var mask = elem.options[elem.selectedIndex].value

        if (mask != '0') {
                $('netmask').onChange = ajaxFunction(cgi_dir+'/a_network_subnets.cgi?'+parentId+'&'+mask, 'network_container', '2');
        }
}


function fillMoreNetworks(uri, index) {
        var elem = $('netmask')
        var mask = elem.options[elem.selectedIndex].value

        if (mask != '0') {
                $('netmask').onChange = ajaxFunction(uri+'&'+index, 'network_container', '2');
        }
}


function fillGroup(cgi_dir) {
    var elem = $('company');
    var companies_id = elem.options[elem.selectedIndex].value;

    if (companies_id != '0') {
        $('company').onChange = ajaxFunction(cgi_dir+'/a_groups.cgi?'+companies_id, 'group_id', '3');
    }
    if (companies_id == '0') {
        clearBox('group_id');
        fillBox('group_id', '0', 'select company first...');
    }
}

