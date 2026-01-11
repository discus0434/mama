---
name: template-bootstrapper
description: このテンプレートリポジトリを新規プロジェクトに適用する初期化ガイド。パッケージ名リネーム、pyproject/README更新、uv初期同期、gh初期設定を行うときに使う。
license: Complete terms in LICENSE.txt
---

# Template Bootstrapper

## 前提
- `uv` と `gh` がインストール済み
- 新プロジェクト名（ケバブ/スネーク両方）を決めておく

## Quickstart
1. パッケージ名を決める: 例) プロジェクト名 `awesome-api` → パッケージ名 `awesome_api`
2. モジュールリネーム: `mv src/python_template_for_codex src/<package>`
3. プロジェクト名・パッケージ名を書き換える（手動）
   - 出現箇所を確認: `rg "python_template_for_codex"` / `rg "Python Template for Codex"`（閲覧のみ）
   - エディタで `<package>` / `<Project Title>` に置換（自動置換コマンドは使わない）
4. `pyproject.toml` を更新
   - `[project] name = "<project-name>"`
   - `dependencies`/`optional-dependencies`があれば必要に応じて調整
5. READMEを更新（タイトル、概要、セットアップ手順）
6. `planner` を呼び出して最初のプランを作成
7. `.python-version` を必要なら更新（デフォルト3.12）
8. 初期同期: `uv sync`
9. 動作確認: `make post-change`

## 置換チェックリスト
- `src/`, `tests/`, `pyproject.toml`, `README.md`, `docs/` 内の旧パッケージ名が残っていないか（`rg <old>`で確認して手動修正）
- インポートパス（`from python_template_for_codex import ...`）の置換漏れがないか
- `uv.lock` の更新有無を確認

## 運用メモ
- 余計なファイルを残さない（このスキルはdocsを直接編集しない）
- 初期コミット前に `git status` で不要差分を掃除
- 依存追加は`uv add`、不要なら`uv remove`で調整
