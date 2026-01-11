---
name: gh-pr-runner
description: gh CLIを用いてブランチ作成からPR作成・レビュー対応・マージまでを効率化する手順。PR運用が必要なときに使う。
license: Complete terms in LICENSE.txt
---

# gh PR Flow

## トリガ
- 変更をPRとしてまとめるとき
- レビュー指摘に対応するとき

## Quickstart
1. ブランチ作成: `git checkout -b <branch>`
2. 状態確認: `git status`, `git diff`
3. テスト: `make post-change`
4. PR作成:  
   - `gh pr create --fill`（タイトル/本文を自動生成）  
   - テンプレ修正が必要なら `gh pr create --title "..."`
5. レビュー確認: `gh pr view --web` または `gh pr view`
6. 指摘対応後: 変更→`git commit --amend`（許可される場合のみ）または新規commit → `git push`
7. マージ: `gh pr merge --squash`（方針に合わせて）  
   - デフォルトのマージ戦略はリポ方針に従うこと

## レビューワークフロー
- 変更差分を確認: `gh pr diff` / `gh pr checkout <PR#>`
- コメント返信: `gh pr comment <PR#> --body "<text>"`
- 必要ならローカルで再テストし、結果をコメント

## ベストプラクティス
- PRタイトルは「成果物」を先頭に（例: `Add skill plan-author`）
- 本文に目的/変更点/テスト結果/リスクを簡潔に記載（`--fill`後に修正）
- 1 PRあたりスコープを絞る（1〜2営業日以内）
- 破壊的操作やforce pushはリポ方針に従う。既存コミット改変は合意がある場合のみ。

## トラブル時
- 認証エラー: `gh auth login`
- リモート追従: `git fetch origin --prune`
- CI失敗: ログを確認し、必要ならテストをローカル再現
