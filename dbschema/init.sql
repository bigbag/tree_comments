CREATE TABLE `user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_unique` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `entity` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `type` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_type_unique` (`name`,`type`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `comments` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `parent_id` bigint(19) DEFAULT NULL,
  `level` int(11) NOT NULL,
  `patch` varchar(256) NOT NULL,
  `has_children` tinyint(1) NOT NULL DEFAULT '0',
  `user_id` bigint(20) NOT NULL,
  `entity_id` bigint(20) NOT NULL,
  `text` text NOT NULL,
  `create_date` datetime DEFAULT NULL,
  `update_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_id_key` (`parent_id`),
  KEY `level_key` (`level`),
  KEY `entity_id_key` (`entity_id`),
  KEY `user_id_key` (`user_id`),
  KEY `patch_key` (`patch`(255)),
  CONSTRAINT `id_parent_id_foreign_key` FOREIGN KEY (`parent_id`) REFERENCES `comments` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;