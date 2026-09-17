# -*- coding: utf-8 -*-
"""
NCS 학습모듈 PDF 에서 교안에 쓸 뼈대를 뽑는다.

교안을 지어내지 않기 위해서다. 능력단위요소·학습내용·학습목표·평가방법은
한국직업능력연구원 학습모듈 원문에 있는 문장이고, 그것을 그대로 옮긴다.
우리가 정하는 것은 시간 배분과 차시 묶기뿐이다.

원문 PDF 는 저작물이라 저장소에 올리지 않는다(이 스크립트도 로컬 파일만 읽는다).
뽑아낸 결과(JSON)는 목차·제목 수준의 사실이라 커밋한다.

PDF 의 생김새 (27개 전부 같았다)
  차  례      학습 N. <능력단위요소>  /  N-M. <학습내용>  /  교수·학습 방법  /  평가
              제목 줄 다음 줄에 쪽번호가 온다
  개요        학습모듈의 목표 · 선수학습 · 내용체계(요소 코드번호) · 핵심 용어
  N-M 첫 쪽   학습 목표(•) · 필요 지식(1. 2. 3. …)
  평가 쪽     평가 방법 뒤에 •<방법> 이 온다

  python NCS-CATALOG/scripts/gen/lm_extract.py                 # 전부
  python NCS-CATALOG/scripts/gen/lm_extract.py 20010202        # 한 세분류만
"""
import csv
import json
import re
import sys
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "NCS-CATALOG" / "data"
OUT = DATA / "learning-modules"

LEARN = re.compile(r"^\s*학습\s*(\d+)\s*[.,]\s*(.+?)\s*$")
CONT = re.compile(r"^\s*(\d+)\s*[-‐–]\s*(\d+)\s*[.,]\s*(.+?)\s*$")
NUM = re.compile(r"^\s*(\d{1,3})\s*$")
ELEM_CD = re.compile(r"\d{10}_\d{2}v\d+\.\d+")
TOPIC = re.compile(r"^\s*(\d{1,2})\s*\.\s+(\S.*?)\s*$")
BULLET = re.compile(r"^\s*[•·▪]\s*(.+?)\s*$")
# 필요 지식의 큰 제목 앞에 붙는 글머리. 심볼 폰트가 한글 코드로 떨어져 나온 것이라
# 눈에는 안 보이지만 U+C214~U+C217 이다(27개 PDF 전수 조사). PUA 도 같이 쓰인다.
SYMBOL = re.compile(r"^[\uC214-\uC217\uE000-\uF8FF\u25A0-\u25FF"
                    r"\u2460-\u24FF\u2022\u00B7\u25AA\s]+")


# PDF 는 줄이 끝나는 자리에서 낱말을 자른다. 그대로 이으면 "파 악함으로써" 처럼
# 없던 띄어쓰기가 생긴다. 한글끼리 만났을 때만, 아래 두 경우에 붙여 준다.
#   - 뒷줄이 홀로 설 수 없는 조사·어미로 시작한다 (의, 고, 를, …)
#   - 앞줄이 한 글자로 끝나는데 그 글자가 홀로 쓰이는 말이 아니다 (수, 것, 등 … 제외)
TAIL_OK = set("수것때등중및시내외후전간이그저곳점")   # 홀로 쓰이는 말만
HEAD_JOIN = set("의고를을이가는은에로와과도만서며나야죠던든록써듯")
HANGUL = re.compile(r"[가-힣]")


def mend(a, b):
    """앞 조각 a 와 뒷 조각 b 를 어떻게 이을지 정한다."""
    a, b = a.rstrip(), b.lstrip()
    if not a or not b:
        return (a + b).strip()
    if not (HANGUL.match(a[-1]) and HANGUL.match(b[0])):
        return a + " " + b
    if b[0] in HEAD_JOIN and (len(b) == 1 or not HANGUL.match(b[1]) or b[1] == " "
                              or len(b.split(" ")[0]) <= 2):
        return a + b
    last = a.split(" ")[-1]
    if len(last) == 1 and last not in TAIL_OK:
        return a + b
    return a + " " + b


def clean(s):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s.replace("․", "·").replace("・", "·").replace("，", ",")


def pages_text(doc):
    return [doc[i].get_text() for i in range(doc.page_count)]


def printed_map(texts):
    """인쇄된 쪽번호 -> PDF 쪽 인덱스. 각 쪽 첫 줄이 쪽번호인 형식이다."""
    m = {}
    for i, t in enumerate(texts):
        for ln in t.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            n = NUM.match(ln)
            if n and int(n.group(1)) not in m:
                m[int(n.group(1))] = i
            break
    return m


def parse_toc(texts):
    """차례 -> 학습(요소) 과 그 아래 학습내용·교수학습·평가의 쪽번호."""
    idx = next((i for i, t in enumerate(texts[:25])
                if "차  례" in t or "차 례" in t), None)
    if idx is None:
        return None
    lines = [ln.rstrip() for ln in texts[idx].splitlines()]
    items, pend = [], None
    for ln in lines:
        n = NUM.match(ln)
        if n and pend:
            pend["page"] = int(n.group(1))
            items.append(pend)
            pend = None
            continue
        m = LEARN.match(ln)
        if m:
            items.append({"kind": "learn", "no": m.group(1),
                          "title": clean(m.group(2)), "page": None})
            pend = None
            continue
        m = CONT.match(ln)
        if m:
            pend = {"kind": "cont", "no": f"{m.group(1)}-{m.group(2)}",
                    "title": clean(m.group(3))}
            continue
        s = clean(ln).lstrip("•·▪ ").strip()
        if s.startswith("교수"):
            pend = {"kind": "teach", "title": s}
        elif s == "평가":
            pend = {"kind": "eval", "title": s}
        elif s.startswith("참고"):
            pend = {"kind": "ref", "title": s}
    return items


def section(text, start, *stops):
    """어떤 머리말 다음부터 다음 머리말 전까지."""
    lines = [ln.rstrip() for ln in text.splitlines()]
    try:
        i = next(k for k, ln in enumerate(lines) if clean(ln) == start)
    except StopIteration:
        return []
    out = []
    for ln in lines[i + 1:]:
        c = clean(ln)
        if c in stops or any(c.startswith(s) for s in stops):
            break
        if c:
            out.append(c)
    return out


def join_bullets(lines):
    """줄바꿈으로 잘린 • 항목을 다시 붙인다."""
    out = []
    for ln in lines:
        m = BULLET.match(ln)
        if m:
            out.append(m.group(1))
        elif out:
            out[-1] = mend(out[-1], ln)
        else:
            out.append(ln)
    return [clean(x) for x in out if clean(x)]


def overview(texts, after):
    """진짜 개요는 차례 뒤에 있다. 앞쪽 'NCS학습모듈의 이해' 는 사용법 설명이라
    같은 머리말이 들어 있어 그대로 집으면 방송 제작 예시를 읽게 된다."""
    i = next((k for k in range(after + 1, len(texts))
              if "학습모듈의 목표" in texts[k]), None)
    if i is None:
        return {}, []
    t = texts[i]
    goal = join_bullets(section(t, "학습모듈의 목표", "선수학습"))
    pre = join_bullets(section(t, "선수학습", "학습모듈의 내용체계", "학습모듈의 내용"))
    key = join_bullets(section(t, "핵심 용어", "출처", "[그림"))
    kws = []
    for k in ", ".join(key).split(","):
        k = clean(k)
        if k:
            kws.append(k)
    def merge(parts):
        r = ""
        for x in parts:
            r = mend(r, x) if r else x
        return r

    return ({"goal": merge(goal), "prereq": merge(pre), "keywords": kws},
            ELEM_CD.findall(t))


def gist(lines, limit=220):
    """제목 아래 본문의 첫 한두 문장. 원문 인용이라 손대지 않고 자르기만 한다."""
    body = ""
    for ln in lines:
        c = clean(ln)
        if not c or TOPIC.match(c) or SYMBOL.match(c):
            continue
        if c.startswith(("[그림", "[표", "출처", "<", "(출처")):
            continue
        if re.match(r"^\(\d+\)", c):       # (1) 무엇의 정의 — 소제목이지 본문이 아니다
            continue
        if len(c) < 6:
            continue
        body = mend(body, c) if body else c
        if len(body) > limit:
            break
    if not body:
        return ""
    out = ""
    for part in re.split(r"(?<=다\.)\s+", body):
        if out and len(out) + len(part) > limit:
            break
        out = (out + " " + part).strip()
        if len(out) >= 60:
            break
    return out[:limit].rstrip()


# 제목의 말투로 성격을 나눈다. 준비 교안의 안내가 항목마다 달라지도록.
KINDS = [
    ("개념", ("정의", "개요", "목적", "개념", "의의", "특징")),
    ("절차", ("절차", "단계", "방법", "기법", "프로세스", "수행", "작성", "구현", "설계")),
    ("도구", ("구성도", "도구", "유형", "종류", "형식", "표기", "언어", "도표", "모델")),
    ("판단", ("고려", "기준", "검토", "산정", "평가", "선정", "타당", "적정")),  # "분석" 은 "분석모델" 처럼 이름의 일부라 뺀다
]


def kind_of(title):
    """제목에 든 낱말 수로 정한다. 첫 일치로 정하면 '분석모델의 타당성 분석' 이
    '모델' 때문에 도구가 되어 버린다. 동점이면 아래 순서가 이긴다."""
    order = ["판단", "절차", "도구", "개념"]
    best, hit = "내용", 0
    for k in order:
        words = dict(KINDS)[k]
        n = sum(1 for w in words if w in title)
        if n > hit:
            best, hit = k, n
    return best


def topics(texts, a, b, printed_of):
    """'필요 지식' 과 '수행 내용' 사이의 제목과 그 아래 요지 — 차시 소재로 쓴다.
    그 뒤(수행 내용)는 번호 붙은 절차 문장이라 제목이 아니다."""
    lines = []
    for i in range(a, min(b, len(texts))):
        lines += [(ln.rstrip(), i) for ln in texts[i].splitlines()]

    heads, inside = [], False
    for idx, (ln, pg) in enumerate(lines):
        c = clean(ln)
        if c == "필요 지식":
            inside = True
            continue
        if c in ("수행 내용", "수행 tip"):
            inside = False
            continue
        if not inside or not c:
            continue
        head = SYMBOL.sub("", c)
        if head != c and 4 < len(head) < 60:
            heads.append((head, pg, idx))
            continue
        m = TOPIC.match(c)
        if m:
            t = clean(m.group(2))
            if 3 < len(t) < 60 and not t[0].isdigit():
                heads.append((t, pg, idx))

    out, seen = [], set()
    for n, (title, pg, idx) in enumerate(heads):
        if title in seen:
            continue
        seen.add(title)
        end = heads[n + 1][2] if n + 1 < len(heads) else len(lines)
        out.append({"t": title, "p": printed_of(pg),
                    "k": kind_of(title),
                    "s": gist([x for x, _ in lines[idx + 1:end]])})
    return out


def eval_of(texts, a, b):
    text = "\n".join(texts[a:min(b, len(texts))])
    methods = []
    lines = [clean(x) for x in text.splitlines()]
    grab = False
    for ln in lines:
        if ln == "평가 방법":
            grab = True
            continue
        if ln == "피드백":
            grab = False
            continue
        if not grab:
            continue
        m = BULLET.match(ln)
        if m:
            s = clean(m.group(1))
            if s and s not in methods and 1 < len(s) < 30:
                methods.append(s)
    fb = join_bullets(section(text, "피드백", "학습 "))
    return {"methods": methods, "feedback": fb[:6]}


def extract(pdf: Path, code: str, name: str):
    doc = pymupdf.open(pdf)
    texts = pages_text(doc)
    doc.close()

    items = parse_toc(texts)
    if not items:
        return None, "차례를 찾지 못함"
    pm = printed_map(texts)
    toc_i = next(k for k, t in enumerate(texts[:25])
                 if "차  례" in t or "차 례" in t)
    ov, elem_codes = overview(texts, toc_i)

    def pdfpage(printed):
        return pm.get(printed)

    inv = {v: k for k, v in sorted(pm.items())}

    def printed_of(i):
        """PDF 쪽 인덱스 -> 인쇄된 쪽번호. 그 쪽에 번호가 없으면 앞쪽 것을 쓴다."""
        for k in range(i, -1, -1):
            if k in inv:
                return inv[k]
        return None

    elements, cur = [], None
    for it in items:
        if it["kind"] == "learn":
            cur = {"no": it["no"], "name": it["title"], "code": "",
                   "contents": [], "eval": {}}
            elements.append(cur)
        elif cur is None:
            continue
        elif it["kind"] == "cont":
            cur["contents"].append({"no": it["no"], "title": it["title"],
                                    "printed": it["page"], "goals": [], "topics": []})
        elif it["kind"] == "eval":
            cur["_evalpage"] = it["page"]

    # 요소 코드번호는 개요에 나온 순서대로 붙는다
    for e, c in zip(elements, elem_codes):
        e["code"] = c

    # 학습내용별 학습목표·소재
    flat = [(e, c) for e in elements for c in e["contents"]]
    for n, (e, c) in enumerate(flat):
        a = pdfpage(c["printed"])
        if a is None:
            continue
        nxt = flat[n + 1][1]["printed"] if n + 1 < len(flat) else None
        b = pdfpage(nxt) if nxt else (pdfpage(e.get("_evalpage")) or a + 12)
        c["goals"] = join_bullets(section(texts[a], "학습 목표", "필요 지식"))
        c["topics"] = topics(texts, a, b or a + 12, printed_of)

    starts = [pdfpage(e["contents"][0]["printed"]) for e in elements if e["contents"]]
    for n, e in enumerate(elements):
        p = pdfpage(e.pop("_evalpage", None) or 0)
        nxt = starts[n + 1] if n + 1 < len(starts) else len(texts)
        e["eval"] = (eval_of(texts, p, nxt) if p is not None
                     else {"methods": [], "feedback": []})

    # 인쇄 1쪽이 PDF 몇 번째 쪽인가 — 준비 교안이 원문 쪽을 바로 열 때 쓴다
    out = {"code": code, "name": name, "pages": len(texts), "src": pdf.name,
           "front": (pdfpage(1) or 0) + 1 - 1}
    out.update(ov)
    out["elements"] = elements
    return out, None


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rows = list(csv.DictReader(open(DATA / "learning-modules.csv", encoding="utf-8-sig")))
    OUT.mkdir(parents=True, exist_ok=True)
    done = fail = 0
    for r in rows:
        if only and r["ncs_code"] != only:
            continue
        pdf = ROOT / Path(r["saved_as"].replace("\\", "/"))
        if not pdf.exists():
            continue
        d, err = extract(pdf, r["module_code"], r["unit_name"])
        if err:
            print(f"  ! {r['unit_name']} — {err}")
            fail += 1
            continue
        (OUT / f"{r['module_code']}.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        n_c = sum(len(e["contents"]) for e in d["elements"])
        n_g = sum(len(c["goals"]) for e in d["elements"] for c in e["contents"])
        n_t = sum(len(c["topics"]) for e in d["elements"] for c in e["contents"])
        n_m = sum(len(e["eval"]["methods"]) for e in d["elements"])
        warn = "" if (d["elements"] and n_g and n_t and n_m) else "   ← 빈 곳 있음"
        print(f"{r['unit_name'][:22]:24} 요소 {len(d['elements'])} · 내용 {n_c:2} · "
              f"목표 {n_g:2} · 소재 {n_t:3} · 평가방법 {n_m}{warn}")
        done += 1
    print(f"\n뽑음 {done} · 실패 {fail} -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
