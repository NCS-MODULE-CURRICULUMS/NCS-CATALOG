# -*- coding: utf-8 -*-
"""
학습하기 페이지 — 준비 교안의 세부항목을 카드로 펼친다.

준비 교안(guides/mNN.html)은 한 장짜리 긴 문서라 어디부터 손대야 할지 보이지 않는다.
그 안의 빠른 이동(#qnav)에 이미 묶음과 단계가 정의되어 있으므로, 그것을 그대로
카드로 펼쳐 놓는다. 카드를 누르면 교안의 해당 자리(#stN)로 바로 들어간다.

내용을 새로 쓰지 않는다 — 교안에 있는 것을 다른 모양으로 보여 줄 뿐이다.
교안을 고치면 이 스크립트를 다시 돌려 카드도 맞춘다.

  python NCS-CATALOG/scripts/gen/gen_study.py
"""
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parents[2] / "COURSE-MANAGEMENT"
A = SITE / "assets"
OUT = SITE / "study"

NAV = re.compile(r'<nav id="qnav".*?</nav>', re.S)
ITEM = re.compile(r'<i class="qg">(.*?)</i>|<a href="#(st\d+)"><b>(.*?)</b><span>(.*?)</span></a>')


def esc(s):
    return html.escape(str(s), quote=True)


def jsvar(path, var):
    p = A / path
    if not p.exists():
        return None
    m = re.search(rf"window\.{var}\s*=\s*(\[.*?\]|\{{.*?\}});\s*$",
                  p.read_text(encoding="utf-8"), re.S | re.M)
    if not m:
        return None
    raw = m.group(1)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        fixed = re.sub(r'([{,]\s*)([A-Za-z_]\w*)\s*:',
                       lambda x: x.group(1) + '"' + x.group(2) + '":', raw)
        fixed = re.sub(r",(\s*[}\]])", lambda x: x.group(1), fixed)
        return json.loads(fixed)


def steps_of(guide: Path):
    """교안의 빠른 이동에서 (묶음, 앵커, 번호, 제목) 을 순서대로 뽑는다."""
    s = guide.read_text(encoding="utf-8")
    nav = NAV.search(s)
    if not nav:
        return []
    out, group = [], ""
    for m in ITEM.finditer(nav.group(0)):
        if m.group(1):
            group = m.group(1).strip()
        elif m.group(2):
            out.append((group, m.group(2), m.group(3).strip(), m.group(4).strip()))
    return out


def page(cid, mid, name, steps):
    groups = []
    for g, anchor, num, title in steps:
        if not groups or groups[-1][0] != g:
            groups.append((g, []))
        groups[-1][1].append((anchor, num, title))

    body = []
    for g, items in groups:
        body.append(f'<h2 class="sub2">{esc(g) if g else "단계"}'
                    f'<span class="cnt">{len(items)}</span></h2>')
        cards = "".join(
            f'<div class="card">'
            f'<h3><i>{esc(num)}</i>{esc(title)}</h3>'
            f'<div class="go"><a class="btn" href="../guides/{mid}.html#{anchor}">교안에서 보기</a></div>'
            f'</div>'
            for anchor, num, title in items)
        body.append(f'<div class="cards">{cards}</div>')

    return f"""<meta charset="utf-8"><title>{esc(name)} — 학습하기</title>
<link rel="stylesheet" href="../assets/site.css">
<script src="../assets/auth.js"></script>
<script>EXAM_AUTH.guard("../");</script>
<div class="top"><div class="tbar">
  <div class="brand"><a href="../index.html">과정관리</a>
  <small><a href="../courses/{cid}.html">능력단위 모듈 목록</a> / {esc(name)} / 학습하기</small></div>
  <div class="tuser" id="tUser"><b id="tName"></b><button id="tOut" type="button">로그아웃</button></div>
</div></div>
<script>EXAM_AUTH.paintTop("../");</script>
<style>
  .sub2{{font-size:15px;margin:26px 0 8px;padding-bottom:6px;border-bottom:1px solid #000;font-weight:700}}
  .cnt{{font-weight:400;font-size:11.5px;color:#555;margin-left:8px}}
  .card{{flex:1 1 260px;min-width:240px;min-height:0}}
  .card h3{{display:flex;align-items:flex-start;gap:9px;font-size:13.5px;line-height:1.5;margin:0 0 12px}}
  .card h3 i{{font-style:normal;flex:0 0 auto;width:22px;height:22px;line-height:20px;
             text-align:center;border:1px solid #000;font-size:11.5px;font-weight:700}}
  .memo{{font-size:12.5px;line-height:1.7;color:#555}}
  .bar{{display:flex;gap:6px;flex-wrap:wrap;margin:24px 0 0}}
  .bar a{{border:1px solid #000;background:#fff;color:#000;padding:5px 14px;
         font-size:12.5px;text-decoration:none}}
  .bar a:hover{{background:#000;color:#fff}}
</style>
<div class="wrap">
<h1>{esc(name)} — 학습하기</h1>
<p class="sub">준비 교안의 단계를 순서대로 펼친 것입니다. 카드를 누르면 교안의 해당 자리로 들어갑니다.</p>

<div class="note"><b>쓰는 법</b> — 위에서부터 한 단계씩 따라갑니다.
끝낸 단계는 교안에서 산출물을 확인하고 다음으로 넘어가세요.
단계 수 <b>{len(steps)}</b>개 · 묶음 {len(groups)}개</div>

{"".join(body)}

<p class="bar">
  <a href="../courses/{cid}.html">← 능력단위 모듈 목록으로</a>
  <a href="../guides/{mid}.html">준비 교안 전체 보기</a>
</p>
<footer>담당 정우균</footer>
</div>
"""


def main():
    courses = jsvar("courses.js", "CM_COURSES") or []
    for c in courses:
        cid = c["id"]
        guides = jsvar(f"items-{cid}.js", "CM_GUIDES") or {}
        if not guides:
            continue
        OUT.mkdir(parents=True, exist_ok=True)
        counts, made = {}, 0
        for mid, name in guides.items():
            g = SITE / "guides" / f"{mid}.html"
            if not g.exists():
                print(f"  ! guides/{mid}.html 없음 — 건너뜀")
                continue
            st = steps_of(g)
            if not st:
                print(f"  ! guides/{mid}.html 에 빠른 이동이 없음 — 건너뜀")
                continue
            (OUT / f"{cid}-{mid}.html").write_text(page(cid, mid, name, st), encoding="utf-8")
            counts[mid] = len(st)
            made += 1

        # 표의 [학습하기] 단추가 참고할 단계 수
        p = A / f"items-{cid}.js"
        s = p.read_text(encoding="utf-8")
        blk = ("\n/* 학습하기 — 준비 교안의 세부항목 수. gen_study.py 가 채운다. */\n"
               "window.CM_STUDY = " + json.dumps(counts, ensure_ascii=False, indent=2) + ";\n")
        s = re.sub(r"\n/\* 학습하기[\s\S]*?window\.CM_STUDY = \{[\s\S]*?\};\n", "\n", s)
        p.write_text(s.rstrip("\n") + "\n" + blk, encoding="utf-8")
        print(f"[{cid}] 학습하기 {made}개 · 단계 합계 {sum(counts.values())}")


if __name__ == "__main__":
    main()
