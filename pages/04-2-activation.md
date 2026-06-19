## 04-2. Remote Control 활성화 방법 3가지

Remote Control은 상황에 따라 세 가지 방법으로 활성화할 수 있습니다. 항상 켜두고 싶다면 전역 설정을, 특정 세션에만 적용하려면 CLI 플래그나 세션 내 명령을 사용합니다.

> 💡 **비유:** 설정 파일(방법 1)은 현관 자동잠금 장치처럼 늘 작동합니다. 나머지 둘은 그때그때 손으로 잠그는 쪽인데, CLI 플래그는 들어가기 전에, 슬래시 명령은 이미 들어온 뒤에 잠근다는 차이가 있습니다.

<hr>

## 방법 1: settings.json 전역 설정

모든 Claude Code 세션에서 Remote Control을 자동 활성화합니다. 한 번만 설정하면 됩니다.

### 설정 파일 위치

```
~/.claude/settings.json
```

### 설정 추가

```bash
# settings.json이 없으면 생성, 있으면 편집
cat ~/.claude/settings.json 2>/dev/null || echo "{}"
```

`~/.claude/settings.json` 파일에 다음 내용을 추가합니다.

```json
{
  "remoteControlAtStartup": true
}
```

이 설정이 `true`이면 `claude` 명령을 실행할 때마다 자동으로 Remote Control이 활성화됩니다.

> 💡 **settings.json이란?** Claude Code의 동작을 저장해 두는 설정 파일입니다. 여기에 한 번 적어 두면 매번 옵션을 입력하지 않아도 항상 같은 설정으로 실행됩니다. 반대로, 그때그때만 켜고 싶으면 아래 방법 2(CLI 플래그)를 쓰면 됩니다.

전체 `settings.json`을 세 가지 논리 블록으로 나누어 살펴보겠습니다.

세 블록은 각각 이런 역할을 합니다.

- **hooks(훅)** — 특정 시점(예: 도구 실행 전후)에 자동으로 끼어들 명령을 등록합니다. 명령 실행 전 검증 스크립트를 돌리는 식으로, "언제 무엇을 자동으로 할지"를 정합니다.
- **enabledPlugins(활성 플러그인)** — 어떤 플러그인을 켤지 이름으로 나열합니다. 여기 적힌 것만 로드되므로, "무엇을 켤지"의 목록입니다.
- **extraKnownMarketplaces · 시작 옵션** — 플러그인을 받아올 추가 마켓플레이스 주소와, 앞서 본 `remoteControlAtStartup` 같은 시작 시 동작을 함께 둡니다. "어디서 받아올지 · 켤 때 어떻게 시작할지"에 해당합니다.

결국 `settings.json` 하나에 세 블록이 모여 있는 셈입니다. hooks는 끼어들 시점을, plugins는 켤 대상을, marketplaces는 받아올 곳을 정합니다. 세 블록은 서로 독립적이라 필요한 것만 적고 나머지는 비워 둬도 됩니다.

### 따라하기: settings.json 설정 단계

```bash
# 1단계: 홈 디렉토리의 .claude 폴더 확인
ls ~/.claude/

# 2단계: 기존 settings.json 내용 확인
cat ~/.claude/settings.json

# 3단계: 설정 추가 (파일이 없으면 새로 생성)
# 파일이 없는 경우
echo '{"remoteControlAtStartup": true}' > ~/.claude/settings.json

# 기존 설정이 있는 경우, 편집기로 열어서 항목 추가
nano ~/.claude/settings.json

# 4단계: 적용 확인 (새 claude 세션 시작 후 메시지 확인)
claude
# → "Remote Control active" 메시지가 뜨면 성공
```

### /config 메뉴로 설정

직접 파일을 편집하는 대신 Claude Code 내부에서 설정할 수도 있습니다.

```
> /config
```

`/config` 메뉴에서 **Enable Remote Control for all sessions** 항목을 `true`로 변경합니다.

> 💡 `/config`는 터미널에서 JSON을 직접 편집할 필요 없이 메뉴 형식으로 설정을 바꿀 수 있습니다. settings.json 문법 오류 걱정 없이 안전하게 설정할 때 유용합니다.

<hr>

## 방법 2: CLI 플래그 (일회성)

특정 세션에만 Remote Control을 활성화하려면 실행 시 플래그를 사용합니다.

방법 2는 이번 한 번만 켜는 방식입니다. 방법 1과 달리 설정 파일은 건드리지 않고, 실행할 때 플래그 하나만 덧붙이면 그 세션에서만 Remote Control이 동작합니다. 아래 형식처럼 `claude` 뒤에 옵션을 붙이면 됩니다.

### 인터랙티브 세션 + 원격 접근

```bash
# 기본 형식
claude --remote-control

# 세션 이름 지정
claude --remote-control "백엔드 API 리팩토링"
claude --remote-control "프론트엔드 작업"
```

세션 이름을 지정하면 `claude.ai/code` 세션 목록에서 쉽게 찾을 수 있습니다. 이름은 `--remote-control` 옵션 바로 뒤에 공백으로 구분해 적고, 생략하면 랜덤 이름이 자동으로 배정됩니다.

### 세션 이름을 지정해야 하는 이유

Remote Control을 켜면 세션에 자동으로 이름이 붙습니다. 이름을 지정하지 않으면 `hostname-swift-eagle` 처럼 랜덤 단어가 붙어 나중에 찾기 어렵습니다. 이름을 지정하면:

- `claude.ai/code` 세션 목록에서 이름으로 검색 가능
- 팀원이 어떤 세션인지 한눈에 파악
- 여러 세션을 동시에 열었을 때 구분이 쉬움

```bash
# 프로젝트와 날짜를 이름에 포함하면 관리가 쉬움
claude --remote-control "myapp-240426-리팩토링"
```

### 서버 모드 실행

```bash
# 기본 서버 모드 (다중 원격 세션 관리)
claude remote-control

# 세션 이름 접두사 지정
claude remote-control --remote-control-session-name-prefix myproject
```

서버 모드는 4-3 챕터에서 자세히 다룹니다.

<hr>

## 방법 3: 실행 중인 세션에서 활성화

이미 실행 중인 Claude Code 세션에서 Remote Control을 켤 수 있습니다.

### 기본 활성화

```
> /remote-control
```

### 세션 이름 지정

```
> /remote-control 내 프로젝트 작업
```

명령을 입력하면 Claude가 Remote Control URL과 QR 코드를 제공합니다.

### 언제 방법 3을 쓸까?

가장 흔한 상황은 "세션을 시작했는데 갑자기 자리를 비워야 할 때"입니다. 방법 1·2처럼 미리 켜두지 않아도, 실행 중에 언제든 `/remote-control`을 입력하면 즉시 활성화됩니다.

```
(작업 중 갑자기 외출이 필요한 상황)

> /remote-control 오늘 작업
Remote Control active
Session: 오늘 작업-graceful-unicorn
URL: https://claude.ai/code?session=abc123...

Press SPACE to show QR code
```

이 URL 또는 QR을 폰으로 스캔하면, 이동 중에도 같은 세션에서 이어서 지시를 내릴 수 있습니다.

### VS Code 확장에서도 동일

VS Code의 Claude 확장 내에서도 동일한 명령이 동작합니다.

```
/remote-control
/rc
```

<hr>

## 활성화 확인

Remote Control이 활성화되면 터미널에 다음과 같은 메시지가 표시됩니다.

```
Remote Control active
Session: my-project-graceful-unicorn
URL: https://claude.ai/code?session=abc123...

Press SPACE to show QR code
```

각 항목의 의미:

| 항목 | 의미 |
|------|------|
| `Session:` | 이 세션의 이름 (세션 목록에서 보이는 이름) |
| `URL:` | 다른 기기에서 바로 접속할 수 있는 직접 링크 |
| `Press SPACE` | 스페이스바를 누르면 QR 코드가 표시됨 |

> 💡 URL의 `session=` 뒤 값이 세션 ID입니다. 이 URL을 복사해 폰 브라우저에서 열거나 북마크하면 다시 접속할 때 편합니다.

<hr>

## 접속 방법

활성화 후 다른 기기에서 세 가지 방법으로 접속합니다.

```bash
# 방법 1: URL 직접 접속
https://claude.ai/code?session=<session-id>

# 방법 2: QR 코드 (서버 모드에서 스페이스바)
# → Claude 모바일 앱으로 스캔

# 방법 3: claude.ai/code 세션 목록
# → 세션 이름 검색 → 컴퓨터 아이콘 + 초록 점 선택
```

### 접속 방법별 추천 상황

| 접속 방법 | 추천 상황 |
|-----------|-----------|
| URL 직접 | 이미 URL을 알고 있을 때, 북마크 활용 |
| QR 코드 | 처음 접속할 때 가장 빠름 (타이핑 없음) |
| 세션 목록 | 세션 이름을 알고 있을 때, 또는 URL을 잃어버렸을 때 |

<hr>

## 멀티에이전트 팀에서 활용

팀 셋업 스크립트에서 팀장(쭌) 파인만 Remote Control을 활성화하면 모바일에서 팀장에게 지시할 수 있습니다.

```bash
# 팀장 파인(0)에 Remote Control 포함하여 Claude 실행
tmux send-keys -t team:0.0 \
    "claude --remote-control '팀장 쭌' --dangerously-skip-permissions" Enter
```

팀 전체에 Remote Control을 켜고 싶다면, 각 파인의 실행 명령에 `--remote-control`을 추가하고 이름으로 구분합니다.

```bash
# 각 팀원 파인을 이름으로 구분
tmux send-keys -t team:0.0 "claude --remote-control '쭌-팀장'" Enter
tmux send-keys -t team:0.1 "claude --remote-control '민준-PM'" Enter
tmux send-keys -t team:0.2 "claude --remote-control '지훈-리서쳐'" Enter
```

이렇게 하면 `claude.ai/code` 세션 목록에 `쭌-팀장`, `민준-PM`, `지훈-리서쳐`가 각각 표시됩니다.

<hr>

## 세 가지 방법 비교

| 방법 | 적용 범위 | 사용 시점 |
|------|-----------|-----------|
| `settings.json` | 모든 세션 | 항상 켜두고 싶을 때 |
| CLI 플래그 (`--remote-control`) | 특정 세션 1개 | 그때그때 켜고 싶을 때 |
| `/remote-control` | 현재 실행 중 세션 | 실행 후 필요해졌을 때 |

![활성화 방법 선택 가이드](../assets/04-2-activation-method-decision.png)

### 선택 가이드

```
항상 원격 접속이 필요하다
  → settings.json (방법 1)

특정 작업에만 원격 접속이 필요하다
  → CLI 플래그 --remote-control (방법 2)

세션을 이미 시작했는데 원격 접속이 필요해졌다
  → /remote-control 슬래시 명령 (방법 3)
```

<hr>

## 자주 발생하는 문제 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| "Remote Control active" 메시지가 안 뜸 | OAuth 인증이 되어 있지 않음 | `claude auth login` 실행 |
| URL로 접속해도 연결이 안 됨 | 구독 플랜이 없음 | Pro 이상 구독 필요 |
| 모바일 앱에서 세션이 보이지 않음 | 같은 계정으로 로그인하지 않음 | 모바일 앱에서 동일 계정 로그인 |
| 스페이스바를 눌러도 QR이 안 뜸 | 인터랙티브 모드가 아님 | 서버 모드(`claude remote-control`) 사용 |

<hr>

## 요약

일상적인 개발 환경이라면 `settings.json`에 `"remoteControlAtStartup": true` 한 줄을 넣어 두는 방법 1로 충분합니다. 한 번 적어 두면 매번 켤 필요가 없으니까요. 이어지는 챕터에서는 원격 세션 여러 개를 한 머신에서 관리하는 서버 모드로 넘어갑니다.
