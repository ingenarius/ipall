function ajaxFunction(scripturl, formname) {
	var xmlHttp;
	try	{
		// Firefox, Opera 8.0+, Safari
		xmlHttp=new XMLHttpRequest();
	}
	catch (e) {
		// Internet Explorer
		try	{
			xmlHttp=new ActiveXObject("Msxml2.XMLHTTP");
		}
		catch (e) {
			try	{
					xmlHttp=new ActiveXObject("Microsoft.XMLHTTP");
			}
			catch (e) {
				alert("Your browser does not support AJAX!");
				return false;
			}
		}
	}
		
	xmlHttp.onreadystatechange=function() {
		if(xmlHttp.readyState==4) {
				document.getElementById(formname).innerHTML=xmlHttp.responseText;
		}
	}
	xmlHttp.open("GET",scripturl,true);
	xmlHttp.send(null);
}
