---
name: repo-guarder
description: このリポジトリで変更を行う際の必須ガードレール（TDD、docs更新、禁止事項）を短縮版で提供。コード/ドキュメント/テストの変更開始前に参照する。
license: Complete terms in LICENSE.txt
---

# Repo Guarder

## まず確認すること
- 変更はTDDで進めるか？（先に失敗テストを書く）
- 非テストコードを触るなら対応テストを追加/更新するか？
- docs/ の現況を上書き更新できるか？（追記ではなく更新）
- 禁止操作をしないか？（下記参照）

## ライフサイクル（仕様追加・変更の標準手順）
1. **プラン作成**: `plans/TEMPLATE.md` をコピーして埋める（1〜2営業日サイズ）。リスクが高ければ分割。
2. **テスト先行**: 変更点に対応する失敗テストを追加（正常/異常/境界/NotFound/権限の両面）。
3. **実装**: 最小実装→リファクタ。遅延import・不要フォールバックは禁止。
4. **検証**: `make post-change`（ruff format+lint+pytest）。必要に応じて限定pytest。
5. **セルフレビュー**: plan-reviewer でプランとコード/テストの一致を確認し、乖離があれば修正。
6. **ドキュメント**: docs/REQUIREMENTS.md / docs/DESIGN.md を現況で上書き。履歴は `docs/CHANGELOG.md` に日付降順で追記。
7. **クリーンアップ**: プランの完了条件を満たしたら plans/ から削除。

## TODO更新
- プランに記載したTODOは「開始/完了/中断」の節目で更新する（開始→in_progress、完了→done、中断→blocked/hold+理由1行）。
- ユーザーに制御を返す前に、最低1回はTODOの状態を最新化する。
- 2ターン以上かかりそうなTODOは、可能なら分割して追跡する。

## Pythonルール
- Python 3.12 前提。型は標準形（`dict[str, int]` など）、`from __future__ import annotations` は使わない。
- 依存管理・実行は `uv` に統一（`uv sync` / `uv run ...` / `uv add/remove`）。pip/poetry等は使わない。
- import はファイル先頭にまとめ、遅延importはしない。
- データモデルは Pydantic を使用。
- 不要なフォールバックや黙殺は避け、エラーは明示的に raise。

## Decision Tree（着手前）
- **コードを変える?**
  - はい → 先にテストを書く → 実装 → `make post-change`
  - いいえ → 次へ
- **ドキュメントだけ?**
  - はい → docsを現況に上書き → `docs/CHANGELOG.md` 追記 → 必要なら `make post-change`（任意）
  - いいえ → 次へ
- **テスト追加のみ?**
  - はい → 新テストが実装変更をカバーするか確認 → `make post-change`

## DO
- `uv sync` で環境統一、実行は `uv run ...`
- テストは正常/異常/境界/NotFound/権限など到達可能な分岐を両面で書く
- docs更新後は必ず現況に整える（履歴はCHANGELOGへ）

## DON'T
- `git reset --hard`, `git checkout --` など破壊的操作（ユーザー明示指示なしで禁止）
- 遅延importの追加や不要なフォールバック
- READMEやdocsへの追記形式の更新（現況上書きが原則）
- python以外の依存管理ツール追加（pip/env切替など）

## 実行チェック（作業後）
- `make post-change` で format/lint/pytest を一括確認
- 変更がdocsのみなら任意だが、リンクやパスを目視で再確認

## トラブル時
- 環境ずれ: `.venv` を削除→`uv sync`
- テスト失敗: 該当テストを開き、想定分岐が網羅されているか確認
- docsの整合性: リンク切れや表記ゆれは目視で修正し、必要なら再度 `make post-change`
