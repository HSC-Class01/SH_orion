# GitHub Actions 설치 안내

ZIP에는 업로드가 어려운 숨김 경로를 만들지 않기 위해 workflow 파일을 `github_workflows/`에 넣었습니다.

GitHub 저장소에서는 아래처럼 **정확히** `.github/workflows/`로 이동/복사해야 Actions가 인식합니다.

```text
github_workflows/monthly_update.yml
→ .github/workflows/monthly_update.yml

github_workflows/deploy-pages.yml
→ .github/workflows/deploy-pages.yml
```

## Windows PowerShell

```powershell
New-Item -ItemType Directory -Force .github\workflows
Copy-Item github_workflows\*.yml .github\workflows\
```

## API Key

GitHub:
`Settings → Secrets and variables → Actions → New repository secret`

- Name: `DART_API_KEY`
- Secret: OpenDART에서 발급한 40자리 인증키

키를 소스 코드에 직접 넣지 마세요.

## Pages

`Settings → Pages → Build and deployment → Source: GitHub Actions`

설정 후 `Deploy Dashboard to GitHub Pages` workflow를 한 번 `Run workflow`로 실행하면 됩니다.

## About 링크

`https://hsc-class01.github.io/SH_lunit/`

를 Repository → About → Website에 입력하세요.
