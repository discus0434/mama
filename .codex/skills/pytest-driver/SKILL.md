---
name: pytest-driver
description: 仕様追加・変更時にpytestで先に失敗するテストを書き、正常/異常/境界を網羅するためのTDDガイド。テスト設計と最小実装の往復時に使う。
license: Complete terms in LICENSE.txt
---

# Pytest TDD

## トリガ
- 非テストコードを変更する前
- 新しい分岐や例外を追加するとき
- 既存バグを再現テストで押さえたいとき

## Quickstart（典型フロー）
1) 期待する振る舞いを1ケース書く → まず失敗させる  
2) 境界/異常ケースを追加（到達可能なtrue/false両面）  
3) 最小実装でグリーン → リファクタ → 繰り返し  
4) `make post-change` でformat/lint/testを一括確認

## テスト設計チェックリスト
- 正常系: 期待する戻り値/副作用を具体的にassert
- 異常系: 例外型とメッセージをassert（`with pytest.raises(...)`）
- 境界/空/NotFound/権限: 条件分岐の両面を網羅
- 副作用: 状態変化（ファイル/DB/呼び出し回数）を検証
- 固定時刻/乱数: fixtureやmonkeypatchで決定的にする

## よく使うパターン
- 例外検証:  
  ```python
  with pytest.raises(ValueError, match="invalid foo"):
      func("bad")
  ```
- パラメトリックテスト:  
  ```python
  @pytest.mark.parametrize("value,expected", [(1,2),(0,1)])
  def test_inc(value, expected):
      assert inc(value) == expected
  ```
- tmp_path利用: ファイル出力/読み込みの検証に使う
- monkeypatch: 環境変数や関数置換で外部依存を切る

## 運用メモ
- 追加した分岐に対し「到達したこと」をassertで示す（例: return値、呼び出し回数）
- 実装後は必ず`make post-change`（ruff format+lint+pytest）を実行
- テストだけ変更する場合も同コマンドで退行を防ぐ
