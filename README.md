# mama

Raspberry Pi 5 上で動く、WiFi 内の DNS を制御するゲートキーパー。X / YouTube / TikTok を遮断し、
1 日 1 時間のご褒美タイムと、GPT-5.2 による例外申請（5〜30分）で解除します。

## 概要

- mama が AP/DHCP/DNS/FW を担い、端末は mama の SSID に接続する
- 既存ルーター設定には依存しない（上流はインターネット回線として扱う）
- 例外申請はローカル Web UI から行い、GPT-5.2 が判定する

## 対象環境

- Raspberry Pi 5
- Raspberry Pi OS 64-bit

## 使い方（Raspberry Pi 実機）

### 1. 依存関係の準備

```bash
uv sync
```

### 2. 環境変数ファイルを用意

```bash
sudo mkdir -p /etc/mama
sudo cp scripts/mama.env.example /etc/mama/mama.env
sudo ${EDITOR:-nano} /etc/mama/mama.env
```

最低限、以下を自分用に設定してください。
- `MAMA_SSID`
- `MAMA_PASSPHRASE`
- `MAMA_AUTH_PASSWORD`
- `MAMA_OPENAI_API_KEY`

### 3. ブロックリスト配置

デフォルトは `data/blocklists/` を使います。運用向けには以下のように配置すると便利です。

```bash
sudo mkdir -p /opt/mama/data/blocklists
sudo cp data/blocklists/*.txt /opt/mama/data/blocklists/
```

`/etc/mama/mama.env` の `MAMA_BLOCKLIST_DIR` を `/opt/mama/data/blocklists` に設定してください。

### 4. ネットワーク設定を適用

```bash
sudo uv run mama apply-net
```

> hostapd / dnsmasq / nftables / sysctl を適用します。root 権限が必要です。

### 5. Gatekeeper を起動

```bash
uv run python -m mama.gatekeeper.runtime
```

ブラウザで `http://192.168.50.1:8080` にアクセス（Basic 認証）します。  
（IP やポートは `MAMA_LAN_ADDRESS` / `MAMA_GATEKEEPER_PORT` で変更可能）

### 6. systemd で自動起動（推奨）

```bash
sudo cp scripts/systemd/mama-net-apply.service /etc/systemd/system/
sudo cp scripts/systemd/mama-gatekeeper.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mama-net-apply.service mama-gatekeeper.service
```

> `scripts/systemd/mama-gatekeeper.service` の `WorkingDirectory` は `/opt/mama` 前提です。  
> リポジトリ配置に合わせて変更してください。

## 便利コマンド

```bash
# DNS ブロックを適用（標準）
sudo uv run mama apply-dns

# 一時的に DNS ブロック解除
sudo uv run mama apply-dns --unblock
```

## ブロック対象の更新

`data/blocklists/*.txt`（または `MAMA_BLOCKLIST_DIR` 配下）を編集後、`mama apply-dns` を実行してください。

## 開発セットアップ

```bash
uv sync            # 依存関係をインストール（.venv を作成）
make post-change   # format → lint → test を一括実行
uv run pytest -k ...  # 任意でテストを絞り込み
```

## ワークフロー

- 仕様追加・変更は `plans/` にプランを作成し、TDD で実装
- 実装後は `make post-change` を実行
- docs は現況を上書き更新し、履歴は `docs/CHANGELOG.md` に集約

詳細は `AGENTS.md` を参照してください。
