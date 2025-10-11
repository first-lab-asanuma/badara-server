from hashids import Hashids
import os

# .env 파일에서 HASHIDS_SALT 환경 변수를 불러옵니다.
# 이 값이 설정되어 있지 않으면 애플리케이션이 시작되지 않도록 하여, 
# 안전하지 않은 기본값으로 실행되는 것을 방지합니다.
SALT = "BADARA_TAMANEGI_HARUGI"
if not SALT:
    raise ValueError("Security Error: HASHIDS_SALT environment variable is not set. Please define it in your .env file.")

MIN_LENGTH = 8

hashids = Hashids(salt=SALT, min_length=MIN_LENGTH)

def encode_id(id_integer: int) -> str:
    """정수 ID를 해시 ID로 인코딩합니다."""
    return hashids.encode(id_integer)

def decode_id(id_hash: str) -> int | None:
    """해시 ID를 정수 ID로 디코딩합니다."""
    decoded_tuple = hashids.decode(id_hash)
    # decode()는 튜플을 반환하므로, 첫 번째 요소를 확인하고 반환합니다.
    if decoded_tuple:
        return decoded_tuple[0]
    return None