# Orion DART Financial Intelligence Dashboard

[![🔗 대시보드 바로가기](https://img.shields.io/badge/%F0%9F%94%97%20%EB%8C%80%EC%8B%9C%EB%B3%B4%EB%93%9C%20%EB%B0%94%EB%A1%9C%EA%B0%80%EA%B8%B0-1565C0?style=for-the-badge)](https://hsc-class01.github.io/SH_orion/)

**Dashboard:** https://hsc-class01.github.io/SH_orion/

OpenDART에서 오리온(주식코드 271560)의 사업보고서·반기보고서·분기보고서를 수집하고 주요 재무수치 및 재무비율을 산출하는 프로젝트입니다.

## 수집 범위와 유의사항
- 탐색 시작 연도: 2010년
- OpenDART 재무제표 API `fnlttSinglAcntAll`의 재무수치는 2015년부터 제공됩니다. 2010~2014년은 이 API로 채울 수 없으므로 수치를 임의로 생성하지 않고 상태 정보로 표시합니다.
- 오리온은 2017년 오리온홀딩스와 인적분할된 회사이므로 2017년 이전 수치를 현 법인의 동일한 연속 시계열로 해석하기 전에 DART 원문과 분할 관련 공시를 확인해야 합니다.
- 사업보고서(11011), 반기보고서(11012), 1분기보고서(11013), 3분기보고서(11014)를 처리합니다.
- 매월 1일 한국시간 오전 9시 5분에 자동 실행되도록 설정합니다. GitHub Actions 스케줄은 UTC 기준 `5 0 1 * *`입니다.

## 분석 지표
첨부된 「재무제표 및 재무비율 실무 가이드」의 흐름인 **매출 성장 → 이익률 → 현금흐름 → 차입 부담 → 투자수익률 → 시장평가**를 기준으로 구성했습니다.

- **손익:** 매출액, 매출원가, 매출총이익, 영업이익, 세전이익, 당기순이익, 지배주주순이익, EPS, EBITDA
- **재무상태:** 자산총계, 유동자산, 당좌자산, 매출채권, 재고자산, 현금및현금성자산, 부채총계, 유동부채, 자본총계, 차입금
- **현금흐름:** 영업·투자·재무활동현금흐름, CAPEX, FCF
- **수익성:** 매출총이익률, 영업이익률, 순이익률, EBITDA 마진, ROA, ROE, ROIC
- **유동성·레버리지:** 유동비율, 당좌비율, 부채비율, 자기자본비율, 차입금 의존도, 순차입금, 순차입금/EBITDA, 이자보상배율
- **활동성·성장:** 매출채권회전일수(DSO), 재고자산회전일수(DIO), 매입채무회전일수(DPO), 현금전환주기(CCC), 매출증가율

분기·반기 손익 수치의 기간 정의는 DART API 응답 필드에 따라 달라질 수 있으므로 원천 JSON을 함께 보관합니다. 비율은 분모가 0이거나 자료가 없는 경우 계산하지 않습니다. ROA·ROE 등 평균 잔액이 필요한 지표는 가능한 경우 기초·기말 평균을 사용합니다.

## 설치 및 GitHub 설정
1. ZIP을 내려받아 저장소 루트에 압축을 풉니다. 기존 파일과 겹치면 README, `src`, `dashboard`, `requirements.txt`, `SETUP_GITHUB_ACTIONS.md`를 확인해 병합하세요.
2. ZIP에서는 숨김 경로 문제를 피하기 위해 워크플로 파일을 `github_workflows/`에 넣었습니다. GitHub에 업로드한 뒤 폴더명을 **`.github/workflows/`** 로 옮기고 두 YAML 파일을 그 안에 둡니다. GitHub Actions가 인식하려면 실제 경로가 반드시 `.github/workflows/`여야 합니다.
3. 저장소의 **Settings → Secrets and variables → Actions → New repository secret**에서 이름을 `DART_API_KEY`, 값에 OpenDART 인증키를 입력합니다. 코드나 README에 API 키를 직접 입력하거나 커밋하지 마세요.
4. **Settings → Pages → Build and deployment → Source: GitHub Actions**로 설정합니다. `Deploy Dashboard to GitHub Pages` 워크플로를 실행합니다.
5. 저장소 첫 화면의 **About → 톱니바퀴(Edit repository details) → Website**에 `https://hsc-class01.github.io/SH_orion/`을 입력하고 저장합니다.
6. README 상단 배지는 Shields.io로 생성했습니다. 첨부한 별도 배지 이미지 파일은 이번 대화의 파일 목록에서 확인되지 않아, 클릭 가능한 대체 배지를 사용했습니다.

## 워크플로 검증
- `github_workflows/monthly_update.yml`: 매월 1일 자동 수집·분석 후 CSV와 대시보드 데이터를 커밋합니다.
- `github_workflows/deploy-pages.yml`: `dashboard/`를 GitHub Pages로 배포합니다.
- YAML 문법, Python 컴파일, JavaScript 구문을 로컬에서 확인한 후 ZIP에 포함하세요. GitHub Actions 실행 성공 여부는 저장소에 파일을 올리고 실제 실행한 뒤 확인할 수 있습니다.

## 국내 Peer Firms (참고 비교군)
| 기업 | 종목코드 | 비교 관점 |
|---|---:|---|
| 롯데웰푸드 | 280360 | 제과·빙과·식품 |
| 농심 | 004370 | 라면·스낵·식품 |
| 삼양식품 | 003230 | 라면·가공식품 |
| 오뚜기 | 007310 | 가공식품·소스 |
| 해태제과식품 | 101530 | 제과·스낵 |

이 비교군은 사업·제품군을 고려한 참고 목록이며, 사업구조와 회계정책 차이를 고려해 재무비율을 비교해야 합니다.

## 공식 출처
- OpenDART: https://opendart.fss.or.kr/
- OpenDART 단일회사 전체 재무제표 API: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020
- DART 전자공시: https://dart.fss.or.kr/
