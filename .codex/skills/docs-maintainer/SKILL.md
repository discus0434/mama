---
name: docs-maintainer
description: docs/REQUIREMENTS.md と docs/DESIGN.md を現況に上書き更新し、docs/CHANGELOG.md に履歴を集約するためのガイド。仕様変更や設計更新を反映するときに使う。
license: Complete terms in LICENSE.txt
---

# Docs Maintainer

## トリガ
- 仕様・設計が確定したとき
- 実装変更に伴い要求/設計の記述を更新するとき

## 原則
- docs配下は「確定した現況のみ」を記述（追記形式にしない）
- 履歴は `docs/CHANGELOG.md` に集約
- 設計/要求は上書き更新で常に最新

## 更新手順
1. 対応範囲を決める: REQUIREMENTSかDESIGNか、両方か
2. 現行内容を読み、不要/古い記述を削除・書き換え（追記しない）
3. 新仕様・設計を反映し、用語・整合性を確認
4. 変更概要を `docs/CHANGELOG.md` に日付降順で追記
5. 必要に応じて関連ファイル（例: 図やサンプル）を更新

## チェックリスト
- 要求と設計が矛盾していないか
- 用語の表記ゆれを統一したか
- 不要になった節を残していないか
- 変更箇所がテストでカバーされているか（別プランのテストを確認）
- パスやファイル名の整合性を確認したか

## 運用メモ
- docsのみ更新なら`make post-change`は任意だが、リンクやパスは目視確認
- 図や補足が必要なら `docs/` に追加し、本文から参照する（README等は作らない）
