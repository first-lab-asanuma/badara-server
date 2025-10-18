from typing import Any


_TRANSLATIONS: dict[str, str] = {
    # Auth（利用者向けに簡潔で丁寧な表現に）
    "Could not validate credentials": "認証に失敗しました。もう一度ログインしてください。",
    "Inactive user": "アカウントが利用できません。サポートへお問い合わせください。",
    "Incorrect lineId": "ログインに失敗しました。情報をご確認ください。",
    "Incorrect username or password": "ユーザーIDまたはパスワードが正しくありません。",

    # Hospital
    "Hospital not found": "医療機関情報が見つかりませんでした。",
    "Not authorized to update hospital information": "この操作を行う権限がありません。",
    "treatment must be a list": "治療内容の形式が正しくありません。",
    "treatment items cannot be empty": "治療内容を入力してください。",
    "Not authorized to add holiday": "休日を追加する権限がありません。",
    "Not authorized to delete holiday": "休日を削除する権限がありません。",
    "Holiday not found": "休日情報が見つかりませんでした。",

    # Reservation
    "Cannot make a reservation on a holiday.": "休日には予約できません。別の日付をお選びください。",
    "Requested time slot is not available.": "その時間帯は予約できません。別の時間をお選びください。",
    "Not authorized": "操作の権限がありません。",
    "Requested time slot is fully booked (2 reservations already exist).": "その時間帯は満席です。別の時間をお選びください。",
    "Not authorized to view all reservations": "予約一覧を閲覧する権限がありません。",
    "Reservation not found": "予約が見つかりませんでした。",
    "Not authorized to view this reservation": "この予約を閲覧する権限がありません。",
    "Not authorized to cancel this reservation": "この予約をキャンセルする権限がありません。",

    # AuthRouter
    "User is not a patient": "患者としての権限がありません。",
    "User is not a hospital admin or system admin": "病院管理者としての権限がありません。",

    # Patient
    "Hospital with the given code not found.": "医療機関が見つかりませんでした。コードをご確認ください。",
    "Patient user not found": "患者が見つかりませんでした。",
    "Not authorized to update patient information": "患者情報を更新する権限がありません。",
    "Not authorized to update this patient's information": "この患者情報を更新する権限がありません。",
    "Medical record number already exists for another patient in this hospital.": "このカルテ番号は既に使用されています。",
    "Not authorized to view patient information": "患者情報を閲覧する権限がありません。",
    "Not authorized to view this patient's information": "この患者情報を閲覧する権限がありません。",
    "Only hospital administrators can view their hospital's patient list": "病院管理者のみが患者一覧を閲覧できます。",
    "Only hospital administrators can query this resource": "病院管理者のみが参照できます。",
}


def translate_detail(detail: Any) -> Any:
    """Translate known error detail strings to Japanese. Leave non-strings as-is."""
    if not isinstance(detail, str):
        return detail

    # Exact match first
    if detail in _TRANSLATIONS:
        return _TRANSLATIONS[detail]

    # 動的メッセージ: カルテ番号で患者が見つからない場合は値を伏せて返す
    prefix = "Patient with medical record number '"
    suffix = "' not found in this hospital."
    if detail.startswith(prefix) and detail.endswith(suffix):
        return "該当する患者が見つかりませんでした。"

    # Fallback: return original if not matched
    return detail
