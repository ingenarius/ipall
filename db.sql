-- *****************************
-- IP@LL IP addressmanagement
-- Copyright 2007 Andreas Poiss
-- *****************************
--
-- phpMyAdmin SQL Dump
-- version 2.6.3-pl1
-- http://www.phpmyadmin.net
-- 
-- Host: localhost
-- Erstellungszeit: 10. Januar 2007 um 14:15
-- Server Version: 4.1.12
-- PHP-Version: 4.3.9
-- 
-- Datenbank: `ipall`
-- 

-- 
-- Tabellenstruktur für Tabelle `ipall_group`
-- 

CREATE TABLE `ipall_group` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `groupname` varchar(50) NOT NULL default '',
  `user_admin` tinyint(1) unsigned NOT NULL default '0',
  `company_admin` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

-- 
-- Daten für Tabelle `ipall_group`
-- 

INSERT INTO `ipall_group` VALUES (1, 'Super Administratoren', 1, 1);
INSERT INTO `ipall_group` VALUES (2, 'Company1 Administrators', 1, 1);
INSERT INTO `ipall_group` VALUES (3, 'Company1 Users', 0, 0);

-- --------------------------------------------------------

-- 
-- Tabellenstruktur für Tabelle `ipall_ip`
-- 

CREATE TABLE `ipall_ip` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `parent_id` bigint(20) unsigned NOT NULL default '0',
  `label` varchar(50) NOT NULL default '',
  `address` bigint(20) unsigned NOT NULL default '0',
  `net_name` varchar(35) NOT NULL default '',
  `description` text,
  `path` varchar(250) NOT NULL default '',
  `subnetted` tinyint(1) NOT NULL default '0',
  `peering_info_id` bigint(20) unsigned default NULL,
  `vrf` varchar(50) NOT NULL default '',
  `aggregated` tinyint(1) unsigned NOT NULL default '0',
  `product_id` bigint(20) unsigned default NULL,
  `interface_id` bigint(20) unsigned default NULL,
  `service_id` bigint(20) unsigned default NULL,
  `allocated` tinyint(1) unsigned NOT NULL default '0',
  `interface_name` varchar(250) default NULL,
  `companies_id` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


-- 
-- Tabellenstruktur für Tabelle `ipall_network_types`
-- 

CREATE TABLE `ipall_network_types` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `typename` varchar(50) NOT NULL default '',
  `description` varchar(250) default NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `typename` (`typename`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=11 ;

-- 
-- Daten für Tabelle `ipall_network_types`
-- 

INSERT INTO `ipall_network_types` VALUES (1, 'ADSL Pool dynamic', 'IP address pool for ADSL customers who get a dynamic assigned IP');
INSERT INTO `ipall_network_types` VALUES (2, 'ADSL Pool static', 'IP address pool for ADSL customers who get always the same IP');
INSERT INTO `ipall_network_types` VALUES (3, 'ADSL Customer Network', 'Customer Network for ADSL connected customers');
INSERT INTO `ipall_network_types` VALUES (4, 'Backbone POP LAN', 'LANs where backbone devices can be connected to');
INSERT INTO `ipall_network_types` VALUES (5, 'Backbone Loopback', 'Loopbacks for backbone devices');
INSERT INTO `ipall_network_types` VALUES (6, 'Backbone Linknet', 'Linknets for backbone devices');
INSERT INTO `ipall_network_types` VALUES (7, 'Customer Loopback', 'Loopbacks for internet customers');
INSERT INTO `ipall_network_types` VALUES (8, 'Customer Linknet', 'Linknets for internet customers');
INSERT INTO `ipall_network_types` VALUES (9, 'Customer Network', 'LAN networks for internet customers');
INSERT INTO `ipall_network_types` VALUES (10, 'Peering LAN', 'Internet Exchange Peering LAN');

-- --------------------------------------------------------

-- 
-- Tabellenstruktur für Tabelle `ipall_peering_info`
-- 

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
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- 
-- Tabellenstruktur für Tabelle `ipall_rights`
-- 

CREATE TABLE `ipall_rights` (
  `group_id` bigint(20) unsigned NOT NULL default '0',
  `path` varchar(250) NOT NULL default '',
  `delete_net` tinyint(1) unsigned NOT NULL default '0',
  `edit_net` tinyint(1) unsigned NOT NULL default '0',
  `subnet_net` tinyint(1) unsigned NOT NULL default '0',
  `view_net` tinyint(1) unsigned NOT NULL default '0',
  `edit_vrf` tinyint(1) unsigned NOT NULL default '0',
  `delete_vrf` tinyint(1) unsigned NOT NULL default '0',
  PRIMARY KEY  (`group_id`,`path`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


-- 
-- Tabellenstruktur für Tabelle `ipall_rights_vrf`
-- 

CREATE TABLE `ipall_rights_vrf` (
  `group_id` int(11) NOT NULL default '0',
  `vrf` varchar(250) NOT NULL default '',
  `create_net` int(1) NOT NULL default '0',
  PRIMARY KEY  (`group_id`,`vrf`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;


-- 
-- Tabellenstruktur für Tabelle `ipall_user_group`
-- 

CREATE TABLE `ipall_user_group` (
  `username` varchar(250) NOT NULL default '',
  `group_id` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`username`,`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- 
-- Daten für Tabelle `ipall_user_group`
-- 

INSERT INTO `ipall_user_group` VALUES ('admin', 1);
INSERT INTO `ipall_user_group` VALUES ('testuser', 3);

-- 
-- Tabellenstruktur für Tabelle `networks`
-- 

CREATE TABLE `networks` (
  `networks_id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(30) NOT NULL default '',
  `description` varchar(30) NOT NULL default '',
  `companies_id` int(10) unsigned NOT NULL default '0',
  `vpn_vrf_name` varchar(30) NOT NULL default '',
  `vpn_rd` varchar(30) NOT NULL default '',
  PRIMARY KEY  (`networks_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;


-- 
-- Tabellenstruktur für Tabelle `nms_log`
-- 

CREATE TABLE `nms_log` (
  `id` bigint(20) unsigned NOT NULL auto_increment,
  `user` varchar(250) NOT NULL default '',
  `time` datetime NOT NULL default '0000-00-00 00:00:00',
  `table_name` varchar(250) NOT NULL default '',
  `sql_statement` text NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- 
-- Tabellenstruktur für Tabelle `ncompanies`
-- 

CREATE TABLE `companies` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `name` varchar(250) NOT NULL default '',
  `description` varchar(30) NOT NULL default '',
  `street` varchar(50) NOT NULL default '',
  `street_number` varchar(10) NOT NULL default '',
  `postal_code` varchar(8) NOT NULL default '',
  `city` varchar(30) NOT NULL default '',
  `country` varchar(20) NOT NULL default '',
  `as_nr` int(5) NOT NULL default 0,
  `as_set` varchar(250) NOT NULL default '',
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;


-- 
-- Tabellenstruktur für Tabelle `persons`
-- 

CREATE TABLE `persons` (
  `persons_id` int(11) NOT NULL auto_increment,
  `surname` varchar(100) NOT NULL default '',
  `forename` varchar(100) NOT NULL default '',
  `mobile` varchar(40) NOT NULL default '',
  `phone` varchar(40) NOT NULL default '',
  `mail` varchar(50) NOT NULL default '',
  `web` varchar(50) NOT NULL default '',
  `username` varchar(30) NOT NULL default '',
  `password` varchar(32) NOT NULL default '',
  `companies_id` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`persons_id`),
  KEY `username` (`username`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;

-- 
-- Daten für Tabelle `persons`
-- 

INSERT INTO `persons` VALUES (1, 'Super Administrator', '', '', '', '', '', 'admin', MD5('admin'), 0);