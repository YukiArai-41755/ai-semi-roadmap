#!/bin/bash
# v2.3.1: 検索機能 + モバイル対応 + 細かいバグ修正
# Cowork サンドボックスの権限制約でgit操作ができないため、ホスト側で実行する
set -e
cd "$(dirname "$0")"

# stale lock 除去
rm -f .git/index.lock

# サンドボックスが残した一時ファイル (自分の足跡)
rm -f test123.txt .git/testfile 2>/dev/null || true

# .gitignore に Cowork サンドボックスの一時痕跡を追加(将来の汚染防止)
if ! grep -q "^test123.txt$" .gitignore 2>/dev/null; then
  printf "\n# Cowork sandbox 残骸\ntest*.txt\n.git/testfile\n" >> .gitignore
fi

git add -A
echo "=== to commit ==="
git status --short | head -40
echo "---"
echo "files changed: $(git status --short | wc -l)"
echo "---"

git commit -m "v2.3.1: 用語検索機能・モバイル対応・swimlane等バグ修正

【検索機能】
- assets/app.js: graph.json + companies.json から 199 アイテムの
  軽量インバーテッドインデックスを起動時に構築、topbarに検索ボックスを
  自動挿入、'/'でフォーカス、↑↓Enter で選択、Esc クローズ。
  technology/material/company/trend/layer の5種を1ボックスで横断検索。
- assets/base.css: 検索ボックス・ドロップダウンのスタイル、モバイル時は
  検索ボックスが topbar の2行目に独立配置、tr:target で
  飛び先の銘柄行をゴールド点滅でハイライト。
- scripts/gen_companies.py: 企業ユニバース表の <tr> に id=\"co-{cid}\"
  アンカーを追加(126銘柄)、検索結果から行へ直接ジャンプ可能に。
- companies.html: 上記反映で再生成。

【モバイル/タッチ対応】
- assets/app.js: タッチデバイス検出 (hover:none/pointer:coarse)、
  tap-to-show / tap-again-to-navigate ロジック、外部タップ/Escape/
  scroll で自動クローズ、ハンバーガーメニュー自動挿入。
  T-mem/T-sys 等トレンドIDの解決も追加。
- assets/base.css: @media (hover: none) で hover残り防止、820pxで
  サイドバー左ドロワー化、480pxで logo 非表示。テーブル font/padding
  縮小、thead非sticky化(iOS Safariバグ回避)、card-meta 1カラム化、
  pager 縦積み化等。

【バグ修正】
- cards/switch-silicon.html: 誤リンク m-glass-int → glass-int を修正
- materials/m-hbond.html: 不存在カード 3dv-cache.html へのリンクを除去
- scripts/gen_views.py & views/swimlane.html: 時間edgeリンクが
  /cards/ 固定で material ノード(m-sicap, m-retimer)へのリンクが
  切れていたのを kind 判定で /materials/ に振り分け修正

【動画制作の足場(Claude Code Desktop への引き継ぎ)】
- video/ ディレクトリを新設、Manim Community Edition での動画制作環境
- video/HANDOFF.md: 引き継ぎブリーフ(コンテキスト + ミッション + やる順序)
- video/setup.sh: brew + python venv + manim の一発インストール(冪等)
- video/skeleton/hello.py: 動作確認用 hello world
- video/scenes/hbm_roadmap.py: 初回作品「HBM4 vs HBM4E vs HBM5
  ロードマップ」3幕構成の骨格、各幕に TODO コメント残し
- video/README.md: 制作プロセス概要
- .gitignore: video/.venv/, video/media/ 等を追加

🤖 Generated with Claude Cowork
"

git push origin "$(git branch --show-current)"
echo "DONE"
