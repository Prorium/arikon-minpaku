# 有村昆の民泊塾 | 民泊収益シミュレーター

## 概要
民泊投資の収益性を簡単にシミュレーションできるWebアプリケーションです。

## 機能
- 地域別・物件タイプ別の収益シミュレーション
- 年間利回り・投資回収期間の自動計算
- LINE Bot連携による結果通知
- レスポンシブデザイン対応

## 技術スタック
- **フロントエンド**: React, JavaScript, CSS
- **バックエンド**: Flask, Python
- **データベース**: SQLite
- **API**: LINE Messaging API

## デプロイURL
https://vgh0i1coy709.manus.space

## LINE Webhook URL
https://vgh0i1coy709.manus.space/api/line/webhook

## セットアップ

### バックエンド
```bash
cd backend
pip install -r requirements.txt
python src/main.py
```

### フロントエンド
```bash
cd frontend
npm install
npm start
```

## LINE Bot設定
1. LINE Developer Consoleでチャネル作成
2. Webhook URL設定: `https://vgh0i1coy709.manus.space/api/line/webhook`
3. 応答メッセージ: オフ
4. Webhook: オン

## 使用方法
1. Webサイトでシミュレーション実行
2. LINEで「結果」と送信して最新結果を取得

## 作成者
有村昆 / LEONEX Inc.

