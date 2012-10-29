-- MySQL dump 10.11
--
-- Host: localhost    Database: ipall
-- ------------------------------------------------------
-- Server version	5.0.51a-3ubuntu5.7

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `companies`
--

DROP TABLE IF EXISTS `companies`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `companies` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `name` varchar(250) NOT NULL default '',
  `description` varchar(30) NOT NULL default '',
  `street` varchar(50) NOT NULL default '',
  `street_number` varchar(10) NOT NULL default '',
  `postal_code` varchar(8) NOT NULL default '',
  `city` varchar(30) NOT NULL default '',
  `country` varchar(20) NOT NULL default '',
  `as_nr` int(5) NOT NULL default '0',
  `as_set` varchar(250) NOT NULL default '',
  `ripe_header` text,
  `ripe_trailer` text,
  `ripe_password` varchar(250) default NULL,
  `ripe_mntby` varchar(250) default NULL,
  `ripe_admin_c` varchar(250) default NULL,
  `ripe_tech_c` varchar(250) default NULL,
  `ripe_notify` varchar(250) default NULL,
  `is_lir` int(1) NOT NULL default '0',
  `send_delete_mail` int(1) NOT NULL default '0',
  `delete_mail` varchar(250) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `companies`
--
/*
LOCK TABLES `companies` WRITE;
INSERT INTO `companies` VALUES (1,'home','','Seepark','33','2486','Landegg','AT',4711,'AS-4711','','','weissnicht','AS4711-MNT','KOELN-RIPE','KOELN-RIPE','webmaster@poiss.priv.at',0,0,'webmaster@poiss.priv.at'),(5,'demo','','demo','1','1234','demo','AT',9999,'AS-DEMO','','','pw','ADMIN-C','ADMIN-C','ADMIN-C','notify@demo.com',1,0,' '),(6,'Austro Control GmbH','','Schnirchgasse','11','1030','Wien','',0,'','','','','','','','',0,0,' '),(8,'ACG Internet','Austro Control Oesterreichisch','Schnirchgasse','11','1030','Wien','AT',51066,'','org:          ORG-ACOG1-RIPE\r\nremarks:      *************************\r\nremarks:      * UPSTREAM              *\r\nremarks:      ************************* \r\nimport:       from AS1764  accept   ANY\r\nexport:       to AS1764    announce AS51066\r\nimport:       from AS8447  accept   ANY\r\nexport:       to AS8447    announce AS51066','admin-c:      AP11959-RIPE\r\nadmin-c:      DW1875-RIPE\r\ntech-c:       AP11959-RIPE\r\ntech-c:       DW1875-RIPE\r\nmnt-by:       RIPE-NCC-END-MNT\r\nmnt-by:       AS1764-MNT\r\nmnt-by:       AUSTROCONTROL-MNT\r\nmnt-routes:   AS1764-MNT\r\nmnt-routes:   AUSTROCONTROL-MNT\r\nchanged:      hostmaster@ripe.net 20100526\r\nsource:       RIPE','ZA93r@ph-@','AUSTROCONTROL-MNT','AP11959-RIPE','AP11959-RIPE','andreas.poiss@austrocontrol.at',1,0,' ');
UNLOCK TABLES;
*/
--
-- Table structure for table `ipall_group`
--

DROP TABLE IF EXISTS `ipall_group`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `ipall_group` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `groupname` varchar(50) NOT NULL default '',
  `user_admin` tinyint(1) unsigned NOT NULL default '0',
  `company_admin` tinyint(1) unsigned NOT NULL default '0',
  `companies_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `ipall_group`
--

LOCK TABLES `ipall_group` WRITE;
/*!40000 ALTER TABLE `ipall_group` DISABLE KEYS */;
INSERT INTO `ipall_group` VALUES (1,'Super Administrators',1,1,0);
/*!40000 ALTER TABLE `ipall_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ipall_ip`
--

DROP TABLE IF EXISTS `ipall_ip`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `ipall_ip` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `parent_id` bigint(20) unsigned NOT NULL default '0',
  `label` varchar(50) NOT NULL default '',
  `address` varchar(250) NOT NULL default '0',
  `net_name` varchar(35) NOT NULL default '',
  `description` text,
  `path` varchar(250) NOT NULL default '',
  `subnetted` tinyint(1) NOT NULL default '0',
  `peering_info_id` bigint(20) unsigned default NULL,
  `vrf` varchar(50) NOT NULL default '',
  `aggregated` tinyint(1) unsigned NOT NULL default '0',
  `product_id` bigint(20) unsigned default NULL,
  `interface_id` bigint(20) unsigned default NULL,
  `service_id` bigint(20) unsigned NOT NULL default '1',
  `allocated` tinyint(1) unsigned NOT NULL default '0',
  `interface_name` varchar(250) default NULL,
  `companies_id` bigint(20) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=270 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `ipall_network_types`
--

DROP TABLE IF EXISTS `ipall_network_types`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `ipall_network_types` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `typename` varchar(50) NOT NULL default '',
  `description` varchar(250) default NULL,
  `is_peering` tinyint(1) NOT NULL default '0',
  `font_color` varchar(7) default '#000000',
  `bg_color` varchar(7) default '#FFFFFF',
  `companies_id` bigint(20) unsigned NOT NULL auto_increment,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `typename` (`typename`)
) ENGINE=MyISAM AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `ipall_network_types`
--

LOCK TABLES `ipall_network_types` WRITE;
/*!40000 ALTER TABLE `ipall_network_types` DISABLE KEYS */;
INSERT INTO `ipall_network_types` VALUES (1,'Default','',0,'#33CC00','#FFFFFF'),(2,'ADSL Pool dynamic','IP address pool for ADSL customers who get a dynamic assigned IP',0,'#000000','#FFFFFF'),(3,'ADSL Pool static','IP address pool for ADSL customers who get always the same IP',0,'#000000','#FFFFFF'),(4,'ADSL Customer Network','',0,'#6600FF','#FFFFFF'),(5,'Backbone POP LAN','LANs where backbone devices can be connected to',0,'#000000','#FFFFFF'),(6,'Backbone Loopback','Loopbacks for backbone devices',0,'#000000','#FFFFFF'),(7,'Backbone Linknet','Linknets for backbone devices',1,'#000000','#FFFFFF'),(8,'Customer Loopback','Loopbacks for internet customers',0,'#000000','#FFFFFF'),(9,'Customer Linknet','Linknets for internet customers',1,'#000000','#FFFFFF'),(10,'Customer Network','LAN networks for internet customers',0,'#000000','#FFFFFF'),(11,'Peering LAN','',1,'#FFCC00','#FFFFFF');
/*!40000 ALTER TABLE `ipall_network_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ipall_peering_info`
--

DROP TABLE IF EXISTS `ipall_peering_info`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `ipall_peering_info` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `as_nr` int(10) unsigned NOT NULL default '0',
  `as_set` varchar(50) default NULL,
  `md5` varchar(250) default NULL,
  `rs` tinyint(1) unsigned NOT NULL default '0',
  `session_up` tinyint(1) unsigned NOT NULL default '0',
  `contact` varchar(250) default NULL,
  `comment` text,
  `device` varchar(50) default NULL,
  `max_prefix` int(11) unsigned default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `ipall_rights`
--

DROP TABLE IF EXISTS `ipall_rights`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `ipall_rights` (
  `group_id` bigint(20) unsigned NOT NULL default '0',
  `path` varchar(250) NOT NULL default '',
  `delete_net` tinyint(1) unsigned NOT NULL default '0',
  `edit_net` tinyint(1) unsigned NOT NULL default '0',
  `subnet_net` tinyint(1) unsigned NOT NULL default '0',
  `view_net` tinyint(1) unsigned NOT NULL default '0',
  `edit_vrf` tinyint(1) unsigned NOT NULL default '0',
  `delete_vrf` tinyint(1) unsigned NOT NULL default '0',
  `companies_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY  (`group_id`,`path`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `ipall_rights_vrf`
--

DROP TABLE IF EXISTS `ipall_rights_vrf`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `ipall_rights_vrf` (
  `group_id` bigint(20) NOT NULL default '0',
  `vrf` varchar(250) NOT NULL default '',
  `create_net` int(1) NOT NULL default '0',
  `companies_id` bigint(20) unsigned NOT NULL,
  PRIMARY KEY  (`group_id`,`vrf`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;


--
-- Table structure for table `ipall_user_group`
--

DROP TABLE IF EXISTS `ipall_user_group`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `ipall_user_group` (
  `username` varchar(250) NOT NULL default '',
  `group_id` bigint(20) unsigned NOT NULL default '0',
  PRIMARY KEY  (`username`,`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `ipall_user_group`
--

LOCK TABLES `ipall_user_group` WRITE;
/*!40000 ALTER TABLE `ipall_user_group` DISABLE KEYS */;
INSERT INTO `ipall_user_group` VALUES ('admin',1);
/*!40000 ALTER TABLE `ipall_user_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `networks`
--

DROP TABLE IF EXISTS `networks`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `networks` (
  `networks_id` bigint(20) unsigned NOT NULL auto_increment,
  `name` varchar(30) NOT NULL default '',
  `description` varchar(30) NOT NULL default '',
  `companies_id` bigint(20) unsigned NOT NULL default '0',
  `vpn_vrf_name` varchar(30) NOT NULL default '',
  `vpn_rd` varchar(30) NOT NULL default '',
  PRIMARY KEY  (`networks_id`)
) ENGINE=MyISAM AUTO_INCREMENT=28 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `networks`
--

LOCK TABLES `networks` WRITE;
/*!40000 ALTER TABLE `networks` DISABLE KEYS ;
INSERT INTO `networks` VALUES (1,'dmz','',1,'dmz','4711:0'),(20,'inet','NULL',5,'demo-inet','9999:0'),(19,'private','NULL',1,'private','4711:4711'),(27,'internet','NULL',8,'internet','51066:0'),(21,'INFOnet','NULL',6,'infonet','0:65100'),(22,'SOA LAN','',6,'soamux','0:1234'),(23,'XBone','NULL',6,'xbone','0:666');
/*!40000 ALTER TABLE `networks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `nms_log`
--

DROP TABLE IF EXISTS `nms_log`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `nms_log` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `user` varchar(250) NOT NULL default '',
  `time` datetime NOT NULL default '0000-00-00 00:00:00',
  `table_name` varchar(250) NOT NULL default '',
  `sql_statement` text NOT NULL,
  `companies_id` bigint(20) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=552 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;


--
-- Table structure for table `persons`
--

DROP TABLE IF EXISTS `persons`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `persons` (
  `persons_id` bigint(20) NOT NULL auto_increment,
  `surname` varchar(100) NOT NULL default '',
  `forename` varchar(100) NOT NULL default '',
  `mobile` varchar(40) NOT NULL default '',
  `phone` varchar(40) NOT NULL default '',
  `mail` varchar(50) NOT NULL default '',
  `web` varchar(50) NOT NULL default '',
  `username` varchar(30) NOT NULL default '',
  `password` varchar(32) NOT NULL default '',
  `companies_id` bigint(20) unsigned NOT NULL default '0',
  `show_config` int(1) unsigned NOT NULL default '0',
  `show_ripe` int(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`persons_id`),
  KEY `username` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `persons`
--

LOCK TABLES `persons` WRITE;
/*!40000 ALTER TABLE `persons` DISABLE KEYS */;
INSERT INTO `persons` VALUES (1,'Administrator','','','','','','admin',MD5('admin'),0,0,0);
/*!40000 ALTER TABLE `persons` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `php_session`
--

DROP TABLE IF EXISTS `php_session`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `php_session` (
  `phpsessid` varchar(250) NOT NULL,
  `username` varchar(20) default NULL,
  `ip` varchar(250) default NULL,
  `starttime` varchar(50) default NULL,
  `endtime` varchar(50) default NULL,
  PRIMARY KEY  (`phpsessid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `php_session`
--

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2010-06-17 10:21:41
