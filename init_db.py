SCHEMA=[
    '''
/* CREATE SCHEMA `xmcp_fire_bird` DEFAULT CHARACTER SET utf8mb4; */

CREATE TABLE `users` (
  `uid` int NOT NULL AUTO_INCREMENT,
  `user_token` varchar(100) NOT NULL,
  `unique_id` varchar(40) NOT NULL,
  `name` varchar(40) DEFAULT NULL,
  `ring` int NOT NULL,
  `splash_index` int(11) NOT NULL,
  `remarks` text NOT NULL,
  `settings` mediumtext NOT NULL,
  `last_refresh` bigint DEFAULT NULL,
  PRIMARY KEY (`uid`),
  UNIQUE KEY `k_user_token` (`user_token`),
  UNIQUE KEY `k_unique_id` (`unique_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ''',
    '''
CREATE TABLE `zones` (
  `zid` int NOT NULL AUTO_INCREMENT,
  `next_zid` int DEFAULT NULL,
  `name` varchar(80) NOT NULL,
  `uid` int NOT NULL,
  PRIMARY KEY (`zid`),
  KEY `k_uid` (`uid`),
  CONSTRAINT `fk_z_uid` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ''',
    '''
CREATE TABLE `projects` (
  `pid` int NOT NULL AUTO_INCREMENT,
  `next_pid` int DEFAULT NULL,
  `name` varchar(80) NOT NULL,
  `uid` int,
  `zid` int,
  `extpid` int DEFAULT NULL,
  `share_hash` varchar(60) DEFAULT NULL,
  `share_name` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`pid`),
  KEY `k_zid` (`zid`),
  KEY `k_uid` (`uid`),
  UNIQUE KEY `k_share_hash` (`share_hash`),
  FULLTEXT KEY `k_share_name` (`share_name`) WITH PARSER ngram,
  CONSTRAINT `fk_p_uid` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_p_zid` FOREIGN KEY (`zid`) REFERENCES `zones` (`zid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_p_extpid` FOREIGN KEY (`extpid`) REFERENCES `projects` (`pid`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ''',
    '''
CREATE TABLE `tasks` (
  `tid` int NOT NULL AUTO_INCREMENT,
  `next_tid` int DEFAULT NULL,
  `name` varchar(80) NOT NULL,
  `uid` int,
  `pid` int DEFAULT NULL,
  `status` enum('placeholder','active') NOT NULL DEFAULT 'placeholder',
  `due` bigint DEFAULT NULL, 
  `description` text DEFAULT NULL,
  PRIMARY KEY (`tid`),
  KEY `k_pid` (`pid`),
  KEY `k_uid` (`uid`),
  CONSTRAINT `fk_t_pid` FOREIGN KEY (`pid`) REFERENCES `projects` (`pid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_t_uid` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ''',
    '''
CREATE TABLE `completes` (
  `uid` int NOT NULL,
  `tid` int NOT NULL,
  `completeness` enum('todo','done','highlight','ignored') NOT NULL DEFAULT 'todo',
  `update_timestamp` bigint NOT NULL,
  `description_idx` int DEFAULT NULL,
  PRIMARY KEY (`uid`,`tid`),
  KEY `k_tid` (`tid`),
  KEY `k_uid` (`uid`),
  KEY `k_description_idx` (`tid`, `description_idx`),
  CONSTRAINT `fk_c_tid` FOREIGN KEY (`tid`) REFERENCES `tasks` (`tid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_c_uid` FOREIGN KEY (`uid`) REFERENCES `users` (`uid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ''',
]

def create_tables():
    with app.app_context():
        db=mysql.get_db()
        cur=db.cursor()
        for stmt in SCHEMA:
            cur.execute(stmt)
        db.commit()
        app.logger.info('init db done')

if __name__=='__main__':
    answer=input('Type {CREATE TABLES} to proceed: ')
    assert answer=='CREATE TABLES'

    from mysql import mysql
    from app import app
    create_tables()