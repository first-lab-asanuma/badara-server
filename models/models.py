from sqlalchemy import Column, Integer, String, Date, DateTime, Time, Text, Boolean, func
from db.database import Base

class THoliday(Base):
    __tablename__ = 't_holiday'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='定休日ID')
    hospital_id = Column(Integer, nullable=False, comment='病院ID')
    holiday_date = Column(Date, nullable=False, comment='定休日')
    deleted_flag = Column(Boolean, default=False, comment='削除フラグ')
    created_at = Column(DateTime, default=func.now(), comment='作成日')
    created_by = Column(String(255), comment='作成者')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新日')
    updated_by = Column(String(255), comment='更新者')

class TReservation(Base):
    __tablename__ = 't_reservation'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='予約id')
    user_id = Column(Integer, nullable=False, comment='ユーザーID')
    hospital_id = Column(Integer, nullable=False, comment='病院ID')
    reservation_date = Column(Date, nullable=False, comment='予約日')
    reservation_time = Column(Time, nullable=False, comment='予約時間')
    cancel_date = Column(Date, comment='予約キャンセル日')
    treatment = Column(Text, comment='治療内容')
    deleted_flag = Column(Boolean, default=False, comment='削除フラグ')
    created_at = Column(DateTime, default=func.now(), comment='作成日')
    created_by = Column(String(255), comment='作成者')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新日')
    updated_by = Column(String(255), comment='更新者')

class TUser(Base):
    __tablename__ = 't_user'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='ユーザーID')
    hospital_id = Column(Integer, nullable=False, comment='病院ID')
    medical_record_no = Column(String(255), comment='カルテ番号')
    line_id = Column(String(255), comment='ラインID')
    login_id = Column(String(255), comment='ログインID')
    email = Column(String(255), comment='メールアドレス')
    password = Column(String(255), comment='パスワード')
    user_type = Column(String(50), comment='ユーザー種類:0:患者, 1:病院担当者')
    last_name = Column(String(50), comment='名前（姓）')
    first_name = Column(String(50), comment='名前（名）')
    contact = Column(String(50), comment='連絡先')
    deleted_flag = Column(Boolean, default=False, comment='削除フラグ')
    created_at = Column(DateTime, default=func.now(), comment='作成日')
    created_by = Column(String(255), comment='作成者')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新日')
    updated_by = Column(String(255), comment='更新者')

class THospital(Base):
    __tablename__ = 't_hospital'
    id = Column(Integer, primary_key=True, autoincrement=True, comment='病院ID')
    name = Column(String(255), nullable=False, comment='病院名')
    website = Column(String(255), comment='病院HP_URL')
    postal_code = Column(String(20), comment='郵便番号')
    address = Column(String(255), comment='住所')
    phone = Column(String(20), comment='連絡先')
    fax = Column(String(20), comment='fax')
    line_qr_code = Column(String(255), comment='LINEQRコード')
    reservation_policy_header = Column(Text, comment='予約ポリシーヘッダー')
    reservation_policy_body = Column(Text, comment='予約ポリシーボディー')
    treatment = Column(Text, comment='治療内容')
    deleted_flag = Column(Boolean, default=False, comment='削除フラグ')
    created_at = Column(DateTime, default=func.now(), comment='作成日')
    created_by = Column(String(255), comment='作成者')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新日')
    updated_by = Column(String(255), comment='更新者')
