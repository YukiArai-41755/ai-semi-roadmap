#!/bin/bash
# v2.3-deep-cards commit & push
# Cowork サンドボックスの権限制約でgit操作ができないため、ホスト側で実行する
set -e
cd "$(dirname "$0")"

# stale lock があれば除去
rm -f .git/index.lock

# sandbox が残した一時ファイル
rm -f test_workspace.txt .git/testfile 2>/dev/null || true

git add -A
git status --short | head -80
echo "---"
echo "files changed: $(git status --short | wc -l)"
echo "---"

git commit -m "v2.3-deep-cards: 60+カード全面深化、MLCC/水晶 再リサーチで上方修正、銘柄マップ更新

【部材カード】
- m-mlcc.html, m-clock.html を約3.5倍に深化、再リサーチで上方修正
  - MLCC: 供給逼迫度 4→5、価格決定力 3→4 (Murata +15-35% 値上げ、
    GB300ラック44万個、Murata+SEMCO 84%寡占)
  - 水晶/クロック: 供給逼迫度 2→4、価格決定力 2→3 (SiTime AI-DC +158% YoY、
    SiTime→Renesas Timing \$3B 買収、Kyocera 30fs差動XO量産、合成石英autoclave日本集中)

【全レイヤーカード深化 (60枚)】
- L1 電力・冷却 (12枚): m-vrm, m-drmos, m-powerinductor, m-shunt, m-gansic,
  m-cdu, m-tim, hvdc, transformer, power-supply, liquid-cooling, pdn
- L2 プロセス (5枚): m-resist, m-euvmask, litho, gaa, bspdn
- L3 パッケージ (18枚): m-abf, m-ccl, m-copperfoil, m-glasscloth, m-sicap,
  m-tsv, m-tgv, m-hbond, m-ihs, m-esd, cowos, soic, emib, foveros,
  glass-int, glass-sub, copos-note, org-sub
- L4 メモリ (6枚): hbm4, hbm4e, hbm-basedie, hbf, nand, socamm
- L5 演算 (9枚): rubin, mi400, tpu, trainium, vera-cpu, cerebras,
  sambanova, hyperscaler-asic, china-asic
- L6 スケールアップ (6枚): m-optengine, nvlink, ualink, cxl, ucie, cpo
- L7 スケールアウト (4枚): m-retimer, switch-silicon, ethernet-uec, infiniband

各カード: AI server文脈リード、構造・物性、AI内階層・実装数、5軸メトリクス、
確度タグ付き価格・供給説明、サプライヤ・シェア、代替材・競合、3-5年見通しを実装。

【データ層】
- data/graph.json: m-mlcc, m-clock の pricing/tightness/priceetag/pricenote 更新
- data/companies.json: 11社追加 (Kyocera, NDK, Skyworks, Microchip, Daishinku,
  TXC, Empower Semi[未上場], AAOI, Ayar[未上場], Lightmatter[未上場], IPGP)、
  既存社の note/type 更新 (SiTime 周辺→中核、SEMCO 準中核→中核、Nittobo→中核 など)、
  material_rows をクロックを独立行化、CPO/光フォトニクスにシリコンフォトニクスベンチャー追加

【自動生成ページ】
- matrix.html: m-mlcc/m-clock の座標とテキスト更新、過小評価系統的再点検に
  6巡目(2026-05再リサーチ)を追加
- companies.html: v2.3更新ハイライト callout を追加、131KB
- components.html, basics.html, glossary.html, index.html: 再生成

【スクリプト】
- scripts/gen_matrix.py: MLCC/水晶の説明と過小評価系統的再点検を更新
- scripts/add_priceaxes.py: 評価値とテキストを更新
- scripts/gen_companies.py: v2.3更新ハイライト callout を追加

🤖 Generated with Claude Cowork
"

git push origin "$(git branch --show-current)"
echo "DONE"
