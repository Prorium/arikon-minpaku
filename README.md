# 有村昆の民泊塾 | 民泊収益シミュレーター

## 概要
民泊投資の収益性を簡単にシミュレーションできるWebアプリケーションです。
**LINE Bot連携必須** - シミュレーション結果をLINEで自動通知

## 🌐 デプロイURL
- **フロントエンド**: https://prorium.github.io/arikon-minpaku/
- **バックエンドAPI**: https://your-api-server.herokuapp.com
- **LINE Webhook**: https://your-api-server.herokuapp.com/api/line/webhook

## ✨ 機能
- 地域別・物件タイプ別の収益シミュレーション
- 年間利回り・投資回収期間の自動計算
- **LINE Bot連携による結果通知（必須機能）**
- レスポンシブデザイン対応
- GitHub Pages対応の静的サイト

## 🛠 技術スタック
- **フロントエンド**: React (CDN), JavaScript, Tailwind CSS (GitHub Pages)
- **バックエンド**: Flask, Python (Heroku/Vercel推奨)
- **データベース**: SQLite
- **API**: LINE Messaging API（必須）

## 📦 デプロイ手順

### 1. フロントエンド (GitHub Pages)
```bash
# このリポジトリをフォーク
git clone https://github.com/Prorium/arikon-minpaku.git
cd arikon-minpaku

# GitHub Pagesで公開
# Settings > Pages > Source: Deploy from a branch
# Branch: main, Folder: / (root)
```

### 2. バックエンド (Heroku推奨)
```bash
# backend/フォルダを別リポジトリまたはHerokuにデプロイ
cd backend

# Herokuにデプロイ
heroku create your-app-name
git add .
git commit -m "Deploy backend"
git push heroku main

# 環境変数設定
heroku config:set LINE_CHANNEL_SECRET=your_channel_secret
heroku config:set LINE_CHANNEL_ACCESS_TOKEN=your_access_token
heroku config:set LINE_CHANNEL_ID=your_channel_id
heroku config:set FRONTEND_URL=https://prorium.github.io/arikon-minpaku/
```

### 3. フロントエンドのAPI設定
`index.html`の`CONFIG`オブジェクトを更新：
```javascript
const CONFIG = {
    API_BASE_URL: 'https://your-app-name.herokuapp.com',
    GITHUB_PAGES_URL: 'https://prorium.github.io/arikon-minpaku/'
};
```

## 📱 LINE Bot設定（必須手順）

### 1. LINE Developer Console
1. https://developers.line.biz/console/ にアクセス
2. 新しいチャネル作成（Messaging API）
3. 以下の情報を取得：
   - Channel Secret
   - Channel Access Token
   - Channel ID

### 2. Webhook設定
```
Webhook URL: https://your-app-name.herokuapp.com/api/line/webhook
Webhookの利用: オン
応答メッセージ: オフ（重要！）
```

### 3. 環境変数設定
```bash
# Herokuの場合
heroku config:set LINE_CHANNEL_SECRET=your_actual_channel_secret
heroku config:set LINE_CHANNEL_ACCESS_TOKEN=your_actual_access_token
heroku config:set LINE_CHANNEL_ID=your_actual_channel_id
```

## 🚀 使用方法
1. https://prorium.github.io/arikon-minpaku/ でシミュレーション実行
2. **LINEで「結果」と送信して最新結果を取得（メイン機能）**

## 🔧 ローカル開発

### バックエンド
```bash
cd backend
pip install -r requirements.txt

# 環境変数設定
export LINE_CHANNEL_SECRET=your_channel_secret
export LINE_CHANNEL_ACCESS_TOKEN=your_access_token
export LINE_CHANNEL_ID=your_channel_id
export FRONTEND_URL=http://localhost:3000

python main.py
```

### フロントエンド
```bash
# index.htmlをブラウザで開く
# または簡易サーバー起動
python -m http.server 3000
```

## 📋 ファイル構成
```
arikon-minpaku/
├── index.html              # GitHub Pages用メインファイル
├── README.md               # このファイル
└── backend/
    ├── main.py             # Flask APIサーバー
    ├── requirements.txt    # Python依存関係
    └── database/           # SQLiteデータベース（自動作成）
```

## 🔍 トラブルシューティング

### CORS エラー
- バックエンドのCORS設定を確認
- GitHub PagesのURLが許可されているか確認

### LINE Webhook エラー
- Webhook URLが正しく設定されているか確認
- 環境変数が正しく設定されているか確認
- `/api/line/webhook`エンドポイントにGETアクセスして動作確認

### API接続エラー
- バックエンドサーバーが起動しているか確認
- `CONFIG.API_BASE_URL`が正しく設定されているか確認

## 📞 サポート
- GitHub Issues: https://github.com/Prorium/arikon-minpaku/issues
- 作成者: 有村昆 / LEONEX Inc.

## 📄 ライセンス
MIT License

---

**🎯 重要**: LINE Bot連携は必須機能です。必ずLINE Developer Consoleでの設定を完了してください。

