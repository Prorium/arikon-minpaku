import os
import sys
import sqlite3
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# 環境変数からLINE設定を取得
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', 'your_channel_secret_here')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', 'your_access_token_here')
LINE_CHANNEL_ID = os.environ.get('LINE_CHANNEL_ID', 'your_channel_id_here')

# GitHub Pages URL（環境変数で設定可能）
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://prorium.github.io/arikon-minpaku/')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_here')

# CORS設定 - GitHub Pagesからのアクセスを許可
CORS(app, origins=[
    'https://prorium.github.io',
    'http://localhost:3000',
    'http://127.0.0.1:3000'
])

def get_base_url():
    """動的にベースURLを取得"""
    if request:
        return f"{request.scheme}://{request.host}"
    return "http://localhost:3000"

def get_frontend_url():
    """フロントエンドのURLを取得"""
    return FRONTEND_URL

# データベース初期化
def init_db():
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # シミュレーションテーブル作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulations (
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
    
    conn.commit()
    conn.close()

def get_latest_simulation():
    """最新のシミュレーション結果を取得"""
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT region, property_type, monthly_rent, annual_revenue, annual_costs, annual_profit, roi, recovery_period
            FROM simulations 
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
        return None
        
    except Exception as e:
        print(f"Database error: {e}")
        return None

# シミュレーション計算API
@app.route('/api/simulation/calculate', methods=['POST'])
def calculate_simulation():
    try:
        data = request.get_json()
        
        # 地域データ
        region_data = {
            '東京都': {'稼働率': 0.70, '平均単価': 25000},
            '大阪府': {'稼働率': 0.68, '平均単価': 20000},
            '京都府': {'稼働率': 0.65, '平均単価': 22000},
            '福岡県': {'稼働率': 0.60, '平均単価': 18000},
            '沖縄県': {'稼働率': 0.62, '平均単価': 20000},
            '北海道': {'稼働率': 0.55, '平均単価': 15000},
            'その他地方': {'稼働率': 0.40, '平均単価': 10000}
        }
        
        # 物件タイプデータ
        property_data = {
            '1K': {'初期費用倍率': 4, '月額清掃費': 15000, '家具家電費': 300000},
            '1DK': {'初期費用倍率': 4, '月額清掃費': 18000, '家具家電費': 350000},
            '1LDK': {'初期費用倍率': 4, '月額清掃費': 20000, '家具家電費': 400000},
            '2LDK': {'初期費用倍率': 4, '月額清掃費': 25000, '家具家電費': 500000},
            '3LDK': {'初期費用倍率': 4, '月額清掃費': 30000, '家具家電費': 600000},
            '戸建て': {'初期費用倍率': 4, '月額清掃費': 35000, '家具家電費': 800000}
        }
        
        region = data.get('region')
        property_type = data.get('propertyType')
        monthly_rent = data.get('monthlyRent', 100000)
        furniture_appliances = data.get('furnitureAppliances', True)
        renovation_cost = data.get('renovationCost', 0)
        management_fee_rate = data.get('managementFeeRate', 10)
        
        # 計算
        region_info = region_data.get(region, region_data['その他地方'])
        property_info = property_data.get(property_type, property_data['1K'])
        
        occupancy_rate = region_info['稼働率']
        daily_rate = region_info['平均単価']
        
        # 年間売上
        annual_revenue = int(daily_rate * 365 * occupancy_rate)
        
        # 年間費用
        monthly_cleaning = property_info['月額清掃費']
        annual_cleaning = monthly_cleaning * 12
        annual_rent = monthly_rent * 12
        management_fee = annual_revenue * (management_fee_rate / 100)
        
        annual_costs = int(annual_rent + annual_cleaning + management_fee)
        
        # 年間利益
        annual_profit = annual_revenue - annual_costs
        
        # 初期費用
        initial_deposit = monthly_rent * property_info['初期費用倍率']
        furniture_cost = property_info['家具家電費'] if furniture_appliances else 0
        total_initial_cost = initial_deposit + furniture_cost + renovation_cost
        
        # ROIと回収期間
        roi = (annual_profit / total_initial_cost * 100) if total_initial_cost > 0 else 0
        recovery_period = (total_initial_cost / annual_profit) if annual_profit > 0 else 0
        
        result = {
            'region': region,
            'property_type': property_type,
            'monthly_rent': monthly_rent,
            'annualRevenue': annual_revenue,
            'annualCosts': annual_costs,
            'annualProfit': annual_profit,
            'roi': round(roi, 1),
            'recoveryPeriod': round(recovery_period, 1),
            'initialCost': total_initial_cost,
            'occupancyRate': occupancy_rate,
            'dailyRate': daily_rate
        }
        
        # データベースに保存
        db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO simulations (region, property_type, monthly_rent, annual_revenue, annual_costs, annual_profit, roi, recovery_period)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (region, property_type, monthly_rent, annual_revenue, annual_costs, annual_profit, roi, recovery_period))
        
        conn.commit()
        conn.close()
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Calculation error: {e}")
        return jsonify({'error': str(e)}), 500

def send_line_message(reply_token, message):
    """LINE APIを使用してメッセージを送信"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
        }
        
        data = {
            'replyToken': reply_token,
            'messages': [{'type': 'text', 'text': message}]
        }
        
        response = requests.post('https://api.line.me/v2/bot/message/reply', 
                               headers=headers, data=json.dumps(data))
        print(f"LINE API response: {response.status_code}, {response.text}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"LINE API error: {e}")
        return False

# LINE Webhook
@app.route('/api/line/webhook', methods=['POST'])
def line_webhook():
    try:
        body = request.get_json()
        print(f"Received LINE webhook: {body}")
        
        if not body or 'events' not in body:
            return jsonify({}), 200
        
        events = body['events']
        if not events:
            return jsonify({}), 200
        
        for event in events:
            if event['type'] == 'message' and event['message']['type'] == 'text':
                user_message = event['message']['text'].strip()
                reply_token = event['replyToken']
                
                print(f"User message: {user_message}")
                
                # 「結果」というメッセージに応答
                if '結果' in user_message or 'けっか' in user_message or 'ケッカ' in user_message:
                    simulation_data = get_latest_simulation()
                    
                    if simulation_data:
                        frontend_url = get_frontend_url()
                        
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
{frontend_url}

💡 新しいシミュレーションを実行するには、上記URLにアクセスしてください。"""
                    else:
                        frontend_url = get_frontend_url()
                        response_text = f"""🏠 民泊収益シミュレーター

まだシミュレーション結果がありません。

🌐 シミュレーションを開始:
{frontend_url}

上記URLにアクセスして、あなたの民泊投資収益をシミュレーションしてみましょう！"""
                    
                    send_line_message(reply_token, response_text)
                    
                else:
                    # その他のメッセージに対する応答
                    frontend_url = get_frontend_url()
                    response_text = f"""🏠 民泊収益シミュレーター

「結果」と入力すると最新のシミュレーション結果をお送りします。

🌐 新しいシミュレーション:
{frontend_url}

上記URLでシミュレーションを実行してください！"""
                    
                    send_line_message(reply_token, response_text)
        
        return jsonify({}), 200
        
    except Exception as e:
        print(f"LINE webhook error: {e}")
        return jsonify({}), 200

@app.route('/api/line/webhook', methods=['GET'])
def line_webhook_verify():
    """LINE Webhook URL検証用"""
    return jsonify({
        'status': 'LINE Webhook is ready',
        'frontend_url': get_frontend_url(),
        'backend_url': get_base_url()
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェック用エンドポイント"""
    return jsonify({
        'status': 'healthy',
        'frontend_url': get_frontend_url(),
        'backend_url': get_base_url(),
        'line_configured': bool(LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_ACCESS_TOKEN != 'your_access_token_here')
    }), 200

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

