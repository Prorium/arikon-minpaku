import os
import sys
import sqlite3
import json
import hashlib
import hmac
import base64
from datetime import datetime
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import requests

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
    # データベースディレクトリを作成
    os.makedirs('database', exist_ok=True)
    
    conn = sqlite3.connect('database/simulations.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            region TEXT,
            operation_type TEXT,
            property_type TEXT,
            area INTEGER,
            capacity INTEGER,
            minpaku_law TEXT,
            monthly_rent INTEGER,
            purchase_price INTEGER,
            renovation_cost INTEGER,
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
    """静的ファイルを配信"""
    return send_from_directory(app.static_folder, filename)

@app.route('/api/simulation/calculate', methods=['POST'])
def calculate_simulation():
    """シミュレーション計算API"""
    try:
        data = request.get_json()
        
        # 入力データの検証
        required_fields = ['region', 'operationType', 'propertyType', 'area', 'capacity', 'minpakuLaw']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 計算ロジック
        region = data['region']
        operation_type = data['operationType']
        property_type = data['propertyType']
        area = int(data['area'])
        capacity = int(data['capacity'])
        minpaku_law = data['minpakuLaw']
        
        # 投資金額
        monthly_rent = int(data.get('monthlyRent', 0))
        purchase_price = int(data.get('purchasePrice', 0))
        renovation_cost = int(data.get('renovationCost', 0))
        initial_cost = int(data.get('initialCost', 0))
        
        # 地域別の基本データ
        region_data = {
            '東京都': {'daily_rate': 12000, 'occupancy': 0.75, 'expenses_rate': 0.35},
            '大阪府': {'daily_rate': 8000, 'occupancy': 0.70, 'expenses_rate': 0.30},
            '京都府': {'daily_rate': 10000, 'occupancy': 0.72, 'expenses_rate': 0.32},
            '神奈川県': {'daily_rate': 9000, 'occupancy': 0.68, 'expenses_rate': 0.33},
            '愛知県': {'daily_rate': 7000, 'occupancy': 0.65, 'expenses_rate': 0.28},
            '福岡県': {'daily_rate': 6000, 'occupancy': 0.62, 'expenses_rate': 0.25}
        }
        
        base_data = region_data.get(region, region_data['東京都'])
        
        # 収容人数による単価調整
        capacity_multiplier = 1 + (capacity - 2) * 0.15
        daily_rate = int(base_data['daily_rate'] * capacity_multiplier)
        
        # 民泊新法による営業日数制限
        max_days = 180 if minpaku_law == '民泊新法対応（180日制限あり）' else 365
        
        # 年間収益計算
        operating_days = int(max_days * base_data['occupancy'])
        annual_revenue = daily_rate * operating_days
        
        # 年間費用計算
        annual_expenses = int(annual_revenue * base_data['expenses_rate'])
        if operation_type == '転貸':
            annual_expenses += monthly_rent * 12
        
        # 年間利益
        annual_profit = annual_revenue - annual_expenses
        
        # 総投資額
        total_investment = purchase_price + renovation_cost + initial_cost
        
        # ROI計算
        roi = (annual_profit / total_investment * 100) if total_investment > 0 else 0
        
        # 投資回収期間
        recovery_period = (total_investment / annual_profit) if annual_profit > 0 else 999
        
        result = {
            'region': region,
            'operationType': operation_type,
            'propertyType': property_type,
            'area': area,
            'capacity': capacity,
            'minpakuLaw': minpaku_law,
            'monthlyRent': monthly_rent,
            'purchasePrice': purchase_price,
            'renovationCost': renovation_cost,
            'initialCost': initial_cost,
            'dailyRate': daily_rate,
            'operatingDays': operating_days,
            'annualRevenue': annual_revenue,
            'annualExpenses': annual_expenses,
            'annualProfit': annual_profit,
            'totalInvestment': total_investment,
            'roi': round(roi, 2),
            'recoveryPeriod': round(recovery_period, 1)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulation/save', methods=['POST'])
def save_simulation():
    """シミュレーション結果を保存"""
    try:
        data = request.get_json()
        user_id = data.get('userId', 'anonymous')
        
        conn = sqlite3.connect('database/simulations.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO simulations (
                user_id, region, operation_type, property_type, area, capacity,
                minpaku_law, monthly_rent, purchase_price, renovation_cost,
                initial_cost, annual_revenue, annual_costs, annual_profit,
                roi, recovery_period
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, data['region'], data['operationType'], data['propertyType'],
            data['area'], data['capacity'], data['minpakuLaw'],
            data.get('monthlyRent', 0), data.get('purchasePrice', 0),
            data.get('renovationCost', 0), data.get('initialCost', 0),
            data['annualRevenue'], data['annualExpenses'], data['annualProfit'],
            data['roi'], data['recoveryPeriod']
        ))
        
        simulation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'simulationId': simulation_id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulation/latest/<user_id>', methods=['GET'])
def get_latest_simulation(user_id):
    """最新のシミュレーション結果を取得"""
    try:
        conn = sqlite3.connect('database/simulations.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM simulations 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [description[0] for description in cursor.description]
            result = dict(zip(columns, row))
            return jsonify(result)
        else:
            return jsonify({'error': 'No simulation found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def verify_line_signature(body, signature):
    """LINE Webhook署名を検証"""
    hash = hmac.new(
        LINE_CHANNEL_SECRET.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(hash).decode('utf-8') == signature

def send_line_message(user_id, message):
    """LINEメッセージを送信"""
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    
    data = {
        'to': user_id,
        'messages': [{'type': 'text', 'text': message}]
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.status_code == 200

@app.route('/api/line/webhook', methods=['POST'])
def line_webhook():
    """LINE Webhook エンドポイント"""
    try:
        # 署名検証
        signature = request.headers.get('X-Line-Signature')
        body = request.get_data(as_text=True)
        
        if not verify_line_signature(body, signature):
            return 'Invalid signature', 400
        
        # イベント処理
        events = json.loads(body).get('events', [])
        
        for event in events:
            if event['type'] == 'message' and event['message']['type'] == 'text':
                user_id = event['source']['userId']
                message_text = event['message']['text'].strip()
                
                if message_text == '結果':
                    # 最新のシミュレーション結果を取得
                    conn = sqlite3.connect('database/simulations.db')
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        SELECT * FROM simulations 
                        WHERE user_id = ? 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    ''', (user_id,))
                    
                    row = cursor.fetchone()
                    conn.close()
                    
                    if row:
                        # 結果メッセージを作成
                        result_message = f"""🏠 民泊シミュレーション結果

📍 地域: {row[2]}
🏢 運営形態: {row[3]}
🏠 物件タイプ: {row[4]}
📐 面積: {row[5]}㎡
👥 収容人数: {row[6]}名
⚖️ 民泊法: {row[7]}

💰 投資金額:
・月額家賃: {row[8]:,}円
・物件購入価格: {row[9]:,}円
・リノベーション費用: {row[10]:,}円
・初期費用: {row[11]:,}円

📊 収益予測:
・年間売上: {row[12]:,}円
・年間費用: {row[13]:,}円
・年間利益: {row[14]:,}円
・ROI: {row[15]}%
・投資回収期間: {row[16]}年

📅 計算日時: {row[17]}

※ この結果は概算です。実際の収益は市場状況により変動します。"""
                        
                        send_line_message(user_id, result_message)
                    else:
                        send_line_message(user_id, "シミュレーション結果が見つかりません。まずはWebサイトでシミュレーションを実行してください。\n\n🌐 https://prorium.github.io/arikon-minpaku/")
                
                elif message_text in ['シミュレーション', 'シミュレーター', 'sim']:
                    send_line_message(user_id, "民泊シミュレーターはこちらからご利用ください！\n\n🌐 https://prorium.github.io/arikon-minpaku/\n\nシミュレーション完了後、「結果」とメッセージを送信すると詳細な結果をお送りします。")
                
                else:
                    send_line_message(user_id, "こんにちは！有村昆の民泊塾です。\n\n以下のコマンドをお試しください：\n・「結果」- 最新のシミュレーション結果を表示\n・「シミュレーション」- シミュレーターのURLを表示\n\n🌐 https://prorium.github.io/arikon-minpaku/")
        
        return 'OK', 200
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return 'Error', 500

@app.route('/api/line/webhook', methods=['GET'])
def line_webhook_verify():
    """LINE Webhook 検証用エンドポイント"""
    return 'LINE Webhook is working!', 200

if __name__ == '__main__':
    init_database()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

