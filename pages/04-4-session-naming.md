## 04-4. 세션 이름 설정

원격에서 여러 Claude Code 세션에 접속할 때 세션 이름이 중요합니다. 이름을 잘 설정하면 `claude.ai/code` 세션 목록에서 원하는 세션을 빠르게 찾을 수 있습니다.

> 💡 **비유:** 세션 이름은 사무실 자리 명패와 같습니다. 명패가 없으면 어느 자리가 누구 것인지 알 수 없고, 명패가 있어도 "자리 3-B"보다 "민준 PM 자리"가 훨씬 찾기 쉽습니다.

<hr>

## 세션 이름 결정 우선순위

Claude Code는 세션 이름을 다음 순서로 결정합니다.

| 순위 | 소스 | 예시 |
|------|------|------|
| 1 | 실행 시 명시한 이름 | `claude --remote-control "백엔드 API 작업"` |
| 2 | 대화 기록의 마지막 의미 있는 메시지 | (자동) |
| 3 | `{hostname}-{랜덤형용사}-{랜덤명사}` | `mypc-graceful-unicorn` |

이름은 위에서부터 차례로 "있으면 그걸 쓰고, 없으면 다음으로 내려가는" 방식으로 정해집니다. 직접 지어 준 이름(1순위)이 있으면 그대로 쓰고, 없으면 대화 내용에서 의미 있는 문구를 골라(2순위) 붙입니다. 그것마저 없으면 마지막으로 `호스트명-형용사-명사` 꼴의 임의 이름(3순위, 예: `mypc-graceful-unicorn`)이 자동으로 매겨집니다. 즉 가장 명확한 이름이 항상 우선이고, 아무것도 정해 주지 않아도 빈 이름이 되는 일은 없습니다.

### 우선순위별 실제 동작 예시

```bash
# 순위 1: 명시적 이름 (가장 우선)
claude --remote-control "결제 API 리팩토링"
# → 세션 이름: "결제 API 리팩토링"

# 순위 3: 아무것도 지정 안 했을 때 (자동 생성)
claude --remote-control
# → 세션 이름: "mypc-graceful-unicorn" (랜덤)
```

> 💡 자동 생성 이름(4순위)은 접속할 때마다 바뀌지 않습니다. 세션 시작 시 한 번 정해지면 세션이 살아 있는 동안 그 이름을 유지합니다. 단, 세션을 종료하고 다시 시작하면 새 랜덤 이름이 붙습니다.

<hr>

## 이름 직접 지정

### CLI 플래그로 지정

```bash
# --remote-control 다음에 이름 입력
claude --remote-control "백엔드 API 리팩토링"
claude --remote-control "프론트엔드 로그인 화면"
```

### 실행 중 세션에서 지정

```
> /remote-control 내 프로젝트 작업
```

`/remote-control` 명령어 뒤에 이름을 입력합니다.

<hr>

## 세션 이름 접두사 설정

`--remote-control-session-name-prefix`는 자동 생성 이름의 앞부분을 고정합니다. 여러 세션이 같은 프로젝트임을 알아보기 쉽게 만들 때 유용합니다.

```bash
# 플래그로 접두사 지정
claude --remote-control-session-name-prefix dev-machine
# 결과: dev-machine-graceful-unicorn
# 결과: dev-machine-swift-eagle
# 결과: dev-machine-calm-river
```

자동 생성 이름은 **`{접두사}-{형용사}-{명사}`** 세 토막으로 이뤄집니다. 접두사는 위 플래그로 고정한 부분(`dev-machine`)이고, 뒤의 형용사·명사는 실행할 때마다 무작위로 골라 붙어 세션끼리 겹치지 않게 합니다. 그래서 같은 프로젝트의 여러 세션이 `dev-machine-`이라는 공통 머리말로 묶이면서도 뒤쪽 두 단어로 서로 구별됩니다 — 사람이 일일이 짓지 않아도 알아보기 쉬운 고유 이름이 자동으로 생기는 셈입니다.

### 언제 접두사를 쓸까?

| 상황 | 접두사 예시 | 결과 이름 예시 |
|------|------------|---------------|
| 여러 프로젝트를 동시 운영 | `myapp` | `myapp-swift-eagle` |
| 팀 공유 서버 구분 | `team` | `team-calm-river` |
| 머신별 구분 | `macbook` / `workstation` | `macbook-gentle-forest` |

### 환경변수로 설정

매번 플래그를 입력하는 번거로움을 없애려면 환경변수를 사용합니다.

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
export CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX=myproject

# 적용
source ~/.bashrc

# 이후 접두사 없이 실행해도 자동 적용
claude --remote-control
# 결과: myproject-gentle-forest
```

<hr>

> 💡 **환경변수란?** 터미널이 기억하는 "공용 설정값"입니다. `~/.bashrc`(또는 `~/.zshrc`)에 한 줄 적어 두면, 터미널을 새로 열 때마다 자동 적용되어 매번 같은 옵션을 타이핑하지 않아도 됩니다.

### 따라하기: 환경변수 접두사 영구 설정

```bash
# 1단계: bashrc 파일 열기
nano ~/.bashrc

# 2단계: 맨 아래에 추가
export CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX=myproject

# 3단계: 저장 후 적용
source ~/.bashrc

# 4단계: 확인
echo $CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX
# 출력: myproject

# 5단계: 새 세션 시작해서 이름 확인
claude --remote-control
# Remote Control active
# Session: myproject-gentle-forest   ← 접두사가 붙음
```

<hr>

## 멀티에이전트 팀에서 세션 이름 관리

팀 환경에서는 각 파인(에이전트)의 세션 이름을 역할로 지정하면 원격에서 누구에게 접속하는지 즉시 알 수 있습니다.

```bash
# 팀 셋업 스크립트에서 각 파인 시작 시
# 파인 0: 팀장
tmux send-keys -t team:0.0 \
    "claude --remote-control '팀장-쭌' --dangerously-skip-permissions" Enter

# 파인 1: 아키텍트
tmux send-keys -t team:0.1 \
    "claude --remote-control '아키텍트-민준' --dangerously-skip-permissions" Enter

# 파인 2: 리서쳐
tmux send-keys -t team:0.2 \
    "claude --remote-control '리서쳐-지훈' --dangerously-skip-permissions" Enter
```

이렇게 하면 `claude.ai/code`에서 세션 목록을 열었을 때 다음과 같이 표시됩니다.

```
● 팀장-쭌           (컴퓨터 아이콘 + 초록 점 = 활성)
● 아키텍트-민준
● 리서쳐-지훈
● 디자이너-수아
● 개발자-서연
● 리뷰어-태양
```

> 💡 초록 점(●)이 표시된 세션이 현재 활성 상태입니다. 회색 점이면 세션이 종료된 상태이므로 재시작이 필요합니다.

<hr>

## 환경변수 기반 접두사와 역할 이름 결합

```bash
# .env 또는 셋업 스크립트에서
export CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX="team"

# 각 파인에서 역할 이름으로 시작
claude --remote-control "pane0-팀장"     # → team-pane0-팀장 (접두사 + 이름)
```

<hr>

## 세션 이름 모범 사례

### 프로젝트 + 역할 조합

```
myapp-backend-dev
myapp-frontend-design
myapp-architect
```

### 날짜 포함 (일시적 작업)

```bash
claude --remote-control "$(date +%Y%m%d)-데이터마이그레이션"
# 결과: 20260426-데이터마이그레이션
```

날짜를 앞에 붙이면 세션 목록에서 날짜 순서대로 정렬되어 찾기 쉽습니다.

### 짧고 명확하게

세션 목록에서 잘리지 않도록 이름은 20자 이내로 유지합니다.

```
❌ 길고 모호: "2026년 4월 26일 백엔드 API 인증 토큰 리팩토링 작업"
✅ 짧고 명확: "0426-auth-리팩토링"
```

### 상황별 이름 패턴 예시

| 상황 | 이름 패턴 | 예시 |
|------|----------|------|
| 기능 개발 | `{날짜}-{기능명}` | `0426-login-feature` |
| 버그 수정 | `{날짜}-fix-{설명}` | `0426-fix-null-pointer` |
| 리뷰 세션 | `review-{브랜치명}` | `review-feat-auth` |
| 팀 공유 | `{팀명}-{역할}` | `team-backend` |

<hr>

## 세션 이름 확인

현재 세션 이름은 `/status` 명령으로 확인합니다.

```
> /status

Session: 팀장-쭌
Remote Control: Active
Model: claude-sonnet-4-6
```

### 다른 기기에서 세션 찾기

`claude.ai/code` 접속 후 세션 목록에서 이름 또는 키워드로 검색합니다.

```
검색창: "팀장"  →  "팀장-쭌" 세션 표시
검색창: "0426"  →  날짜로 찾기
```

컴퓨터 아이콘 + 초록 점 조합이 현재 원격 접속 가능한 활성 세션입니다.

<hr>

## 자주 발생하는 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| 세션 목록에 세션이 보이지 않음 | Remote Control이 활성화되지 않음 | `--remote-control` 플래그 또는 `/remote-control` 실행 |
| 이름이 너무 길어 잘림 | 이름이 20자 초과 | 20자 이내로 줄이기 |
| 같은 이름 세션이 여러 개 보임 | 접두사 없이 동일 이름 사용 | 접두사 또는 날짜 포함 |
| 환경변수 접두사가 적용 안 됨 | `source ~/.bashrc` 미실행 | 새 터미널 열거나 `source ~/.bashrc` 실행 |

<hr>

## 요약

세션 이름 설정 방법 요약:

```bash
# 일회성 이름 지정
claude --remote-control "세션 이름"

# 접두사 설정 (플래그)
claude --remote-control-session-name-prefix 접두사

# 접두사 설정 (환경변수, 영구)
export CLAUDE_REMOTE_CONTROL_SESSION_NAME_PREFIX=접두사

# 현재 세션 이름 확인
/status
```

다음 챕터에서는 프로그램 방식으로 Claude를 제어할 수 있는 **Stream JSON 모드**를 설명합니다.
