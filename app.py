from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import hashlib

app = Flask(__name__)
CORS(app)

# In-memory storage for simulation results (in production, use a database)
simulation_results = {}

# Configuration
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', '')

# Region data
REGIONS = {
    'tokyo': {'name': '東京都', 'price': 8500, 'occupancy': 75},
    'osaka': {'name': '大阪府', 'price': 6500, 'occupancy': 70},
    'kyoto': {'name': '京都府', 'price': 7000, 'occupancy': 68},
    'kanagawa': {'name': '神奈川県', 'price': 7500, 'occupancy': 72},
    'aichi': {'name': '愛知県', 'price': 5500, 'occupancy': 65},
    'fukuoka': {'name': '福岡県', 'price': 4500, 'occupancy': 62}
}

MINPAKU_LAWS = {
    'shinpo': {'name': '民泊新法対応', 'days': 180},
    'ryokan': {'name': '旅館業法', 'days': 365},
    'tokku': {'name': '特区民泊', 'days': 365}
}

OPERATION_TYPES = {
    'rental': {'name': '転貸', 'subtitle': '賃貸物件で民泊運営'},
    'purchase': {'name': '購入', 'subtitle': '物件購入して民泊運営'}
}

def calculate_simulation_results(data):
    """Calculate detailed simulation results"""
    try:
        # Get region data
        region_data = REGIONS.get(data['region'], {})
        daily_price = region_data.get('price', 0)
        occupancy_rate = region_data.get('occupancy', 0) / 100
        
        # Get minpaku law data
        law_data = MINPAKU_LAWS.get(data['minpakuLaw'], {})
        max_days = law_data.get('days', 365)
        
        # Calculate basic metrics
        area = int(data.get('customArea') or data.get('area', 0))
        capacity = int(data.get('capacity', 1))
        
        # Annual revenue calculation
        annual_operating_days = min(max_days, 365)
        actual_operating_days = int(annual_operating_days * occupancy_rate)
        annual_revenue = daily_price * actual_operating_days
        
        # Cost calculations
        renovation_cost = int(data.get('renovationCost', 0)) * 10000  # Convert to yen
        
        if data['operationType'] == 'rental':
            monthly_rent = int(data.get('monthlyRent', 0))
            annual_rent = monthly_rent * 12
            
            # Initial costs
            initial_costs = data.get('initialCosts', {})
            total_initial_costs = sum(int(cost) for cost in initial_costs.values() if cost)
            
            # Total investment
            total_investment = renovation_cost + total_initial_costs
            
            # Annual profit
            annual_profit = annual_revenue - annual_rent
            
        else:  # purchase
            purchase_price = int(data.get('purchasePrice', 0)) * 10000  # Convert to yen
            total_investment = purchase_price + renovation_cost
            annual_profit = annual_revenue
        
        # ROI calculation
        roi = (annual_profit / total_investment * 100) if total_investment > 0 else 0
        payback_period = (total_investment / annual_profit) if annual_profit > 0 else float('inf')
        
        # Monthly breakdown
        monthly_revenue = annual_revenue / 12
        monthly_profit = annual_profit / 12
        
        return {
            'region': region_data.get('name', ''),
            'operationType': OPERATION_TYPES.get(data['operationType'], {}).get('name', ''),
            'propertyType': data.get('propertyType', ''),
            'area': area,
            'capacity': capacity,
            'minpakuLaw': law_data.get('name', ''),
            'dailyPrice': daily_price,
            'occupancyRate': occupancy_rate * 100,
            'actualOperatingDays': actual_operating_days,
            'annualRevenue': annual_revenue,
            'annualProfit': annual_profit,
            'totalInvestment': total_investment,
            'roi': roi,
            'paybackPeriod': payback_period,
            'monthlyRevenue': monthly_revenue,
            'monthlyProfit': monthly_profit,
            'renovationCost': renovation_cost,
            'monthlyRent': int(data.get('monthlyRent', 0)) if data['operationType'] == 'rental' else 0,
            'purchasePrice': int(data.get('purchasePrice', 0)) * 10000 if data['operationType'] == 'purchase' else 0,
            'initialCosts': data.get('initialCosts', {}) if data['operationType'] == 'rental' else {},
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Calculation error: {e}")
        return None

def format_result_message(results):
    """Format simulation results for LINE message"""
    if not results:
        return "計算エラーが発生しました。"
    
    message = f"""🏠 民泊収益シミュレーション結果

📍 基本情報
地域: {results['region']}
運営形態: {results['operationType']}
物件: {results['propertyType']} {results['area']}㎡
収容人数: {results['capacity']}名
民泊法: {results['minpakuLaw']}

💰 収益予測
1泊単価: ¥{results['dailyPrice']:,}
稼働率: {results['occupancyRate']:.1f}%
年間稼働日数: {results['actualOperatingDays']}日

年間売上: ¥{results['annualRevenue']:,}
年間利益: ¥{results['annualProfit']:,}
月間売上: ¥{results['monthlyRevenue']:,.0f}
月間利益: ¥{results['monthlyProfit']:,.0f}

📊 投資指標
総投資額: ¥{results['totalInvestment']:,}
ROI: {results['roi']:.1f}%
投資回収期間: {results['paybackPeriod']:.1f}年

💡 この結果は概算です。実際の運営では清掃費、光熱費、管理費等の運営コストも考慮してください。

詳細な相談は有村昆の民泊塾まで！"""

    return message

@app.route('/api/simulation', methods=['POST'])
def save_simulation():
    """Save simulation data and return success"""
    try:
        data = request.json
        
        # Generate unique ID for this simulation
        simulation_id = hashlib.md5(
            (str(data) + str(datetime.now())).encode()
        ).hexdigest()[:8]
        
        # Calculate results
        results = calculate_simulation_results(data)
        
        if results:
            # Store results with ID
            simulation_results[simulation_id] = results
            
            # Also store with a simple key for LINE bot access
            # In a real app, you'd associate this with the user's LINE ID
            simulation_results['latest'] = results
            
            return jsonify({
                'success': True,
                'simulationId': simulation_id,
                'message': 'シミュレーションが完了しました'
            })
        else:
            return jsonify({
                'success': False,
                'message': '計算エラーが発生しました'
            }), 400
            
    except Exception as e:
        print(f"Simulation error: {e}")
        return jsonify({
            'success': False,
            'message': '計算中にエラーが発生しました'
        }), 500

@app.route('/api/webhook', methods=['POST'])
def line_webhook():
    """Handle LINE webhook events"""
    try:
        body = request.get_data(as_text=True)
        events = json.loads(body).get('events', [])
        
        for event in events:
            if event['type'] == 'message' and event['message']['type'] == 'text':
                user_message = event['message']['text'].strip()
                reply_token = event['replyToken']
                
                if user_message == '結果':
                    # Get latest simulation results
                    latest_results = simulation_results.get('latest')
                    
                    if latest_results:
                        response_message = format_result_message(latest_results)
                    else:
                        response_message = """まだシミュレーション結果がありません。

以下の手順でシミュレーションを実行してください：
1. 民泊シミュレーターサイトにアクセス
2. 必要な情報を入力
3. 「結果を計算」ボタンをクリック
4. 再度「結果」とメッセージを送信

サイト: https://prorium.github.io/arikon-minpaku/"""
                    
                    # Send reply (in production, use LINE Messaging API)
                    send_line_reply(reply_token, response_message)
                
                elif user_message in ['こんにちは', 'はじめまして', 'ヘルプ']:
                    response_message = """🏠 有村昆の民泊塾へようこそ！

民泊収益シミュレーターの使い方：

1. シミュレーターサイトで物件情報を入力
2. 「結果を計算」ボタンをクリック
3. このLINEで「結果」と送信
4. 詳細な収益予測を確認

サイト: https://prorium.github.io/arikon-minpaku/

何かご質問があれば、お気軽にお声かけください！"""
                    
                    send_line_reply(reply_token, response_message)
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'status': 'error'}), 500

def send_line_reply(reply_token, message):
    """Send reply message via LINE Messaging API"""
    # In production, implement actual LINE Messaging API call
    # For now, just log the message
    print(f"LINE Reply: {message}")
    
    # Uncomment and configure for production:
    """
    import requests
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    
    data = {
        'replyToken': reply_token,
        'messages': [{
            'type': 'text',
            'text': message
        }]
    }
    
    response = requests.post(
        'https://api.line.me/v2/bot/message/reply',
        headers=headers,
        json=data
    )
    """

@app.route('/api/results/<simulation_id>', methods=['GET'])
def get_simulation_results(simulation_id):
    """Get simulation results by ID"""
    results = simulation_results.get(simulation_id)
    
    if results:
        return jsonify({
            'success': True,
            'results': results
        })
    else:
        return jsonify({
            'success': False,
            'message': 'シミュレーション結果が見つかりません'
        }), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'stored_results': len(simulation_results)
    })

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'message': '有村昆の民泊塾 - 民泊収益シミュレーター API',
        'version': '1.0.0',
        'endpoints': {
            'simulation': '/api/simulation (POST)',
            'webhook': '/api/webhook (POST)',
            'results': '/api/results/<id> (GET)',
            'health': '/api/health (GET)'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

