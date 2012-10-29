<?php
session_start();

if ((!isset($_POST["username"])) OR (!isset($_POST["passwd"]))) {
    die ("Sorry, you have to fill out name and password!");
}
$username = trim($_POST["username"]);
$password = trim($_POST["passwd"]);

include 'var.inc.php';
$conn = @ mysql_connect($dbserver,$dbuser,$dbpass);
if (!$conn) {
    die ("Sorry, no database connection!");
}

mysql_select_db($dbname,$conn);

$query = "SELECT phpsessid FROM php_session WHERE username = '".$username."'";
$result =  mysql_query($query,$conn);
$rows =  mysql_fetch_array($result,MYSQL_ASSOC);

if ($rows) {
    $sql_del = "DELETE FROM php_session WHERE phpsessid='".$rows["phpsessid"]."'";
    mysql_query($sql_del,$conn) or die(mysql_error());
}


$query = "SELECT password FROM persons WHERE username = '".$username."'";
$result =  mysql_query($query,$conn);

$rows =  mysql_fetch_array($result,MYSQL_ASSOC);

if (!$rows) {
    die ("Sorry, no such user!");
}

if ($rows["password"] <> md5($password)) {
    die ("Sorry, wrong password!");
}

$_SESSION["PHPSESSID"] = session_id();
$start = date("YmdHis", time());
$end = date("YmdHis", time()+3600);
$sql_ins_sess = "INSERT php_session SET phpsessid='".$_SESSION["PHPSESSID"]."', username='".$username."', 
ip='".$_SERVER['REMOTE_ADDR']."', starttime=".$start.", endtime=".$end;
mysql_query($sql_ins_sess,$conn) or die(mysql_error());
mysql_close($conn);

header("Location:/cgi-bin/index.cgi");
