UPDATE badara_dev.t_user t
JOIN (
  SELECT
    id,
    ROW_NUMBER() OVER (ORDER BY created_at) + 9 AS new_no
  FROM badara_dev.t_user
  WHERE medical_record_no = ''
) AS numbered
ON t.id = numbered.id
SET t.medical_record_no = numbered.new_no;
