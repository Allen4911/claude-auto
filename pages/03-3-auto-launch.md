## 03-3. 각 파인에 Claude Code 자동 실행

레이아웃이 준비되었다면 이제 각 파인에 Claude Code를 자동으로 실행하는 방법을 구현합니다. 핵심은 Claude Code 시작 시 나타나는 대화 상자를 자동으로 처리하는 것입니다.

> 💡 **자동 실행이 필요한 이유:** 6개 파인에 수동으로 Claude를 실행하면 각각 클릭하고 대화 상자에 응답하는 과정을 6번 반복해야 합니다. 팀 환경을 자주 재시작하거나 파인이 죽었을 때마다 이 작업을 반복하면 금세 번거로워집니다. 자동 실행 스크립트는 이 과정을 한 번에 처리합니다.

<hr>

## Claude Code 시작 시 나타나는 다이얼로그

Claude Code를 처음 실행하면 두 가지 대화 상자가 순서대로 나타납니다.

```
[다이얼로그 1] Do you trust the files in this folder?
> Yes, I trust this folder (proceed)
  No, exit

[다이얼로그 2] Do you accept the terms of service?
  No, exit
> Yes, I accept
```

- 다이얼로그 1: Enter만 누르면 됩니다 (기본값이 "Yes").
- 다이얼로그 2: 기본값이 "No"이므로 아래 방향키를 한 번 누른 후 Enter가 필요합니다.

> 💡 **다이얼로그 2의 함정:** 두 다이얼로그 모두 Enter로 응답하면 된다고 착각하기 쉽습니다. 하지만 다이얼로그 2의 기본 커서는 "No, exit"에 있습니다. Enter를 그대로 누르면 거부 처리되어 Claude가 종료됩니다. 반드시 방향키 ↓로 "Yes, I accept"를 선택한 뒤 Enter를 눌러야 합니다.

> 💡 **이 다이얼로그는 언제 나타나나요?** 인증 후에는 두 다이얼로그 모두 다시 나타나지 않습니다 — 폴더 신뢰는 현재 작업 폴더에 `.claude` 디렉터리를 만들어 기록하고, 이용 약관 동의는 계정에 한 번만 필요합니다. 따라서 같은 폴더에서 재실행할 때는 다이얼로그 없이 바로 프롬프트가 뜹니다.

정리하면 자동 실행 스크립트는 파인마다 이 두 단계를 똑같이 반복해야 합니다 — 1번 다이얼로그엔 Enter, 2번엔 "↓ 후 Enter". 6개 파인을 띄울 때 이 응답을 일일이 손으로 누르는 대신, 다음에 나오는 함수가 각 파인에 같은 키 입력을 자동으로 흘려보내 줍니다.

<hr>

## 파인 대기 함수

파인에 특정 텍스트가 나타날 때까지 기다리는 헬퍼 함수입니다.

> 💡 **이 함수가 왜 필요할까요?** Claude 실행은 몇 초가 걸리는데, 화면이 준비되기 전에 키를 보내면 입력이 사라집니다. `wait_for_pane`은 화면에 특정 글자(예: "trust this folder")가 보일 때까지 1초 간격으로 확인(폴링)한 뒤 다음 단계로 넘어갑니다. "화면 상태를 보고 나서 다음 키를 보낸다"는 원칙이 이 함수의 핵심입니다.

```bash
# 특정 pane에 패턴이 나타날 때까지 대기
# $1: pane 주소 (예: team:0.1)
# $2: 대기할 텍스트 패턴
# $3: 최대 대기 시간(초, 기본 30)
wait_for_pane() {
    local pane="$1"
    local pattern="$2"
    local timeout="${3:-30}"
    local waited=0

    while [ $waited -lt $timeout ]; do
        if tmux capture-pane -t "$pane" -p 2>/dev/null | grep -q "$pattern"; then
            return 0
        fi
        sleep 1
        waited=$((waited + 1))
    done
    return 1  # 타임아웃
}
```

> 💡 **함수 내부 동작 설명:** `tmux capture-pane -p`로 파인 화면 텍스트를 읽고, `grep -q`로 원하는 패턴이 있는지 확인합니다. 있으면 `return 0`(성공)으로 즉시 빠져나오고, 없으면 1초 기다렸다 다시 확인합니다. `timeout` 초가 지나도 패턴이 나타나지 않으면 `return 1`(실패)을 반환해 호출한 쪽에서 예외 처리를 할 수 있게 합니다.

이 함수를 활용하면 환경마다 다른 Claude 시작 시간(빠른 PC에서 1초, 느린 서버에서 10초)에 관계없이 동일하게 작동합니다.

<hr>

## 파인별 Claude 실행 함수

```bash
# $1: 파인 주소 (예: team:0.2)
# $2: 모델 (기본값: claude-sonnet-4-6)
start_claude_in_pane() {
    local pane="$1"
    local model="${2:-claude-sonnet-4-6}"
    local claude_bin
    claude_bin="$(command -v claude)"

    # 이전 입력 초기화
    tmux send-keys -t "$pane" C-c 2>/dev/null
    sleep 0.3
    tmux send-keys -t "$pane" C-u 2>/dev/null
    sleep 0.2

    # Claude 실행
    tmux send-keys -t "$pane" \
        "cd /home/user && unset CLAUDECODE && $claude_bin --model $model --dangerously-skip-permissions" \
        Enter

    # 다이얼로그 1: "trust this folder" → Enter
    if wait_for_pane "$pane" "trust this folder" 20; then
        tmux send-keys -t "$pane" Enter
        sleep 1
    fi

    # 다이얼로그 2: "I accept" → Down + Enter
    if wait_for_pane "$pane" "I accept" 20; then
        tmux send-keys -t "$pane" Down
        sleep 0.5
        tmux send-keys -t "$pane" Enter
        sleep 1
    fi

    # Claude 프롬프트(>) 나타날 때까지 대기
    wait_for_pane "$pane" ">" 30
}
```

함수 내부의 단계별 의미를 짚어보면 다음과 같습니다.

| 단계 | 코드 | 이유 |
|------|------|------|
| 초기화 | `C-c`, `C-u` | 이전에 실행 중인 프로세스나 입력 잔여물 제거 |
| `unset CLAUDECODE` | 환경변수 제거 | 이전 세션 환경변수가 새 Claude 실행에 충돌하는 경우 방지 |
| `command -v claude` | 경로 동적 탐색 | PATH가 다를 수 있는 환경에서 실제 실행 파일 경로를 확인 |
| 다이얼로그 대기 | `wait_for_pane` | 화면 준비 전에 키가 날아가지 않도록 확인 후 전송 |

> 💡 **`C-c`와 `C-u`의 역할:** `C-c`(Ctrl+C)는 실행 중인 프로세스에 인터럽트 신호를 보내 중단시킵니다. `C-u`는 터미널에서 현재 줄의 입력을 지웁니다. 재시작 시 이전 Claude 인스턴스가 살아 있을 수 있으므로, 두 명령으로 깨끗하게 초기화한 뒤 새로 실행합니다.

> 💡 **`--dangerously-skip-permissions` 다시 보기:** 이 플래그는 파일 읽기·쓰기·명령 실행 등의 권한 확인 팝업을 자동 승인합니다. 자동화 환경에서는 필수지만, 이름 그대로 위험을 내포합니다. **신뢰하는 코드만 있는 로컬 환경**에서 사용하고, 출처가 불분명한 코드를 다룰 때는 해당 파인에서 이 플래그를 빼고 실행하세요.

이 함수가 한 파인에서 밟는 순서는 이렇습니다 — 먼저 해당 파인에 `claude` 실행 명령을 보내고, 첫 다이얼로그(trust)가 뜨길 기다렸다 Enter, 다음 다이얼로그(accept)엔 ↓와 Enter를 보낸 뒤, 마지막으로 Claude 입력 프롬프트(`>`)가 나타날 때까지 기다립니다.

<hr>

## 전체 팀에 Claude 실행

6개 파인 모두에 순서대로 Claude를 실행합니다.

```bash
SESSION="team"

# 파인별 이름과 모델 배열
MEMBER_NAMES=("쭌" "민준" "지훈" "수아" "서연" "태양")
MEMBER_MODELS=(
    "claude-sonnet-4-6"  # 0: 쭌
    "claude-opus-4-8"    # 1: 민준 (복잡한 설계 → Opus)
    "claude-sonnet-4-6"  # 2: 지훈
    "claude-sonnet-4-6"  # 3: 수아
    "claude-sonnet-4-6"  # 4: 서연
    "claude-sonnet-4-6"  # 5: 태양
)

for pane in 0 1 2 3 4 5; do
    model="${MEMBER_MODELS[$pane]}"
    echo -n "  Pane $pane (${MEMBER_NAMES[$pane]}): 시작 중..."

    start_claude_in_pane "$SESSION:0.$pane" "$model"

    # 성공 여부 확인
    if tmux capture-pane -t "$SESSION:0.$pane" -p 2>/dev/null | grep -q ">"; then
        echo " ✅ 준비 완료"
    else
        echo " ⚠️  타임아웃 — 수동 확인 필요"
    fi
done
```

> 💡 **왜 순차 실행인가?** 6개 파인에 동시에 Claude를 실행하면 다이얼로그 응답 타이밍이 겹쳐 키 입력이 엉킬 수 있습니다. 순차 실행은 하나씩 완전히 준비된 것을 확인한 뒤 다음으로 넘어가므로 느리지만 안정적입니다. 모든 파인이 준비되면 이후 작업은 병렬로 처리됩니다.

위 반복문은 0번부터 5번 파인까지 하나씩 차례로 같은 시작 절차를 돌립니다. 각 파인은 성공하면 "✅ 준비 완료", 타임아웃이면 "⚠️ 타임아웃"을 출력해 어느 파인이 막혔는지 한눈에 보입니다.

<hr>

## 이미 실행 중인 파인에 메시지 보내기

Claude가 실행 중인 파인에 메시지를 전송하는 방법입니다.

```bash
# 특정 파인에 메시지 전송 (줄바꿈 = Enter)
tmux send-keys -t team:0.1 "민준, 현재 아키텍처 검토해줘" Enter

# 여러 파인에 동시 전송 (브로드캐스트)
for pane in 0 1 2 3 4 5; do
    tmux send-keys -t "team:0.$pane" "모두 현재 상태 보고해줘" Enter
done
```

> 💡 **메시지와 Enter를 분리해야 할 때:** 긴 메시지나 특수 문자가 포함된 경우 `send-keys`와 Enter를 한 번에 보내면 파인에서 제대로 받지 못할 수 있습니다. 이럴 때는 메시지를 먼저 보내고 짧게 대기한 뒤 Enter를 별도로 전송합니다.

```bash
# 안전한 분리 전송 패턴
tmux send-keys -t team:0.1 "긴 지시 내용..."
sleep 0.3
tmux send-keys -t team:0.1 "" Enter
```

<hr>

## 파인 상태 확인

각 파인이 Claude 프롬프트 상태인지 확인합니다.

```bash
for pane in 0 1 2 3 4 5; do
    content=$(tmux capture-pane -t "team:0.$pane" -p 2>/dev/null)
    if echo "$content" | grep -q ">"; then
        echo "  Pane $pane: ✅ Claude 대기 중"
    elif echo "$content" | grep -q "trust this folder"; then
        echo "  Pane $pane: ⚠️  다이얼로그 1 대기 중"
    elif echo "$content" | grep -q "I accept"; then
        echo "  Pane $pane: ⚠️  다이얼로그 2 대기 중"
    else
        echo "  Pane $pane: ❓ 상태 불명"
    fi
done
```

> 💡 **`❓ 상태 불명`이 나오는 경우:** 파인이 완전히 비어 있거나, Claude 시작 중 오류가 났거나, 전혀 다른 프로세스가 실행 중일 때입니다. 이 경우 `tmux capture-pane -t team:0.N -p`로 화면을 직접 읽어 무슨 내용이 있는지 확인하세요.

<hr>

## --dangerously-skip-permissions 주의사항

이 플래그는 파일 읽기/쓰기/실행 권한 요청을 자동 승인합니다. 자동화에 편리하지만 다음 사항을 인지하고 사용하세요.

- 신뢰할 수 있는 로컬 환경에서만 사용
- 외부에서 접근 가능한 서버에서는 주의
- 작업 완료 후 플래그 없이 재실행하면 권한 확인이 다시 활성화됨

> 💡 **언제 이 플래그 없이 써야 할까요?** 팀원이 생성한 코드를 처음 검토하거나, 신뢰하지 못하는 외부 프로젝트를 분석할 때는 이 플래그를 빼고 Claude를 실행하세요. 그러면 파일 쓰기나 명령 실행 전에 Claude가 매번 확인을 요청합니다. 안전 확인이 번거롭더라도, 중요한 환경에서는 이 절차가 실수를 막아 줍니다.

<hr>

## 요약

자동 실행의 핵심은 세 가지입니다.

1. **`wait_for_pane`으로 화면 상태를 확인** — 준비 전에 키를 보내지 않는다
2. **두 다이얼로그를 순서대로 처리** — Enter → ↓+Enter
3. **순차 실행으로 안정성 확보** — 하나가 준비된 후 다음으로 넘어간다

다음 챕터에서는 각 에이전트에게 고유한 역할을 부여하는 `CLAUDE.md` 파일 작성법을 설명합니다.
