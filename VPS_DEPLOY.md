# Human Resource AI - Ubuntu VPS配置手順

本手順は第1回記事の構成に合わせています。`.env`の実値は利用者側で設定してください。

## 1. VPSへ配置

```bash
sudo mkdir -p /opt/docker/human-resource-ai
sudo chown -R $USER:$USER /opt/docker/human-resource-ai
cd /opt/docker/human-resource-ai
```

修正版ソース一式をこのディレクトリへ配置します。

## 2. proxyネットワーク確認

```bash
docker network ls
```

`proxy`が存在することを確認します。存在しない場合のみ作成します。

```bash
docker network create proxy
```

## 3. .env設定

`.env.example`を参考に、VPS上で`.env`を作成してください。

```bash
nano .env
chmod 600 .env
```

`.env`の実値は本成果物では設定していません。

## 4. SQLiteと永続化ディレクトリ確認

既存の`database.db`を利用する場合はプロジェクトルートへ配置します。

```bash
mkdir -p uploads outputs
ls -l database.db
```

## 5. Compose設定確認

```bash
docker compose config
```

## 6. ビルド・起動

```bash
docker compose build
docker compose up -d
docker compose ps
```

## 7. ログ確認

```bash
docker compose logs -f human-resource-ai
```

Gunicornが`0.0.0.0:5000`で起動していることを確認します。

## 8. コンテナ内部から確認

```bash
docker compose exec human-resource-ai python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/login').status)"
```

`200`が返ればアプリケーションは起動しています。

## 9. proxyネットワーク参加確認

```bash
docker network inspect proxy
```

`human-resource-ai`が参加していることを確認します。

## 10. DNS設定

Human Resource AI用のホスト名をUbuntu VPSのグローバルIPへ向けます。例：

```text
hr.example.com -> Ubuntu VPSのグローバルIP
```

## 11. Nginx Proxy Manager

Proxy Hostを追加します。

| 項目 | 設定 |
| --- | --- |
| Domain Names | Human Resource AI用ドメイン |
| Scheme | `http` |
| Forward Hostname / IP | `human-resource-ai` |
| Forward Port | `5000` |
| Block Common Exploits | ON |

SSLタブでLet's Encrypt証明書を取得し、HTTPSを有効にします。

## 12. 外部動作確認

ブラウザからHuman Resource AI用HTTPS URLへアクセスし、ログイン画面、各ロール、社員管理、研修管理、評価管理、日報、RAG検索、FAQを確認します。

## 13. 更新手順

ソース更新後はHuman Resource AIだけを再ビルドします。

```bash
cd /opt/docker/human-resource-ai
docker compose build
docker compose up -d
docker compose ps
```

既存の他Composeプロジェクトを停止する必要はありません。

## 今回の主なソース修正

- Gunicorn追加
- Flask-WTF / CSRF保護追加
- POSTフォームへCSRFトークン追加
- FAQ JSON POSTへ`X-CSRFToken`追加
- `/login`へFlask-Limiterによる試行回数制限追加
- production時の動作確認用ユーザー自動作成を停止
- production時の`SECRET_KEY`必須化
- CookieのSecure / HttpOnly / SameSite設定
- `Dockerfile`追加
- `.dockerignore`追加
- `compose.yml`追加
- SQLite、uploads、outputsをVPS側へ永続化
- `proxy`外部ネットワークへ参加
- ホストへの5000番`ports`公開は行わず`expose`のみ使用

## 初期ログインパスワード

本番用の初期パスワードはソースコードへ直接記述せず、`.env` に設定します。

```env
ADMIN_INITIAL_PASSWORD=管理者用パスワード
STAFF_INITIAL_PASSWORD=担当者用パスワード
USER_INITIAL_PASSWORD=一般ユーザー用パスワード
EMP001_INITIAL_PASSWORD=EMP001用パスワード
```

初期ユーザー作成時にWerkzeugの `generate_password_hash()` でハッシュ化し、SQLiteにはハッシュ値を保存します。`.env` はGitへ登録しないでください。
