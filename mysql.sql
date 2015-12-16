/*
SQLyog Community v8.62 
MySQL - 5.1.49-1ubuntu8.1 : Database - kakazoo
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`kakazoo` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `kakazoo`;

/*Table structure for table `alchemy` */

DROP TABLE IF EXISTS `alchemy`;

CREATE TABLE `alchemy` (
  `player_id` int(11) NOT NULL,
  `alchemy_info` text,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `auction_event` */

DROP TABLE IF EXISTS `auction_event`;

CREATE TABLE `auction_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `seller` int(11) NOT NULL,
  `buyer` int(11) NOT NULL,
  `action_time` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `collection` */

DROP TABLE IF EXISTS `collection`;

CREATE TABLE `collection` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `status` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `collection_list` */

DROP TABLE IF EXISTS `collection_list`;

CREATE TABLE `collection_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `status` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `cost_log` */

DROP TABLE IF EXISTS `cost_log`;

CREATE TABLE `cost_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `player_id` int(11) DEFAULT NULL,
  `cost_kb` int(11) DEFAULT NULL,
  `cost_action` varchar(100) DEFAULT NULL,
  `cost_time` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `daily_task` */

DROP TABLE IF EXISTS `daily_task`;

CREATE TABLE `daily_task` (
  `player_id` int(11) NOT NULL,
  `task_info` text,
  `task_time` int(11) DEFAULT NULL,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `event_log` */

DROP TABLE IF EXISTS `event_log`;

CREATE TABLE `event_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `info` text,
  `create_time` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `exchange_task` */

DROP TABLE IF EXISTS `exchange_task`;

CREATE TABLE `exchange_task` (
  `player_id` int(11) NOT NULL,
  `create_time` int(11) DEFAULT NULL,
  `task_id` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `explore` */

DROP TABLE IF EXISTS `explore`;

CREATE TABLE `explore` (
  `player_id` int(11) NOT NULL,
  `leader` int(11) DEFAULT NULL,
  `score` int(11) DEFAULT NULL,
  `reward` varchar(20) DEFAULT NULL,
  `sns_name` varchar(255) DEFAULT NULL,
  `sns_pic` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `explore_event_log` */

DROP TABLE IF EXISTS `explore_event_log`;

CREATE TABLE `explore_event_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `leader_id` int(11) NOT NULL,
  `create_time` int(11) DEFAULT NULL,
  `type` int(11) DEFAULT NULL,
  `info` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `explore_reward` */

DROP TABLE IF EXISTS `explore_reward`;

CREATE TABLE `explore_reward` (
  `player_id` int(11) NOT NULL,
  `create_time` int(11) DEFAULT NULL,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `explore_team` */

DROP TABLE IF EXISTS `explore_team`;

CREATE TABLE `explore_team` (
  `leader_id` int(11) NOT NULL,
  `total_score` int(11) DEFAULT NULL,
  `floor` int(11) DEFAULT NULL,
  `step` int(11) DEFAULT NULL,
  PRIMARY KEY (`leader_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `festival_gift` */

DROP TABLE IF EXISTS `festival_gift`;

CREATE TABLE `festival_gift` (
  `player_id` int(11) NOT NULL,
  `presented_friends` text,
  `start_time` int(11) DEFAULT NULL,
  `gifts` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `free_gift` */

DROP TABLE IF EXISTS `free_gift`;

CREATE TABLE `free_gift` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sender_id` varchar(100) DEFAULT NULL,
  `receiver_id` varchar(100) DEFAULT NULL,
  `op_mode` varchar(10) DEFAULT NULL,
  `gift_id` varchar(50) DEFAULT NULL,
  `send_time` int(11) DEFAULT NULL,
  `verify_code` varchar(100) DEFAULT NULL,
  `is_send_back` int(11) DEFAULT '0',
  `is_accept` int(11) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `gift_event_log` */

DROP TABLE IF EXISTS `gift_event_log`;

CREATE TABLE `gift_event_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `player_id` int(11) DEFAULT NULL,
  `info` varchar(255) DEFAULT NULL,
  `create_time` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `invite` */

DROP TABLE IF EXISTS `invite`;

CREATE TABLE `invite` (
  `invite_id` varchar(100) NOT NULL,
  `accepter_ids` text,
  `sys_reward_times` int(11) DEFAULT '0',
  PRIMARY KEY (`invite_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `item1` */

DROP TABLE IF EXISTS `item1`;

CREATE TABLE `item1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `x` int(11) DEFAULT NULL,
  `y` int(11) DEFAULT NULL,
  `item_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `created_time` int(11) NOT NULL,
  `detail` varchar(255) DEFAULT NULL,
  `habitat` INT(11) DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `level_task` */

DROP TABLE IF EXISTS `level_task`;

CREATE TABLE `level_task` (
  `player_id` int(11) NOT NULL,
  `task_info` text,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `pay` */

DROP TABLE IF EXISTS `pay`;

CREATE TABLE `pay` (
  `order_id` bigint(20) NOT NULL,
  `sns_id` varchar(100) DEFAULT NULL,
  `currency` varchar(50) DEFAULT NULL,
  `amount` int(11) DEFAULT NULL,
  `pay_time` int(11) DEFAULT NULL,
  `kb` int(11) DEFAULT NULL,
  `is_done` int(11) DEFAULT '0',
  PRIMARY KEY (`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `player` */

DROP TABLE IF EXISTS `player`;

CREATE TABLE `player` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sns_id` varchar(255) NOT NULL,
  `gb` int(11) NOT NULL DEFAULT '0',
  `kb` int(11) NOT NULL DEFAULT '0',
  `energy` int(11) NOT NULL DEFAULT '0',
  `vip` int(11) NOT NULL DEFAULT '0',
  `regist_time` int(11) DEFAULT '0',
  `last_login_time` int(11) DEFAULT NULL,
  `last_energy_time` int(11) DEFAULT NULL,
  `expand` int(11) DEFAULT '0',
  `exp` int(11) DEFAULT '0',
  `level` int(11) DEFAULT '1',
  `title_id` int(11) DEFAULT '0',
  `titles` varchar(255) DEFAULT '',
  `guide` int(11) DEFAULT '0',
  `login_times` int(11) DEFAULT '0',
  `free_times` int(11) DEFAULT '0',
  `system_reward` varchar(255) DEFAULT '',
  `lottery_num` int(11) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `sns_id` (`sns_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `produce` */

DROP TABLE IF EXISTS `produce`;

CREATE TABLE `produce` (
  `user_id` int(11) NOT NULL,
  `info` text,
  `level` INT(11) DEFAULT '1',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `prop` */

DROP TABLE IF EXISTS `prop`;

CREATE TABLE `prop` (
  `user_id` int(11) NOT NULL,
  `props` text,
  `capacity` int(11) DEFAULT '120',
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `search_team` */

DROP TABLE IF EXISTS `search_team`;

CREATE TABLE `search_team` (
  `user_id` int(11) DEFAULT NULL,
  `last_start_time` int(11) DEFAULT NULL,
  `area` int(11) DEFAULT '1',
  `friends` text,
  `type` INT(11) DEFAULT NULL,
  `number` INT(11) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `session` */

DROP TABLE IF EXISTS `session`;

CREATE TABLE `session` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `create_time` int(11) DEFAULT NULL,
  `skey` varchar(255) DEFAULT NULL,
  `sns_id` varchar(255) DEFAULT NULL,
  `player_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `transaction` */

DROP TABLE IF EXISTS `transaction`;

CREATE TABLE `transaction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `price` int(11) NOT NULL DEFAULT '0',
  `number` int(11) NOT NULL DEFAULT '0',
  `user_id` int(11) NOT NULL,
  `prop_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `treasure` */

DROP TABLE IF EXISTS `treasure`;

CREATE TABLE `treasure` (
  `player_id` int(11) NOT NULL,
  `start_time` int(11) DEFAULT '0',
  `status` int(11) DEFAULT '0',
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `user_box` */

DROP TABLE IF EXISTS `user_box`;

CREATE TABLE `user_box` (
  `owner_id` varchar(100) NOT NULL,
  `helper_ids` text,
  `is_open` int(11) DEFAULT NULL,
  `start_time` int(11) DEFAULT NULL,
  PRIMARY KEY (`owner_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `visit_friend` */

DROP TABLE IF EXISTS `visit_friend`;

CREATE TABLE `visit_friend` (
  `player_id` int(11) NOT NULL,
  `first_visit` text,
  `daily_visit` text,
  `visit_time` int(11) DEFAULT NULL,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `life_tree` */

DROP TABLE IF EXISTS `life_tree`;

CREATE TABLE `life_tree` (
  `player_id` INT(11) NOT NULL,
  `info` VARCHAR(255) DEFAULT NULL,
  `level` INT(1) DEFAULT NULL,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `purchase` */

DROP TABLE IF EXISTS `purchase`;

CREATE TABLE `purchase` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `price` INT(11) DEFAULT '0',
  `number` INT(11) DEFAULT '0',
  `user_id` INT(11) DEFAULT NULL,
  `prop_id` INT(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `purchase_event_log` */

DROP TABLE IF EXISTS `purchase_event_log`;

CREATE TABLE `purchase_event_log` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `type` INT(11) DEFAULT NULL,
  `user_id` INT(11) DEFAULT NULL,
  `info` VARCHAR(255) DEFAULT NULL,
  `create_time` INT(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Table structure for table `interval_box` */

DROP TABLE IF EXISTS `interval_box`;

CREATE TABLE `interval_box` (
  `player_id` INT(11) NOT NULL,
  `op_time` INT(11) DEFAULT NULL,
  `number` INT(11) DEFAULT '0',
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
