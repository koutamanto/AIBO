from pymongo import MongoClient
from datetime import datetime

# MongoDBに接続
client = MongoClient('mongodb://localhost:27017/')
db = client['healthcare_system']

# FacilitiesコレクションのCRUD操作
facilities = db['Facilities']

def create_facility(facility_data):
    """
    施設を作成する。
    capacityは初期値として0を設定し、後で所属するcounselorの数に基づいて更新される。
    """
    facility_data['created_at'] = datetime.now()
    facility_data['updated_at'] = datetime.now()
    facility_data['capacity'] = 0  # 初期値は0
    result = facilities.insert_one(facility_data)
    print(f"施設作成: ID={result.inserted_id}")


# CounselorsコレクションのCRUD操作
counselors = db['Counselors']

def create_or_update_counselor(counselor_data):
    """
    相談員を作成または更新する。
    availabilityには曜日と時間帯を含める。
    施設のcapacityも、対応可能な相談員が追加または更新されるたびに更新される。
    """
    counselor_data['updated_at'] = datetime.now()

    # 存在確認し、存在する場合は更新、存在しない場合は新規作成 (upsert)
    result = counselors.update_one(
        {'counselor_id': counselor_data['counselor_id']},  # 同じIDの相談員を検索
        {'$set': counselor_data},  # データを更新
        upsert=True  # 存在しない場合は新規作成
    )
    
    if result.matched_count > 0:
        print(f"相談員 {counselor_data['counselor_id']} を更新しました。")
    else:
        print(f"相談員 {counselor_data['counselor_id']} を新規作成しました。")
    
    # 所属施設のcapacityを更新する
    update_facility_capacity(counselor_data['affiliation'])

def is_counselor_available(counselor, current_time=None):
    """
    相談員が現在の日時に対応可能かを確認する関数。
    availabilityフィールドに基づいて現在の曜日と時間に対応可能な相談員のみを返す。
    """
    if current_time is None:
        current_time = datetime.now()

    # 現在の曜日と時間を取得
    current_day_of_week = current_time.strftime('%A')  # 曜日
    current_time_only = current_time.time()  # 時刻部分のみを取得 (datetime.time 型)

    for availability in counselor.get('availability', []):
        # 曜日が一致しているか確認
        if availability['day_of_week'] == current_day_of_week:
            # 文字列を time オブジェクトに変換して比較
            start_time = datetime.strptime(availability['time_range']['start'], '%H:%M').time()
            end_time = datetime.strptime(availability['time_range']['end'], '%H:%M').time()

            # 現在の時刻が対応可能な時間範囲に含まれているか確認
            if start_time <= current_time_only <= end_time:
                return True

    return False

def get_available_counselors(facility_id, current_time=None):
    """
    特定の施設に所属する対応可能な相談員を取得する。
    """
    # 施設に所属するすべての相談員を取得
    affiliated_counselors = counselors.find({'affiliation': facility_id})

    # 現在対応可能な相談員をフィルタリング
    available_counselors = [
        counselor for counselor in affiliated_counselors
        if is_counselor_available(counselor, current_time)
    ]

    return available_counselors

def update_facility_capacity(facility_id):
    """
    施設に所属するcounselorの数に基づいて、施設のcapacityを更新する。
    """
    affiliated_counselors = counselors.find({'affiliation': facility_id})

    # 現在の対応可能な相談員数をカウント
    # available_counselor_count = sum(1 for _ in affiliated_counselors if affiliated_counselors)
    available_counselor_count = len(get_available_counselors(facility_id, datetime.now()))

    # capacityを更新
    facilities.update_one(
        {'facility_id': facility_id},
        {'$set': {'capacity': available_counselor_count, 'updated_at': datetime.now()}}
    )
    print(f"施設 {facility_id} のcapacityを {available_counselor_count} に更新しました。")


# UsersコレクションのCRUD操作
users = db['Users']

def create_user(user_data):
    """ユーザーの作成"""
    user_data['created_at'] = datetime.now()
    user_data['updated_at'] = datetime.now()
    result = users.insert_one(user_data)
    print(f"ユーザー作成: ID={result.inserted_id}")

def read_user(user_id):
    """ユーザーの読み込み"""
    user = users.find_one({'user_id': user_id})
    print(f"ユーザー情報: {user}")
    return user

def update_user(user_id, new_values):
    """ユーザー情報の更新"""
    new_values['updated_at'] = datetime.now()
    result = users.update_one({'user_id': user_id}, {'$set': new_values})
    print(f"更新されたユーザー: {result.modified_count}")

def delete_user(user_id):
    """ユーザーの削除"""
    result = users.delete_one({'user_id': user_id})
    print(f"削除されたユーザー: {result.deleted_count}")


# ConsultationLogsコレクションのCRUD操作
consultation_logs = db['ConsultationLogs']

def create_consultation_log(log_data):
    """相談ログの作成"""
    log_data['created_at'] = datetime.now()
    log_data['updated_at'] = datetime.now()
    result = consultation_logs.insert_one(log_data)
    print(f"相談ログ作成: ID={result.inserted_id}")

def read_consultation_log(log_id):
    """相談ログの読み込み"""
    log = consultation_logs.find_one({'log_id': log_id})
    print(f"相談ログ: {log}")
    return log

def update_consultation_log(log_id, new_values):
    """相談ログの更新"""
    new_values['updated_at'] = datetime.now()
    result = consultation_logs.update_one({'log_id': log_id}, {'$set': new_values})
    print(f"更新された相談ログ: {result.modified_count}")

def delete_consultation_log(log_id):
    """相談ログの削除"""
    result = consultation_logs.delete_one({'log_id': log_id})
    print(f"削除された相談ログ: {result.deleted_count}")


# TriageResultsコレクションのCRUD操作
triage_results = db['TriageResults']

def create_triage_result(triage_data):
    """トリアージ結果の作成"""
    triage_data['calculated_at'] = datetime.now()
    result = triage_results.insert_one(triage_data)
    print(f"トリアージ結果作成: ID={result.inserted_id}")

def read_triage_result(triage_id):
    """トリアージ結果の読み込み"""
    triage = triage_results.find_one({'triage_id': triage_id})
    print(f"トリアージ結果: {triage}")
    return triage

def update_triage_result(triage_id, new_values):
    """トリアージ結果の更新"""
    result = triage_results.update_one({'triage_id': triage_id}, {'$set': new_values})
    print(f"更新されたトリアージ結果: {result.modified_count}")

def delete_triage_result(triage_id):
    """トリアージ結果の削除"""
    result = triage_results.delete_one({'triage_id': triage_id})
    print(f"削除されたトリアージ結果: {result.deleted_count}")


# ActivityLogsコレクションのCRUD操作
activity_logs = db['ActivityLogs']

def create_activity_log(activity_data):
    """アクティビティログの作成"""
    activity_data['activity_time'] = datetime.now()
    result = activity_logs.insert_one(activity_data)
    print(f"アクティビティログ作成: ID={result.inserted_id}")

def read_activity_log(activity_id):
    """アクティビティログの読み込み"""
    activity = activity_logs.find_one({'activity_id': activity_id})
    print(f"アクティビティログ: {activity}")
    return activity

def update_activity_log(activity_id, new_values):
    """アクティビティログの更新"""
    result = activity_logs.update_one({'activity_id': activity_id}, {'$set': new_values})
    print(f"更新されたアクティビティログ: {result.modified_count}")

def delete_activity_log(activity_id):
    """アクティビティログの削除"""
    result = activity_logs.delete_one({'activity_id': activity_id})
    print(f"削除されたアクティビティログ: {result.deleted_count}")


# 使用例
if __name__ == "__main__":

    # # 1. 施設を作成
    # facility_data = {
    #     'facility_id': 'facility001',
    #     'name': 'Tokyo Mental Health Center',
    #     'type': 'Public',
    #     'contact_info': '123-456-7890',
    #     'address': 'Tokyo, Japan',
    #     'specializations': ['Mental Health', 'Family Issues']
    # }
    # create_facility(facility_data)

    # # 2. 相談員を作成し、施設に所属させる
    # counselor_data = {
    #     'counselor_id': 'counselor001',
    #     'name': 'John Doe',
    #     'affiliation': 'facility001',  # 所属する施設のID
    #     'contact_info': '987-654-3210',
    #     'specialization': 'Mental Health',
    #     'availability': [
    #         { 'day_of_week': 'Monday', 'time_range': { 'start': '09:00', 'end': '17:00' }},
    #         { 'day_of_week': 'Wednesday', 'time_range': { 'start': '13:00', 'end': '18:00' }}
    #     ]
    # }
    # create_or_update_counselor(counselor_data)

    # # 3. さらに別の相談員を作成し、同じ施設に所属させる
    # counselor_data_2 = {
    #     'counselor_id': 'counselor002',
    #     'name': 'Jane Smith',
    #     'affiliation': 'facility001',  # 同じ施設に所属
    #     'contact_info': '987-654-3220',
    #     'specialization': 'Family Issues',
    #     'availability': [
    #         { 'day_of_week': 'Tuesday', 'time_range': { 'start': '10:00', 'end': '16:00' }},
    #         { 'day_of_week': 'Thursday', 'time_range': { 'start': '09:00', 'end': '14:00' }}
    #     ]
    # }
    # create_or_update_counselor(counselor_data_2)

    counselor_data_3 = {
        'counselor_id': 'counselor001',
        'name': 'John Doe',
        'affiliation': 'facility001',  # 同じ施設に所属
        'contact_info': '987-654-0001',
        'specialization': 'Family Issues',
        'availability': [
            { 'day_of_week': 'Tuesday', 'time_range': { 'start': '10:00', 'end': '16:00' }},
            { 'day_of_week': 'Thursday', 'time_range': { 'start': '09:00', 'end': '14:00' }},
            { 'day_of_week': 'Friday', 'time_range': { 'start': '10:00', 'end': '14:00' }}
        ]
    }
    create_or_update_counselor(counselor_data_3)
    update_facility_capacity("facility001")