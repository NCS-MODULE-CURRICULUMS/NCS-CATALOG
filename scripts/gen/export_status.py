# -*- coding: utf-8 -*-
"""
커리큘럼 진행 상태를 공개 데이터로 내보낸다.

커리큘럼 4종(CURRICULUM-*)은 비공개 저장소다. 과정관리 사이트는 공개 저장소에 있다.
그래서 사이트가 "지금 교안이 어디까지 됐는지" 를 보여주려면 상태만 따로 뽑아야 한다.

  나가는 것 — 능력단위코드 · 시간 · 수준 · 차시 · 상태 · 산출물 유무
  안 나가는 것 — 교안 본문, 평가 문항, 모범답안, 실습 정답

이 스크립트가 조직에서 비공개 저장소를 읽는 유일한 자리다. 여기 말고 다른 곳에서
CURRICULUM-* 를 읽지 않는다.

  python NCS-CATALOG/scripts/gen/export_status.py
"""
import json
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "NCS-CATALOG" / "data"
OUT = DATA / "curriculum-status.json"

# 능력단위 폴더 안에서 세는 산출물. 열쇠 이름은 사이트가 그대로 쓴다.
PARTS = {"lp": "lesson-plans", "lab": "labs", "as": "assessment", "sl": "slides"}

# 진척 단계. 교안 파일이 있다/없다 는 진척이 아니다 — 골격 파일도 파일이다.
#   골격   : 섹션 제목만 있는 279바이트짜리 틀
#   작성중 : 표준 강의 교안 6시트를 씌웠고 '채울 자리' 가 남음
#   완성   : 빈칸 없음. 강사 검수 전
#   검수   : frontmatter status: ready
STAGES = ["골격", "작성중", "완성", "검수"]
SIX = "① 교과개요"


def stage_of(body, todo, st):
    if SIX not in body:
        return 0
    if todo:
        return 1
    return 3 if st == "ready" else 2
FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def frontmatter(p: Path):
    m = FM.search(p.read_text(encoding="utf-8"))
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def load_domains():
    """mapping-domain.yml 의 primary 세분류만 읽는다 (모듈 폴더가 있는 것)."""
    txt = (DATA / "mapping-domain.yml").read_text(encoding="utf-8")
    doms, cur, sect = {}, None, None
    for line in txt.splitlines():
        if re.match(r"^  [a-z0-9-]+:\s*$", line):
            cur, sect = line.strip().rstrip(":"), None
            doms[cur] = {"repo": "", "label": "", "subs": [], "rel": []}
        elif cur and re.match(r"^    (repo|label):", line):
            k, v = line.split(":", 1)
            doms[cur][k.strip()] = v.strip()
        elif re.match(r"^    (primary|related):\s*$", line):
            sect = line.strip().rstrip(":")
        elif cur and sect:
            m = re.search(r'code:\s*"(\d+)"\s*,\s*name:\s*([^\s}]+)', line)
            if m:
                key = "subs" if sect == "primary" else "rel"
                doms[cur][key].append((m.group(1), m.group(2)))
    return doms


def pdf_index():
    """학습모듈 PDF 를 받아 둔 능력단위코드 (learning-modules.csv 는 공개 자료)."""
    import csv
    have = set()
    f = DATA / "learning-modules.csv"
    if f.exists():
        for r in csv.DictReader(open(f, encoding="utf-8-sig")):
            if r.get("module_code"):
                have.add(r["module_code"])
    return have


def main():
    doms, pdfs = load_domains(), pdf_index()
    out = {
        "generated": date.today().isoformat(),
        "note": "상태 요약만 담는다. 교안 본문·평가 문항은 담지 않는다.",
        "domains": {}, "subs": {}, "units": {},
    }
    miss = []

    for dom, v in doms.items():
        repo = ROOT / v["repo"]
        out["domains"][dom] = {"repo": v["repo"], "label": v["label"], "subs": [],
                               "rel": {c: n for c, n in v["rel"]}}

        for code, name in v["subs"]:
            base = repo / "modules" / f"{code}_{name}"
            if not base.exists():                       # 폴더명이 다를 수 있다
                cand = list((repo / "modules").glob(f"{code}_*"))
                base = cand[0] if cand else None
            if base is None:
                miss.append(f"{v['repo']} : {code}_{name} 폴더 없음")
                continue

            out["domains"][dom]["subs"].append(code)
            units = []
            for d in sorted(p for p in base.iterdir() if p.is_dir()):
                if d.name.startswith("_"):      # _unmatched — 능력단위가 아니라 PDF 보관함
                    continue
                tp = d / "teaching-plan.md"
                if not tp.exists():
                    miss.append(f"{base.name}/{d.name} : teaching-plan.md 없음")
                    continue
                body = tp.read_text(encoding="utf-8")
                fm = frontmatter(tp)
                uc = fm.get("unit_code", "")
                if not uc:
                    miss.append(f"{base.name}/{d.name} : unit_code 없음")
                    continue
                has = {k: int(any(x.name != ".gitkeep" for x in (d / sub).iterdir()))
                       if (d / sub).exists() else 0 for k, sub in PARTS.items()}
                has["pdf"] = int(uc in pdfs)
                out["units"][uc] = {
                    "n": fm.get("unit_name", d.name),
                    "d": dom, "s": code, "seq": d.name.split("_", 1)[0],
                    "hr": int(fm["hours"]) if fm.get("hours", "").isdigit() else None,
                    "lv": int(fm["lv"]) if fm.get("lv", "").isdigit()
                          else (int(fm["level"]) if fm.get("level", "").isdigit() else None),
                    "ses": int(fm["sessions"]) if fm.get("sessions", "").isdigit() else None,
                    "st": fm.get("status", "draft"),
                    "todo": body.count("채울 자리"),
                    "sz": len(body),
                    "stg": stage_of(body, body.count("채울 자리"), fm.get("status", "draft")),
                    "up": fm.get("updated", ""),
                    "has": has,
                }
                units.append(uc)
            out["subs"][code] = {"name": name, "d": dom, "units": units}

    out["stages"] = STAGES
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    n_d, n_s, n_u = len(out["domains"]), len(out["subs"]), len(out["units"])
    ready = sum(1 for u in out["units"].values() if u["st"] == "ready")
    print(f"도메인 {n_d} · 세분류 {n_s} · 능력단위 {n_u} · ready {ready}")
    for i, nm in enumerate(STAGES):
        c = sum(1 for u in out["units"].values() if u["stg"] == i)
        print(f"  {i} {nm:4} {c:4}건")
    print(f"  채울 자리 {sum(u['todo'] for u in out['units'].values())}곳")
    for k in ("lp", "lab", "as", "sl", "pdf"):
        print(f"  {k:4} {sum(u['has'][k] for u in out['units'].values()):4}건")
    for m in miss:
        print("  ! " + m)
    print(f"→ {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
