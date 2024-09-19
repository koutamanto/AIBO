from pymongo import MongoClient
from datetime import datetime

# MongoDBに接続
client = MongoClient('mongodb://localhost:27017/')  # ローカルのMongoDBに接続
db = client['healthcare_system']  # データベース名

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


# FacilitiesコレクションのCRUD操作
facilities = db['Facilities']

def create_facility(facility_data):
    """施設の作成"""
    facility_data['created_at'] = datetime.now()
    facility_data['updated_at'] = datetime.now()
    result = facilities.insert_one(facility_data)
    print(f"施設作成: ID={result.inserted_id}")

def read_facility(facility_id):
    """施設の読み込み"""
    facility = facilities.find_one({'facility_id': facility_id})
    print(f"施設情報: {facility}")
    return facility

def update_facility(facility_id, new_values):
    """施設の更新"""
    new_values['updated_at'] = datetime.now()
    result = facilities.update_one({'facility_id': facility_id}, {'$set': new_values})
    print(f"更新された施設: {result.modified_count}")

def delete_facility(facility_id):
    """施設の削除"""
    result = facilities.delete_one({'facility_id': facility_id})
    print(f"削除された施設: {result.deleted_count}")


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
    # ユーザー作成例
    user_data = {
        'user_id': 'user001',
        'username': 'taro',
        'password': 'hashed_password',
        'nickname': 'Taro',
        'age': 30,
        'gender': 'male',
        'region': 'Tokyo',
        'occupation': 'Engineer'
    }
    create_user(user_data)

    # 相談ログの作成例
    consultation_data = {
        'log_id': 'log001',
        'user_id': 'user001',
        'consultation_date': datetime.now(),
        'content': '相談内容です。',
        'score': 85,
        'facility_id': 'facility001'
    }
    create_consultation_log(consultation_data)

    # 施設の作成例
    facility_data = {
        'facility_id': 'facility001',
        'name': 'Tokyo Mental Health Center',
        'type': 'Public',
        'contact_info': '123-456-7890',
        'address': 'Tokyo, Japan',
        'capacity': 100,
        'specializations': ['Mental Health', 'Family Issues']
    }
    create_facility(facility_data)
