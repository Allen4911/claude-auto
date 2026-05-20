## 3-5. 팀 셋업 스크립트 작성

지금까지 배운 레이아웃 구성, Claude 자동 실행, 역할 정의를 하나의 스크립트로 통합합니다. 이 스크립트를 한 번 실행하면 팀 전체 환경이 자동으로 구성됩니다.

<hr>

## 스크립트 전체 구조

```
setup-team.sh
│
├── [0단계] 사전 의존성 확인 (tmux, claude)
├── [1단계] 기존 세션 정리
├── [2단계] TMUX 세션 & 레이아웃 생성
├── [3단계] 파인 이름 설정
├── [4단계] 각 파인에 Claude 자동 실행
└── [5단계] 세션 접속
```

![[03-5-setup-script.png]]

<hr>

## 완성된 셋업 스크립트

```bash
#!/bin/bash
# setup-team.sh — Claude 멀티에이전트 팀 환경 자동 구성

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
        "cd /home/user && unset CLAUDECODE && $claude_bin --model $model --dangerously-skip-permissions" Enter

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
command -v tmux   &>/dev/null || MISSING+=("tmux (sudo apt install -y tmux)")
command -v claude &>/dev/null || MISSING+=("claude (npm install -g @anthropic-ai/claude-code)")

if [ ${#MISSING[@]} -gt 0 ]; then
    echo -e "${RED}❌ 누락된 의존성:${NC}"
    for m in "${MISSING[@]}"; do echo "   - $m"; done
    exit 1
fi

echo "  ✅ tmux $(tmux -V | awk '{print $2}')"
echo "  ✅ claude $(claude --version 2>/dev/null | head -1)"

# ── [1/4] 기존 세션 정리 ────────────────────────────────────
echo -e "\n${YELLOW}[1/4] 기존 세션 초기화...${NC}"
tmux has-session -t "$SESSION" 2>/dev/null && {
    tmux kill-session -t "$SESSION"
    echo "  기존 '$SESSION' 세션 종료"
}

# ── [2/4] TMUX 세션 & 레이아웃 구성 ────────────────────────
echo -e "\n${YELLOW}[2/4] TMUX 세션 & 레이아웃 구성...${NC}"

TERM_WIDTH=$(tput cols 2>/dev/null || echo 317)
TERM_HEIGHT=$(tput lines 2>/dev/null || echo 85)

tmux new-session -d -s "$SESSION" -x "$TERM_WIDTH" -y "$TERM_HEIGHT"

# 파인 5개 분할
tmux split-window -t "$SESSION:0.0" -h
tmux split-window -t "$SESSION:0.1" -h
tmux split-window -t "$SESSION:0.2" -h
tmux split-window -t "$SESSION:0.3" -h
tmux split-window -t "$SESSION:0.4" -h

# main-vertical 레이아웃 (팀장 왼쪽 넓게)
tmux select-layout -t "$SESSION:0" even-horizontal
tmux select-layout -t "$SESSION:0" main-vertical
tmux set-option -t "$SESSION" main-pane-width 158

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
    "claude-sonnet-4-6"
    "claude-opus-4-6"
    "claude-sonnet-4-6"
    "claude-sonnet-4-6"
    "claude-sonnet-4-6"
    "claude-sonnet-4-6"
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

## 스크립트 실행

```bash
# 실행 권한 부여
chmod +x setup-team.sh

# 실행
bash setup-team.sh
```

<hr>

## 실행 결과 확인

스크립트 완료 후 TMUX 세션에 접속합니다.

```bash
tmux attach -t team
```

각 파인 상단에 이름이 표시되고, 모든 파인에 Claude 프롬프트(>)가 나타나면 성공입니다.

<hr>

## 특정 에이전트에 작업 전달

팀 환경이 실행 중이면 터미널 어디서든 아래 명령으로 에이전트에게 작업을 전달할 수 있습니다.

```bash
# 지훈에게 리서치 요청
tmux send-keys -t team:0.2 "지훈, Rust와 Go의 성능 비교 조사해줘" Enter

# 서연에게 코드 작성 요청
tmux send-keys -t team:0.4 "서연, main.py에 사용자 인증 함수 추가해줘" Enter

# 태양에게 코드 리뷰 요청
tmux send-keys -t team:0.5 "태양, 방금 작성된 auth.py 코드 리뷰해줘" Enter
```

<hr>

## 요약

셋업 스크립트 하나로 팀 전체 환경을 재현할 수 있습니다. 다음 4장에서는 이 팀 환경을 스마트폰이나 다른 기기에서 원격으로 제어하는 **Remote-Control** 기능을 설명합니다.
