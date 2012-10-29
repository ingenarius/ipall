/**
*
*  Simple Context Menu
*  http://www.webtoolkit.info/
*
**/


var SimpleContextMenu = {

    // private attributes
    _menuElement : null,
    _preventDefault : true,
    _preventForms : false,
    _hidetimer : null,



    // public method. Sets up whole context menu stuff..
    setup : function (conf) {
        if ( document.all && document.getElementById && !window.opera ) {
            SimpleContextMenu.IE = true;
        }

        if ( !document.all && document.getElementById && !window.opera ) {
            SimpleContextMenu.FF = true;
        }

        if ( document.all && document.getElementById && window.opera ) {
            SimpleContextMenu.OP = true;
        }

        if ( SimpleContextMenu.IE || SimpleContextMenu.FF ) {

            //document.oncontextmenu = SimpleContextMenu._show;
            //document.onclick = SimpleContextMenu._hide;

            if (conf && typeof(conf.preventDefault) != "undefined") {
                SimpleContextMenu._preventDefault = conf.preventDefault;
            }

            if (conf && typeof(conf.preventForms) != "undefined") {
                SimpleContextMenu._preventForms = conf.preventForms;
            }

        }
        SimpleContextMenu.sourceid = '';

    },


    // private method. Shows context menu
    _getReturnValue : function (e) {

        var returnValue = true;
        var evt = SimpleContextMenu.IE ? window.event : e;

        if (evt.button != 1) {
            if (evt.target) {
                var el = evt.target;
            } else if (evt.srcElement) {
                var el = evt.srcElement;
            }

            var tname = el.tagName.toLowerCase();

            if ((tname == "input" || tname == "textarea")) {
                if (!SimpleContextMenu._preventForms) {
                    returnValue = true;
                } else {
                    returnValue = false;
                }
            } else {
                if (!SimpleContextMenu._preventDefault) {
                    returnValue = true;
                } else {
                    returnValue = false;
                }
            }
        }
        return returnValue;
    },


    // private method. Shows context menu
    _show : function (e, menuElementId) {

        SimpleContextMenu._hide();
		//SimpleContextMenu.data = data;

        if (menuElementId) {
            var m = SimpleContextMenu._getMousePosition(e);
            var s = SimpleContextMenu._getScrollPosition(e);

            SimpleContextMenu._menuElement = document.getElementById(menuElementId);
            var w = 120;
            SimpleContextMenu._menuElement.style.left = m.x + s.x + 'px';
            SimpleContextMenu._menuElement.style.top = m.y + s.y + 'px';
            SimpleContextMenu._menuElement.style.display = 'block';
            SimpleContextMenu._menuElement.onmouseout = SimpleContextMenu._mouseout
            SimpleContextMenu._menuElement.onmouseover = SimpleContextMenu._mouseover
            return false;
        }
        return SimpleContextMenu._getReturnValue(e);

    },

    _mouseout : function () {
        SimpleContextMenu._hidetimer = window.setInterval('SimpleContextMenu._hide()',500);
    },
    _mouseover : function () {
        window.clearInterval(SimpleContextMenu._hidetimer);
    },
    


    // private method. Hides context menu
    _hide : function () {
	window.clearInterval(SimpleContextMenu._hidetimer);

        if (SimpleContextMenu._menuElement) {
            SimpleContextMenu._menuElement.style.display = 'none';
        }

    },


    // private method. Returns mouse position
    _getMousePosition : function (e) {

        e = e ? e : window.event;
        var position = {
            'x' : e.clientX,
            'y' : e.clientY
        }

        return position;

    },


    // private method. Get document scroll position
    _getScrollPosition : function () {

        var x = 0;
        var y = 0;

        if( typeof( window.pageYOffset ) == 'number' ) {
            x = window.pageXOffset;
            y = window.pageYOffset;
        } else if( document.documentElement && ( document.documentElement.scrollLeft || document.documentElement.scrollTop ) ) {
            x = document.documentElement.scrollLeft;
            y = document.documentElement.scrollTop;
        } else if( document.body && ( document.body.scrollLeft || document.body.scrollTop ) ) {
            x = document.body.scrollLeft;
            y = document.body.scrollTop;
        }

        var position = {
            'x' : x,
            'y' : y
        }

        return position;

    },

    click : function (e, menu, vars) {
        SimpleContextMenu.menu_create(menu, vars);
        SimpleContextMenu._show(e, 'cmenu');
    },

    menu_create : function (menu, vars) {
        switch(menu) {
          case 'prefix':
            // data format of "vars":
            // 'ipall_dir;cgi_dir;id;vrf;path,smoothbox'
            var tmp = vars.split(';');
            viewurl = tmp[1]+'/network_view.cgi?'+tmp[2]+tmp[5];
            printurl = tmp[1]+'/network_print.cgi?'+tmp[2]+tmp[5];
            //printurl = tmp[1]+'/network_print.cgi?'+tmp[2];
            editurl = tmp[1]+'/network_edit.cgi?'+tmp[2]+tmp[5];
            subneturl = tmp[1]+'/network_subnet.cgi?'+tmp[2]+tmp[5];
            importurl = tmp[1]+'/network_upload_csv.cgi?'+tmp[2]+tmp[5];
            deleteurl = tmp[1]+'/network_delete.cgi?'+tmp[3]+'&'+tmp[4]+'&'+tmp[2]+tmp[5];
            deletetext = 'Do you really want to delete this network?';
            permurl = tmp[1]+'/network_permissions.cgi?'+tmp[2]+tmp[5];
            ipall_dir = tmp[0];
            // menu header
            htmlText = '<li class=\"SimpleContextMenuHeader\">prefix menu</li>';
            //view
            //htmlText += '<li><a style=&quot;background-image: url('+ipall_dir'+/images/viewOn.png);&quot; ';
            htmlText += '<li><a class=\"smoothbox\" style=\"background-image: url(\''+ipall_dir+'\/images/viewOn.png\');\" ';
            htmlText += ' href=\"'+viewurl+'\">view</a></li>';
            //print
            htmlText += '<li><a class=\"smoothbox\" style=\"background-image: url(\''+ipall_dir+'/images/printOn.png\');\" ';
            htmlText += ' href=\"'+printurl+'\">print view</a></li>';
            //edit
            htmlText += '<li><a class=\"smoothbox\" style=\"background-image: url(\''+ipall_dir+'\/images/editOn.png\');\" ';
            htmlText += ' href=\"'+editurl+'\">edit</a></li>';
            //subnet
            htmlText += '<li><a class=\"smoothbox\" style=\"background-image: url(\''+ipall_dir+'\/images/subnetOn.png\');\" ';
            htmlText += ' href=\"'+subneturl+'\">create subnet</a></li>';
            //import csv
            htmlText += '<li><a class=\"smoothbox\" style=\"background-image: url(\''+ipall_dir+'\/images/importOn.png\');\" ';
            htmlText += ' href=\"'+importurl+'\">import CSV</a></li>';
            //delete
            htmlText += '<li><a class=\"smoothbox\" style=\"background-image: url(\''+ipall_dir+'\/images/deleteOn.png\');\" ';
            htmlText += ' href=\"'+deleteurl+'\"><span onClick=\"confirm(\''+deletetext+'\');\">delete</span></a></li>';
            //permissions
            htmlText += '<li><a class=\"smoothbox\" style=\"background-image: url(\''+ipall_dir+'\/images/permissionOn.png\');\" ';
            htmlText += ' href=\"'+permurl+'\">permissions</a></li>';

            $('cmenu').set('html', htmlText);
            // init smoothbox links
            TB_init();
            break;
          default:
           	$('cmenu').set('html', '<li class="SimpleContextMenuHeader">unknown menu</li>');
            break;
        }
    }

};
