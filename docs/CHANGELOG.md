# CHANGELOG

## 記載ルール
- 日付降順で追記する（YYYY-MM-DD）。
- 変更概要と関連PR/Issueがあれば併記する。
- 仕様・設計ドキュメントは常に現況を上書きで反映し、履歴は本ファイルに集約する。

## エントリ
- 2026-01-11: 日次カウントのリセット条件を時計逆行に強くし、Gatekeeper の時刻取得を注入可能にしてテストを安定化。
- 2026-01-11: Gatekeeper の起動/停止を FastAPI lifespan に移行し、on_event の非推奨警告を解消。
- 2026-01-11: mama MVP を実装（設定モデル、dnsmasq/hostapd/nftables/sysctl の生成・適用、Gatekeeper UI/申請/判定、OpenAI 連携、JSONL ログ、CLI、systemd ユニット、ブロックリスト同梱）。
