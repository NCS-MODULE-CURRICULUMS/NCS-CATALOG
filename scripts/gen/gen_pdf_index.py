# -*- coding: utf-8 -*-
"""
학습모듈 PDF 색인을 만든다 — 파일이 아니라 '어디에 있는지'만.

NCS 학습모듈 PDF 는 한국직업능력연구원 저작물이라 공개 저장소에 올리지 않는다
(291개 3.0GB, 최대 116MB — GitHub Pages 한도로도 불가능하다).
그래서 사이트에는 색인만 두고, 파일은 강사 PC 에 있는 것을 브라우저가 직접 연다.

  window.CM_PDF[능력단위코드] = {
    p : 조직 루트 기준 경로 조각들   — 폴더를 한 번 고르면 이걸로 찾아 들어간다
    n : 파일명
    mb: 크기(MB)                    — 없으면 아직 안 받은 것
    d : ncs.go.kr 내려받기 키       — 파일이 없을 때 여기서 받는다
  }

색인은 learning-modules.csv(공개 자료)에서 나온다. 저작물 자체는 나가지 않는다.

  python NCS-CATALOG/scripts/gen/gen_pdf_index.py
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "NCS-CATALOG" / "data"
OUT = ROOT / "COURSE-MANAGEMENT" / "assets" / "modules-pdf.js"


def main():
    rows = list(csv.DictReader(open(DATA / "learning-modules.csv", encoding="utf-8-sig")))
    idx, here, gone = {}, 0, 0

    for r in rows:
        code = (r.get("module_code") or "").strip()
        saved = (r.get("saved_as") or "").strip()
        if not code or not saved:
            continue
        parts = saved.replace("\\", "/").split("/")
        p = ROOT / Path(*parts)
        mb = round(p.stat().st_size / 1024 / 1024, 1) if p.exists() else 0
        if mb:
            here += 1
        else:
            gone += 1
        idx[code] = {
            "p": parts,
            "n": parts[-1],
            "mb": mb,
            "d": "|".join((r.get("sysDstinCd") or "", r.get("fileMstky") or "",
                           r.get("filedetlSeq") or "")),
        }

    OUT.write_text(
        "/* 학습모듈 PDF 색인 — 파일이 아니라 위치만 담는다.\n"
        " * gen_pdf_index.py 가 만든다. 손으로 고치지 않는다.\n"
        " * PDF 원문은 한국직업능력연구원 저작물이라 이 저장소에 올리지 않는다.\n"
        " */\nwindow.CM_PDF = "
        + json.dumps(idx, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")

    print(f"색인 {len(idx)}건 · 내 PC 에 있음 {here} · 아직 없음 {gone}")
    print(f"-> {OUT.relative_to(ROOT)}  ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
