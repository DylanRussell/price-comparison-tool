

-- ----------------------------
-- Table structure for amazon_products
-- ----------------------------
DROP TABLE IF EXISTS `amazon_products`;
CREATE TABLE `amazon_products` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(2048) CHARACTER SET utf8 DEFAULT NULL,
  `price` varchar(40) DEFAULT NULL,
  `img_url` varchar(255) DEFAULT NULL,
  `product_url` varchar(255) DEFAULT NULL,
  `listing_page_url` varchar(255) DEFAULT NULL,
  `rating` varchar(40) DEFAULT NULL,
  `num_ratings` varchar(50) DEFAULT NULL,
  `asin` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

-- ----------------------------
-- Table structure for categories
-- ----------------------------
DROP TABLE IF EXISTS `categories`;
CREATE TABLE `categories` (
  `retailer` varchar(255) DEFAULT NULL,
  `category` varchar(255) DEFAULT NULL,
  `num_items` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for dollargeneral_products
-- ----------------------------
DROP TABLE IF EXISTS `dollargeneral_products`;
CREATE TABLE `dollargeneral_products` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(2048) DEFAULT NULL,
  `price` varchar(40) DEFAULT NULL,
  `img_url` varchar(255) DEFAULT NULL,
  `department` varchar(255) DEFAULT NULL,
  `external_id` varchar(50) DEFAULT NULL,
  `category` varchar(255) DEFAULT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41081 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for target_products
-- ----------------------------
DROP TABLE IF EXISTS `target_products`;
CREATE TABLE `target_products` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `brand` varchar(255) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `available_in_store` varchar(50) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `available` varchar(50) DEFAULT NULL,
  `description` mediumtext,
  `url` varchar(255) DEFAULT NULL,
  `rating` decimal(10,2) DEFAULT NULL,
  `num_ratings` int(10) DEFAULT NULL,
  `name` mediumtext,
  `img_url` varchar(255) DEFAULT NULL,
  `external_id` varchar(50) DEFAULT NULL,
  `is_range` tinyint(1) NOT NULL DEFAULT '0',
  `upc` varchar(13) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `crawl_num` int(11) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `upc` (`upc`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2931982 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for target_products_unique
-- ----------------------------
DROP TABLE IF EXISTS `target_products_unique`;
CREATE TABLE `target_products_unique` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `brand` varchar(255) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `available_in_store` varchar(50) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `available` varchar(50) DEFAULT NULL,
  `description` mediumtext,
  `url` varchar(255) DEFAULT NULL,
  `rating` decimal(10,2) DEFAULT NULL,
  `num_ratings` int(10) DEFAULT NULL,
  `name` mediumtext,
  `img_url` varchar(255) DEFAULT NULL,
  `external_id` varchar(50) DEFAULT NULL,
  `is_range` tinyint(1) NOT NULL DEFAULT '0',
  `upc` varchar(13) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `crawl_num` int(11) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_id` (`external_id`) USING BTREE,
  KEY `upc` (`upc`) USING BTREE,
  KEY `category` (`category`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=746288 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for walmart_latest_crawl
-- ----------------------------
DROP TABLE IF EXISTS `walmart_latest_crawl`;
CREATE TABLE `walmart_latest_crawl` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(2048) NOT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `img_url` varchar(255) DEFAULT NULL,
  `product_url` varchar(512) DEFAULT NULL,
  `rating` decimal(10,2) DEFAULT NULL,
  `upc` varchar(13) DEFAULT NULL,
  `department` varchar(255) DEFAULT NULL,
  `seller` varchar(255) DEFAULT NULL,
  `num_ratings` int(10) DEFAULT NULL,
  `external_id` varchar(50) DEFAULT NULL,
  `description` mediumtext,
  `category` varchar(105) DEFAULT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `quantity` varchar(50) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `crawl_num` int(10) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unq_product` (`external_id`),
  UNIQUE KEY `unique_id` (`external_id`) USING BTREE,
  KEY `upc` (`upc`) USING BTREE,
  KEY `category` (`category`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=61449850 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for walmart_products
-- ----------------------------
DROP TABLE IF EXISTS `walmart_products`;
CREATE TABLE `walmart_products` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(2048) NOT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `img_url` varchar(255) DEFAULT NULL,
  `product_url` varchar(512) DEFAULT NULL,
  `rating` decimal(10,2) DEFAULT NULL,
  `upc` varchar(40) DEFAULT NULL,
  `department` varchar(255) DEFAULT NULL,
  `seller` varchar(255) DEFAULT NULL,
  `num_ratings` int(10) DEFAULT NULL,
  `external_id` varchar(50) DEFAULT NULL,
  `description` mediumtext,
  `category` varchar(255) DEFAULT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `quantity` varchar(50) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `crawl_num` int(10) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37108384 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for walmart_products_unique
-- ----------------------------
DROP TABLE IF EXISTS `walmart_products_unique`;
CREATE TABLE `walmart_products_unique` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(2048) NOT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `img_url` varchar(255) DEFAULT NULL,
  `product_url` varchar(512) DEFAULT NULL,
  `rating` decimal(10,2) DEFAULT NULL,
  `upc` varchar(13) DEFAULT NULL,
  `department` varchar(255) DEFAULT NULL,
  `seller` varchar(255) DEFAULT NULL,
  `num_ratings` int(10) DEFAULT NULL,
  `external_id` varchar(50) DEFAULT NULL,
  `description` mediumtext,
  `category` varchar(105) DEFAULT NULL,
  `brand` varchar(255) DEFAULT NULL,
  `quantity` varchar(50) DEFAULT NULL,
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `crawl_num` int(10) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `unq_product` (`external_id`),
  KEY `upc` (`upc`) USING BTREE,
  KEY `category` (`category`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=30904197 DEFAULT CHARSET=utf8;
