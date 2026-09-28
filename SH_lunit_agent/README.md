# Lunit DART Financial Intelligence Dashboard

> OpenDART의 정기보고서(사업보고서·반기보고서·분기보고서)를 수집하고, 주요 재무수치와 재무비율을 계산해 GitHub Pages 대시보드로 보여주는 자동화 프로젝트입니다.

[![🔗 대시보드 바로가기](https://img.shields.io/badge/%F0%9F%94%97%20%EB%8C%80%EC%8B%9C%EB%B3%B4%EB%93%9C%20%EB%B0%94%EB%A1%9C가기-1565C0?style=for-the-badge)](https://hsc-class01.github.io/SH_lunit/)

**Dashboard:** https://hsc-class01.github.io/SH_lunit/

## 1. 프로젝트 개요

- 대상: 주식회사 루닛 (Lunit, KOSDAQ 328130)
- 데이터 원천: 금융감독원 OpenDART API
- 보고서: 사업보고서(11011), 반기보고서(11012), 1분기보고서(11013), 3분기보고서(11014)
- 수집 시작 연도: 2010년을 기준으로 탐색하되, OpenDART 재무제표 API가 제공하는 2015년 이후 데이터를 자동 수집합니다.
- 자동 업데이트: 매월 1일 KST 기준 GitHub Actions 실행
- 결과물: 원천 JSON, 정규화 CSV, 재무비율 CSV, 정적 HTML Dashboard

> **2010~2014 주의:** OpenDART의 `fnlttSinglAcntAll` 재무제표 API는 2015년 이후부터 정보를 제공합니다. 따라서 2010~2014는 임의로 보간하지 않고 상태 로그에 `unavailable`로 남깁니다.

## 2. 주요 분석 항목

### 손익
매출액, 매출원가, 매출총이익, 영업이익, 세전이익, 당기순이익, 지배주주순이익, EBITDA(가능한 경우), EPS

### 재무상태
자산총계, 부채총계, 자본총계, 현금및현금성자산, 유동자산, 유동부채, 차입금/금융부채

### 현금흐름
영업활동현금흐름(CFO), 투자활동현금흐름(CFI), 재무활동현금흐름(CFF), CAPEX(공시 계정이 확인되는 경우), FCF

### 재무비율
매출증가율, 매출총이익률, 영업이익률, 순이익률, 유동비율, 부채비율, ROA, ROE, CFO/순이익, 순차입금, 순차입금/EBITDA, 이자보상배율(필요 계정 확인 시), ROIC(가능한 경우)

## 3. Dashboard 구성

1. 상단 KPI cards
2. 매출·영업이익 추이
3. 수익성 및 현금흐름 시각화
4. 재무구조/레버리지 시각화
5. **Annual** table
6. **Half-year** table
7. **Quarterly** table
8. 국내 peer firms table

## 4. 국내 Peer Firms

루닛의 국내 의료AI 사업 영역과 비교 가능성이 높은 상장사를 참고 peer set으로 구성했습니다. 이는 투자 추천이나 우열 평가가 아니라 사업/재무 비교를 위한 분석 대상입니다.

| 기업 | 종목코드 | 비교 포인트 |
|---|---:|---|
| 뷰노 | 338220 | 의료영상·생체신호 기반 AI 의료기기 |
| 제이엘케이 | 322510 | 뇌졸중 중심 의료영상 AI |
| 딥노이드 | 315640 | 의료영상 AI 및 의료 AI 플랫폼 |
| 코어라인소프트 | 384470 | CT 영상 기반 의료 AI |
| 뉴로핏 | 380550 | 뇌 영상 분석 및 치료 보조 AI |

## 5. 설치 / API Key 설정

### OpenDART API Key 발급

1. [OpenDART](https://opendart.fss.or.kr/)에서 인증키를 발급합니다.
2. GitHub 저장소의 **Settings → Secrets and variables → Actions → New repository secret**으로 이동합니다.
3. Name: `DART_API_KEY`
4. Secret: 발급받은 40자리 인증키
5. 저장합니다.

API Key는 코드, README, `data/` 파일에 절대 넣지 않습니다.

## 6. GitHub Pages

저장소 **Settings → Pages → Build and deployment → Source: GitHub Actions**로 설정합니다. 이후 `deploy-pages.yml` workflow가 `dashboard/`를 GitHub Pages에 배포합니다.

Repository의 **About → Website**에는 다음 주소를 넣어 Dashboard 바로가기를 만들 수 있습니다.

`https://hsc-class01.github.io/SH_lunit/`

## 7. 로컬 실행

```bash
pip install -r requirements.txt
set DART_API_KEY=YOUR_KEY   # Windows PowerShell: $env:DART_API_KEY="YOUR_KEY"
python src/pipeline.py
```

## 8. 자동화

`.github/workflows/monthly_update.yml`은 매월 1일 00:05 UTC(한국시간 09:05)에 실행됩니다. 수집 후 분석 CSV와 Dashboard를 갱신하고 커밋합니다.

필요하면 Actions 화면에서 `workflow_dispatch`로 수동 실행할 수 있습니다.

## 9. 데이터 구조

```text
data/raw/YYYY/11011.json
                  11012.json
                  11013.json
                  11014.json
data/processed/annual.csv
data/processed/half_year.csv
data/processed/quarterly.csv
data/processed/ratios.csv
```

## 10. 데이터 출처

- OpenDART: https://opendart.fss.or.kr/
- Lunit: https://www.lunit.io/ko/

OpenDART API의 보고서 코드는 사업보고서 `11011`, 반기보고서 `11012`, 1분기 `11013`, 3분기 `11014`입니다.
