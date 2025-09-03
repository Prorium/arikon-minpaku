import json
import requests
import os
import sqlite3
from datetime import datetime
from flask import Blueprint, request, jsonify

line_final_bp = Blueprint('line_final', __name__)

def get_current_domain():
    """現在のドメインを動的に取得"""
    try:
        # リクエストヘッダーから取得を試行
        if request and hasattr(request, 'host'):
            return f"https://{request.host}"
        
        # フォールバック（デフォルトURL）
        return "https://vgh0i1coy709.manus.space"
    except:
        return "https://vgh0i1coy709.manus.space"

# LINE Messaging API設定
LINE_CHANNEL_ACCESS_TOKEN = "m/uvGJ0/dxSZqLea6jLhOm9F3bzPwBm3l83MUbnsQuyjLGtH0qnFBW2H8nrTnxKMu88ciaWcqQoNueyY3om+uM9A1xsOieHDZIxxkTZxye0A2g6tcFL2NHDRTl9DyTU2WSwoc9uHZBtjmbecDynmKAdB04t89/1O/w1cDnyilFU="
LINE_API_URL = "https://api.line.me/v2/bot/message/reply"

def get_db_path():
    """データベースファイルのパスを取得"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'app.db')

def get_latest_simulation_direct():
    """SQLiteを直接使用して最新のシミュレーション結果を取得"""
    try:
        db_path = get_db_path()
        
        # データベースファイルが存在しない場合は作成
        if not os.path.exists(os.path.dirname(db_path)):
            os.makedirs(os.path.dirname(db_path))
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 辞書形式でアクセス可能
        cursor = conn.cursor()
        
        # テーブルが存在しない場合は作成
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simulation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT,
                property_type TEXT,
                monthly_rent INTEGER,
                annual_revenue INTEGER,
                annual_costs INTEGER,
                annual_profit INTEGER,
                roi REAL,
                recovery_period REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 最新のシミュレーション結果を取得
        cursor.execute('''
            SELECT region, property_type, monthly_rent, annual_revenue, annual_costs, annual_profit, roi, recovery_period
            FROM simulation 
            ORDER BY created_at DESC 
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'region': result['region'],
                'property_type': result['property_type'],
                'monthly_rent': result['monthly_rent'],
                'annual_revenue': result['annual_revenue'],
                'annual_costs': result['annual_costs'],
                'annual_profit': result['annual_profit'],
                'roi': result['roi'],
                'recovery_period': result['recovery_period']
            }
        else:
            return None
            
    except Exception as e:
        print(f"Database error: {e}")
        return None

def send_line_message(reply_token, message):
    """LINE APIを使用してメッセージを送信"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
        }
        
        data = {
            'replyToken': reply_token,
            'messages': [
                {
                    'type': 'text',
                    'text': message
                }
            ]
        }
        
        response = requests.post(LINE_API_URL, headers=headers, data=json.dumps(data))
        print(f"LINE API response: {response.status_code}, {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"LINE API error: {e}")
        return False

@line_final_bp.route('/webhook', methods=['POST'])
def line_webhook():
    """LINE Webhook エンドポイント"""
    try:
        # LINE Webhookリクエストを解析
        body = request.get_json()
        print(f"Received LINE webhook: {body}")
        
        # eventsが存在するかチェック
        if not body or 'events' not in body:
            return jsonify({}), 200
        
        events = body['events']
        if not events:
            return jsonify({}), 200
        
        # 各イベントを処理
        for event in events:
            if event['type'] == 'message' and event['message']['type'] == 'text':
                user_message = event['message']['text'].strip()
                reply_token = event['replyToken']
                
                print(f"User message: {user_message}")
                
                # 「結果」というメッセージに応答
                if '結果' in user_message or 'けっか' in user_message or 'ケッカ' in user_message:
                    # 最新のシミュレーション結果を取得
                    simulation_data = get_latest_simulation_direct()
                    
                    if simulation_data:
                        # 動的URLを取得
                        base_url = get_current_domain()
                        
                        response_text = f"""🏠 最新のシミュレーション結果

📊 基本情報:
• 地域: {simulation_data['region']}
• 物件タイプ: {simulation_data['property_type']}
• 月額家賃: ¥{simulation_data['monthly_rent']:,}

💰 収益分析:
• 年間売上: ¥{simulation_data['annual_revenue']:,}
• 年間費用: ¥{simulation_data['annual_costs']:,}
• 年間利益: ¥{simulation_data['annual_profit']:,}
• 年間利回り: {simulation_data['roi']}%
• 投資回収期間: {simulation_data['recovery_period']}年

🌐 詳細はこちら:
{base_url}

💡 新しいシミュレーションを実行するには、上記URLにアクセスしてください。"""
                    else:
                        base_url = get_current_domain()
                        response_text = f"""🏠 民泊収益シミュレーター

まだシミュレーション結果がありません。

🌐 シミュレーションを開始:
{base_url}

上記URLにアクセスして、あなたの民泊投資収益をシミュレーションしてみましょう！"""
                    
                    # LINE APIを使用してメッセージを送信
                    print(f"Sending response: {response_text}")
                    send_line_message(reply_token, response_text)
                    
                else:
                    # その他のメッセージに対する応答
                    base_url = get_current_domain()
                    response_text = f"""🏠 民泊収益シミュレーター

「結果」と入力すると最新のシミュレーション結果をお送りします。

🌐 新しいシミュレーション:
{base_url}

上記URLでシミュレーションを実行してください！"""
                    
                    send_line_message(reply_token, response_text)
        
        return jsonify({}), 200
        
    except Exception as e:
        print(f"LINE webhook error: {e}")
        return jsonify({}), 200

@line_final_bp.route('/webhook', methods=['GET'])
def line_webhook_verify():
    """LINE Webhook URL検証用"""
    return jsonify({'status': 'LINE Webhook is ready'}), 200

