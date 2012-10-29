<?php
session_start();
if ($_SESSION["PHPSESSID"] == session_id() && $_COOKIE["PHPSESSID"] == session_id()) {
    header("Location:/cgi-bin/index.cgi");
}
else {
    require_once("header.inc.php");
?>
<div class=textPurple style="margin-top: 100px;">
<form action="login.php" method="post">
<div id=table_main>
      <div id=pos_left_small class=lineHeight>Username</div>
      <div id=pos_right_wide class=lineHeight>
        <input type="text" name="username" id="username" size="20" maxlength="20" class=b_eingabefeld><br>
      </div>
      <div id=pos_left_small class=lineHeight>Password</div>
      <div id=pos_right_wide class=lineHeight>
        <input type="password" name="passwd" id="passwd" size="20" maxlength="20" class=b_eingabefeld><br>
      </div>
      <div id=pos_right_wide class=lineHeight>
        <input type="submit" name="send" value="Login" class="button">
      </div>
      <div id=pos_clear></div>
</div>

<div class=textGrey style="margin-top: 50px;" class="table_main">
    <span style="margin-left: 50px;">for a demo please use:</span><br>
    <span style="margin-left: 50px;">username: demo</span><br>
    <span style="margin-left: 50px;">password: demouser01</span><br>
    <span style="margin-left: 50px;">best viewed with 
        <a href="http://www.mozilla.com" target="_blank">Mozilla Firefox</a><br>
    </span>
    </span>
</div>
<script type="text/javascript">
    setFocus("username");
</script>

</body>
</html>
<? } ?>
