-- 병원 관리자 샘플 데이터
-- hospital_id는 t_hospital 테이블에서 hospital_code가 'H001'인 병원의 id를 동적으로 조회합니다.
-- password는 'password' 문자열을 bcrypt로 해싱한 값입니다.
INSERT INTO t_user (
  hospital_id,
  login_id,
  password,
  user_type,
  last_name,
  first_name,
  email,
  contact,
  created_by,
  updated_by
) VALUES (
  (SELECT id FROM t_hospital WHERE hospital_code = 'H001'),
  'admin',
  '$2b$12$Z0gEN6lL9bLE.KShHgGvxOsDA4FnmcJ6zz6fF8XPLW2mnB78Ozu/m',
  '1',
  '病院',
  '管理者',
  'admin@example.com',
  '010-0000-0000',
  'system',
  'system'
);