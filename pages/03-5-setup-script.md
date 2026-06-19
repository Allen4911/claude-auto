## 03-5. 팀 셋업 스크립트 작성

지금까지 배운 레이아웃 구성, Claude 자동 실행, 역할 정의를 하나의 스크립트로 통합합니다. Docker 이미지를 빌드하고 컨테이너를 기동하면 스크립트가 컨테이너 내부에서 TMUX 팀 환경을 자동으로 꾸립니다.

> **원클릭 셋업이란?** 앞 절들에서 하나씩 익힌 명령(Dockerfile 빌드·컨테이너 기동·세션 생성·파인 분할·Claude 실행)을 두 파일에 모아, 명령 한 줄로 6인 팀 환경을 통째로 재현합니다. 컴퓨터를 껐다 켜거나 새 장비로 옮겨도 이 스크립트만 실행하면 같은 환경이 됩니다.

<hr>

## Docker 기반 팀 환경 구조

기존 TMUX 팀 구성은 호스트에 직접 설치했지만, Docker 기반에서는 구성을 두 계층으로 나눕니다.

```
[호스트]
  docker build -t claude-team .      ← 이미지 빌드 (최초 1회)
  docker-team.sh                     ← 호스트 랩퍼 스크립트
        │
        └─ docker exec → 컨테이너 내부
              │
              setup-team.sh          ← TMUX + Claude 자동 실행
              │
              ├─ Pane 0: 쭌 (claude-opus-4-8)
              ├─ Pane 1: 민준 (claude-opus-4-8)
              ├─ Pane 2: 지훈 (claude-sonnet-4-6)
              ├─ Pane 3: 수아 (claude-sonnet-4-6)
              ├─ Pane 4: 서연 (claude-sonnet-4-6)
              └─ Pane 5: 태양 (claude-sonnet-4-6)
```

<hr>

## Dockerfile — 팀 이미지 정의

프로젝트 루트에 아래 `Dockerfile`을 만듭니다. 이 파일이 팀 환경의 청사진입니다.

```dockerfile
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl ca-certificates git tmux \
  && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
  && apt-get install -y nodejs \
  && npm install -g @anthropic-ai/claude-code openclaw \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

CMD ["bash"]
```

각 줄이 하는 일을 확인합니다.

| 줄 | 설명 |
|----|------|
| `FROM ubuntu:22.04` | 베이스 이미지 — 검증 환경과 동일한 Ubuntu 22.04.5 LTS |
| `ENV DEBIAN_FRONTEND=noninteractive` | apt 설치 중 대화형 프롬프트 차단 (자동화 필수) |
| `apt-get install curl ca-certificates git tmux` | 기본 도구 설치 |
| `nodesource setup_22.x` | Node.js 22 저장소 등록 (기본 apt는 구버전) |
| `npm install -g @anthropic-ai/claude-code openclaw` | Claude Code(2.1.181)·OpenClaw(2026.6.8) 전역 설치 |
| `apt-get clean && rm -rf /var/lib/apt/lists/*` | 이미지 용량 최적화 |
| `WORKDIR /workspace` | 컨테이너 기동 시 기본 작업 디렉터리 |

> **`DEBIAN_FRONTEND=noninteractive`이 필요한 이유**: `tzdata` 같은 패키지는 설치 중 시간대를 묻는 대화형 화면을 표시합니다. `docker build`처럼 사람이 입력할 수 없는 환경에서는 이 화면에서 빌드가 영구히 멈춥니다. 이 환경변수로 모든 대화형 프롬프트를 차단합니다.

> **주의** **OpenClaw 사용 시 주의사항**: OpenClaw는 Anthropic 공식 도구가 아닌 서드파티 멀티채널 AI 게이트웨이입니다. 사용은 본인 책임이며, 연결하는 각 서비스의 이용 약관(ToS)을 직접 확인하세요.

### 이미지 빌드

```bash
docker build -t claude-team .
```

최초 빌드는 패키지 다운로드로 수 분이 걸립니다. 빌드 완료 후에는 캐시를 사용하므로 이후 빌드는 빠릅니다.

```bash
# 빌드 확인
docker images claude-team
```

`REPOSITORY` 컬럼에 `claude-team`이 보이면 성공입니다.

<hr>

## 호스트 랩퍼 스크립트 — docker-team.sh

호스트에서 실행하는 스크립트입니다. 이미지를 확인하고 컨테이너를 기동한 뒤 컨테이너 내부에서 `setup-team.sh`를 실행합니다.

```bash
#!/bin/bash
# docker-team.sh — Docker 기반 팀 환경 구성 (호스트 실행)

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

IMAGE="claude-team"
CONTAINER="claude-env"
PROJECT_DIR="${PROJECT_DIR:-$HOME/project}"

# ── API 키 확인 ──────────────────────────────────────────────
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}❌ ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.${NC}"
    echo "   export ANTHROPIC_API_KEY='sk-ant-...'"
    exit 1
fi

echo -e "${GREEN}✅ API 키 확인 완료${NC}"

# ── 이미지 존재 확인 ─────────────────────────────────────────
if ! docker image inspect "$IMAGE" &>/dev/null; then
    echo -e "${YELLOW}이미지가 없습니다. 빌드를 시작합니다...${NC}"
    docker build -t "$IMAGE" .
fi

echo -e "${GREEN}✅ 이미지 준비 완료 ($IMAGE)${NC}"

# ── 기존 컨테이너 정리 ───────────────────────────────────────
if docker container inspect "$CONTAINER" &>/dev/null; then
    echo "기존 컨테이너 '$CONTAINER' 종료 및 삭제..."
    docker rm -f "$CONTAINER"
fi

# ── 컨테이너 기동 ────────────────────────────────────────────
echo -e "\n${YELLOW}컨테이너 기동 중...${NC}"
mkdir -p "$PROJECT_DIR"

docker run -d --name "$CONTAINER" \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -v "$PROJECT_DIR":/workspace \
  "$IMAGE" sleep infinity

echo -e "${GREEN}✅ 컨테이너 기동 완료 ($CONTAINER)${NC}"

# ── 컨테이너 내에서 팀 셋업 스크립트 실행 ────────────────────
echo -e "\n${YELLOW}팀 환경 구성 중 (컨테이너 내부)...${NC}"

# setup-team.sh를 컨테이너로 복사 후 실행
docker cp setup-team.sh "$CONTAINER":/root/setup-team.sh
docker exec -it "$CONTAINER" bash /root/setup-team.sh
```

실행 방법:

```bash
chmod +x docker-team.sh
export ANTHROPIC_API_KEY="sk-ant-..."
bash docker-team.sh
```

> **`docker cp`란?** 호스트 파일을 실행 중인 컨테이너로 복사하는 명령입니다. `docker cp 호스트경로 컨테이너명:컨테이너경로` 형식으로 씁니다. 반대 방향(`컨테이너 → 호스트`)도 가능합니다.

<hr>

## 스크립트 전체 구조

```
docker-team.sh  (호스트)
│
├── [0단계] API 키 확인
├── [1단계] Docker 이미지 확인·빌드
├── [2단계] 기존 컨테이너 정리
├── [3단계] 컨테이너 기동 (API 키 + 볼륨)
└── [4단계] 컨테이너 내 setup-team.sh 실행

setup-team.sh  (컨테이너 내부)
│
├── [0단계] 사전 의존성 확인 (tmux, claude)
├── [1단계] 기존 세션 정리
├── [2단계] TMUX 세션 & 레이아웃 생성
├── [3단계] 파인 이름 설정
├── [4단계] 각 파인에 Claude 자동 실행
└── [5단계] 세션 접속
```

각 단계는 독립적으로 실패를 감지하며, 앞 단계가 실패하면 뒤 단계는 실행되지 않습니다(`set -e`).

<hr>

## 컨테이너 내부 셋업 스크립트 — setup-team.sh

컨테이너 내부에서 실행되는 TMUX 팀 구성 스크립트입니다.

```bash
#!/bin/bash
# setup-team.sh — 컨테이너 내부 Claude 멀티에이전트 팀 환경 자동 구성

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SESSION="team1"

# ── 유틸: 파인에 패턴이 나타날 때까지 대기 ──────────────────
wait_for_pane() {
    local pane="$1" pattern="$2" timeout="${3:-30}" waited=0
    while [ $waited -lt $timeout ]; do
        tmux capture-pane -t "$pane" -p 2>/dev/null | grep -q "$pattern" && return 0
        sleep 1; waited=$((waited + 1))
    done
    return 1
}

# ── 유틸: Claude 실행 + 다이얼로그 자동 처리 ────────────────
start_claude_in_pane() {
    local pane="$1" model="${2:-claude-sonnet-4-6}"
    local claude_bin; claude_bin="$(command -v claude)"

    tmux send-keys -t "$pane" C-c 2>/dev/null; sleep 0.3
    tmux send-keys -t "$pane" C-u 2>/dev/null; sleep 0.2

    tmux send-keys -t "$pane" \
        "cd /workspace && unset CLAUDECODE && $claude_bin --model $model --dangerously-skip-permissions" Enter

    # 다이얼로그 1: trust folder → Enter
    wait_for_pane "$pane" "trust this folder" 20 && {
        tmux send-keys -t "$pane" Enter; sleep 1
    }

    # 다이얼로그 2: terms of service → Down + Enter
    wait_for_pane "$pane" "I accept" 20 && {
        tmux send-keys -t "$pane" Down; sleep 0.5
        tmux send-keys -t "$pane" Enter; sleep 1
    }

    wait_for_pane "$pane" ">" 30
}

# ── [0/4] 사전 요구사항 확인 ────────────────────────────────
echo -e "${YELLOW}[0/4] 사전 요구사항 확인...${NC}"

MISSING=()
command -v tmux   &>/dev/null || MISSING+=("tmux (apt-get install -y tmux)")
command -v claude &>/dev/null || MISSING+=("claude (npm install -g @anthropic-ai/claude-code)")

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "${RED}❌ 누락된 의존성:${NC}"
    for m in "${MISSING[@]}"; do echo "   - $m"; done
    exit 1
fi

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}❌ ANTHROPIC_API_KEY 환경변수가 없습니다.${NC}"
    echo "   docker run 시 -e ANTHROPIC_API_KEY=... 옵션을 확인하세요."
    exit 1
fi

echo "  ✅ tmux $(tmux -V | awk '{print $2}')"
echo "  ✅ claude $(claude --version 2>/dev/null | head -1)"
echo "  ✅ API 키 주입 확인"

# ── [1/4] 기존 세션 정리 ────────────────────────────────────
echo -e "\n${YELLOW}[1/4] 기존 세션 초기화...${NC}"
tmux has-session -t "$SESSION" 2>/dev/null && {
    tmux kill-session -t "$SESSION"
    echo "  기존 '$SESSION' 세션 종료"
}

# ── [2/4] TMUX 세션 & 레이아웃 구성 ────────────────────────
echo -e "\n${YELLOW}[2/4] TMUX 세션 & 레이아웃 구성...${NC}"

tmux new-session -d -s "$SESSION" -x 220 -y 50

# 파인 5개 분할
tmux split-window -t "$SESSION:0.0" -h
tmux split-window -t "$SESSION:0.1" -h
tmux split-window -t "$SESSION:0.2" -h
tmux split-window -t "$SESSION:0.3" -h
tmux split-window -t "$SESSION:0.4" -h

# main-vertical 레이아웃 (팀장 왼쪽 넓게)
tmux select-layout -t "$SESSION:0" even-horizontal
tmux select-layout -t "$SESSION:0" main-vertical
tmux set-option -t "$SESSION" main-pane-width 110

# 파인 제목 표시 설정
tmux set-option -t "$SESSION" pane-border-status top
tmux set-option -t "$SESSION" pane-border-format " #{pane_title} "
tmux set-option -t "$SESSION" allow-rename off

# 파인 이름 설정
tmux select-pane -t "$SESSION:0.0" -T "쭌"
tmux select-pane -t "$SESSION:0.1" -T "민준 아키텍트"
tmux select-pane -t "$SESSION:0.2" -T "지훈 리서쳐"
tmux select-pane -t "$SESSION:0.3" -T "수아 UI/UX디자이너"
tmux select-pane -t "$SESSION:0.4" -T "서연 개발자"
tmux select-pane -t "$SESSION:0.5" -T "태양 QA·리뷰어"

echo "  ✅ 레이아웃 구성 완료 (6 panes)"

# ── [3/4] Claude 자동 실행 ──────────────────────────────────
echo -e "\n${YELLOW}[3/4] Claude 실행 중... (파인당 최대 1분)${NC}"

MEMBER_NAMES=("쭌" "민준" "지훈" "수아" "서연" "태양")
MEMBER_MODELS=(
    "claude-opus-4-8"    # 쭌 (팀장 — 판단·조율 중심)
    "claude-opus-4-8"    # 민준 (PM — 설계·추론 중심)
    "claude-sonnet-4-6"  # 지훈
    "claude-sonnet-4-6"  # 수아
    "claude-sonnet-4-6"  # 서연
    "claude-sonnet-4-6"  # 태양
)

for pane in 0 1 2 3 4 5; do
    echo -n "  Pane $pane (${MEMBER_NAMES[$pane]}): "
    start_claude_in_pane "$SESSION:0.$pane" "${MEMBER_MODELS[$pane]}"

    tmux capture-pane -t "$SESSION:0.$pane" -p 2>/dev/null | grep -q ">" \
        && echo -e "${GREEN}✅ 준비 완료${NC}" \
        || echo -e "${RED}⚠️  타임아웃 — 수동 확인 필요${NC}"
done

# ── [4/4] 완료 ──────────────────────────────────────────────
echo -e "\n${GREEN}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║   ✅ 팀 환경 구성 완료!              ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${NC}"

# 터미널에서 직접 실행한 경우 자동 attach
[ -t 1 ] && tmux attach -t "$SESSION"
```

<hr>

## 스크립트 핵심 함수 해설

두 유틸 함수가 자동화를 떠받칩니다.

### wait_for_pane — "응답 올 때까지 기다려"

```bash
wait_for_pane() {
    local pane="$1" pattern="$2" timeout="${3:-30}" waited=0
    while [ $waited -lt $timeout ]; do
        tmux capture-pane -t "$pane" -p 2>/dev/null | grep -q "$pattern" && return 0
        sleep 1; waited=$((waited + 1))
    done
    return 1
}
```

이 함수는 지정한 파인의 화면을 1초마다 캡처해서 원하는 문자열이 나타날 때까지 기다립니다.

| 매개변수 | 설명 | 예시 |
|----------|------|------|
| `pane` | 감시할 파인 주소 | `team1:0.2` |
| `pattern` | 기다릴 문자열 | `">"` (Claude 프롬프트) |
| `timeout` | 최대 대기 시간(초) | `30` |

> **비유: 택배 도착 알림** 매 1초마다 현관문을 살짝 열어 택배가 왔는지 확인하는 것과 같습니다. 택배(패턴)가 보이면 문을 닫고 다음 일을 합니다. 30초가 지나도 안 오면 "타임아웃"을 반환합니다.

### start_claude_in_pane — "파인에 Claude 띄워"

1. **기존 프로세스 정리** — `C-c`로 혹시 실행 중인 것을 멈추고, `C-u`로 입력창을 비웁니다.
2. **Claude 실행** — 지정 모델로 Claude Code를 `/workspace`에서 실행합니다.
3. **초기화 다이얼로그 자동 처리** — "trust this folder"와 약관 동의 창이 뜨면 자동으로 Enter/Down을 눌러 처리합니다.

```bash
# 다이얼로그 1: trust folder → Enter
wait_for_pane "$pane" "trust this folder" 20 && {
    tmux send-keys -t "$pane" Enter; sleep 1
}

# 다이얼로그 2: terms of service → Down + Enter
wait_for_pane "$pane" "I accept" 20 && {
    tmux send-keys -t "$pane" Down; sleep 0.5
    tmux send-keys -t "$pane" Enter; sleep 1
}
```

> **컨테이너에서 브라우저 인증 다이얼로그가 뜨면?** 컨테이너에 브라우저가 없으면 로그인 화면이 뜹니다. `-e ANTHROPIC_API_KEY`가 올바르게 주입됐는지 확인하세요. API 키가 없거나 잘못됐으면 Claude Code가 로그인을 요청합니다.

> **`--dangerously-skip-permissions` 플래그란?** Claude Code는 파일 쓰기·명령 실행 등 위험한 작업을 할 때 사용자에게 확인을 요청합니다. 이 플래그를 쓰면 그 확인창을 모두 생략합니다. 자동화 환경에서는 사람이 키보드 앞에 없으니 이 플래그가 필수입니다. 단, 신뢰하는 컨테이너 환경에서만 쓰세요.

<hr>

## 스크립트 실행

```bash
# 최초 1회: 이미지 빌드
docker build -t claude-team .

# 실행 (API 키 주입)
export ANTHROPIC_API_KEY="sk-ant-..."
chmod +x docker-team.sh setup-team.sh
bash docker-team.sh
```

### 실행 중 터미널 출력 예시

스크립트를 실행하면 아래와 같은 상태 메시지가 순서대로 출력됩니다.

```
✅ API 키 확인 완료
✅ 이미지 준비 완료 (claude-team)
컨테이너 기동 중...
✅ 컨테이너 기동 완료 (claude-env)

팀 환경 구성 중 (컨테이너 내부)...

[0/4] 사전 요구사항 확인...
  ✅ tmux 3.2a
  ✅ claude 2.1.181 (Claude Code)
  ✅ API 키 주입 확인

[1/4] 기존 세션 초기화...
  기존 'team1' 세션 종료

[2/4] TMUX 세션 & 레이아웃 구성...
  ✅ 레이아웃 구성 완료 (6 panes)

[3/4] Claude 실행 중... (파인당 최대 1분)
  Pane 0 (쭌): ✅ 준비 완료
  Pane 1 (민준): ✅ 준비 완료
  Pane 2 (지훈): ✅ 준비 완료
  Pane 3 (수아): ✅ 준비 완료
  Pane 4 (서연): ✅ 준비 완료
  Pane 5 (태양): ✅ 준비 완료

  ╔══════════════════════════════════════╗
  ║   ✅ 팀 환경 구성 완료!              ║
  ╚══════════════════════════════════════╝
```

<hr>

## 실행 결과 확인

스크립트 완료 후 컨테이너 내 TMUX 세션에 접속합니다.

```bash
# 컨테이너 재진입 후 세션 접속
docker exec -it claude-env bash
tmux attach -t team1
```

각 파인 상단에 이름이 표시되고, 모든 파인에 Claude 프롬프트(`>`)가 나타나면 성공입니다.

왼쪽 넓은 칸에 팀장(쭌), 오른쪽에 민준·지훈·수아·서연·태양 다섯 파인이 세로로 늘어서고, 각 칸 위에는 이름표가, 칸 안에는 입력 대기를 뜻하는 `>` 프롬프트가 떠 있습니다. 여섯 칸 모두 `>`가 보인다면 팀 전원이 지시를 받을 준비가 된 것입니다.

### 파인별 빠른 상태 확인

```bash
for pane in 0 1 2 3 4 5; do
    result=$(tmux capture-pane -t "team1:0.$pane" -p 2>/dev/null | grep -c ">")
    echo "Pane $pane: $( [ "$result" -gt 0 ] && echo '✅' || echo '⚠️  확인 필요' )"
done
```

<hr>

## 특정 에이전트에 작업 전달

팀 환경이 실행 중이면 컨테이너 외부에서도 아래 명령으로 에이전트에게 작업을 전달합니다.

```bash
# 컨테이너 밖에서 전달
docker exec claude-env tmux send-keys -t team1:0.2 "지훈, Rust와 Go의 성능 비교 조사해줘" Enter

# 컨테이너 내부 bash에서 전달
tmux send-keys -t team1:0.4 "서연, main.py에 사용자 인증 함수 추가해줘" Enter

# 태양에게 코드 리뷰 요청
tmux send-keys -t team1:0.5 "태양, 방금 작성된 auth.py 코드 리뷰해줘" Enter
```

> **`team1:0.2` 주소 읽는 법** `세션명:윈도우번호.파인번호` 형식입니다. `team1`이 세션, `0`이 첫 번째 윈도우, `2`가 세 번째 파인(0부터 시작)입니다. 지훈은 Pane 2이므로 `team1:0.2`가 됩니다.

<hr>

## 자주 발생하는 문제와 해결법

### 문제 1: 특정 파인에서 `⚠️ 타임아웃` 메시지가 뜬다

Claude가 초기화 다이얼로그에서 멈춘 경우입니다.

```bash
# 컨테이너 내 해당 파인으로 이동해서 수동 확인
docker exec -it claude-env bash
tmux attach -t team1
# Ctrl+B, q 로 파인 번호 확인 후 해당 파인 클릭
# 화면을 보고 Enter 또는 방향키로 다이얼로그 해결
```

### 문제 2: `Not logged in · Please run /login`

API 키가 컨테이너에 주입되지 않았을 때 발생합니다.

```bash
# 컨테이너 내 API 키 확인
docker exec claude-env env | grep ANTHROPIC
# 값이 없으면 컨테이너를 재생성
docker rm -f claude-env
export ANTHROPIC_API_KEY="sk-ant-..."
bash docker-team.sh
```

### 문제 3: `docker: command not found`

호스트에 Docker가 설치되지 않은 경우입니다. 플랫폼에 맞는 02-1~02-3 챕터를 다시 확인하세요.

### 문제 4: 세션이 이미 존재한다는 오류

스크립트는 기존 세션을 자동으로 정리합니다. 만약 `kill-session`이 실패하면:

```bash
docker exec claude-env tmux kill-session -t team1
bash docker-team.sh
```

<hr>

## 스크립트 커스터마이징

### 팀원 수 변경

4인 팀으로 줄이려면 `split-window` 호출을 두 개 줄이고, 배열에서 해당 항목을 제거합니다.

```bash
# 4인 팀: Pane 0~3만 사용
MEMBER_NAMES=("쭌" "민준" "서연" "태양")
MEMBER_MODELS=(
    "claude-sonnet-4-6"
    "claude-opus-4-8"
    "claude-sonnet-4-6"
    "claude-sonnet-4-6"
)
```

### 모델 변경

팀원별 모델을 바꾸려면 `MEMBER_MODELS` 배열의 해당 항목만 수정합니다.

```bash
MEMBER_MODELS=(
    "claude-opus-4-8"    # 쭌 (팀장 — Opus 유지)
    "claude-opus-4-8"    # 민준 (PM — Opus 유지)
    "claude-sonnet-4-6"  # 지훈
    "claude-sonnet-4-6"  # 수아
    "claude-sonnet-4-6"  # 서연
    "claude-sonnet-4-6"  # 태양
)
```

### 프로젝트 디렉터리 변경

기본 마운트 경로(`$HOME/project`)를 바꾸려면 실행 전 환경변수를 설정합니다.

```bash
export PROJECT_DIR="/path/to/my/project"
bash docker-team.sh
```

<hr>

## 요약

두 파일(`Dockerfile`, `docker-team.sh` + `setup-team.sh`)로 Docker 기반 팀 환경을 그대로 되살립니다.

```bash
# 최초 1회
docker build -t claude-team .

# 이후 매번
export ANTHROPIC_API_KEY="sk-ant-..."
bash docker-team.sh
```

다음 4장에서는 이 팀 환경을 스마트폰이나 다른 기기에서 원격으로 제어하는 **Remote-Control** 기능을 설명합니다.
