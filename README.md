# Python Template for Codex

開発を素早く立ち上げるための最小構成テンプレートです。`uv` を用いた依存管理、`ruff`/`pytest` による品質チェック、ドキュメント駆動のワークフローを前提としています。

## 前提ツールのインストール

- **uv**: 依存管理とコマンド実行に使用。
- **gh (GitHub CLI)**: PR 作成・レビュー対応に使用。

### macOS (Homebrew)
```bash
brew install uv gh
```

### Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh
```

インストール後、`uv --version` と `gh --version` が通ることを確認してください。

## 推奨ツールのインストール（任意）

検索・レビューを高速化するための推奨CLIツールです。

- ripgrep (`rg`), fd, bat, jq, yq (mikefarah版), git-delta (`delta`), direnv

### macOS (Homebrew)
```bash
brew install ripgrep fd bat jq yq git-delta direnv
```

### Debian/Ubuntu 系
```bash
sudo apt-get update
sudo apt-get install -y ripgrep fd-find bat jq git-delta direnv
# fd-find の実行ファイルは fdfind なので、fd にエイリアスを張る
command -v fd >/dev/null || sudo ln -s /usr/bin/fdfind /usr/local/bin/fd
# yq (mikefarah版) - バイナリ取得
curl -L https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 \
  -o /tmp/yq && sudo install /tmp/yq /usr/local/bin/yq
```

インストール後は `rg --version` などで動作確認してください。

## クイックスタート

```bash
uv sync            # 依存関係をインストール（.venv を作成）
make post-change   # format → lint → test を一括実行
uv run pytest -k ...  # 任意でテストを絞り込み
```

## 初回利用の流れ（テンプレート初期化）

1. Codexに `template-bootstrapper` を呼び出すよう指示し、リポジトリ名/パッケージ名/README/pyproject を初期化する。
2. そのタイミングで「このリポジトリで何をするか」を対話で明確化し、最初のプランを作成する。
   - 何を作るか（目的・成果物）
   - MVPのスコープとノンゴール
   - 期限・依存・実行環境の制約
   - 使用する技術

## 利用できるSkills（概要）

- `template-bootstrapper`: テンプレート初期化と初回プラン作成のガイド
- `planner`: 新規仕様追加・変更の要請を対話で明確化し、`plans/TEMPLATE.md` をコピーしてプランを作る
- `repo-guarder`: TDD/ドキュメント更新/禁止事項などのガードレール
- `uv-runner`: uvの依存管理・実行・トラブルシュート
- `pytest-driver`: 失敗テスト先行のTDDとテスト設計チェック
- `docs-maintainer`: REQUIREMENTS/DESIGNの上書き更新とCHANGELOG運用
- `gh-pr-runner`: gh CLIでのPR作成〜レビュー対応
- `utility-helper`: ローカル検索・差分・抽出系ツールの活用

## リポジトリ構成

- `src/python_template_for_codex/` : サンプルの Pydantic ベース設定モデル
- `tests/` : テンプレートのテスト（TDD の起点）
- `docs/REQUIREMENTS.md` : 現行の要求仕様
- `docs/DESIGN.md` : アーキテクチャと設計ドキュメント
- `plans/` : 仕様追加・変更時に作成するプラン置き場（`plans/TEMPLATE.md` を雛形に）
- `Makefile` : format/lint/test 用コマンド
- `.github/workflows/ci.yml` : GitHub Actions で `make post-change` を自動実行

## ワークフロー（抜粋）

1. 仕様追加・変更はまず `plans/` にプランを作成し、TDD で実装。
2. 非テストコードを触ったら必ず対応するテストを追加/更新。
3. 実装後は `make post-change` を実行しエラーが出ないことを確認する（CI も同じコマンドを実行）。
4. docs 下のドキュメントを最新状態に上書きで反映し、`plans/` 下のプランを削除する。

より詳細なルールやライフサイクルは `AGENTS.md` を参照してください。
