# AI人事・研修業務支援システム

AI業務アプリケーションをUbuntu VPSのDocker環境へ公開する 〜Gunicorn・Nginx Proxy Manager・HTTPS〜

## ロール別アクセス権限

| 機能 | user | staff | admin |
|---|:---:|:---:|:---:|
| ダッシュボード | ✅ | ✅ | ✅ |
| 社員一覧・検索 | ❌ | ✅ | ✅ |
| 社員登録・更新 | ❌ | ✅ | ✅ |
| 社員削除 | ❌ | ❌ | ✅ |
| 研修一覧 | ❌ | ✅ | ✅ |
| 研修登録・履歴入力 | ❌ | ✅ | ✅ |
| 評価管理・AIコメント生成 | ❌ | ✅ | ✅ |
| Excel取込・出力 | ❌ | ✅ | ✅ |
| 日報登録・確認 | ✅ | ✅ | ✅ |
| 社内文書検索 | ✅ | ✅ | ✅ |
| FAQチャット | ✅ | ✅ | ✅ |


## 追加済み機能

- 社員CRUD
- 研修登録・研修履歴入力
- 評価一覧・AIコメント生成
- Excel取込・Excel出力
- 日報登録・一覧
- 社内文書検索
- FAQチャット
- ログイン認証
- ロール別認可（user / staff / admin）
- 社員番号ログインと社員本人用マイページ
- CSS / JavaScript

Difyを使う場合は `.env` に `DIFY_API_KEY` を設定してください。未設定の場合はローカル確認用のダミー回答で動作します。


## DB初期化手順(PowerShellで以下を実行)
 - Remove-Item .\database.db
 - python create_admin.py

