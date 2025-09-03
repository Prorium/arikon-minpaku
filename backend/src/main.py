import os
import sys
import sqlite3
import json
from datetime import datetime

# 環境変数を直接設定
os.environ['LINE_CHANNEL_SECRET'] = 'da9304a0ba9f50054710655d64a81680'
os.environ['LINE_CHANNEL_ACCESS_TOKEN'] = 'm/uvGJ0/dxSZqLea6jLhOm9F3bzPwBm3l83MUbnsQuyjLGtH0qnFBW2H8nrTnxKMu88ciaWcqQoNueyY3om+uM9A1xsOieHDZIxxkTZxye0A2g6tcFL2NHDRTl9DyTU2WSwoc9uHZBtjmbecDynmKAdB04t89/1O/w1cDnyilFU='
os.environ['LINE_CHANNEL_ID'] = '2007761838'

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

CORS(app)

# データベース初期化
def init_db():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'app.db')
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
    
    # LINEユーザーテーブル作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS line_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            display_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

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
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'app.db')
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

# LINE Webhook
@app.route('/api/line/webhook', methods=['POST'])
def line_webhook():
    try:
        # 最新のシミュレーション結果を取得
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'app.db')
        conn = sqlite3.connect(db_path)
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
            region, property_type, monthly_rent, annual_revenue, annual_costs, annual_profit, roi, recovery_period = result
            
            # 動的URLを取得
            base_url = request.host_url.rstrip('/')
            
            response_text = f"""🏠 最新のシミュレーション結果

📊 基本情報:
• 地域: {region}
• 物件タイプ: {property_type}
• 月額家賃: ¥{monthly_rent:,}

💰 収益分析:
• 年間売上: ¥{annual_revenue:,}
• 年間費用: ¥{annual_costs:,}
• 年間利益: ¥{annual_profit:,}
• 年間利回り: {roi}%
• 投資回収期間: {recovery_period}年

🌐 詳細はこちら:
{base_url}

💡 新しいシミュレーションを実行するには、上記URLにアクセスしてください。"""
        else:
            base_url = request.host_url.rstrip('/')
            response_text = f"""🏠 民泊収益シミュレーター

まだシミュレーション結果がありません。

🌐 シミュレーションを開始:
{base_url}

上記URLにアクセスして、あなたの民泊投資収益をシミュレーションしてみましょう！"""
        
        return jsonify({
            'replyToken': 'dummy',
            'messages': [{'type': 'text', 'text': response_text}]
        }), 200
        
    except Exception as e:
        print(f"LINE webhook error: {e}")
        return jsonify({'error': str(e)}), 200

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, "index.html")
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)

