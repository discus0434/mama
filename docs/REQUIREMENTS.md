# 要求仕様

## 目的
Python プロジェクトを `uv` / `ruff` / `pytest` を軸に素早く立ち上げるためのテンプレートを提供する。TDD と計画駆動の開発フローを標準化し、ドキュメントを常に現況へ同期させる。

## 機能要件
- 依存管理は `uv` を用い、Python 3.12 で動作する。
- 最小限のサンプルコードとして Pydantic ベースの `ApplicationConfig` モデルを提供する。
  - デフォルトで `debug=False`、`name` と `version` を必須とする。
  - `version` は `MAJOR.MINOR.PATCH` 形式（例: `1.2.3`）を受け付ける。
- テストは `pytest` で実行でき、サンプルモデルに対する正常系・異常系テストが用意されている。
- `Makefile` から `format`（ruff format）、`lint`（ruff check）、`test`（pytest）、`post-change`（上記一括）が実行できる。

## 非機能要件
- コードスタイルは Ruff の設定に従い、行長 88、インデント幅 4。
- ドキュメントは `docs/` 配下に置き、仕様変更時は内容を上書きし常に最新状態を保つ。
- プランニングは `plans/` 配下に 1 開発単位ごとに作成し、完了後は削除してドキュメントへ反映する。

## 運用要件
- 変更時は TDD を実施し、非テストコードの変更に対しテストを必ず追加・更新する。
- `make post-change` を変更毎に実行し、format/lint/test の全てを通す。
- 依存の再現性確保のため `uv.lock` を生成し、リポジトリに含める。
- Push / PR 時は GitHub Actions（`.github/workflows/ci.yml`）で `make post-change` を実行し、品質チェックを自動化する。
