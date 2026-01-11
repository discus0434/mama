---
name: uv-runner
description: uvを使った依存管理・実行・追加/削除・トラブルシュートの手順集。Pythonコマンド実行やパッケージ変更時に参照する。
license: Complete terms in LICENSE.txt
---

# uv Workflow

## Quickstart
- 環境構築: `uv sync`
- テスト/CIと同等: `make post-change`（format → lint → pytest）
- 単発実行: `uv run <script_or_module> ...`

## 依存追加/削除
- 本番依存追加: `uv add <pkg>[extras]==<version?>`
- 開発依存追加: `uv add --dev <pkg>`
- 削除: `uv remove <pkg>`
- 依存確認: `uv tree` / `uv pip list`

## よく使う実行例
- pytestを絞る: `uv run pytest -k "<pattern>"`
- 単一スクリプト: `uv run python path/to/script.py`
- Ruffのみ: `uv run ruff check .` / フォーマット: `uv run ruff format .`

## トラブルシュート
- venv破損/ズレ: `rm -rf .venv && uv sync`
- ロック差分調整: `uv lock`（必要なら実行）。`uv sync`で再解決。
- PATH衝突: 実行時に `UV_NO_SYNC=1` を付けて不要な自動同期を避ける
- キャッシュ疑い: `uv cache clean`

## 運用メモ
- 依存管理はuvに統一（pip/conda等は使用しない）
- pythonバージョンは `.python-version` と `pyproject.toml` の想定(3.12)に合わせる
- 変更後は`uv.lock`の更新有無を確認し、必要ならコミット対象に含める
