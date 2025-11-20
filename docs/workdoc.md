# 作業計画書 兼 記録書

---

**日付：** `[YYYY年MM月DD日]`  
**作業ディレクトリ・リポジトリ:** `/home/inaho-omen/Project/reactpy_bbox_annotator_sandbox`  
**作業者：** `[作業者名]`

**参考リポジトリ（temp 配下）:** `https://github.com/younesZdDz/react-bbox-annotator`, `https://github.com/reactive-python/reactpy.git`

**参考ドキュメント:** `/home/inaho-omen/Project/claude_code_web_sandbox/README.md`, `/home/inaho-omen/Project/claude_code_web_sandbox/docs/ONBOARDING.md`, `/home/inaho-omen/Project/claude_code_web_sandbox/docs/workdoc.md`, `/home/inaho-omen/Project/claude_code_web_sandbox/docs/workdoc_gallery_bdd_e2e.md`

---

## 1. 作業目的

本日の作業は、以下の目標を達成するために実施します。

* **目標1:** ReactPy + FastAPI で bbox 注釈 UI を実装し、`temp/react-bbox-annotator` 同等のフローを再現する。
* **目標2:** ヘッドレス環境で apt セットアップ → uv 環境構築 → Playwright 導入を行い、DRY/KISS/SOLID と t-wada TDD に沿って実装する。
* **目標3:** Playwright MCP 経由で E2E 動作確認を行い、完全な自動テスト手順までドキュメント化する。

---

## 2. 作業内容

### フェーズ 1: 事前準備・設計 (見積: 0.7h)
このフェーズでは、参照コードの読み解きと環境準備方針を固める。

1. **参照実装の構造確認：**
   * **タスク内容：** `app.py` の状態遷移と `temp/react-bbox-annotator` の挙動差分を整理し、削除ボタン表示・入力キャンセル・スケール計算を明文化。
   * **目的：** 実装ギャップを明確化。
2. **環境前提の確認：**
   * **タスク内容：** headless 前提で apt 依存（playwright install-deps 含む）と uv 仮想環境の手順を決定。
   * **目的：** 後続ステップの手戻り防止。
3. **テスト設計：**
   * **タスク内容：** Playwright (Python) ベースで fail-first の E2E テストケースを決め、検証条件を先に記述。
   * **目的：** TDD で進める土台を作る。
4. **参考リポジトリの取得と初期調査（他LLMエージェント向け共有）:**
   * **タスク内容：** `temp/react-bbox-annotator` と `temp/reactpy` を git clone で取得（既存の場合は fetch/pull 確認）。必要に応じ別タブの LLM エージェントにコード調査（構造・API・差分要約）を依頼するタスクを明示。
   * **目的：** 参照元コードが手元にあり、他エージェントでも迷わず調査開始できる状態を作る。

### フェーズ 2: 実装・TDD (見積: 1.8h)
このフェーズでは、uv 環境構築から実装・テストまでを反復する。

1. **環境構築：**
   * **タスク内容：** apt で Playwright 依存を導入し、`uv venv`/`uv pip install -e .` で Python 依存を揃える。justfile で再現コマンドを整備。
   * **目的：** 再現性の高い実行環境を確立。
2. **テスト先行：**
   * **タスク内容：** Playwright MCP テストシナリオ（ドラッグ→ラベル追加→削除→リセット→URL変更）を先に実装し、初回は失敗させる。
   * **目的：** 振る舞いをコード化した受け入れ基準を固定。
3. **ReactPy 実装：**
   * **タスク内容：** 参照仕様に合わせて状態管理・座標正規化・UI 部品を実装し、テストを緑にするまでリファクタリング。
   * **目的：** 要求仕様を満たしつつ DRY/KISS/SOLID を担保。

### フェーズ 3: 動作検証・仕上げ (見積: 1.0h)
このフェーズでは、E2E 確認とドキュメント仕上げを行う。

1. **Playwright MCP 実行：**
   * **タスク内容：** サーバ起動 + MCP テストを headless で流し、ログ・スクリーンショットを保存。
   * **目的：** 本番同等環境での完全動作を確認。
2. **品質チェック：**
   * **タスク内容：** ruff/black（導入時）で静的検査・整形、justfile/README の最終確認。
   * **目的：** 品質と再現性を保証。
3. **作業記録反映：**
   * **タスク内容：** 実績・エラー・解決策・ログパスを本ファイルの記録欄に追記。
   * **目的：** 再現と振り返りを容易にする。

---

## 3. 作業チェックリスト
*作業が完了したら `[ ]` を `[x]` に変更します。各手順は原子的操作+確認+テスト+エラー対処付き。*

### フェーズ 1: 事前準備・設計

### 手順 1: 現時刻を記録
- [x] 🖐 **操作**: `date "+%Y-%m-%d %H:%M:%S %Z%z"` を実行し、結果を本作業記録に貼り付ける。
- [x] 🔎 **確認**: 本ファイルの記録欄に実行結果が残っている。
- [x] 🧪 **テスト**: なし（記録目的）。
- [x] 🛠 **エラー時対処**: `date` 未インストールの場合は `busybox date` で代替。

### 手順 2: 参照コード整合確認
- [x] 🖐 **操作**: `sed -n '1,240p' app.py` と `sed -n '1,260p' temp/react-bbox-annotator/src/BBoxAnnotator/index.tsx` を閲覧し、状態遷移/スケール/削除ボタン/入力キャンセルの差分をメモ。
- [x] 🔎 **確認**: 差分メモが本ファイルの記録欄に残る。
- [x] 🧪 **テスト**: なし（設計確認）。
- [x] 🛠 **エラー時対処**: パス誤り時は `rg BBoxAnnotator temp` で位置検索。

### 手順 3: 参考リポジトリの取得（他LLM着手準備）
- [x] 🖐 **操作**: `mkdir -p temp && cd temp && git clone https://github.com/younesZdDz/react-bbox-annotator && git clone https://github.com/reactive-python/reactpy.git` を実行（既存なら `cd temp/react-bbox-annotator && git pull` / `cd temp/reactpy && git pull`）。クローン後、別LLMタブ/セッションに「構造・主要コンポーネント・イベントフローの要約」を依頼する。
- [x] 🔎 **確認**: `temp/react-bbox-annotator/.git` と `temp/reactpy/.git` が存在し、最新 commit を取得できている。LLM 依頼メモが記録欄に残る。
- [x] 🧪 **テスト**: `cd temp/react-bbox-annotator && git status` が clean、`cd temp/reactpy && git status` が clean。
- [x] 🛠 **エラー時対処**: clone 失敗時はネットワーク制約を確認し、tarball ダウンロードを検討。権限エラーは `sudo` 不要な場所で再実行。

### 手順 4: headless 依存の apt 更新
- [x] 🖐 **操作**: `sudo apt-get update` を実行（headless 環境前提）。
- [x] 🔎 **確認**: Update 成功ログが表示されエラーなし。
- [x] 🧪 **テスト**: なし（環境前提）。
- [x] 🛠 **エラー時対処**: 署名エラー時は `sudo apt-get update -o Acquire::AllowInsecureRepositories=true` で再試行し、失敗時はミラー変更を検討。

### 手順 5: Playwright 依存の apt 導入
- [x] 🖐 **操作**: `sudo apt-get install -y wget ca-certificates libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 xvfb` を実行。
- [x] 🔎 **確認**: すべてのパッケージが `... already the newest` もしくは `Setting up ...` で完了。
- [x] 🧪 **テスト**: `xvfb-run --auto-servernum --server-args='-screen 0 1280x720x24' echo ok` が `ok` を出す。
- [x] 🛠 **エラー時対処**: パッケージ未検出時は `apt-cache search <name>` で代替名を確認。ロック競合時は `sudo fuser -v /var/lib/dpkg/lock-frontend` でプロセス確認。

### 手順 6: uv 仮想環境の生成
- [x] 🖐 **操作**: `uv venv .venv` を実行し、`source .venv/bin/activate` を実施。
- [x] 🔎 **確認**: `which python` の結果が `.venv/bin/python` を指す。
- [x] 🧪 **テスト**: `python -c "import sys; print(sys.prefix.endswith('.venv'))"` が `True` を出す。
- [x] 🛠 **エラー時対処**: uv 未導入なら `curl -LsSf https://astral.sh/uv/install.sh | sh` を検討（ネット許諾要確認）。失敗時は既存 `.venv` を削除して再作成。

### 手順 7: Python 依存の導入
- [x] 🖐 **操作**: `uv pip install -e . && uv pip install playwright pytest pytest-asyncio` を実行。
- [x] 🔎 **確認**: 依存解決が成功しエラーなし。
- [x] 🧪 **テスト**: `python -c "import playwright, fastapi, reactpy"` が例外を出さない。
- [x] 🛠 **エラー時対処**: ビルド失敗時は `uv pip install -U pip setuptools wheel` 後に再実行。

### 手順 8: Playwright ブラウザの headless 導入
- [x] 🖐 **操作**: `uv run playwright install-deps chromium` を実行し、続けて `uv run playwright install chromium` を実行。
- [x] 🔎 **確認**: インストール完了ログが表示される。
- [x] 🧪 **テスト**: `uv run python - <<'PY'\nfrom playwright.async_api import async_playwright\nimport asyncio\nasync def main():\n    async with async_playwright() as p:\n        browser = await p.chromium.launch(headless=True)\n        page = await browser.new_page()\n        await page.goto('about:blank')\n        await browser.close()\nasyncio.run(main())\nPY` が例外なく終了。
- [x] 🛠 **エラー時対処**: ランタイムライブラリ不足は apt 追加。`chromium not found` 時は `rm -rf ~/.cache/ms-playwright` 後に再実行。

### 手順 9: テストスケルトンを fail-first で作成
- [x] 🖐 **操作**: `tests/e2e/test_bbox.py` を作成し、Playwright MCP シナリオ（ドラッグ→select ラベル→text ラベル→削除→リセット→URL 変更）を TODO 付きで記述し、未実装で失敗させる。
- [x] 🔎 **確認**: テストが `assert False` 等で意図的に失敗する。
- [x] 🧪 **テスト**: `uv run pytest tests/e2e/test_bbox.py -q` が RED になる。
- [x] 🛠 **エラー時対処**: import エラー時は `PYTHONPATH` を `.` に設定。Playwright fixture 未設定なら `pytest-playwright` の fixture 例を追加。

### 手順 10: ReactPy 実装を改善
- [ ] 🖐 **操作**: `app.py` に状態管理・スケール正規化・削除ボタン hover 表示・入力キャンセル対応を実装（DRY/KISS/SOLID を守る）。
- [ ] 🔎 **確認**: コードレビューで責務分離と関数分割が明確。
- [ ] 🧪 **テスト**: 手順 9 のテストが GREEN になるまで `uv run pytest tests/e2e/test_bbox.py -q` を回す。
- [ ] 🛠 **エラー時対処**: 座標ずれは計算式をログ出力して検証。無限ループ時は `CTRL+C` で停止し状態遷移を再設計。

### 手順 11: justfile と README の整備
- [ ] 🖐 **操作**: `just serve`（uvicorn 起動）、`just test-e2e`（Playwright E2E）、`just lint`（導入時）などのレシピを justfile に追加し、README に headless + uv 手順を追記。
- [ ] 🔎 **確認**: `just --list` にレシピが現れ、README にコマンドが記述されている。
- [ ] 🧪 **テスト**: `just serve` がサーバを起動し、`just test-e2e` がテストを通る。
- [ ] 🛠 **エラー時対処**: `just: command not found` 時はインストール手順を README に補足。

### 手順 12: Playwright MCP で最終 E2E
- [ ] 🖐 **操作**: `uv run uvicorn app:fastapi_app --host 0.0.0.0 --port 8000 --reload` を起動した状態で、Playwright MCP からシナリオを実行し、ログ/スクリーンショットを `artifacts/` に保存。
- [ ] 🔎 **確認**: MCP 実行ログが成功し、シナリオ全工程が完了。
- [ ] 🧪 **テスト**: 実行前は未実施、実行後に全ステップ成功ログを残す。
- [ ] 🛠 **エラー時対処**: セレクタ不一致時は DOM スナップショットで修正。タイムアウト時は待機を挿入。

### 手順 13: 品質チェックと記録
- [ ] 🖐 **操作**: （導入時）`uv run ruff check .` と `uv run black --check app.py` を実行し、作業記録に結果を追記。
- [ ] 🔎 **確認**: 警告がない、または修正済みである。
- [ ] 🧪 **テスト**: 失敗→修正→成功の履歴を残す。
- [ ] 🛠 **エラー時対処**: ルール過剰なら設定ファイルで無効化を検討（理由を記録）。

---

## 4. 作業に使用するコマンド参考情報

### 基本的な開発ワークフロー
```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e .
uv run uvicorn app:fastapi_app --host 0.0.0.0 --port 8000 --reload
```

### テストと品質管理
```bash
uv run pytest tests/e2e/test_bbox.py -q
uv run playwright install-deps chromium
uv run playwright install chromium
uv run ruff check .           # 導入時
uv run black --check app.py   # 導入時
```

### 特定機能の実行・デバッグ例
```bash
# Playwright MCP 実行例（サーバ起動後にシナリオを流す）
# 例: MCP ターミナルで browser_navigate -> 操作 -> ログ保存

# 画像メタの簡易確認
uv run python - <<'PY'
from app import fetch_image_meta
import asyncio
print(asyncio.run(fetch_image_meta("https://example.com/image.jpg")))
PY
```

---

## 6. 完了の定義

*作業が最後まで完了したら `[ ]` を `[x]` にしつつ、作業が本当に完了したかをチェックします*
- [ ] 参照リポジトリ（react-bbox-annotator/reactpy）が `temp/` に取得済みで最新状態、他LLMへの調査依頼メモが記録されている。
- [ ] ReactPy bbox アノテータが参照実装同等に動作（ドラッグ/追加/削除/リセット/URL変更が全て成功し、座標は元画像基準で正規化）。
- [ ] headless apt + uv + Playwright セットアップ手順が README/justfile に明記され、`just serve`/`just test-e2e`（想定）で再現可能。
- [ ] Playwright MCP E2E が緑になり、ログ・スクリーンショットが `artifacts/` などに保存済み。
- [ ] 品質チェック（lint/format）が通過、または未導入の場合その旨を記録。
- [ ] 作業記録に時刻・エラー・対処・テスト結果が残っている。

---

## 7. 作業記録

**重要な注意事項：**

* 作業開始前に必ず `date "+%Y-%m-%d %H:%M:%S %Z%z"` コマンドで現在時刻を確認し、正確な日時を記録します。
* 各作業項目を開始する際と完了する際の両方で記録を行うこと。
* 作業内容は具体的なコマンドや操作手順を詳細に記載すること。
* 結果・備考欄には成功／失敗、エラー内容、解決方法、重要な気づきを必ず記入すること。
* 複数のフェーズがある場合は、フェーズごとに開始・完了の記録を取ること。
* コード変更を行った場合は、変更したファイル名と変更内容の概要を記録すること。
* エラーが発生した場合は、エラーメッセージと解決策を詳細に記録すること。

| 日付 | 時刻 | 作業者 | 作業内容 | 結果・備考 |
| :--- | :--- | :--- | :--- | :--- |
| 2025-11-20 | 08:07:13 UTC+0000 | Claude | フェーズ1開始: 現状調査 | 作業計画書確認・タスク把握完了 |
| 2025-11-20 | 08:07:13 UTC+0000 | Claude | 手順1: 現時刻を記録 | ✅ date コマンド実行成功 |
| 2025-11-20 | 08:08:00 UTC+0000 | Claude | 手順3: 参照リポジトリ取得 | ✅ react-bbox-annotator と reactpy を temp/ にクローン完了 |
| 2025-11-20 | 08:08:30 UTC+0000 | Claude | app.py/pyproject.toml作成 | ✅ ユーザー提供の参考実装を作成 |
| 2025-11-20 | 08:09:00 UTC+0000 | Claude | 手順2: 参照コード確認 | ✅ React版との差分確認: 削除ボタンのホバー表示、マウスイベントリスナーの違い、スケール計算方式の違いを確認 |
| 2025-11-20 | 08:10:00 UTC+0000 | Claude | 手順4: apt更新 | ✅ /tmp パーミッション修正後、apt-get update 成功 |
| 2025-11-20 | 08:11:00 UTC+0000 | Claude | 手順5: Playwright依存導入 | ✅ xvfb含む必要パッケージをインストール、テスト成功 |
| 2025-11-20 | 08:12:00 UTC+0000 | Claude | 手順6: uv仮想環境作成 | ✅ .venv作成、pyproject.toml修正、テスト成功 |
| 2025-11-20 | 08:13:00 UTC+0000 | Claude | 手順7: Python依存導入 | ✅ reactpy/fastapi/playwright等35パッケージインストール成功 |
| 2025-11-20 | 08:14:00 UTC+0000 | Claude | 手順8: Playwright chromium導入 | ✅ ブラウザインストール・テスト成功 |
| 2025-11-20 | 08:15:00 UTC+0000 | Claude | 手順9: テストスケルトン作成 | ✅ 7つのE2Eテストを作成、fail-first確認 |
| 2025-11-20 | 08:16:00 UTC+0000 | Claude | 手順10: 実装開始 | 🔄 conftest.py作成、テスト実装中、use_effect API修正対応中 |
| 2025-11-20 | 08:35:49 UTC+0000 | Claude | 手順10継続: ReactPy API調査 | ✅ WebSearchでReactPy 1.1.0のuse_effectとhtml要素構文を調査完了 |
| 2025-11-20 | 08:35:49 UTC+0000 | Claude | 手順10継続: トイプロブレム作成 | ✅ toy_app.py作成、7つのパターンテスト全てGREEN確認 |
| 2025-11-20 | 08:35:49 UTC+0000 | Claude | 手順10継続: app.py修正 | ✅ use_effectをasync対応、html要素引数順序修正(props→content) |
| 2025-11-20 | 08:35:49 UTC+0000 | Claude | 手順10継続: E2Eテスト実行 | 🔄 basic_flow testがタイムアウト、デバッグ中 |
| | | | | |
