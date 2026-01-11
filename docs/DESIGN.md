# Design Doc

## アーキテクチャ概要
本テンプレートは「設定モデル + テスト + 品質コマンド + ドキュメント」で構成される最小スケルトンであり、依存管理に `uv`、品質管理に `ruff` / `pytest` を採用する。アプリケーションコードは `src/python_template_for_codex` 配下に集約し、テストは `tests/` に配置する。

## アーキテクチャ詳細
- **パッケージ構成**: `src/python_template_for_codex` を単一パッケージとしてビルド対象に登録。
- **設定モデル**: `ApplicationConfig`（Pydantic v2）でアプリ名・バージョン・デバッグフラグを管理。入力バリデーションとデフォルト適用を担当。
- **品質ゲート**: `Makefile` 経由で `ruff format` → `ruff check` → `pytest` を実行する `post-change` ターゲットを提供し、変更時のチェックを統一。
- **CI/CD**: GitHub Actions (`.github/workflows/ci.yml`) で Push / PR ごとに `make post-change` を実行し、ローカルと同一の品質ゲートを強制。
- **ドキュメント**: 要求仕様（`docs/REQUIREMENTS.md`）と設計（本ドキュメント）を最新状態に保ち、履歴ではなく現況を記載する。

## データモデル / データフロー
- `ApplicationConfig`
  - `name: str` — サービス識別子（必須）
  - `version: str` — `MAJOR.MINOR.PATCH` 形式のバージョン（必須）
  - `debug: bool = False` — デバッグ挙動の有効/無効
  - `field_validator("version")` で先頭の "v" を許容しつつ SemVer 形式へ正規化する。
- フロー: 入力（dict など）→ Pydantic による検証・正規化 → `ApplicationConfig` インスタンスとしてアプリに供給。

## 各パートの概要
- **config.py**: 設定モデルの定義と軽微な正規化ロジック。
- **tests/**: 設定モデルに対する正常系・異常系テスト。TDD の起点となる。
- **Makefile**: 開発者が覚えるコマンドを最小化し、フォーマット・Lint・テストを統一。
- **plans/**: 仕様追加・変更ごとの計画を置くディレクトリ。`TEMPLATE.md` を雛形として利用する。

## 内部仕様 / 処理フロー
1. 開発開始時に `uv sync` で環境を構築し、`uv.lock` に依存をロック。
2. 仕様追加・変更は `plans/` にプランを作成（1開発単位）。TDD でテスト→実装の順に進める。
3. 実装後に `make post-change` を実行して format/lint/test を通し、`docs/` を上書きで最新状態に保つ。
4. プランが完了したら `plans/` から削除し、ドキュメントへ反映する。
