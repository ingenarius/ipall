<?php
/*
// Comment this out if you don't want to use https only
// begin https redirection 
if ($_SERVER["SERVER_PORT"] != "443" && $_SERVER['SERVER_NAME'] != "localhost")
{
  $port = $_SERVER["SERVER_PORT"];
  $ssl_port = "443";  //Change 443 to whatever port you use for https (443 is the default and will work in most cases)
  if ($port != $ssl_port)
  {
    $host = $_SERVER["HTTP_HOST"];
    $uri = $_SERVER["REQUEST_URI"];
    header("Location: https://$host$uri");
  }
}
// end https redirection
*/
?>

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
    <title>IP@LL</title>
    <link type="text/css" href="ipall_style_new.css" rel="stylesheet">
    <script type="text/javascript" src="utils/ipall_utils.js"></script>
    <script type="text/javascript" src="utils/ajax.js"></script>
    <script type="text/javascript" src="utils/contextmenu.js"></script>
    <script type="text/javascript" src="utils/mootools.js"></script>
</head>

<?php
include 'var.inc.php';
?>
<body bgcolor="#FFFFFF">
<div id="table_index">
    <span class="headlineLogo"><a href="%s"><img src="/images/logo0.gif" width=120 border=0></a></span>
    <span class="headlineText">IP@LL <span class="headlineVersion">v<? echo $version ?></span> </span>
    <div style="text-align: right;" class="TextBlackSmall">&copy; 2007 
    <a href="<? echo $company_url?>" target="_blank"><? echo $company ?></a>
    </div>
</div>
