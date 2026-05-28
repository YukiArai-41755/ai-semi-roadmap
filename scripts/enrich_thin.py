#!/usr/bin/env python3
"""Enrich the two important-but-thin nodes (power inductor #4 priority, ESD).
Leave terse-but-complete L3 materials as-is. Idempotent."""
import json, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P=os.path.join(ROOT,"data","graph.json"); d=json.load(open(P))
def upd(nid, **kw):
    n=next(x for x in d['nodes'] if x['id']==nid); n.update(kw)
upd("m-powerinductor",
  props={"用途":"VRM出力平滑、GPU/HBM電源","形態":"メタルコンポジット/一体成型","課題":"大電流での飽和・DCR損失・小型化"},
  def_="VRMの出力段でスイッチング電流を平滑しエネルギーを蓄える磁性部品。AIの大電流(数百A/相)・小型化要求でメタルコンポジット系が主流。ダイ直下の垂直給電ではインダクタの配置と低背化がPDN性能を左右する。PDN priority #4。")
# python dict can't have key 'def_' map to 'def'; fix:
n=next(x for x in d['nodes'] if x['id']=='m-powerinductor')
n['def']=n.pop('def_')
upd("m-esd",
  props={"対象":"PCIe/USB/Ethernet/管理ポート等の高速I/O","要件":"低容量(信号劣化回避)+高サージ耐量","関連":"TVSダイオード(電源サージ)"},
  def_="静電気放電やサージから高速I/Oを守る保護素子。AIサーバは外部接続点が多く必須。高速差動信号では保護素子の寄生容量が信号品質を劣化させるため、低容量化が技術課題。L7ネットワークの信頼性を支える。")
n=next(x for x in d['nodes'] if x['id']=='m-esd')
n['def']=n.pop('def_')
out=json.dumps(d,ensure_ascii=False,indent=2);json.loads(out)
open(P,"w").write(out+"\n")
print("enriched m-powerinductor, m-esd")
