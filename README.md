# Badara Server

## 技術スタック (Tech Stack)

このプロジェクトは以下の技術スタックを使用しています。

*   **Webフレームワーク**: FastAPI (Python)
*   **データベース**: MySQL
*   **ORM (Object-Relational Mapping)**: SQLAlchemy
*   **認証**: JWT (JSON Web Tokens) (python-jose), bcrypt (passlib)
*   **環境変数管理**: python-dotenv
*   **ASGIサーバー**: Uvicorn

## バージョン情報 (Version Information)

*   **Python**: 3.9+
*   **FastAPI**: 最新互換バージョン
*   **Uvicorn**: 最新互換バージョン
*   **SQLAlchemy**: 最新互換バージョン
*   **MySQL**: 8.0.28
*   **bcrypt**: 4.0.1

## 実行方法 (How to Run)

### 1. 環境構築 (Environment Setup)

*   Python 3.x がインストールされていることを確認してください。
*   Docker および Docker Compose がインストールされていることを確認してください。

### 2. 依存関係のインストール (Install Dependencies)

プロジェクトのルートディレクトリで以下のコマンドを実行し、必要なPythonパッケージをインストールします。

```bash
pip install -r requirements.txt
```

### 3. データベースの起動 (Start Database)

Docker Compose を使用してMySQLデータベースを起動します。

```bash
docker-compose -f etc/db/docker-compose.yml up -d
```

### 4. 環境変数の設定 (Environment Variables Configuration)

プロジェクトのルートディレクトリに `.env` ファイルを作成し、必要な環境変数を設定します。
例:

```
DATABASE_URL="mysql+pymysql://user:password@localhost:3306/badara_dev"
TOKEN_SECRET_KEY="your_super_secret_key_here"
```

*   `TOKEN_SECRET_KEY` は `auth/authManager.py` にハードコードされていますが、セキュリティのために `.env` ファイルで管理することを推奨します。

### 5. アプリケーションの起動 (Start Application)

以下のコマンドを実行してFastAPIアプリケーションを起動します。

```bash
uvicorn main:app --reload
```

*   `--reload` オプションは、コードの変更を検知すると自動的にサーバーを再起動します。これは開発中に非常に便利です。
