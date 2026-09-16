# -*- coding: utf-8 -*-
"""
data/mapping-domain.yml + data/competency-units.csv 를 읽어
CURRICULUM-<DOMAIN>/modules/<세분류코드>_<세분류명>/<능력단위번호>_<능력단위명>/ 스켈레톤을 만든다.
기존 파일은 절대 덮어쓰지 않는다(_meta.yml 제외: --force 시 갱신).
"""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]      # NCS-CATALOG/
ORG = ROOT.parent                                # 조직 루트
UNITS = ROOT / "data" / "competency-units.csv"
MAP = ROOT / "data" / "mapping-domain.yml"
FORCE = "--force" in sys.argv


def load_units():
    by_sub = {}
    with UNITS.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            by_sub.setdefault(r["세분류코드"], []).append(r)
    return by_sub


def load_map():
    """의존성 없이 mapping-domain.yml의 필요한 부분만 파싱한다."""
    domains, cur, sect = {}, None, None
    for line in MAP.read_text(encoding="utf-8").splitlines():
        if re.match(r"^  [a-z0-9-]+:\s*$", line):
            cur = line.strip().rstrip(":")
            domains[cur] = {"repo": None, "primary": []}
            sect = None
        elif cur and re.match(r"^    repo:", line):
            domains[cur]["repo"] = line.split(":", 1)[1].strip()
        elif cur and re.match(r"^    (primary|related):", line):
            sect = line.strip().rstrip(":")
        elif cur and sect == "primary" and "code:" in line:
            m = re.search(r'code:\s*"(\d+)".*?name:\s*([^\s}]+)', line)
            if m:
                domains[cur]["primary"].append((m.group(1), m.group(2)))
    return domains


def safe(s):
    return re.sub(r'[\/:*?"<>|]', "-", s).strip()


def main():
    by_sub, domains, made = load_units(), load_map(), 0
    for dom, info in domains.items():
        base = ORG / info["repo"] / "modules"
        for code, name in info["primary"]:
            units = by_sub.get(code, [])
            sdir = base / f"{code}_{safe(name)}"
            sdir.mkdir(parents=True, exist_ok=True)
            meta = sdir / "_meta.yml"
            if FORCE or not meta.exists():
                lines = [
                    "# 자동 생성 (scripts/scaffold_modules.py). 수정 시 hours/level 만 손대세요.",
                    f"ncs_code: \"{code}\"",
                    f"name: {name}",
                    f"domain: {dom}",
                    f"unit_count: {len(units)}",
                    "units:",
                ]
                for u in units:
                    lines.append(f"  - code: \"{u['능력단위코드']}\"")
                    lines.append(f"    name: {u['능력단위명']}")
                    lines.append("    hours:            # 편성 훈련시간(직접 입력)")
                    lines.append("    level:            # NCS 수준(1~8)")
                meta.write_text("\n".join(lines) + "\n", encoding="utf-8")
            for u in units:
                no = u["능력단위코드"][8:10]
                udir = sdir / f"{no}_{safe(u['능력단위명'])}"
                if not udir.exists():
                    for sub in ("labs", "assessment", "slides"):
                        (udir / sub).mkdir(parents=True, exist_ok=True)
                    (udir / "teaching-plan.md").write_text(
                        "---\n"
                        f"unit_code: \"{u['능력단위코드']}\"\n"
                        f"unit_name: {u['능력단위명']}\n"
                        f"ncs_code: \"{code}\"\n"
                        f"subdivision: {name}\n"
                        "hours:\nlevel:\nstatus: draft\nupdated: \n"
                        "---\n\n"
                        f"# {u['능력단위명']}\n\n"
                        "## 학습목표(수행준거 기준)\n\n## 선수지식\n\n"
                        "## 차시별 전개\n\n| 차시 | 내용 | 방법 | 시간 |\n|---|---|---|---|\n\n"
                        "## 실습(labs/)\n\n## 평가(assessment/)\n\n## 참고자료\n",
                        encoding="utf-8")
                    made += 1
    print(f"생성된 능력단위 폴더: {made}개")


if __name__ == "__main__":
    main()
