# GitHub Actions 및 API 설정

1. GitHub 저장소 `HSC-Class01/SH_orion` → Settings → Secrets and variables → Actions → New repository secret.
2. Name: `DART_API_KEY`; Secret: OpenDART에서 발급한 인증키. 키를 코드 파일에 직접 넣지 마세요.
3. 워크플로는 이미 저장소의 `.github/workflows/deploy-pages.yml` 및 `.github/workflows/monthly_update.yml`에 등록되어 있습니다. Actions 탭에 두 항목이 표시되는지 확인하세요.
4. Settings → Pages → Source에서 GitHub Actions 선택.
5. Actions 탭에서 `Monthly DART update`를 `Run workflow`로 수동 실행하고 로그를 확인합니다. 데이터 수집과 Pages 배포가 같은 실행 안에서 진행되며, 이후 매월 1일 KST 09:05에 자동 실행됩니다.
6. 별도 재배포가 필요하면 `Deploy Dashboard to GitHub Pages`를 실행하고 배포 URL을 확인합니다.

## 실행 순서
수집 작업은 OpenDART corpCode.xml에서 오리온(종목코드 271560)을 찾고, 각 연도·보고서 유형의 전체 재무제표를 가져옵니다. 연결재무제표(CFS)를 우선하며 없으면 별도재무제표(OFS)를 시도합니다. 원천 JSON과 정규화 CSV, 비율 CSV, 대시보드 데이터가 갱신됩니다.

## 참고
OpenDART 재무제표 API는 2015년부터 제공됩니다. 2010~2014년을 현재 API만으로 채울 수 없으며, 오리온의 2017년 인적분할 전후 수치도 같은 법인 기준인지 확인이 필요합니다.
