# Design Doc

## アーキテクチャ概要
mama は Raspberry Pi 5 上で **AP/DHCP/DNS/FW** を担い、Gatekeeper（FastAPI）による申請審査と DNS ブロック制御を統合する。Gatekeeper は HTTP Basic 認証のローカル UI/API を提供し、OpenAI Responses API で判断した結果に基づいて dnsmasq のブロック状態を切り替える。

```
[Client] --WiFi--> [mama AP]
  -> DHCP/DNS (dnsmasq)
  -> FW/NAT (nftables)
  -> Gatekeeper (FastAPI)
  -> OpenAI Responses API (gpt-5.2)
```

## アーキテクチャ詳細
- **ネットワーク層**
  - `hostapd`: AP を提供。
  - `dnsmasq`: DHCP/DNS。ブロックドメインを `address=/domain/0.0.0.0` で遮断。
  - `nftables`: NAT とフォワード制御。
  - `sysctl`: IP フォワーディング有効化。
- **Gatekeeper**
  - FastAPI で `/`, `/request`, `/settings`, `/health` を提供。
  - 例外申請をローカル制限 → GPT 判定 → 状態更新の順に処理。
  - 解除状態は reward window / 例外 window を統合して判定。
  - バックグラウンド監視で次回切替時刻まで sleep し、解除/再遮断を自動反映。
- **自動起動**
  - `mama-net-apply.service`: ネットワーク設定を適用（oneshot）。
  - `mama-gatekeeper.service`: Gatekeeper を起動（`Requires=` で apply を前提）。

## データモデル / データフロー
### 主なモデル
- `AccessRequest`
  - `purpose`, `deadline`, `no_alternative`, `requested_minutes`
- `Decision`
  - `approved`, `minutes`, `reason`, `policy_flags`
- `State`
  - `active_until`, `reward_start`, `reward_enabled`, `daily_count`, `last_denied_at`, `last_reset_date`
- `AppConfig`
  - `NetworkConfig`, `GatekeeperConfig`, `RewardConfig`, `ExceptionPolicyConfig`

### フロー
1. **申請受付**: `/request` が JSON または form を受け取り `AccessRequest` に変換。
2. **ローカル制限**: 日次上限・クールダウンを評価。
3. **GPT 判定**: OpenAI Responses API で `Decision` を構造化出力で取得。
4. **状態更新**: 例外時間を `active_until` に反映、日次カウント更新。
5. **解除判定**: reward window / exception window を統合して解除状態を決定。
6. **DNS 適用**: dnsmasq 設定を更新し reload。
7. **バックグラウンド監視**: `next_transition` で次回切替時刻を計算し、自動的に再遮断/解除を反映。

## 各モジュールの概要
- `src/mama/config.py`
  - 設定モデル（Pydantic）。パスや閾値、タイムゾーンを管理。
- `src/mama/env.py`
  - 環境変数から `AppConfig` を構築。
- `src/mama/net/*`
  - `render.py`: 設定ファイル生成。
  - `apply.py`: 書き込み + reload (`dnsmasq` / `hostapd` / `nftables` / `sysctl`)。
- `src/mama/gatekeeper/*`
  - `app.py`: FastAPI / 認証 / 申請 / 設定更新。
  - `policy.py`: 日次上限・クールダウン評価。
  - `scheduler.py`: reward/exception window 判定。
  - `storage.py`: JSON/JSONL 永続化。
  - `openai_client.py`: Responses API 経由の判定。
- `src/mama/cli.py`
  - `apply-net` / `apply-dns` の CLI。
- `templates/index.html`
  - UI テンプレート（mama のローカル画面）。

## 内部仕様 / 処理フロー
- **apply-net**
  1. sysctl 設定を書き込み → `sysctl --system`
  2. hostapd 設定を書き込み → `systemctl restart hostapd`
  3. nftables 設定を書き込み → `nft -f <config>`
  4. dnsmasq 設定を書き込み → `systemctl reload dnsmasq`
- **apply-dns**
  - blocklist を空にする（解除） or 既定リストを適用（遮断） → dnsmasq reload
- **Fail-open**
  - GPT API 失敗時は申請分数をクランプして承認し、遮断解除を優先する。
