# -*- coding: utf-8 -*-
"""
능력단위 수준(1~8)을 받아 competency-units.csv 를 채운다.

수준은 `getCompeUnit.do` 에는 없다. NCS 검색 상세 화면이 쓰는

  POST /unity/hth01/hth0101/ncsResultSearchList.do   (본문이 JSON 이어야 한다)

에만 있고, 세분류 한 번 호출로 그 안의 능력단위 수준을 한꺼번에 준다.
쿼리스트링으로 보내면 빈 응답이 온다 — Content-Type: application/json 이 필요하다.

같이 받아 두는 것
  수준        compeUnitLevel   1~8
  서비스중단  serviceStopYn    Y 면 더는 쓰지 않는 능력단위
  숨김        compeUnitHideYn  Y 면 검색에 안 나온다

  python NCS-CATALOG/scripts/fetch_ncs_levels.py
"""
import csv
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
URL = "https://www.ncs.go.kr/unity/hth01/hth0101/ncsResultSearchList.do"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
SLEEP = 0.2                      # 공공 사이트 예의상 요청 간 간격

# ncs.go.kr 은 구형 TLS 설정이라 파이썬 기본 컨텍스트로는 handshake 가 실패한다.
CTX = ssl.create_default_context()
CTX.set_ciphers("DEFAULT:@SECLEVEL=1")
if hasattr(ssl, "OP_LEGACY_SERVER_CONNECT"):
    CTX.options |= ssl.OP_LEGACY_SERVER_CONNECT


def txt(v):
    """수준은 숫자로도 문자로도 온다. 둘 다 문자열로 맞춘다."""
    return "" if v is None else str(v).strip()


def units_of(subd: str):
    """세분류 코드 8자리 -> 그 안의 능력단위 목록(수준 포함)."""
    body = json.dumps({
        "dutySvcNo": "", "ncsClCd": "", "ncsCompeUnitCd": "",
        "ncsLclasCd": subd[0:2], "ncsMclasCd": subd[2:4],
        "ncsSclasCd": subd[4:6], "ncsSubdCd": subd[6:8],
        "doCompeUnit": "false", "output": "ncsRsnInfo",
    }).encode()
    req = urllib.request.Request(
        URL, data=body, method="POST",
        headers={"User-Agent": UA, "X-Requested-With": "XMLHttpRequest",
                 "Content-Type": "application/json; charset=UTF-8",
                 "Referer": "https://www.ncs.go.kr/unity/th03/ncsResultSearch.do"})
    with urllib.request.urlopen(req, timeout=40, context=CTX) as r:
        d = json.loads(r.read().decode("utf-8"))
    time.sleep(SLEEP)
    return ((d.get("data") or {}).get("ncsRsnInfo") or {}).get("ncsList") or []


def main():
    src = DATA / "competency-units.csv"
    rows = list(csv.DictReader(open(src, encoding="utf-8-sig")))
    subds = sorted({r["세분류코드"] for r in rows})
    print(f"세분류 {len(subds)}개 · 능력단위 {len(rows)}건")

    lv, stop, hide, miss = {}, {}, {}, []
    for i, sc in enumerate(subds, 1):
        try:
            got = units_of(sc)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            miss.append(f"{sc} — {type(e).__name__}")
            print(f"  ! {sc} 실패 {type(e).__name__}")
            continue
        for u in got:
            code = u.get("ncsClCd")
            if not code:
                continue
            lv[code] = txt(u.get("compeUnitLevel"))
            stop[code] = txt(u.get("serviceStopYn"))
            hide[code] = txt(u.get("compeUnitHideYn"))
        if i % 20 == 0 or i == len(subds):
            print(f"  {i:3}/{len(subds)}  누적 {len(lv)}건")

    # csv 에 칸을 더한다. 이미 있으면 덮어쓴다.
    cols = list(rows[0].keys())
    for c in ("수준", "서비스중단", "숨김"):
        if c not in cols:
            cols.append(c)
    got_lv = 0
    for r in rows:
        c = r["능력단위코드"]
        r["수준"] = lv.get(c, "")
        r["서비스중단"] = stop.get(c, "")
        r["숨김"] = hide.get(c, "")
        if r["수준"]:
            got_lv += 1

    with src.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"\n수준 확보 {got_lv}/{len(rows)}건")
    from collections import Counter
    for k, n in sorted(Counter(r["수준"] for r in rows if r["수준"]).items()):
        print(f"  수준 {k} : {n:4}건")
    blank = [r["능력단위코드"] for r in rows if not r["수준"]]
    if blank:
        print(f"  수준 없음 {len(blank)}건: {', '.join(blank[:8])}"
              + (" ..." if len(blank) > 8 else ""))
    if miss:
        print("  실패한 세분류:", ", ".join(miss))
    print(f"-> {src.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
