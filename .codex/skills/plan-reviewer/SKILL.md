---
name: plan-reviewer
description: プラン実装後・docs更新前に必ず使うレビュースキル。プランと現コード/テストの一致を別エージェントに確認させ、乖離を洗い出して修正を実施する。
license: Complete terms in LICENSE.txt
---

# Plan Reviewer

## 目的
- プランと現コード/テストの**一致**を確認し、乖離を洗い出して修正を実施する。
- レビューエージェントに洗い出しのみ行わせ、あなたが修正を実施する。

## トリガ
- 実装が完了し、**docs更新に入る直前**
- 「プラン通りに実装できているか」確認したいとき

## 役割分担

### あなた（メインエージェント）
- `make plan-review` を実行してレビュー結果を取得する。
- 出力のGAP/FIXをもとに修正する。
- 乖離がゼロになるまで **レビュー→修正** を繰り返す。
- 計画変更の合意が必要なズレはユーザーに確認する。

## 運用フロー（ループ）
1. `make plan-review PROMPT="<プロンプト>"` で乖離を洗い出す。
2. 出力のGAP/FIXをもとに修正する。
3. 再度 `make plan-review PROMPT="<プロンプト>"` を実行する。乖離（GAP）がゼロになるまで繰り返す。

## 入力
- 対象プラン: `plans/<plan-name>.md`

## レビューの呼び出しコマンド
- レビューはPROMPTを渡して別エージェントで実行する（出力は stdout。`/tmp/plan-review.txt` にも同じものが保存される）。
  - `make plan-review PROMPT="<プロンプト>"`

## プロンプトテンプレ
```
You are a strict, read-only plan-review agent. Do not modify files.
Follow the plan-review agent procedure in this skill:
1) Extract plan items from "確定事項/設計/タスク/テスト".
2) Only inspect files explicitly listed in the plan. You do NOT need to scan the repository.
3) Verify implementation: planned files exist, modules/classes/functions match responsibilities, data models/validation match, tests cover normal/abnormal/boundary cases.
4) List all gaps and mismatches. If a listed file is missing or you cannot verify it, mark it as GAP.
Output ONLY the Self-Review Summary with OK/GAP/FIX. In GAP/FIX, cite concrete file paths and plan sections when possible.
Then exit.
```

## 注意
- プラン自体が誤っていると判明した場合や、プランと実装が著しく乖離し修正不可能だと判断した場合は、修正前にユーザーへ確認し合意を取る。
