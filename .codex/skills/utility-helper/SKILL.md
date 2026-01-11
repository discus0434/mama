---
name: utility-helper
description: ローカルでのコード検索・差分閲覧・JSON/YAML抽出・環境切替を高速化するためのツールセット（rg/fd/bat/jq/yq/delta/direnv）。これらが遅い/見づらいときに使う。
license: Complete terms in LICENSE.txt
---

## トリガ（いつ使うか）
- コード検索が遅い/ノイズが多い → `rg` / `fd`
- JSON/YAMLから値を抜きたい → `jq` / `yq`
- 差分が読みにくい → `git diff | delta`
- 大きめファイルを色付きで一部だけ見たい → `bat`
- ブランチまたぎで PATH や秘密情報を自動切替したい → `direnv`

## Quickstart
1. 目的を特定（検索/差分/抽出/閲覧/環境切替）。
2. 手元にツールがあるか `rg --version` 等で確認。無ければ導入可否をユーザーに確認。
3. 下の速習コマンドから該当のものを選んで実行。

## 速習コマンド
- `rg foo src/` : .gitignore尊重で全文検索
- `rg "pattern" -g"*.py" -n --context 2` : 拡張子絞り+前後2行
- `rg --files-with-matches "pattern" src/` : ヒットしたファイル名のみ
- `fd config docs` : docs配下で名前にconfigを含むファイル
- `bat -n file.py` : 行番号付き表示（`-r 40:80` 範囲表示）
- `jq '.items[].id' data.json` : JSON配列からid抽出
- `yq '.jobs | keys' .github/workflows/ci.yml` : YAMLのキー一覧
- `git diff | delta` : カラー差分表示
- `direnv allow` : .envrcを許可してENV切替

## インストール（必要な場合のみ案内）
- macOS (Homebrew例): `brew install ripgrep fd bat jq yq git-delta direnv`
- Debian/Ubuntu例: `sudo apt-get install ripgrep fd-find bat jq git-delta direnv`  
  - `fd-find` は `fd` へシンボリックリンクを貼る: `sudo ln -s /usr/bin/fdfind /usr/local/bin/fd`
- CIには組み込まない。ローカル効率化目的で任意導入。

## 運用メモ
- プロジェクト必須にはしない（使える環境で活用する）
- 新しいツールを追加するときは、インストール手順と代表コマンド2–3個を追記する
