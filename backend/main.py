import os
import sys
import sqlite3
import json
from datetime import datetime
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS

# LINE設定（実際の値）
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', 'da9304a0ba9f50054710655d64a81680')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '14e9b69b3cfdf71dd1298dfbe2bc4cae')
LINE_CHANNEL_ID = os.environ.get('LINE_CHANNEL_ID', '2007761838')

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_here')

CORS(app)

def get_base_url():
    """動的にベースURLを取得"""
    if request:
        return f"{request.scheme}://{request.host}"
    return "http://localhost:3000"  # フォールバック

def init_database():
    """データベースを初期化"""
    conn = sqlite3.connect('database/simulations.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT,
            property_type TEXT,
            monthly_rent INTEGER,
            initial_cost INTEGER,
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

@app.route('/')
def index():
    """メインページを表示"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """静的ファイルを提供"""
    return send_from_directory(app.static_folder, filename)

@app.route('/api/simulation/calculate', methods=['POST'])
def calculate_simulation():
    """シミュレーション計算API"""
    try:
        data = request.get_json()
        
        # 計算ロジック（簡略版）
        region = data.get('region', '東京都')
        property_type = data.get('propertyType', '1K')
        monthly_rent = data.get('monthlyRent', 100000)
        initial_cost = data.get('initialCost', 1000000)
        
        # 地域別データ
        region_data = {
            '東京都': {'occupancy': 0.70, 'avg_price': 8000},
            '大阪府': {'occupancy': 0.68, 'avg_price': 6500},
            '京都府': {'occupancy': 0.65, 'avg_price': 7000},
            '福岡県': {'occupancy': 0.60, 'avg_price': 5500},
            '沖縄県': {'occupancy': 0.62, 'avg_price': 6000},
            '北海道': {'occupancy': 0.55, 'avg_price': 5000},
            'その他地方': {'occupancy': 0.40, 'avg_price': 4000}
        }
        
        # 物件別データ
        property_data = {
            '1K': {'max_capacity': 3, 'cleaning_fee': 15000},
            '1DK': {'max_capacity': 4, 'cleaning_fee': 18000},
            '1LDK': {'max_capacity': 5, 'cleaning_fee': 20000},
            '2LDK': {'max_capacity': 6, 'cleaning_fee': 25000},
            '3LDK': {'max_capacity': 8, 'cleaning_fee': 30000},
            '戸建て': {'max_capacity': 10, 'cleaning_fee': 40000}
        }
        
        region_info = region_data.get(region, region_data['東京都'])
        property_info = property_data.get(property_type, property_data['1K'])
        
        # 年間売上計算
        daily_revenue = property_info['max_capacity'] * region_info['avg_price']
        annual_occupied_days = 365 * region_info['occupancy']
        annual_revenue = daily_revenue * annual_occupied_days
        
        # 年間費用計算
        annual_rent = monthly_rent * 12
        annual_cleaning = property_info['cleaning_fee'] * 12
        annual_utilities = 15000 * 12  # 光熱費
        annual_insurance = 16000 * 12  # 保険料
        management_fee = annual_revenue * 0.10  # 運営代行費10%
        annual_costs = annual_rent + annual_cleaning + annual_utilities + annual_insurance + management_fee
        
        # 年間利益
        annual_profit = annual_revenue - annual_costs
        
        # ROI計算
        roi = (annual_profit / initial_cost) * 100 if initial_cost > 0 else 0
        recovery_period = initial_cost / annual_profit if annual_profit > 0 else 0
        
        result = {
            'region': region,
            'property_type': property_type,
            'monthly_rent': monthly_rent,
            'initial_cost': initial_cost,
            'annualRevenue': int(annual_revenue),
            'annualCosts': int(annual_costs),
            'annualProfit': int(annual_profit),
            'roi': round(roi, 1),
            'recoveryPeriod': round(recovery_period, 1)
        }
        
        # データベースに保存
        try:
            conn = sqlite3.connect('database/simulations.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO simulations 
                (region, property_type, monthly_rent, initial_cost, annual_revenue, annual_costs, annual_profit, roi, recovery_period)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                region, property_type, monthly_rent, initial_cost,
                result['annualRevenue'], result['annualCosts'], result['annualProfit'],
                result['roi'], result['recoveryPeriod']
            ))
            
            conn.commit()
            conn.close()
        except Exception as db_error:
            print(f"Database error: {db_error}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Calculation error: {e}")
        return jsonify({'error': str(e)}), 500

# LINE Webhook
@app.route('/api/line/webhook', methods=['POST'])
def line_webhook():
    """LINE Webhook処理"""
    try:
        import requests
        
        body = request.get_json()
        
        if not body or 'events' not in body:
            return jsonify({}), 200
        
        for event in body['events']:
            if event['type'] == 'message' and event['message']['type'] == 'text':
                reply_token = event['replyToken']
                message_text = event['message']['text'].strip().lower()
                
                # 「結果」メッセージの検出
                if message_text in ['結果', 'けっか', 'ケッカ', 'kekka', '結果を見る', '最新結果']:
                    # 最新のシミュレーション結果を取得
                    try:
                        conn = sqlite3.connect('database/simulations.db')
                        cursor = conn.cursor()
                        
                        cursor.execute('''
                            SELECT * FROM simulations 
                            ORDER BY created_at DESC 
                            LIMIT 1
                        ''')
                        
                        result = cursor.fetchone()
                        conn.close()
                        
                        if result:
                            base_url = get_base_url()
                            response_text = f"""🏠 最新のシミュレーション結果

📊 基本情報:
• 地域: {result[1]}
• 物件タイプ: {result[2]}
• 月額家賃: ¥{result[3]:,}
• 初期費用: ¥{result[4]:,}

💰 収益分析:
• 年間売上: ¥{result[5]:,}
• 年間費用: ¥{result[6]:,}
• 年間利益: ¥{result[7]:,}
• 年間利回り: {result[8]}%
• 投資回収期間: {result[9]}年

🌐 詳細はこちら:
{base_url}

📱 有村昆の民泊塾
運営: 株式会社Prorium"""
                        else:
                            base_url = get_base_url()
                            response_text = f"""🏠 民泊収益シミュレーター

まだシミュレーション結果がありません。

🌐 シミュレーションを開始:
{base_url}

📱 有村昆の民泊塾
運営: 株式会社Prorium"""
                    
                    except Exception as db_error:
                        print(f"Database error: {db_error}")
                        base_url = get_base_url()
                        response_text = f"""🏠 民泊収益シミュレーター

データベースエラーが発生しました。

🌐 シミュレーションを開始:
{base_url}

📱 有村昆の民泊塾
運営: 株式会社Prorium"""
                    
                    # LINE APIに送信
                    send_line_message(reply_token, response_text)
                
        return jsonify({}), 200
        
    except Exception as e:
        print(f"LINE webhook error: {e}")
        return jsonify({}), 200

def send_line_message(reply_token, message):
    """LINE APIを使用してメッセージを送信"""
    try:
        import requests
        
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
        return response.status_code == 200
        
    except Exception as e:
        print(f"LINE API error: {e}")
        return False

if __name__ == '__main__':
    # データベース初期化
    os.makedirs('database', exist_ok=True)
    init_database()
    
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)

