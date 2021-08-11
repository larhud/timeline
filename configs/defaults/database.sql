-- MySQL dump 10.13  Distrib 5.7.21, for Linux (x86_64)
--
-- Host: localhost    Database: powercms
-- ------------------------------------------------------
-- Server version	5.7.21-0ubuntu0.16.04.1

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
-- Table structure for table `admin_tools_dashboard_preferences`
--

DROP TABLE IF EXISTS `admin_tools_dashboard_preferences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_tools_dashboard_preferences` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `data` longtext COLLATE utf8_unicode_ci NOT NULL,
  `dashboard_id` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_tools_dashboard_prefer_dashboard_id_374bce90a8a4eefc_uniq` (`dashboard_id`,`user_id`),
  KEY `admin_tools_dashboard_preferences_fbfc09f1` (`user_id`),
  CONSTRAINT `user_id_refs_id_f8487376` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_tools_dashboard_preferences`
--

LOCK TABLES `admin_tools_dashboard_preferences` WRITE;
/*!40000 ALTER TABLE `admin_tools_dashboard_preferences` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_tools_dashboard_preferences` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_tools_menu_bookmark`
--

DROP TABLE IF EXISTS `admin_tools_menu_bookmark`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `admin_tools_menu_bookmark` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `url` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `title` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_tools_menu_bookmark_fbfc09f1` (`user_id`),
  CONSTRAINT `user_id_refs_id_63b2844f` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_tools_menu_bookmark`
--

LOCK TABLES `admin_tools_menu_bookmark` WRITE;
/*!40000 ALTER TABLE `admin_tools_menu_bookmark` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_tools_menu_bookmark` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_bda51c3c` (`group_id`),
  KEY `auth_group_permissions_1e014c8f` (`permission_id`),
  CONSTRAINT `group_id_refs_id_3cea63fe` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `permission_id_refs_id_a7792de1` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_e4470c6e` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_728de91f` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add user',3,'add_user'),(8,'Can change user',3,'change_user'),(9,'Can delete user',3,'delete_user'),(10,'Can add content type',4,'add_contenttype'),(11,'Can change content type',4,'change_contenttype'),(12,'Can delete content type',4,'delete_contenttype'),(13,'Can add session',5,'add_session'),(14,'Can change session',5,'change_session'),(15,'Can delete session',5,'delete_session'),(16,'Can add log entry',6,'add_logentry'),(17,'Can change log entry',6,'change_logentry'),(18,'Can delete log entry',6,'delete_logentry'),(19,'Can add migration history',7,'add_migrationhistory'),(20,'Can change migration history',7,'change_migrationhistory'),(21,'Can delete migration history',7,'delete_migrationhistory'),(22,'Can add Histórico de Operações',8,'add_logentry'),(23,'Can change Histórico de Operações',8,'change_logentry'),(24,'Can delete Histórico de Operações',8,'delete_logentry'),(25,'Can add bookmark',9,'add_bookmark'),(26,'Can change bookmark',9,'change_bookmark'),(27,'Can delete bookmark',9,'delete_bookmark'),(28,'Can add dashboard preferences',10,'add_dashboardpreferences'),(29,'Can change dashboard preferences',10,'change_dashboardpreferences'),(30,'Can delete dashboard preferences',10,'delete_dashboardpreferences'),(31,'Can add user admin config',11,'add_useradminconfig'),(32,'Can change user admin config',11,'change_useradminconfig'),(33,'Can delete user admin config',11,'delete_useradminconfig'),(34,'Can add Artigo',12,'add_article'),(35,'Can change Artigo',12,'change_article'),(36,'Can delete Artigo',12,'delete_article'),(37,'Administrar artigos',12,'manage_articles'),(38,'Can add Atributo do Artigo',13,'add_articleattribute'),(39,'Can change Atributo do Artigo',13,'change_articleattribute'),(40,'Can delete Atributo do Artigo',13,'delete_articleattribute'),(41,'Can add Versão do Artigo',14,'add_articlearchive'),(42,'Can change Versão do Artigo',14,'change_articlearchive'),(43,'Can delete Versão do Artigo',14,'delete_articlearchive'),(44,'Can add Comentário',15,'add_articlecomment'),(45,'Can change Comentário',15,'change_articlecomment'),(46,'Can delete Comentário',15,'delete_articlecomment'),(47,'Can add menu',16,'add_menu'),(48,'Can change menu',16,'change_menu'),(49,'Can delete menu',16,'delete_menu'),(50,'Can add Seção',17,'add_section'),(51,'Can change Seção',17,'change_section'),(52,'Can delete Seção',17,'delete_section'),(53,'Can add Artigo da seção',18,'add_sectionitem'),(54,'Can change Artigo da seção',18,'change_sectionitem'),(55,'Can delete Artigo da seção',18,'delete_sectionitem'),(56,'Can add Permissão',19,'add_permissao'),(57,'Can change Permissão',19,'change_permissao'),(58,'Can delete Permissão',19,'delete_permissao'),(59,'Can add Tipo de Grupo',20,'add_grouptype'),(60,'Can change Tipo de Grupo',20,'change_grouptype'),(61,'Can delete Tipo de Grupo',20,'delete_grouptype'),(62,'Can add Item',21,'add_groupitem'),(63,'Can change Item',21,'change_groupitem'),(64,'Can delete Item',21,'delete_groupitem'),(65,'Can add Migração de URL',22,'add_urlmigrate'),(66,'Can change Migração de URL',22,'change_urlmigrate'),(67,'Can delete Migração de URL',22,'delete_urlmigrate'),(68,'Can add Arquivo para download',23,'add_filedownload'),(69,'Can change Arquivo para download',23,'change_filedownload'),(70,'Can delete Arquivo para download',23,'delete_filedownload'),(71,'Can add email agendado',24,'add_emailagendado'),(72,'Can change email agendado',24,'change_emailagendado'),(73,'Can delete email agendado',24,'delete_emailagendado'),(74,'Can add Parâmetro do Site',25,'add_recurso'),(75,'Can change Parâmetro do Site',25,'change_recurso'),(76,'Can delete Parâmetro do Site',25,'delete_recurso'),(77,'Can add Temas',26,'add_theme'),(78,'Can change Temas',26,'change_theme'),(79,'Can delete Temas',26,'delete_theme'),(80,'Can add url not found',27,'add_urlnotfound'),(81,'Can change url not found',27,'change_urlnotfound'),(82,'Can delete url not found',27,'delete_urlnotfound'),(83,'Can add contato',28,'add_contato'),(84,'Can change contato',28,'change_contato'),(85,'Can delete contato',28,'delete_contato'),(86,'Can add source',29,'add_source'),(87,'Can change source',29,'change_source'),(88,'Can delete source',29,'delete_source'),(89,'Can add thumbnail',30,'add_thumbnail'),(90,'Can change thumbnail',30,'change_thumbnail'),(91,'Can delete thumbnail',30,'delete_thumbnail'),(92,'Can add thumbnail dimensions',31,'add_thumbnaildimensions'),(93,'Can change thumbnail dimensions',31,'change_thumbnaildimensions'),(94,'Can delete thumbnail dimensions',31,'delete_thumbnaildimensions');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `first_name` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `last_name` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(75) COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(128) COLLATE utf8_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'admin','','','admin@admin.com','pbkdf2_sha256$10000$nBdFBKFcACaP$MyzdnXSAl8khddpSSPXn1EmZhQRZC0ZRrRTLRhnybnI=',1,1,1,'2018-04-05 11:12:48','2018-04-05 11:12:48');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_fbfc09f1` (`user_id`),
  KEY `auth_user_groups_bda51c3c` (`group_id`),
  CONSTRAINT `group_id_refs_id_f0ee9890` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `user_id_refs_id_831107f1` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_fbfc09f1` (`user_id`),
  KEY `auth_user_user_permissions_1e014c8f` (`permission_id`),
  CONSTRAINT `permission_id_refs_id_67e79cb` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `user_id_refs_id_f2045483` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_article`
--

DROP TABLE IF EXISTS `cms_article`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_article` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `slug` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `header` longtext COLLATE utf8_unicode_ci,
  `content` longtext COLLATE utf8_unicode_ci,
  `author_id` int(11) NOT NULL,
  `keywords` longtext COLLATE utf8_unicode_ci,
  `created_at` date NOT NULL,
  `updated_at` date NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `views` int(11) NOT NULL,
  `conversions` int(11) NOT NULL,
  `allow_comments` varchar(1) COLLATE utf8_unicode_ci NOT NULL,
  `og_title` varchar(250) COLLATE utf8_unicode_ci,
  `og_image` varchar(100) COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `cms_article_cc846901` (`author_id`),
  CONSTRAINT `author_id_refs_id_7ed64069` FOREIGN KEY (`author_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_article`
--

LOCK TABLES `cms_article` WRITE;
/*!40000 ALTER TABLE `cms_article` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_article` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_articlearchive`
--

DROP TABLE IF EXISTS `cms_articlearchive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_articlearchive` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `article_id` int(11) NOT NULL,
  `header` longtext COLLATE utf8_unicode_ci,
  `content` longtext COLLATE utf8_unicode_ci,
  `updated_at` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cms_articlearchive_30525a19` (`article_id`),
  KEY `cms_articlearchive_fbfc09f1` (`user_id`),
  CONSTRAINT `article_id_refs_id_88d040da` FOREIGN KEY (`article_id`) REFERENCES `cms_article` (`id`),
  CONSTRAINT `user_id_refs_id_1df82b74` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_articlearchive`
--

LOCK TABLES `cms_articlearchive` WRITE;
/*!40000 ALTER TABLE `cms_articlearchive` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_articlearchive` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_articleattribute`
--

DROP TABLE IF EXISTS `cms_articleattribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_articleattribute` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `article_id` int(11) NOT NULL,
  `attrib` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `value` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cms_articleattribute_30525a19` (`article_id`),
  CONSTRAINT `article_id_refs_id_8ddf10d6` FOREIGN KEY (`article_id`) REFERENCES `cms_article` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_articleattribute`
--

LOCK TABLES `cms_articleattribute` WRITE;
/*!40000 ALTER TABLE `cms_articleattribute` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_articleattribute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_articlecomment`
--

DROP TABLE IF EXISTS `cms_articlecomment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_articlecomment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `article_id` int(11) NOT NULL,
  `created_at` date NOT NULL,
  `author` varchar(60) COLLATE utf8_unicode_ci NOT NULL,
  `comment` longtext COLLATE utf8_unicode_ci NOT NULL,
  `active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cms_articlecomment_30525a19` (`article_id`),
  CONSTRAINT `article_id_refs_id_16a4cc0f` FOREIGN KEY (`article_id`) REFERENCES `cms_article` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_articlecomment`
--

LOCK TABLES `cms_articlecomment` WRITE;
/*!40000 ALTER TABLE `cms_articlecomment` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_articlecomment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_emailagendado`
--

DROP TABLE IF EXISTS `cms_emailagendado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_emailagendado` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject` varchar(90) COLLATE utf8_unicode_ci NOT NULL,
  `status` varchar(1) COLLATE utf8_unicode_ci NOT NULL,
  `date` datetime NOT NULL,
  `to` longtext COLLATE utf8_unicode_ci NOT NULL,
  `html` longtext COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_emailagendado`
--

LOCK TABLES `cms_emailagendado` WRITE;
/*!40000 ALTER TABLE `cms_emailagendado` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_emailagendado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_filedownload`
--

DROP TABLE IF EXISTS `cms_filedownload`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_filedownload` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` char(32) COLLATE utf8_unicode_ci NOT NULL,
  `file` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `count` int(11) NOT NULL,
  `expires_at` datetime DEFAULT NULL,
  `create_article` tinyint(1) NOT NULL,
  `article_id` int(11),
  `title` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`),
  KEY `cms_filedownload_30525a19` (`article_id`),
  CONSTRAINT `article_id_refs_id_8d5a59aa` FOREIGN KEY (`article_id`) REFERENCES `cms_article` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_filedownload`
--

LOCK TABLES `cms_filedownload` WRITE;
/*!40000 ALTER TABLE `cms_filedownload` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_filedownload` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_groupitem`
--

DROP TABLE IF EXISTS `cms_groupitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_groupitem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `grouptype_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cms_groupitem_7591298` (`grouptype_id`),
  KEY `cms_groupitem_bda51c3c` (`group_id`),
  CONSTRAINT `group_id_refs_id_8cd7044c` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `grouptype_id_refs_id_1972805e` FOREIGN KEY (`grouptype_id`) REFERENCES `cms_grouptype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_groupitem`
--

LOCK TABLES `cms_groupitem` WRITE;
/*!40000 ALTER TABLE `cms_groupitem` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_groupitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_grouptype`
--

DROP TABLE IF EXISTS `cms_grouptype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_grouptype` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) COLLATE utf8_unicode_ci NOT NULL,
  `order` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_grouptype`
--

LOCK TABLES `cms_grouptype` WRITE;
/*!40000 ALTER TABLE `cms_grouptype` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_grouptype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_menu`
--

DROP TABLE IF EXISTS `cms_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_menu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `link` varchar(250) COLLATE utf8_unicode_ci DEFAULT NULL,
  `section_id` int(11) DEFAULT NULL,
  `article_id` int(11) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `lft` int(10) unsigned NOT NULL,
  `rght` int(10) unsigned NOT NULL,
  `tree_id` int(10) unsigned NOT NULL,
  `level` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cms_menu_63f17a16` (`parent_id`),
  KEY `cms_menu_c007bd5a` (`section_id`),
  KEY `cms_menu_30525a19` (`article_id`),
  KEY `cms_menu_42b06ff6` (`lft`),
  KEY `cms_menu_91543e5a` (`rght`),
  KEY `cms_menu_efd07f28` (`tree_id`),
  KEY `cms_menu_2a8f42e8` (`level`),
  CONSTRAINT `article_id_refs_id_a71689e7` FOREIGN KEY (`article_id`) REFERENCES `cms_article` (`id`),
  CONSTRAINT `parent_id_refs_id_4e6bae65` FOREIGN KEY (`parent_id`) REFERENCES `cms_menu` (`id`),
  CONSTRAINT `section_id_refs_id_ae863cb8` FOREIGN KEY (`section_id`) REFERENCES `cms_section` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_menu`
--

LOCK TABLES `cms_menu` WRITE;
/*!40000 ALTER TABLE `cms_menu` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_permissao`
--

DROP TABLE IF EXISTS `cms_permissao`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_permissao` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `section_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cms_permissao_c007bd5a` (`section_id`),
  KEY `cms_permissao_bda51c3c` (`group_id`),
  CONSTRAINT `group_id_refs_id_a67d560b` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `section_id_refs_id_db88cedf` FOREIGN KEY (`section_id`) REFERENCES `cms_section` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_permissao`
--

LOCK TABLES `cms_permissao` WRITE;
/*!40000 ALTER TABLE `cms_permissao` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_permissao` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_recurso`
--

DROP TABLE IF EXISTS `cms_recurso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_recurso` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `recurso` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `valor` longtext COLLATE utf8_unicode_ci,
  `ativo` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `recurso` (`recurso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_recurso`
--

LOCK TABLES `cms_recurso` WRITE;
/*!40000 ALTER TABLE `cms_recurso` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_recurso` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_section`
--

DROP TABLE IF EXISTS `cms_section`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_section` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `slug` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `header` longtext COLLATE utf8_unicode_ci,
  `keywords` longtext COLLATE utf8_unicode_ci,
  `views` int(11) NOT NULL,
  `conversions` int(11) NOT NULL,
  `order` int(10) unsigned NOT NULL,
  `template` varchar(250) COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `cms_section_a951d5d6` (`slug`),
  KEY `cms_section_c45f7136` (`order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_section`
--

LOCK TABLES `cms_section` WRITE;
/*!40000 ALTER TABLE `cms_section` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_section` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_sectionitem`
--

DROP TABLE IF EXISTS `cms_sectionitem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_sectionitem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `section_id` int(11) NOT NULL,
  `article_id` int(11) NOT NULL,
  `order` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `cms_sectionitem_c007bd5a` (`section_id`),
  KEY `cms_sectionitem_30525a19` (`article_id`),
  KEY `cms_sectionitem_c45f7136` (`order`),
  CONSTRAINT `article_id_refs_id_9fa7ab07` FOREIGN KEY (`article_id`) REFERENCES `cms_article` (`id`),
  CONSTRAINT `section_id_refs_id_86ec43d6` FOREIGN KEY (`section_id`) REFERENCES `cms_section` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_sectionitem`
--

LOCK TABLES `cms_sectionitem` WRITE;
/*!40000 ALTER TABLE `cms_sectionitem` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_sectionitem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_theme`
--

DROP TABLE IF EXISTS `cms_theme`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_theme` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(60) COLLATE utf8_unicode_ci NOT NULL,
  `description` longtext COLLATE utf8_unicode_ci,
  `active` tinyint(1) NOT NULL,
  `path` varchar(256) COLLATE utf8_unicode_ci NOT NULL,
  `path_name` varchar(60) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `path_name` (`path_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_theme`
--

LOCK TABLES `cms_theme` WRITE;
/*!40000 ALTER TABLE `cms_theme` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_theme` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_urlmigrate`
--

DROP TABLE IF EXISTS `cms_urlmigrate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_urlmigrate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `old_url` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `new_url` varchar(250) COLLATE utf8_unicode_ci NOT NULL,
  `dtupdate` datetime NOT NULL,
  `views` int(11) NOT NULL,
  `redirect_type` varchar(1) COLLATE utf8_unicode_ci NOT NULL,
  `obs` longtext COLLATE utf8_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `cms_urlmigrate_427de19` (`old_url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_urlmigrate`
--

LOCK TABLES `cms_urlmigrate` WRITE;
/*!40000 ALTER TABLE `cms_urlmigrate` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_urlmigrate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cms_urlnotfound`
--

DROP TABLE IF EXISTS `cms_urlnotfound`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cms_urlnotfound` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `count` bigint(20) NOT NULL,
  `created_at` datetime NOT NULL,
  `update_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cms_urlnotfound`
--

LOCK TABLES `cms_urlnotfound` WRITE;
/*!40000 ALTER TABLE `cms_urlnotfound` DISABLE KEYS */;
/*!40000 ALTER TABLE `cms_urlnotfound` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `crm_contato`
--

DROP TABLE IF EXISTS `crm_contato`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `crm_contato` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nome` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `email` varchar(75) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `crm_contato`
--

LOCK TABLES `crm_contato` WRITE;
/*!40000 ALTER TABLE `crm_contato` DISABLE KEYS */;
/*!40000 ALTER TABLE `crm_contato` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext COLLATE utf8_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_fbfc09f1` (`user_id`),
  KEY `django_admin_log_e4470c6e` (`content_type_id`),
  CONSTRAINT `content_type_id_refs_id_288599e6` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `user_id_refs_id_c8665aa` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `app_label` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'permission','auth','permission'),(2,'group','auth','group'),(3,'user','auth','user'),(4,'content type','contenttypes','contenttype'),(5,'session','sessions','session'),(6,'log entry','admin','logentry'),(7,'migration history','south','migrationhistory'),(8,'Histórico de Operações','filebrowser','logentry'),(9,'bookmark','menu','bookmark'),(10,'dashboard preferences','dashboard','dashboardpreferences'),(11,'user admin config','poweradmin','useradminconfig'),(12,'Artigo','cms','article'),(13,'Atributo do Artigo','cms','articleattribute'),(14,'Versão do Artigo','cms','articlearchive'),(15,'Comentário','cms','articlecomment'),(16,'menu','cms','menu'),(17,'Seção','cms','section'),(18,'Artigo da seção','cms','sectionitem'),(19,'Permissão','cms','permissao'),(20,'Tipo de Grupo','cms','grouptype'),(21,'Item','cms','groupitem'),(22,'Migração de URL','cms','urlmigrate'),(23,'Arquivo para download','cms','filedownload'),(24,'email agendado','cms','emailagendado'),(25,'Parâmetro do Site','cms','recurso'),(26,'Temas','cms','theme'),(27,'url not found','cms','urlnotfound'),(28,'contato','crm','contato'),(29,'source','easy_thumbnails','source'),(30,'thumbnail','easy_thumbnails','thumbnail'),(31,'thumbnail dimensions','easy_thumbnails','thumbnaildimensions');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8_unicode_ci NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_c25c2c28` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `easy_thumbnails_source`
--

DROP TABLE IF EXISTS `easy_thumbnails_source`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `easy_thumbnails_source` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `modified` datetime NOT NULL,
  `storage_hash` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `easy_thumbnails_source_name_7549c98cc6dd6969_uniq` (`name`,`storage_hash`),
  KEY `easy_thumbnails_source_52094d6e` (`name`),
  KEY `easy_thumbnails_source_3a997c55` (`storage_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `easy_thumbnails_source`
--

LOCK TABLES `easy_thumbnails_source` WRITE;
/*!40000 ALTER TABLE `easy_thumbnails_source` DISABLE KEYS */;
/*!40000 ALTER TABLE `easy_thumbnails_source` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `easy_thumbnails_thumbnail`
--

DROP TABLE IF EXISTS `easy_thumbnails_thumbnail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `easy_thumbnails_thumbnail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `modified` datetime NOT NULL,
  `source_id` int(11) NOT NULL,
  `storage_hash` varchar(40) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `easy_thumbnails_thumbnail_source_id_1f50d53db8191480_uniq` (`source_id`,`name`,`storage_hash`),
  KEY `easy_thumbnails_thumbnail_89f89e85` (`source_id`),
  KEY `easy_thumbnails_thumbnail_52094d6e` (`name`),
  KEY `easy_thumbnails_thumbnail_3a997c55` (`storage_hash`),
  CONSTRAINT `source_id_refs_id_5bffe8f5` FOREIGN KEY (`source_id`) REFERENCES `easy_thumbnails_source` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `easy_thumbnails_thumbnail`
--

LOCK TABLES `easy_thumbnails_thumbnail` WRITE;
/*!40000 ALTER TABLE `easy_thumbnails_thumbnail` DISABLE KEYS */;
/*!40000 ALTER TABLE `easy_thumbnails_thumbnail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `easy_thumbnails_thumbnaildimensions`
--

DROP TABLE IF EXISTS `easy_thumbnails_thumbnaildimensions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `easy_thumbnails_thumbnaildimensions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `thumbnail_id` int(11) NOT NULL,
  `width` int(10) unsigned DEFAULT NULL,
  `height` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `thumbnail_id` (`thumbnail_id`),
  CONSTRAINT `thumbnail_id_refs_id_f939906e` FOREIGN KEY (`thumbnail_id`) REFERENCES `easy_thumbnails_thumbnail` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `easy_thumbnails_thumbnaildimensions`
--

LOCK TABLES `easy_thumbnails_thumbnaildimensions` WRITE;
/*!40000 ALTER TABLE `easy_thumbnails_thumbnaildimensions` DISABLE KEYS */;
/*!40000 ALTER TABLE `easy_thumbnails_thumbnaildimensions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `filebrowser_logentry`
--

DROP TABLE IF EXISTS `filebrowser_logentry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `filebrowser_logentry` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `object_id` longtext COLLATE utf8_unicode_ci,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `filebrowser_logentry_fbfc09f1` (`user_id`),
  CONSTRAINT `user_id_refs_id_4cb1c97f` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `filebrowser_logentry`
--

LOCK TABLES `filebrowser_logentry` WRITE;
/*!40000 ALTER TABLE `filebrowser_logentry` DISABLE KEYS */;
/*!40000 ALTER TABLE `filebrowser_logentry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `poweradmin_useradminconfig`
--

DROP TABLE IF EXISTS `poweradmin_useradminconfig`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `poweradmin_useradminconfig` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `url_name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `url_full_path` longtext COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `poweradmin_useradminconfig_fbfc09f1` (`user_id`),
  CONSTRAINT `user_id_refs_id_7780801b` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `poweradmin_useradminconfig`
--

LOCK TABLES `poweradmin_useradminconfig` WRITE;
/*!40000 ALTER TABLE `poweradmin_useradminconfig` DISABLE KEYS */;
/*!40000 ALTER TABLE `poweradmin_useradminconfig` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `south_migrationhistory`
--

DROP TABLE IF EXISTS `south_migrationhistory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `south_migrationhistory` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `migration` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `applied` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `south_migrationhistory`
--

LOCK TABLES `south_migrationhistory` WRITE;
/*!40000 ALTER TABLE `south_migrationhistory` DISABLE KEYS */;
INSERT INTO `south_migrationhistory` VALUES (1,'filebrowser','0001_initial','2018-04-05 11:12:55'),(2,'menu','0001_initial','2018-04-05 11:12:56'),(3,'dashboard','0001_initial','2018-04-05 11:12:56'),(4,'dashboard','0002_auto__add_field_dashboardpreferences_dashboard_id','2018-04-05 11:12:56'),(5,'dashboard','0003_auto__add_unique_dashboardpreferences_dashboard_id_user','2018-04-05 11:12:56'),(6,'poweradmin','0001_initial','2018-04-05 11:12:56'),(7,'cms','0001_initial','2018-04-05 11:12:57'),(8,'cms','0002_auto__del_field_section_site__del_field_article_site__del_field_filedo','2018-04-05 11:12:57'),(9,'cms','0003_auto__add_field_article_allow_comments','2018-04-05 11:12:57'),(10,'cms','0004_auto__add_articlecomment','2018-04-05 11:12:58'),(11,'cms','0005_auto__add_emailagendado__add_recurso','2018-04-05 11:12:58'),(12,'cms','0006_auto__chg_field_filedownload_file__del_index_filedownload_file','2018-04-05 11:12:58'),(13,'cms','0007_auto__add_theme','2018-04-05 11:12:58'),(14,'cms','0008_auto__add_field_theme_path_name__chg_field_theme_name__del_unique_them','2018-04-05 11:12:58'),(15,'cms','0009_auto__add_permissao','2018-04-05 11:12:58'),(16,'cms','0010_auto__add_field_articlecomment_active','2018-04-05 11:12:58'),(17,'cms','0011_auto__chg_field_theme_path','2018-04-05 11:12:58'),(18,'cms','0012_auto__add_field_section_order','2018-04-05 11:12:58'),(19,'cms','0013_auto__add_grouptype__add_groupitem','2018-04-05 11:12:59'),(20,'cms','0014_auto__add_field_filedownload_create_article__add_field_filedownload_ar','2018-04-05 11:12:59'),(21,'cms','0015_auto__add_field_filedownload_title','2018-04-05 11:12:59'),(22,'cms','0016_auto__chg_field_theme_path__add_field_section_template','2018-04-05 11:12:59'),(23,'cms','0017_auto__add_articleattribute','2018-04-05 11:12:59'),(24,'cms','0018_auto__add_field_article_og_title__add_field_article_og_image','2018-04-05 11:12:59'),(25,'cms','0019_auto__add_urlnotfound__chg_field_theme_path','2018-04-05 11:12:59'),(26,'crm','0001_initial','2018-04-05 11:13:00'),(27,'easy_thumbnails','0001_initial','2018-04-05 11:13:00'),(28,'easy_thumbnails','0002_filename_indexes','2018-04-05 11:13:00'),(29,'easy_thumbnails','0003_auto__add_storagenew','2018-04-05 11:13:00'),(30,'easy_thumbnails','0004_auto__add_field_source_storage_new__add_field_thumbnail_storage_new','2018-04-05 11:13:00'),(31,'easy_thumbnails','0005_storage_fks_null','2018-04-05 11:13:00'),(32,'easy_thumbnails','0006_copy_storage','2018-04-05 11:13:00'),(33,'easy_thumbnails','0007_storagenew_fks_not_null','2018-04-05 11:13:00'),(34,'easy_thumbnails','0008_auto__del_field_source_storage__del_field_thumbnail_storage','2018-04-05 11:13:01'),(35,'easy_thumbnails','0009_auto__del_storage','2018-04-05 11:13:01'),(36,'easy_thumbnails','0010_rename_storage','2018-04-05 11:13:01'),(37,'easy_thumbnails','0011_auto__add_field_source_storage_hash__add_field_thumbnail_storage_hash','2018-04-05 11:13:01'),(38,'easy_thumbnails','0012_build_storage_hashes','2018-04-05 11:13:01'),(39,'easy_thumbnails','0013_auto__del_storage__del_field_source_storage__del_field_thumbnail_stora','2018-04-05 11:13:01'),(40,'easy_thumbnails','0014_auto__add_unique_source_name_storage_hash__add_unique_thumbnail_name_s','2018-04-05 11:13:01'),(41,'easy_thumbnails','0015_auto__del_unique_thumbnail_name_storage_hash__add_unique_thumbnail_sou','2018-04-05 11:13:01'),(42,'easy_thumbnails','0016_auto__add_thumbnaildimensions','2018-04-05 11:13:01');
/*!40000 ALTER TABLE `south_migrationhistory` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2018-04-05  8:13:21
