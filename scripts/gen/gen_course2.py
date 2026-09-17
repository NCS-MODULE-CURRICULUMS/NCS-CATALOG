# -*- coding: utf-8 -*-
"""
운영 과정 c2 추가 — (디지털 컨버전스) 공공데이터 융합 풀스택 개발자 양성과정E

원본 NCS_EXAM_PAGE 에 만들어 둔 과정을 그대로 가져와 이 사이트의 틀에 얹는다.
  - 모듈 17개의 강사·기간·평가일·사전평가·능력단위 점수는 원본 assets/modules.js 값
  - 능력단위코드는 NCS-CATALOG 로 현행 코드에 매핑해 새로 붙인다 (원본에는 없던 정보)
  - 평가 개요가 있는 m01 · m16 만 잠금 해제 — 원본 locks.js 와 같다
  - 준비 교안 · 평가 자료 실물은 원본 사이트에 있으므로 그쪽으로 연결한다

데이터 파일을 과정별로 나눈다: assets/modules-cN.js · assets/locks-cN.js
"""
import json
import re
from pathlib import Path

ORG = Path(__file__).resolve().parents[3]
SITE = ORG / "COURSE-MANAGEMENT"
SRC_SITE = "https://my-web-common-lecture.github.io/NCS_EXAM_PAGE"

COURSE = {
    "id": "c2",
    "name": "(디지털 컨버전스) 공공데이터 융합 풀스택 개발자 양성과정E",
    "ncs": "20010202 응용SW엔지니어링 외",
    "period": "2026-02-24 ~ 2026-08-12",
    "hours": "900시간",
    "tc": "정우균",
    "page": "courses/c2.html",
}

CODE = json.loads((Path(__file__).parent / "code_map.json").read_text(encoding="utf-8"))

# 원본 assets/modules.js 값 그대로
RAW = [
 ("m01","화면 설계","정*균","2026-02-24","2026-03-05","2026-03-05","-","-","50.00","86.88"),
 ("m02","UI 디자인","정*균","2026-03-05","2026-03-18","2026-03-18","-","-","37.50","85.63"),
 ("m03","화면 구현","정*균","2026-03-18","2026-03-27","2026-03-27","-","-","62.50","87.19"),
 ("m04","요구사항 확인","정*균","2026-03-30","2026-04-06","2026-04-06","-","-","43.75","72.5"),
 ("m05","데이터베이스 구현","정*균","2026-04-07","2026-04-14","2026-04-14","-","-","25.00","82.5"),
 ("m06","SQL활용","정*균","2026-04-14","2026-04-20","2026-04-20","-","-","81.25","86.5"),
 ("m07","개발 환경 운영 지원","김*우,정*균","2026-04-20","2026-04-27","2026-04-27","-","-","31.25","87.5"),
 ("m08","프로그래밍 언어 활용","정*균","2026-04-27","2026-05-11","2026-05-11","-","-","75.00","92.5"),
 ("m09","네트워크 프로그래밍 구현","정*균","2026-05-11","2026-05-19","2026-05-19","-","-","62.50","77.5"),
 ("m10","인터페이스 구현","정*균","2026-05-19","2026-05-27","2026-05-27","-","-","62.50","93"),
 ("m11","애플리케이션 설계","정*균","2026-05-27","2026-06-08","2026-06-08","2026-06-09","-","37.50","76.5"),
 ("m12","서버프로그램 구현","정*균","2026-06-08","2026-06-18","2026-06-18","-","-","43.75","82.5"),
 ("m13","통합 구현","정*균","2026-06-18","2026-06-25","2026-06-25","-","-","62.50","91"),
 ("m14","애플리케이션 테스트 수행","정*균","2026-06-25","2026-07-02","2026-07-02","-","-","62.50","82.29"),
 ("m15","애플리케이션 배포","정*균","2026-07-02","2026-07-08","2026-07-08","2026-07-10","-","56.25","91.29"),
 ("m16","(비NCS 실기) 공공 데이터 융합 DBMS 구축","정*균","2026-07-08","2026-07-21","-","-","-","0","0"),
 ("m17","(비NCS 실기) 공공 데이터 융합 실무 프로젝트","정*균","2026-07-21","2026-08-12","-","-","-","0","0"),
]

# 원본 modules/m01·m16 의 평가 개요. 나머지는 원본에서도 미등록 상태다.
DETAIL = {
 "m01": {
   "meta": "평가일 2026-03-05 (09:00~18:00) · 포트폴리오 100점",
   "unit": "화면 설계 (2001020224_23v6) / 5수준",
   "method": "포트폴리오 (100점) · 합격선 60점",
   "desc": "[팀별제출] 웹기획을 위한 각 단계를 이행합니다. "
           "유스케이스 다이어그램 · 명세서 → 스타일가이드 → 프로토타입 구현.",
   "score": "① UI 요구사항 확인하기 60점 (과제1 30 + 과제2 30) + ② UI 설계하기 40점 (과제3 40)",
   "submit": "스타일가이드 PDF · 프로토타입 Figma 링크 및 캡처 PDF · 유스케이스 문서",
   "guide": "guides/m01.html",
 },
 "m16": {
   "meta": "평가일 2026-07-21 (09:00~18:00) · 문제해결시나리오 100점",
   "unit": "(비NCS 실기) — NCS 능력단위에 대응하지 않는 자체 실기 과목",
   "method": "문제해결 시나리오 (100점) · 합격선 60점",
   "desc": "공공데이터포털에서 확보한 데이터로 이진분류 모델을 학습하고, 그 모델을 API 로 "
           "서비스한 뒤 인증이 적용된 웹 화면에서 예측하고 이력을 DB 로 관리(CRUD)하는 "
           "서비스를 구축합니다.",
   "score": "공공데이터 융합 기초 30점 + 공공데이터 융합 DBMS 구축 70점",
   "submit": "PPT(실행화면 캡처 포함) · 소스 폴더(01 / 02 / 03) GITHUB REPO 링크",
   "guide": None,
 },
}

OPEN = {"m01", "m16"}      # 원본 locks.js 와 동일


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def build_modules():
    mods = []
    for mid, name, tc, sd, ed, ev, ab, re_, pre, sc in RAW:
        c = CODE.get(name)
        mods.append({
            "id": mid, "name": name,
            "code": c["code"] if c else "",
            "sub": c["sub"] if c else "(비NCS)",
            "tc": tc, "sd": sd, "ed": ed, "ev": ev, "ab": ab, "re": re_,
            "pre": pre, "sc": sc,
            "page": f"modules/{COURSE['id']}-{mid}.html",
            "lp": "",
        })
    return mods


def js(title, writer, var, data):
    return "\n".join([
        f"/* {title}",
        f" * courses/{writer}.html 의 [설정 파일 저장] 이 이 파일을 덮어씁니다. 손으로 고쳐도 됩니다.",
        " * 고친 뒤 git 에 올려야 모두에게 적용됩니다.",
        " */",
        f"window.{var} = " + json.dumps(data, ensure_ascii=False, indent=2) + ";",
        "",
    ])


def detail_page(m):
    d = DETAIL.get(m["id"])
    nav = "".join(
        f'<a class="{"act" if x["id"]==m["id"] else "na"}" '
        f'href="{x["id"] == m["id"] and "#" or ""}{"" if x["id"]==m["id"] else "../"+x["page"]}">'
        f'{esc(x["name"])}</a>'
        for x in MODS)
    if d:
        body = f"""<div class="note"><b>평가 개요</b><br>
능력단위 {esc(d['unit'])} · 평가방법 <b>{esc(d['method'])}</b><br>
{esc(d['desc'])}<br>
배점 — {esc(d['score'])}<br>
제출 — {esc(d['submit'])}</div>

<h2 class="sub2">평가 자료</h2>
<p class="body">이 과정의 준비 교안과 평가 자료(포트폴리오 제출서 · 채점판 · 평가도구)는
원본 사이트에 있습니다.</p>
<p><a class="btn" href="{SRC_SITE}/modules/{m['id']}.html" target="_blank" rel="noopener">평가 자료 열기</a>
{'<a class="btn" href="' + SRC_SITE + '/' + d['guide'] + '" target="_blank" rel="noopener">준비 교안</a>' if d['guide'] else ''}</p>
<p class="memo">원본 사이트도 같은 로그인이 필요합니다.</p>"""
    else:
        body = '<div class="empty">평가 자료가 아직 등록되지 않았습니다.<br>' \
               f'<a href="../courses/{COURSE["id"]}.html">능력단위 모듈 목록으로</a></div>'

    code_line = (f'<span>능력단위코드 <b class="pre">{esc(m["code"])}</b></span>'
                 f'<span>세분류 <b>{esc(m["sub"])}</b></span>') if m["code"] else \
                '<span><b>NCS 능력단위에 대응하지 않는 자체 실기 과목</b></span>'

    return f"""<meta charset="utf-8"><title>{esc(m['name'])}</title>
<link rel="stylesheet" href="../assets/site.css">
<script src="../assets/auth.js"></script>
<script>EXAM_AUTH.guard("../");</script>
<div class="top"><div class="tbar">
  <div class="brand"><a href="../index.html">과정관리</a>
  <small><a href="../courses/{COURSE['id']}.html">{esc(COURSE['name'])}</a> / {esc(m['name'])}</small></div>
  <div class="tuser" id="tUser"><b id="tName"></b><button id="tOut" type="button">로그아웃</button></div>
</div>
<div class="nav">{nav}</div>
</div>
<script>EXAM_AUTH.paintTop("../");</script>
<style>
  .facts{{display:flex;gap:20px;flex-wrap:wrap;border:1px solid #000;padding:10px 14px;
         margin:14px 0;font-size:12.5px}}
  .facts b{{font-size:15px;margin-left:4px}}
  .sub2{{font-size:15px;margin:26px 0 8px;padding-bottom:6px;border-bottom:1px solid #000;font-weight:700}}
  .body{{font-size:13.5px;line-height:1.8}}
  .memo{{font-size:12.5px;line-height:1.7;color:#555}}
</style>
<div class="wrap">
<h1>{esc(m['name'])}</h1>
<p class="sub">{esc(COURSE['name'])}</p>

<div class="facts">
  {code_line}
  <span>강사 <b>{esc(m['tc'])}</b></span>
  <span>기간 <b>{m['sd']} ~ {m['ed']}</b></span>
  <span>본평가 <b>{m['ev']}</b></span>
</div>
{('<p class="memo">' + esc(DETAIL[m['id']]['meta']) + '</p>') if m['id'] in DETAIL else ''}

{body}

<p style="margin-top:20px"><a class="btn" href="../courses/{COURSE['id']}.html">← 능력단위 모듈 목록으로</a></p>
<footer>{esc(COURSE['name'])} · {esc(COURSE['period'])} · 담당 {esc(COURSE['tc'])}</footer>
</div>
"""


MODS = build_modules()


def main():
    A = SITE / "assets"
    # 과정별 데이터 파일
    (A / "modules-c2.js").write_text(
        js("(디지털 컨버전스) 공공데이터 융합 풀스택 개발자 양성과정E 의 능력단위 모듈.",
           "c2", "CM_MODULES", MODS), encoding="utf-8")
    (A / "locks-c2.js").write_text(
        js("모듈별 잠금 상태.  true = 잠김(일반은 상세를 못 엽니다)", "c2", "CM_LOCKS",
           {m["id"]: (m["id"] not in OPEN) for m in MODS}), encoding="utf-8")

    # c1 데이터 파일 이름도 규칙에 맞춘다
    for old, new in [("modules.js", "modules-c1.js"), ("locks.js", "locks-c1.js")]:
        if (A / old).exists():
            (A / new).write_text((A / old).read_text(encoding="utf-8"), encoding="utf-8")
            (A / old).unlink()

    # courses.js — 두 과정
    c1 = None
    txt = (A / "courses.js").read_text(encoding="utf-8")
    m = re.search(r"window\.CM_COURSES = (\[.*?\]);", txt, re.S)
    if m:
        c1 = json.loads(m.group(1))
    (A / "courses.js").write_text(
        js("과정 목록.", "index", "CM_COURSES", (c1 or []) + [COURSE]).replace(
            "courses/index.html 의", "index.html 의"), encoding="utf-8")

    # 모듈 상세
    md = SITE / "modules"
    for m_ in MODS:
        (md / f"c2-{m_['id']}.html").write_text(detail_page(m_), encoding="utf-8")

    print(f"assets/modules-c2.js · locks-c2.js  (모듈 {len(MODS)})")
    print(f"assets/courses.js  과정 {len(c1 or []) + 1}개")
    print(f"modules/c2-m01.html ~ c2-m17.html")


if __name__ == "__main__":
    main()
