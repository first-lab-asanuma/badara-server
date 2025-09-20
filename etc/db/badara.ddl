-- Project Name : noname
-- Date/Time    : 2025/09/21 2:15:08
-- Author       : admin
-- RDBMS Type   : MySQL
-- Application  : A5:SQL Mk-2

-- 定休日
DROP TABLE if exists t_holiday CASCADE;

CREATE TABLE t_holiday (
  id int auto_increment NOT NULL COMMENT '定休日ID'
  , hospital_id int NOT NULL COMMENT '病院ID'
  , holiday_date date NOT NULL COMMENT '定休日'
  , deleted_flag tinyint(1) DEFAULT 0 COMMENT '削除フラグ'
  , created_at datetime DEFAULT CURRENT_TIMESTAMP COMMENT '作成日'
  , created_by varchar(255) COMMENT '作成者'
  , updated_at datetime on update CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '更新日'
  , updated_by varchar(255) COMMENT '更新者'
  , CONSTRAINT t_holiday_PKC PRIMARY KEY (id)
) COMMENT '定休日' ;

-- 予約
DROP TABLE if exists t_reservation CASCADE;

CREATE TABLE t_reservation (
  id int auto_increment NOT NULL COMMENT '予約id'
  , user_id int NOT NULL COMMENT 'ユーザーID'
  , hospital_id int NOT NULL COMMENT '病院ID'
  , reservation_date date NOT NULL COMMENT '予約日'
  , reservation_time time NOT NULL COMMENT '予約時間'
  , cancel_date date COMMENT '予約キャンセル日'
  , treatment text COMMENT '治療内容'
  , deleted_flag tinyint(1) DEFAULT 0 COMMENT '削除フラグ'
  , created_at datetime DEFAULT CURRENT_TIMESTAMP COMMENT '作成日'
  , created_by varchar(255) COMMENT '作成者'
  , updated_at datetime on update CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '更新日'
  , updated_by varchar(255) COMMENT '更新者'
  , CONSTRAINT t_reservation_PKC PRIMARY KEY (id)
) COMMENT '予約' ;

CREATE INDEX FK_Reservation_User
  ON t_reservation(user_id);

-- ユーザー
DROP TABLE if exists t_user CASCADE;

CREATE TABLE t_user (
  id int auto_increment NOT NULL COMMENT 'ユーザーID'
  , hospital_id int NOT NULL COMMENT '病院ID'
  , medical_record_no varchar(255) COMMENT 'カルテ番号'
  , line_id varchar(255) COMMENT 'ラインID'
  , login_id varchar(255) COMMENT 'ログインID'
  , email varchar(255) COMMENT 'メールアドレス'
  , password varchar(255) COMMENT 'パスワード'
  , user_type varchar(50) COMMENT 'ユーザー種類:0:患者, 1:病院担当者'
  , last_name varchar(50) COMMENT '名前（姓）'
  , first_name varchar(50) COMMENT '名前（名）'
  , contact varchar(50) COMMENT '連絡先'
  , deleted_flag tinyint(1) DEFAULT 0 COMMENT '削除フラグ'
  , created_at datetime DEFAULT CURRENT_TIMESTAMP COMMENT '作成日'
  , created_by varchar(255) COMMENT '作成者'
  , updated_at datetime on update CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '更新日'
  , updated_by varchar(255) COMMENT '更新者'
  , CONSTRAINT t_user_PKC PRIMARY KEY (id)
) COMMENT 'ユーザー' ;

-- 病院
DROP TABLE if exists t_hospital CASCADE;

CREATE TABLE t_hospital (
  id int auto_increment NOT NULL COMMENT '病院ID'
  , name varchar(255) NOT NULL COMMENT '病院名'
  , website varchar(255) COMMENT '病院HP_URL'
  , postal_code varchar(20) COMMENT '郵便番号'
  , address varchar(255) COMMENT '住所'
  , phone varchar(20) COMMENT '連絡先'
  , fax varchar(20) COMMENT 'fax'
  , line_qr_code varchar(255) COMMENT 'LINEQRコード'
  , reservation_policy_header text COMMENT '予約ポリシーヘッダー'
  , reservation_policy_body text COMMENT '予約ポリシーボディー'
  , treatment text COMMENT '治療内容'
  , deleted_flag tinyint(1) DEFAULT 0 COMMENT '削除フラグ'
  , created_at datetime DEFAULT CURRENT_TIMESTAMP COMMENT '作成日'
  , created_by varchar(255) COMMENT '作成者'
  , updated_at datetime on update CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '更新日'
  , updated_by varchar(255) COMMENT '更新者'
  , CONSTRAINT t_hospital_PKC PRIMARY KEY (id)
) COMMENT '病院:病院情報' ;

