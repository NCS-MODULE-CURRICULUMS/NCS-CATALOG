# -*- coding: utf-8 -*-
"""
커리큘럼 페이지를 만든다 — 조직의 커리큘럼 저장소 4종을 사이트에서 볼 수 있게.

  허브  ─ 커리큘럼 카드 4장 (도메인)
    └ curriculum/<도메인>.html            ─ 세분류 카드
        └ curriculum/<도메인>-<세분류>.html ─ 능력단위 표

운영 과정(c1·c2)은 '편성된 것', 커리큘럼은 '편성 전 재고'다. 둘을 섞지 않는다.
재고 중 어느 것이 실제 과정에 들어갔는지를 표의 마지막 칸(편성)이 보여 준다.

읽는 것 — curriculum-status.json(상태) · competency-units.csv(원본) · modules-c*.js(편성)
쓰는 것 — assets/curriculum.js · curriculum/*.html

  python NCS-CATALOG/scripts/gen/export_status.py     # 먼저
  python NCS-CATALOG/scripts/gen/gen_curriculum.py
"""
import csv
import html
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "NCS-CATALOG" / "data"
SITE = ROOT / "COURSE-MANAGEMENT"
A = SITE / "assets"
OUT = SITE / "curriculum"
ORG = "https://github.com/NCS-MODULE-CURRICULUMS"
NON = '<span class="non">—</span>'


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


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
        return json.loads(re.sub(r",(\s*[}\]])", lambda x: x.group(1), fixed))


def head(title, up, crumb, pdf=False):
    """모든 커리큘럼 페이지의 머리 — 로그인하지 않으면 아무것도 보이지 않는다."""
    # 학습모듈 PDF 보기는 색인(modules-pdf.js)과 뷰어(pdfview.js)를 함께 싣는다.
    # CM_BASE 는 뷰어가 assets/pdfjs/ 를 찾는 데 쓴다.
    pv = (f'<script>window.CM_BASE="{up}";</script>\n'
          f'<script src="{up}assets/modules-pdf.js"></script>\n'
          f'<script defer src="{up}assets/pdfview.js"></script>\n') if pdf else ""
    return f"""<meta charset="utf-8"><title>{esc(title)}</title>
<link rel="stylesheet" href="{up}assets/site.css">
<script src="{up}assets/auth.js"></script>
<script>EXAM_AUTH.guard("{up}");</script>
{pv}
<div class="top"><div class="tbar">
  <div class="brand"><a href="{up}index.html">과정관리</a><small>{crumb}</small></div>
  <div class="tuser" id="tUser"><b id="tName"></b><button id="tOut" type="button">로그아웃</button></div>
</div></div>
<script>EXAM_AUTH.paintTop("{up}");</script>
"""


CSS = """<style>
  .sub2{font-size:15px;margin:26px 0 8px;padding-bottom:6px;border-bottom:1px solid #000;font-weight:700}
  .cnt{font-weight:400;font-size:11.5px;color:#555;margin-left:8px}
  .bar{display:flex;gap:6px;flex-wrap:wrap;margin:24px 0 0}
  .bar a{border:1px solid #000;background:#fff;color:#000;padding:5px 14px;
         font-size:12.5px;text-decoration:none}
  .bar a:hover{background:#000;color:#fff}
  .tscroll{overflow-x:auto}
  .ccard h3 small{display:block;font-weight:400;color:#555;font-size:11.5px;margin-top:3px}
  .ccard:hover h3 small{color:#ccc}
  td.wip{font-weight:700}
  .flag{font-weight:700;border:1px solid #000;padding:0 5px;font-size:11px;margin-left:6px}
  .stg{display:block;font-size:11px;color:#555;margin-top:5px;white-space:nowrap}
  .tot{font-size:12.5px;color:#555;margin:10px 0 0}
</style>
"""


def lv_range(levels):
    v = sorted(x for x in levels if x)
    return f"{v[0]}~{v[-1]}" if v else "—"


def level_of(uc, u, ncs):
    """수준은 NCS 원본(competency-units.csv)이 기준이다.
    교안 머리말의 값은 사람이 적은 것이라 원본이 있으면 원본을 쓴다."""
    v = (ncs.get(uc) or {}).get("수준", "")
    if v and v.isdigit():
        return int(v)
    return u.get("lv")


def stat_dl(u_all, levels, subs_n=None):
    """카드에 붙는 집계 — 전부 계산된 값이고 손으로 적지 않는다."""
    n = len(u_all)
    hr = sum(u["hr"] or 0 for u in u_all)
    wip = sum(1 for u in u_all if u["stg"] >= 1)
    pdf = sum(u["has"]["pdf"] for u in u_all)
    lv = sorted(x for x in levels if x)
    rows = []
    if subs_n is not None:
        rows.append(("세분류", f"{subs_n}개"))
    rows += [("능력단위", f"{n}개"),
             ("수준", f"{lv[0]}~{lv[-1]}" if lv else "—"),
             ("교안", f"작성 {wip} / 골격 {n - wip}"),
             ("학습모듈", f"{pdf}건")]
    if hr:
        rows.append(("시간", f"{hr}h"))
    return "<dl>" + "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in rows) + "</dl>"


def orphan_block(items, dom):
    """재고 밖에서 편성된 능력단위를 알린다 — 조용히 빠지면 수치가 거짓말이 된다."""
    if not items:
        return ""
    rows = []
    for uc, r, where in items:
        courses = " · ".join(
            f'<a href="../courses/{esc(cid)}.html">{esc(nm)}</a>' for cid, nm in where)
        rows.append(f'<li>{esc(r["능력단위명"])} <code>{esc(uc)}</code> — '
                    f'{esc(r["세분류"])}({esc(r["세분류코드"])}) · 편성 {courses}</li>')
    return (f'<div class="warn"><b>재고 밖에서 편성된 능력단위 {len(items)}개</b> — '
            f'아래 능력단위는 운영 과정에 이미 들어가 있는데 이 도메인의 모듈 폴더에는 '
            f'없습니다. <code>mapping-domain.yml</code> 에서 해당 세분류를 '
            f'<code>related</code> 에서 <code>primary</code> 로 올리고 모듈 폴더를 만들어야 '
            f'집계가 맞습니다.<ul style="margin:8px 0 0;padding-left:20px">'
            f'{"".join(rows)}</ul></div>')


def main():
    st = json.loads((DATA / "curriculum-status.json").read_text(encoding="utf-8"))
    units, subs, doms, STG = st["units"], st["subs"], st["domains"], st["stages"]

    tax = {}
    for r in csv.DictReader(open(DATA / "taxonomy.csv", encoding="utf-8-sig")):
        tax[r["세분류코드"]] = r
    ncs = {}
    for r in csv.DictReader(open(DATA / "competency-units.csv", encoding="utf-8-sig")):
        ncs[r["능력단위코드"]] = r

    # 편성 역매핑 — 어느 능력단위가 어느 운영 과정에 들어갔나.
    # 같이, 그 능력단위로 실제 수업에 쓰는 교안이 사이트 어디에 있는지도 모은다.
    # 과정마다 교안의 모양이 다르다 — c1 은 표준 강의 교안(6시트), c2 는 준비 교안.
    placed, mat = {}, {}
    for c in (jsvar("courses.js", "CM_COURSES") or []):
        cid = c["id"]
        guides = jsvar(f"items-{cid}.js", "CM_GUIDES") or {}
        for m in (jsvar(f"modules-{cid}.js", "CM_MODULES") or []):
            code = m.get("code")
            if not code:
                continue
            placed.setdefault(code, []).append((cid, c["name"]))
            if code in mat:
                continue                    # 먼저 나온 과정의 교안을 쓴다
            if m.get("lp"):
                mat[code] = ("../" + m["lp"], "표준 교안")
            elif m["id"] in guides:
                mat[code] = (f"../guides/{m['id']}.html", "준비 교안")

    # 편성됐는데 재고에 없는 능력단위 — 매핑이 현실을 못 따라간 자리다.
    # 숨기지 않고 그 세분류를 related 로 안고 있는 도메인 페이지에 띄운다.
    orphan = {}
    for uc, where in placed.items():
        if uc in units or uc not in ncs:
            continue                      # 재고에 있거나, 애초에 NCS 능력단위가 아님
        sc = ncs[uc]["세분류코드"]
        owner = next((d for d, v in doms.items() if sc in v.get("rel", {})), None)
        orphan.setdefault(owner, []).append((uc, ncs[uc], where))

    OUT.mkdir(parents=True, exist_ok=True)
    cards, n_pages = [], 0

    lvl = {uc: level_of(uc, u, ncs) for uc, u in units.items()}

    for dom, dv in doms.items():
        d_units = [u for u in units.values() if u["d"] == dom]
        cards.append({
            "id": dom, "label": dv["label"], "repo": dv["repo"],
            "page": f"curriculum/{dom}.html",
            "subs": len(dv["subs"]), "units": len(d_units),
            "wip": sum(1 for u in d_units if u["stg"] >= 1),
            "pdf": sum(u["has"]["pdf"] for u in d_units),
            "placed": sum(1 for u in dv["subs"] for c in subs[u]["units"] if c in placed),
            "lv": lv_range([lvl[c] for s in dv["subs"] for c in subs[s]["units"]]),
        })

        # ── 도메인 페이지 : 세분류 카드
        body = []
        for code in dv["subs"]:
            sv = subs[code]
            su = [units[c] for c in sv["units"]]
            n_pl = sum(1 for c in sv["units"] if c in placed)
            go = f"능력단위 {len(su)}개" + (f" · 편성 {n_pl}" if n_pl else "")
            body.append(
                f'<div class="cwrap"><a class="ccard" href="{dom}-{code}.html">'
                f'<h3>{esc(sv["name"])}<small>{esc(code)}</small></h3>'
                + stat_dl(su, [lvl[c] for c in sv["units"]])
                + f'<span class="go">{esc(go)}</span></a></div>')

        (OUT / f"{dom}.html").write_text(
            head(f'{dv["label"]} 커리큘럼', "../", f'커리큘럼 / {esc(dv["label"])}') + CSS +
            f'''<div class="wrap">
<h1>{esc(dv["label"])} 커리큘럼</h1>
<p class="sub">저장소 <code>{esc(dv["repo"])}</code> · 세분류 {len(dv["subs"])}개 ·
능력단위 {len(d_units)}개</p>

<div class="note"><b>이 목록은 재고입니다</b> — 훈련과정이 아니라, 과정을 짤 때 골라 쓰는
능력단위 모음입니다. 실제로 편성된 과정은 허브의 <b>운영 과정</b>에 있습니다.</div>

{orphan_block(orphan.get(dom), dom)}
<h2 class="sub2">세분류<span class="cnt">{len(dv["subs"])}</span></h2>
<div class="cgrid">{"".join(body)}</div>

<p class="bar"><a href="../index.html">← 과정관리로</a></p>
<p class="sc tot">교안 원본 —
  <a href="{ORG}/{esc(dv["repo"])}">{esc(dv["repo"])}</a> (비공개 저장소)</p>
<footer>담당 정우균</footer>
</div>
''', encoding="utf-8")
        n_pages += 1

        # ── 세분류 페이지 : 능력단위 표
        for code in dv["subs"]:
            sv = subs[code]
            t = tax.get(code, {})
            rows = []
            for uc in sv["units"]:
                u = units[uc]
                pl = placed.get(uc, [])
                pl_td = ("<br>".join(f'<a href="../courses/{esc(cid)}.html">{esc(nm)}</a>'
                                     for cid, nm in pl)
                         if pl else '<span class="non">미편성</span>')
                stg = STG[u["stg"]] + (f' ({u["todo"]})' if u["todo"] else "")
                lv = esc(lvl[uc]) if lvl[uc] else NON
                hr = esc(f'{u["hr"]}h') if u["hr"] else NON
                # 학습모듈 — 배포 주소에서는 열 방법이 없으므로 비워 둔다.
                # data-lm 이 붙은 칸은 로컬 서버로 열었을 때만 pdfview.js 가
                # [PDF] 단추로 바꾼다. 없는 단추를 보여 주지 않는다.
                pdf = (f'<span class="non" data-lm="{esc(uc)}">—</span>'
                       if u["has"]["pdf"] else NON)
                # 교안 칸 — 수업에 쓰는 교안이 있으면 그 화면으로, 없으면 양식으로.
                # 밑에 붙는 작은 글씨는 표준 강의 교안(6시트)이 어느 단계인지다.
                href, kind = mat.get(uc, ("../docs/표준강의교안-샘플.html", ""))
                sub = f"{kind} · {stg}" if kind else stg
                lp_td = (f'<a class="btn" href="{esc(href)}">{"확인" if kind else "양식"}</a>'
                         f'<span class="stg">{esc(sub)}</span>')
                cls = ' class="wip"' if u["stg"] >= 1 else ""
                # 서비스중단·숨김은 NCS 가 더는 쓰지 말라는 뜻이라 이름 옆에 붙인다
                r0 = ncs.get(uc) or {}
                flag = ""
                if r0.get("서비스중단") == "Y":
                    flag = ' <b class="flag">서비스중단</b>'
                elif r0.get("숨김") == "Y":
                    flag = ' <b class="flag">숨김</b>'
                rows.append(
                    f'<tr><td class="nm">{esc(u["n"])}{flag}</td><td>{esc(uc)}</td>'
                    f'<td>{lv}</td><td>{hr}</td><td>{pdf}</td>'
                    f'<td{cls}>{lp_td}</td><td class="nm">{pl_td}</td></tr>')

            n_pl = sum(1 for c in sv["units"] if c in placed)
            n_pdf = sum(units[c]["has"]["pdf"] for c in sv["units"])
            dist = Counter(lvl[c] for c in sv["units"] if lvl[c])
            lv_txt = " · ".join(f"수준 {k} {n}개" for k, n in sorted(dist.items()))
            crumb = (f'커리큘럼 / <a href="{dom}.html">{esc(dv["label"])}</a> / '
                     f'{esc(sv["name"])}')
            (OUT / f"{dom}-{code}.html").write_text(
                head(f'{sv["name"]} — 능력단위', "../", crumb, pdf=True) + CSS +
                f'''<div class="wrap">
<h1>{esc(sv["name"])}</h1>
<p class="sub">{esc(t.get("대분류", ""))} &gt; {esc(t.get("중분류", ""))} &gt;
{esc(t.get("소분류", ""))} &gt; {esc(sv["name"])} · <code>{esc(code)}</code> ·
{esc(t.get("개정차수", ""))}차 개정</p>

<div class="note"><b>읽는 법</b><br>
<b>수준</b> NCS 가 정한 능력단위 수준(1~8) · ncs.go.kr 원본 값<br>
<b>시간</b> 과정에 편성한 훈련시간 — 편성 전에는 비어 있습니다<br>
<b>학습모듈</b> 확보해 둔 건수는 표 아래 집계에 있습니다. 원문은 저작권 때문에
사이트에 두지 않아 이 칸이 비어 있습니다 (아래 참고)<br>
<b>교안</b> <b>확인</b>은 그 능력단위를 실제로 쓰는 과정의 교안으로,
<b>양식</b>은 표준 강의 교안 양식으로 갑니다. 밑의 작은 글씨는 6시트 진척
(골격 → 작성중 → 완성 → 검수. 괄호는 아직 못 채운 칸 수)<br>
<b>편성</b> <b>미편성</b>이면 아직 어느 훈련과정에도 넣지 않은 능력단위</div>

<div class="warn"><b>학습모듈 원문을 보려면</b> — 원문은 한국직업능력연구원 저작물이라
이 사이트에 올려 두지 않습니다. 내 PC 에서 아래를 켜고
<code>http://127.0.0.1:8765/</code> 로 들어오면 <b>학습모듈</b> 칸에 <b>PDF</b> 단추가
생겨 원문을 그대로 펼쳐 봅니다.<br>
<code>python COURSE-MANAGEMENT/tools/pdf-server.py</code></div>

<div class="tscroll"><table>
<thead><tr><th>능력단위</th><th>코드</th><th>수준</th><th>시간</th>
<th>학습모듈</th><th>교안</th><th>편성</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table></div>
<p class="tot">능력단위 {len(sv["units"])}개 · 학습모듈 {n_pdf}건 ·
편성 {n_pl}개 · 미편성 {len(sv["units"]) - n_pl}개<br>{esc(lv_txt)}</p>

<p class="bar">
  <a href="{dom}.html">← {esc(dv["label"])} 커리큘럼으로</a>
  <a href="../index.html">과정관리</a>
</p>
<p class="sc tot">교안 원본 —
  <a href="{ORG}/{esc(dv["repo"])}/tree/main/modules/{esc(code)}_{esc(sv["name"])}">{esc(dv["repo"])}/modules/{esc(code)}_{esc(sv["name"])}</a> (비공개)</p>
<footer>담당 정우균</footer>
</div>
''', encoding="utf-8")
            n_pages += 1

    (A / "curriculum.js").write_text(
        "/* 커리큘럼 도메인 카드. gen_curriculum.py 가 만든다 — 손으로 고치지 않는다.\n"
        " * 고치려면 NCS-CATALOG/data/mapping-domain.yml 을 고치고 다시 돌린다.\n"
        " */\nwindow.CM_CURRICULUM = "
        + json.dumps(cards, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")

    tot = len(units)
    n_pl = sum(1 for c in units if c in placed)
    print(f"커리큘럼 카드 {len(cards)}장 · 페이지 {n_pages}장")
    print(f"능력단위 {tot}개 · 편성 {n_pl}개 · 미편성 {tot - n_pl}개")
    for d, items in orphan.items():
        for uc, r, where in items:
            tag = doms[d]["label"] if d else "임자 없음"
            print(f"  ! 재고 밖 편성 [{tag}] {uc} {r['능력단위명']} "
                  f"— {r['세분류']}({r['세분류코드']}) · {'/'.join(c for c, _ in where)}")
    for c in cards:
        print(f"  {c['label']:14} 세분류 {c['subs']:2} · 능력단위 {c['units']:3} · "
              f"작성 {c['wip']:2} · 학습모듈 {c['pdf']:3} · 편성 {c['placed']:2}")


if __name__ == "__main__":
    main()
