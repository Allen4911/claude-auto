## 5-1. Claude 모바일 앱 설치 및 계정 연결

## 이 장에서 배울 내용

스마트폰으로 PC의 Claude Code 세션을 제어하려면 먼저 Claude 공식 모바일 앱을 설치하고, 데스크톱과 동일한 계정으로 로그인해야 합니다. 이 장에서는 앱 설치부터 계정 연결까지 단계별로 안내합니다.

<hr>

## 준비 사항

Remote Control 기능을 사용하려면 다음 조건을 충족해야 합니다.

| 항목 | 요구 사항 |
|------|-----------|
| Claude 구독 | Pro, Max, Team, Enterprise 중 하나 |
| 계정 | claude.ai 계정 (API 키 계정 불가) |
| 앱 버전 | 최신 버전의 Claude 모바일 앱 |
| 네트워크 | 인터넷 연결 (Wi-Fi 또는 모바일 데이터) |

> **중요:** Remote Control은 API 키 방식 로그인을 지원하지 않습니다. 반드시 claude.ai 계정으로 로그인해야 합니다.

<hr>

## iOS 설치 (iPhone / iPad)

**Step 1 — App Store 열기**

iPhone 또는 iPad에서 App Store를 실행합니다.

![App Store 아이콘 탭하는 화면](../assets/05-1-appstore-icon.png)

**Step 2 — "Claude" 검색**

하단 검색 탭을 누르고 검색창에 **Claude**를 입력합니다. Anthropic이 개발한 공식 앱인지 확인하세요. 개발사가 **Anthropic**으로 표시된 앱을 선택합니다.

![App Store 검색 결과 - Claude by Anthropic](../assets/05-1-appstore-search.png)

**Step 3 — 다운로드 및 설치**

**받기** 버튼을 탭합니다. Face ID 또는 Touch ID로 인증하면 다운로드가 시작됩니다.

![다운로드 진행 화면](../assets/05-1-download.png)

<hr>

## Android 설치

**Step 1 — Google Play Store 열기**

홈 화면 또는 앱 서랍에서 Play Store를 실행합니다.

![Play Store 아이콘](../assets/05-1-playstore-icon.png)

**Step 2 — "Claude" 검색 및 설치**

검색창에 **Claude**를 입력하고, Anthropic의 공식 앱을 찾아 **설치** 버튼을 탭합니다.

![Play Store 검색 결과 - Claude by Anthropic](../assets/05-1-playstore-search.png)

> **삼성/갤럭시 사용자:** Galaxy Store에도 Claude 앱이 있지만, 최신 Remote Control 기능을 보장하려면 Google Play Store 버전을 권장합니다.

<hr>

## 계정 로그인

앱 설치 후 계정을 연결합니다.

**Step 1 — 앱 실행 및 로그인 화면 진입**

Claude 앱을 처음 실행하면 환영 화면이 나타납니다. **Continue** 또는 **로그인** 버튼을 탭합니다.

![Claude 앱 시작 화면](../assets/05-1-splash.png)

**Step 2 — 로그인 방식 선택**

Google, Apple 계정 또는 이메일로 로그인할 수 있습니다. **반드시 데스크톱 Claude Code와 동일한 계정**을 선택해야 세션이 연결됩니다.

![로그인 방식 선택 화면 - Google / Apple / 이메일](../assets/05-1-login.png)

**Step 3 — 인증 완료**

선택한 방식으로 인증을 완료하면 Claude 채팅 화면이 나타납니다. 상단 또는 하단 메뉴에 **Code** 탭이 보이면 Remote Control 기능에 접근할 준비가 된 것입니다.

![Claude 앱 메인 화면 - 하단 Code 탭 표시](../assets/05-1-main-code-tab.png)

<hr>

## 계정 연결 확인

로그인 후 데스크톱과 같은 계정인지 확인합니다.

1. 앱 우측 상단 프로필 아이콘을 탭합니다.
2. **Settings → Account** 메뉴에서 이메일 주소를 확인합니다.
3. 데스크톱 터미널에서 `claude /status`를 입력해 동일한 계정인지 비교합니다.

![앱 설정 > Account 이메일 확인 화면](../assets/05-1-settings-account.png)

<hr>

## 문제 해결

**앱에 Code 탭이 보이지 않는 경우**
- Pro 이상 구독 여부를 확인합니다. Free 플랜은 Remote Control을 지원하지 않습니다.
- 앱을 최신 버전으로 업데이트합니다.

**로그인 오류가 발생하는 경우**
- claude.ai 웹사이트에서 먼저 로그인이 되는지 확인합니다.
- 앱을 완전히 종료 후 재시작합니다.

**"Full-scope login required" 메시지**
- API 키로 로그인을 시도한 경우 이 오류가 발생합니다. Google 또는 이메일 방식으로 다시 로그인하세요.

<hr>

## 다음 장 미리보기

앱 설치와 로그인이 완료되었습니다. 다음 장에서는 QR 코드를 스캔해 PC의 Claude Code 세션에 즉시 연결하는 방법을 알아봅니다.
