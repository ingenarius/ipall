<?php
session_start();

include 'var.inc.php';
$conn = @ mysql_connect($dbserver,$dbuser,$dbpass);
if (!$conn) {
    die ("Sorry, no database connection!");
    }

mysql_select_db($dbname,$conn);

$sql_del = "DELETE FROM php_session WHERE phpsessid='".$_SESSION["PHPSESSID"]."'";
mysql_query($sql_del,$conn) or die(mysql_error());
mysql_close($conn);

session_unset();
session_destroy();
header("Location:/index.php");?> 
