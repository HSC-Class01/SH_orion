import csv, io, json, os, re, sys, time, zipfile
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
DASH = ROOT / "dashboard" / "data.js"
API = "https://opendart.fss.or.kr/api"
START_YEAR = 2010
REPORTS = {"annual":"11011", "half_year":"11012", "quarterly_q1":"11013", "quarterly_q3":"11014"}

# Names used in DART statements can vary slightly by XBRL taxonomy/reporting format.
ALIASES = {
    "revenue": ["매출액", "수익(매출액)", "영업수익", "매출", "수익"],
    "cost_of_sales": ["매출원가"],
    "gross_profit": ["매출총이익", "매출총손익"],
    "operating_income": ["영업이익", "영업이익(손실)"],
    "pretax_income": ["법인세비용차감전순이익", "법인세비용차감전순손익", "세전이익"],
    "net_income": ["당기순이익", "당기순이익(손실)", "분기순이익", "반기순이익"],
    "controlling_net_income": ["지배기업의 소유주에게 귀속되는 당기순이익", "지배기업 소유주지분", "지배주주순이익"],
    "total_assets": ["자산총계"],
    "current_assets": ["유동자산"],
    "quick_assets": ["당좌자산"],
    "receivables": ["매출채권", "매출채권및기타채권", "매출채권 및 기타채권"],
    "inventory": ["재고자산"],
    "payables": ["매입채무", "매입채무및기타채무", "매입채무 및 기타채무"],
    "cash": ["현금및현금성자산", "현금 및 현금성자산", "현금성자산"],
    "total_liabilities": ["부채총계"],
    "current_liabilities": ["유동부채"],
    "total_equity": ["자본총계"],
    "borrowings": ["단기차입금", "장기차입금", "유동성장기부채", "사채", "차입금"],
    "cfo": ["영업활동으로 인한 현금흐름", "영업활동현금흐름", "영업활동으로 인한 현금흐름(손실)"],
    "cfi": ["투자활동으로 인한 현금흐름", "투자활동현금흐름"],
    "cff": ["재무활동으로 인한 현금흐름", "재무활동현금흐름"],
    "capex": ["유형자산의 취득", "유형자산 취득", "무형자산의 취득", "무형자산 취득"],
    "interest_expense": ["이자비용", "금융비용", "이자비용(금융비용)"],
    "tax_expense": ["법인세비용", "법인세비용(수익)"],
    "eps": ["기본주당이익", "기본주당순이익", "기본주당이익(손실)"],
    "depreciation_amortization": ["감가상각비", "감가상각비 및 무형자산상각비", "유형자산감가상각비", "무형자산상각비"],
}

def clean_num(v):
    if v is None: return None
    s = str(v).strip().replace(",", "")
    if not s or s in {"-", "--", "N/A", "nan"}: return None
    try: return float(s)
    except ValueError: return None

def normalize_name(s):
    return re.sub(r"\s+", "", (s or "")).replace("(손실)", "").replace("(이익)", "")

def pick(rows, key, sj=None, prefer_controlling=False):
    aliases = [normalize_name(x) for x in ALIASES.get(key, [])]
    candidates = []
    for r in rows:
        if sj and r.get("sj_div") != sj: continue
        nm = normalize_name(r.get("account_nm"))
        if any(a == nm or a in nm for a in aliases):
            val = clean_num(r.get("thstrm_amount"))
            if val is None: val = clean_num(r.get("thstrm_add_amount"))
            if val is not None: candidates.append((r, val))
    if not candidates: return None
    if key in {"borrowings", "capex"}:
        return sum(v for _, v in candidates)
    # Prefer exact alias and non-detail lines.
    candidates.sort(key=lambda rv: (0 if normalize_name(rv[0].get("account_nm")) in aliases else 1, len(rv[0].get("account_nm", ""))))
    return candidates[0][1]

def request_json(params):
    r = requests.get(f"{API}/fnlttSinglAcntAll.json", params=params, timeout=40)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "000":
        raise RuntimeError(f"DART {data.get('status')}: {data.get('message')}")
    return data

def find_corp_code(api_key):
    r = requests.get(f"{API}/corpCode.xml", params={"crtfc_key": api_key}, timeout=60)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        xml = z.read("CORPCODE.xml").decode("utf-8")

    # Match each <list> record independently so corp_code cannot leak across companies.
    records = re.findall(r"<list>(.*?)</list>", xml, re.S)
    for record in records:
        name = re.search(r"<corp_name>(.*?)</corp_name>", record, re.S)
        stock = re.search(r"<stock_code>(.*?)</stock_code>", record, re.S)
        code = re.search(r"<corp_code>(\d+)</corp_code>", record, re.S)
        if name and stock and code and name.group(1).strip() == "오리온" and stock.group(1).strip() == "271560":
            return code.group(1)

    # Fallback remains confined to a single record and exact company name.
    for record in records:
        name = re.search(r"<corp_name>(.*?)</corp_name>", record, re.S)
        code = re.search(r"<corp_code>(\d+)</corp_code>", record, re.S)
        if name and code and name.group(1).strip() == "오리온":
            return code.group(1)

    raise RuntimeError("오리온(종목코드 271560)의 corp_code를 찾지 못했습니다.")

def extract_record(data, year, report_key, fs_div):
    rows = data.get("list", [])
    vals = {
        "year": year, "report": report_key, "fs_div": fs_div,
        "period_type": "3M" if report_key.startswith("quarterly") else ("6M" if report_key == "half_year" else "12M"),
        "filing_no": rows[0].get("rcept_no") if rows else "",
        "currency": rows[0].get("currency") if rows else "KRW",
    }
    for key, sj in [("revenue","IS"),("cost_of_sales","IS"),("gross_profit","IS"),("operating_income","IS"),("pretax_income","IS"),("net_income","IS"),("controlling_net_income","IS"),("total_assets","BS"),("current_assets","BS"),("quick_assets","BS"),("receivables","BS"),("inventory","BS"),("payables","BS"),("cash","BS"),("total_liabilities","BS"),("current_liabilities","BS"),("total_equity","BS"),("borrowings","BS"),("cfo","CF"),("cfi","CF"),("cff","CF"),("capex","CF"),("interest_expense","IS"),("tax_expense","IS"),("eps","IS"),("depreciation_amortization","IS")]:
        vals[key] = pick(rows, key, sj)
    return vals

def annualize_report(record):
    # Values from fnlttSinglAcntAll are already the reported period values. Ratios use the same period.
    r = dict(record)
    revenue = r.get("revenue")
    op = r.get("operating_income")
    ni = r.get("net_income")
    assets = r.get("total_assets")
    eq = r.get("total_equity")
    liab = r.get("total_liabilities")
    cur_a = r.get("current_assets")
    cur_l = r.get("current_liabilities")
    cash = r.get("cash")
    cfo = r.get("cfo")
    borrow = r.get("borrowings")
    da = r.get("depreciation_amortization")
    ebitda = (op + da) if op is not None and da is not None else None
    r["gross_margin"] = safe_div(r.get("gross_profit"), revenue, 100)
    r["operating_margin"] = safe_div(op, revenue, 100)
    r["net_margin"] = safe_div(ni, revenue, 100)
    r["current_ratio"] = safe_div(cur_a, cur_l, 100)
    quick_assets = r.get("quick_assets")
    if quick_assets is None and cur_a is not None and r.get("inventory") is not None:
        quick_assets = cur_a - r.get("inventory")
    r["quick_ratio"] = safe_div(quick_assets, cur_l, 100)
    r["debt_ratio"] = safe_div(liab, eq, 100)
    r["equity_ratio"] = safe_div(eq, assets, 100)
    r["borrowing_dependency"] = safe_div(r.get("borrowings"), assets, 100)
    r["roa"] = safe_div(ni, assets, 100)
    r["roe"] = safe_div(ni, eq, 100)
    r["asset_turnover"] = safe_div(revenue, assets)
    tax_rate = safe_div(r.get("tax_expense"), r.get("pretax_income"))
    nopat = op * (1 - max(0, min(tax_rate, 0.5))) if op is not None and tax_rate is not None else None
    invested_capital = None
    if eq is not None and r.get("borrowings") is not None and cash is not None:
        invested_capital = eq + r.get("borrowings") - cash
    r["nopat"] = nopat
    r["invested_capital"] = invested_capital
    r["roic"] = safe_div(nopat, invested_capital, 100)
    r["cfo_to_ni"] = safe_div(cfo, ni)
    r["net_debt"] = (borrow - cash) if borrow is not None and cash is not None else None
    r["net_debt_ebitda"] = safe_div(r["net_debt"], ebitda)
    r["interest_coverage"] = safe_div(op, abs(r.get("interest_expense")) if r.get("interest_expense") is not None else None)
    r["ebitda"] = ebitda
    r["fcf"] = (cfo - abs(r.get("capex"))) if cfo is not None and r.get("capex") is not None else None
    r["dso"] = safe_div(r.get("receivables"), revenue, 365)
    r["dio"] = safe_div(r.get("inventory"), r.get("cost_of_sales"), 365)
    r["dpo"] = safe_div(r.get("payables"), r.get("cost_of_sales"), 365)
    if r.get("dso") is not None and r.get("dio") is not None and r.get("dpo") is not None:
        r["ccc"] = r["dso"] + r["dio"] - r["dpo"]
    else:
        r["ccc"] = None
    return r

def avg(a,b):
    return (a+b)/2 if a is not None and b is not None else None

def safe_div(a,b,mult=1):
    try:
        if a is None or b in (None,0): return None
        return (a/b)*mult
    except Exception: return None

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = []
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)

def run():
    api_key = os.environ.get("DART_API_KEY", "").strip()
    if not api_key: raise SystemExit("DART_API_KEY 환경변수가 필요합니다.")
    corp_code = find_corp_code(api_key)
    statuses=[]; records=[]
    for year in range(START_YEAR, time.localtime().tm_year + 1):
        for report_key, report_code in REPORTS.items():
            if year < 2015:
                statuses.append({"year":year,"report":report_key,"status":"unavailable","reason":"OpenDART fnlttSinglAcntAll provides financial data from 2015 onward"})
                continue
            for fs_div in ("CFS", "OFS"):
                try:
                    data = request_json({"crtfc_key":api_key,"corp_code":corp_code,"bsns_year":str(year),"reprt_code":report_code,"fs_div":fs_div})
                    rawdir=RAW/str(year); rawdir.mkdir(parents=True, exist_ok=True)
                    (rawdir/f"{report_code}_{fs_div}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                    if data.get("list"):
                        rec=extract_record(data, year, report_key, fs_div)
                        records.append(annualize_report(rec))
                        statuses.append({"year":year,"report":report_key,"fs_div":fs_div,"status":"ok","filing_no":rec.get("filing_no","")})
                        break
                    else:
                        statuses.append({"year":year,"report":report_key,"fs_div":fs_div,"status":"no_data","reason":data.get("message","")})
                except Exception as e:
                    statuses.append({"year":year,"report":report_key,"fs_div":fs_div,"status":"error","reason":str(e)})
    # Keep CFS preferentially, otherwise OFS.
    dedup={}
    for r in records:
        dedup[(r["year"],r["report"])] = r
    records=list(dedup.values())
    for report_key in {r["report"] for r in records}:
        seq=sorted([r for r in records if r["report"]==report_key and r.get("revenue") is not None], key=lambda x:x["year"])
        prev=None
        for r in seq:
            r["revenue_growth"] = safe_div(r.get("revenue") - prev, prev, 100) if prev not in (None,0) else None
            prev=r.get("revenue")
    # For annual ROA/ROE/turnover/ROIC, apply the guide's average-balance principle when prior-year balances exist.
    annual_seq=sorted([r for r in records if r["report"]=="annual"], key=lambda x:x["year"])
    prev=None
    for r in annual_seq:
        if prev is not None:
            avg_assets=avg(prev.get("total_assets"), r.get("total_assets"))
            avg_eq=avg(prev.get("total_equity"), r.get("total_equity"))
            avg_ic=avg(prev.get("invested_capital"), r.get("invested_capital"))
            r["roa"]=safe_div(r.get("net_income"), avg_assets, 100)
            r["roe"]=safe_div(r.get("net_income"), avg_eq, 100)
            r["asset_turnover"]=safe_div(r.get("revenue"), avg_assets)
            r["roic"]=safe_div(r.get("nopat"), avg_ic, 100)
            avg_ar=avg(prev.get("receivables"), r.get("receivables"))
            avg_inv=avg(prev.get("inventory"), r.get("inventory"))
            avg_ap=avg(prev.get("payables"), r.get("payables"))
            r["dso"]=safe_div(avg_ar, r.get("revenue"), 365)
            r["dio"]=safe_div(avg_inv, r.get("cost_of_sales"), 365)
            r["dpo"]=safe_div(avg_ap, r.get("cost_of_sales"), 365)
            if all(r.get(k) is not None for k in ("dso","dio","dpo")):
                r["ccc"]=r["dso"]+r["dio"]-r["dpo"]
        prev=r
    annual=[r for r in records if r["report"]=="annual"]
    half=[r for r in records if r["report"]=="half_year"]
    quarter=[r for r in records if r["report"] in ("quarterly_q1","quarterly_q3")]
    ratios=[{k:v for k,v in r.items() if k in {"year","report","revenue_growth","gross_margin","operating_margin","net_margin","current_ratio","quick_ratio","debt_ratio","equity_ratio","borrowing_dependency","asset_turnover","roa","roe","roic","dso","dio","dpo","ccc","cfo_to_ni","net_debt","net_debt_ebitda","interest_coverage","ebitda","fcf","eps"}} for r in records]
    write_csv(PROCESSED/"annual.csv", annual); write_csv(PROCESSED/"half_year.csv", half); write_csv(PROCESSED/"quarterly.csv", quarter); write_csv(PROCESSED/"ratios.csv", ratios)
    (PROCESSED/"status.json").write_text(json.dumps({"corp_code":corp_code,"generated_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"statuses":statuses},ensure_ascii=False,indent=2),encoding="utf-8")
    payload={"corp_code":corp_code,"generated_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"annual":annual,"half_year":half,"quarterly":quarter,"ratios":ratios,"peers":[{"name":"롯데웰푸드","ticker":"280360","focus":"제과·빙과·식품"},{"name":"농심","ticker":"004370","focus":"라면·스낵·식품"},{"name":"삼양식품","ticker":"003230","focus":"라면·가공식품"},{"name":"오뚜기","ticker":"007310","focus":"가공식품·소스"},{"name":"해태제과식품","ticker":"101530","focus":"제과·스낵"}]}
    DASH.parent.mkdir(parents=True, exist_ok=True)
    DASH.write_text("window.DASHBOARD_DATA = " + json.dumps(payload,ensure_ascii=False,separators=(",",":")) + ";",encoding="utf-8")
    print(f"Collected {len(records)} report datasets for corp_code={corp_code}")

if __name__ == "__main__": run()
