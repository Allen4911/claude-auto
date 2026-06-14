## 09-4. 자동복구 스크립트

## 이 절에서 배우는 것

[09-2절](09-2-tmux-recovery.md)에서는 상황별 수동 복구 방법을 배웠다. 이 절에서는 수동 절차를 스크립트로 자동화하여, 문제 발생 시 단 한 번의 명령으로 팀 환경 전체를 복구하는 방법을 다룬다.

> 💡 **자동복구 vs 수동복구** 수동 복구는 상황을 이해하는 데 유리하고, 자동복구는 속도와 일관성이 강점입니다. 처음에는 수동 절차를 익히고, 익숙해지면 자동복구 스크립트로 전환하는 것을 권장합니다.

> 💡 **소방 대피 훈련 비유** 자동복구 스크립트는 소방 대피 훈련과 같습니다. 화재가 났을 때 어디로 가야 하는지 미리 정해두면, 실제 상황에서 당황하지 않고 빠르게 대처할 수 있습니다. 팀 환경이 무너진 긴박한 순간에 스크립트 하나로 복구할 수 있도록 평소에 준비해 두는 것입니다.

<hr>

## 자동복구가 필요한 상황

| 상황 | 수동 복구 시간 | 자동복구 시간 |
|------|--------------|-------------|
| SSH 재접속 후 세션 재연결 | 1분 미만 | 즉시 (alias) |
| 파인 1~2개 Claude 종료 | 3~5분 | 30초 |
| TMUX 세션 전체 소실 | 10~15분 | 1~2분 |
| 시스템 재부팅 후 전체 재구성 | 20분 이상 | 2~3분 |

수동 복구 시간과 자동복구 시간의 차이가 가장 두드러지는 것은 "시스템 재부팅 후 전체 재구성"이다. 20분이 걸리는 작업을 2~3분 안에 완료하면, 팀 업무 재개 대기 시간이 대폭 줄어든다.

<hr>

## 원스톱 복구 스크립트

아래 스크립트를 `~/team-recover.sh`로 저장하면, 어떤 상태에서든 팀 환경을 자동으로 점검하고 복구한다.

```bash
#!/usr/bin/env bash
# team-recover.sh — 팀 환경 원스톱 자동복구 스크립트
# 사용법: bash ~/team-recover.sh [--force]
#   --force : 세션이 살아있어도 파인을 전부 재기동

set -euo pipefail

SESSION="team1"  # ← 본인의 TMUX 세션명으로 수정 (예: "myteam", "dev" 등)
FORCE="${1:-}"

# ── 색상 헬퍼 ─────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[OK]${NC}  $*"; }
warn() { echo -e "${YELLOW}[??]${NC}  $*"; }
fail() { echo -e "${RED}[!!]${NC}  $*"; }

# ── 1단계: TMUX 서버 및 세션 확인 ────────────────────
echo "▶ 1단계: TMUX 세션 확인 중..."
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  warn "세션 '$SESSION' 없음 — 새로 생성합니다."
  bash /path/to/setup-team.sh  # 본인 프로젝트의 setup 스크립트 경로로 수정
  ok "세션 재생성 완료"
  exit 0
fi
ok "세션 '$SESSION' 존재 확인"

# ── 2단계: 파인 수 확인 (정상 = 6개) ─────────────────
echo "▶ 2단계: 파인 개수 확인 중..."
PANE_COUNT=$(tmux list-panes -t "$SESSION" | wc -l)
if [[ "$PANE_COUNT" -lt 6 ]]; then
  fail "파인 수 부족: ${PANE_COUNT}/6 — 세션 전체 재생성합니다."
  tmux kill-session -t "$SESSION" 2>/dev/null || true
  bash /path/to/setup-team.sh  # 본인 프로젝트의 setup 스크립트 경로로 수정
  ok "세션 재생성 완료"
  exit 0
fi
ok "파인 수 정상: ${PANE_COUNT}개"

# ── 3단계: 각 파인 Claude 프로세스 확인 ──────────────
echo "▶ 3단계: 파인별 Claude 상태 확인 중..."

# 파인 번호 → 역할 매핑
declare -A ROLE=([0]="쭌" [1]="민준" [2]="지훈" [3]="수아" [4]="서연" [5]="태양")
# 파인 번호 → 모델 매핑 (쭌·민준=Opus, 나머지=Sonnet)
declare -A MODEL=([0]="opus" [1]="opus" [2]="sonnet" [3]="sonnet" [4]="sonnet" [5]="sonnet")

DEAD_PANES=()
for PANE_IDX in 0 1 2 3 4 5; do
  # 파인 화면 마지막 3줄로 Claude 활성 여부 판단
  LAST=$(tmux capture-pane -t "${SESSION}:0.${PANE_IDX}" -p 2>/dev/null | tail -3)
  if echo "$LAST" | grep -qE '❯\s*$|>\s*$|claude>|\$\s*$'; then
    ok "Pane ${PANE_IDX} (${ROLE[$PANE_IDX]}): 활성"
  else
    warn "Pane ${PANE_IDX} (${ROLE[$PANE_IDX]}): 응답 없음 — 재기동 대상"
    DEAD_PANES+=("$PANE_IDX")
  fi
done

# ── 4단계: 죽은 파인 재기동 ──────────────────────────
if [[ ${#DEAD_PANES[@]} -eq 0 && -z "$FORCE" ]]; then
  ok "모든 파인 정상 — 복구 불필요"
  exit 0
fi

if [[ -n "$FORCE" ]]; then
  warn "--force 옵션: 모든 파인을 재기동합니다."
  DEAD_PANES=(0 1 2 3 4 5)
fi

echo "▶ 4단계: 비정상 파인 재기동 중... (${#DEAD_PANES[@]}개)"
for PANE_IDX in "${DEAD_PANES[@]}"; do
  echo "  → Pane ${PANE_IDX} (${ROLE[$PANE_IDX]}) 재기동..."
  bash /path/to/reboot-pane.sh "$PANE_IDX" 2>/dev/null || {  # 본인 프로젝트의 reboot-pane 스크립트 경로로 수정
    fail "reboot-pane.sh 실패 — 수동 확인 필요: Pane ${PANE_IDX}"
    continue
  }
  sleep 2
  ok "Pane ${PANE_IDX} 재기동 완료"
done

# ── 5단계: 역할 정체성 재주입 ─────────────────────────
echo "▶ 5단계: 재기동된 파인에 역할 정체성 주입 중..."
sleep 3  # Claude 초기화 대기

IDENTITY_MSGS=(
  [0]="너는 쭌(팀장)이야. Pane 0. 팀 총괄 및 지시 전달 담당. 직접 코딩하지 않고 팀원에게 위임."
  [1]="너는 민준(PM·아키텍트)이야. Pane 1. 프로젝트 관리와 시스템 설계 담당. 팀원 지시·칸반 관리."
  [2]="너는 지훈(리서쳐)이야. Pane 2. 기술 조사와 정보 수집 담당."
  [3]="너는 수아(디자이너)이야. Pane 3. UI/UX 및 프론트엔드 담당."
  [4]="너는 서연(개발자)이야. Pane 4. 백엔드 구현 담당."
  [5]="너는 태양(리뷰어)이야. Pane 5. 코드 리뷰 및 품질 검토 담당."
)

for PANE_IDX in "${DEAD_PANES[@]}"; do
  MSG="${IDENTITY_MSGS[$PANE_IDX]}"
  # 첫 메시지는 tmux send-keys로 직접 전달 (데몬 미인식 우회)
  tmux send-keys -t "${SESSION}:0.${PANE_IDX}" "$MSG" Enter
  sleep 0.3
  ok "Pane ${PANE_IDX} 정체성 주입 완료"
done

echo ""
ok "═══ 자동복구 완료 ═══"
echo "  재기동된 파인: ${DEAD_PANES[*]:-없음}"
echo "  세션 확인: tmux attach -t $SESSION"
```

<hr>

## 스크립트 단계별 해설

스크립트가 5단계로 나뉘는 이유를 각각 이해하면, 문제가 발생했을 때 어느 단계에서 실패했는지 빠르게 파악할 수 있다.

**1단계: 세션 존재 확인**

> TMUX 세션 자체가 없으면 나머지 단계는 의미가 없다. 가장 먼저 확인하여 빠르게 분기한다.

```bash
tmux has-session -t "$SESSION" 2>/dev/null
```
세션이 없으면 즉시 `setup-team.sh`를 호출하고 종료한다.

<hr>

**2단계: 파인 수 확인**

> 세션은 있지만 파인이 6개 미만이면 레이아웃 복구보다 전체 재구성이 빠르다.

```bash
PANE_COUNT=$(tmux list-panes -t "$SESSION" | wc -l)
```
6개 미만이면 세션을 종료하고 재생성한다.

<hr>

**3단계: 각 파인 Claude 상태 확인**

> 파인은 있지만 Claude가 종료된 경우를 탐지한다. 파인 화면 마지막 3줄을 읽어 프롬프트가 보이는지 확인한다.

```bash
LAST=$(tmux capture-pane -t "${SESSION}:0.${PANE_IDX}" -p 2>/dev/null | tail -3)
```

> 💡 **`tmux capture-pane`이란?** 특정 파인의 화면 내용을 텍스트로 추출하는 명령입니다. `-p`는 "print to stdout" 옵션으로, 추출한 내용을 바로 출력합니다. `tail -3`으로 마지막 3줄만 보면 프롬프트가 있는지 빠르게 판단할 수 있습니다.

<hr>

**4단계: 비정상 파인 재기동**

> 3단계에서 수집한 "죽은 파인" 목록을 대상으로 `reboot-pane.sh`를 실행한다. 이 스크립트는 올바른 모델(쭌·민준=Opus, 나머지=Sonnet)로 Claude를 재시작한다.

```bash
bash /path/to/reboot-pane.sh "$PANE_IDX"  # 본인 프로젝트의 reboot-pane 스크립트 경로로 수정
```

<hr>

**5단계: 역할 정체성 재주입**

> Claude Code를 새로 시작하면 이전 역할을 기억하지 못한다. 재기동 후 각 파인에 역할 메시지를 전달해야 팀원으로서 올바르게 동작한다.

```bash
tmux send-keys -t "${SESSION}:0.${PANE_IDX}" "$MSG" Enter
```

> 💡 **왜 역할 재주입이 필요한가?** Claude Code는 새로 시작할 때 빈 상태로 시작합니다. "너는 서연(개발자)이야"라는 역할 정의가 없으면, Claude는 일반 어시스턴트로 동작합니다. 역할 주입은 Claude가 팀원으로서 적절한 맥락을 갖고 응답할 수 있도록 초기화하는 과정입니다.

<hr>

## 스크립트 설치 및 사용

**1. 스크립트 저장 및 실행 권한 부여**

```bash
# 스크립트 저장
curl -o ~/team-recover.sh \
  https://raw.githubusercontent.com/your-org/your-repo/main/team-recover.sh
# 또는 위 내용을 직접 붙여넣기 후:
chmod +x ~/team-recover.sh
```

**2. 빠른 접근을 위한 alias 등록**

```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
echo "alias recover='bash ~/team-recover.sh'" >> ~/.bashrc
source ~/.bashrc
```

**3. 일반 복구 (죽은 파인만 재기동)**

```bash
recover
# 또는
bash ~/team-recover.sh
```

**4. 강제 전체 재기동 (모든 파인 갱신)**

```bash
recover --force
# 또는
bash ~/team-recover.sh --force
```

<hr>

## 복구 단계별 소요 시간

```
[1] TMUX 세션 확인    ──  즉시
[2] 파인 수 확인      ──  즉시
[3] 상태 점검 (×6)   ──  5~10초
[4] 파인 재기동       ──  파인당 약 5초
[5] 정체성 주입       ──  파인당 약 3초
────────────────────────────────
전체 (파인 2개 복구 기준)  ── 약 30초
전체 (6개 전부 재기동)     ── 약 60~90초
```

> ⚠️ **주의** `--force` 옵션은 현재 작업 중인 Claude 세션을 강제 종료합니다. 팀원이 미커밋 작업을 진행 중이라면 먼저 저장 여부를 확인하세요.

<hr>

## 문제 상황별 권장 명령

| 증상 | 권장 명령 |
|------|----------|
| 특정 파인만 응답 없음 | `bash ~/team-recover.sh` |
| 여러 파인 동시 이상 | `bash ~/team-recover.sh` |
| 모든 파인 역할 혼선 | `bash ~/team-recover.sh --force` |
| TMUX 세션 자체 소실 | `bash /path/to/setup-team.sh` (본인 경로로 수정) |
| 시스템 재부팅 후 | `bash /path/to/setup-team.sh` (본인 경로로 수정) |

> 💡 세션 자체가 소실된 경우는 스크립트가 자동으로 `setup-team.sh`를 호출하므로, 항상 `team-recover.sh` 하나만 기억해도 충분합니다.

<hr>

## 복구 실패 시 트러블슈팅

자동복구 스크립트가 기대대로 동작하지 않을 때 확인할 사항이다.

**`reboot-pane.sh` 실패 시**

```bash
# 스크립트 존재 여부 확인 (경로는 본인 프로젝트에 맞게 수정)
ls -la /path/to/reboot-pane.sh

# 실행 권한 확인
chmod +x /path/to/reboot-pane.sh

# 직접 실행하여 오류 확인
bash /path/to/reboot-pane.sh 2 2>&1
```

**역할 주입 후 Claude가 역할을 인식 못하는 경우**

```bash
# 파인 화면 상태 직접 확인
tmux capture-pane -t team1:0.2 -p | tail -10
```

파인이 Claude 시작 화면에서 멈춰있거나 입력 대기 중이 아니면, Claude 초기화가 아직 끝나지 않은 것이다. `sleep 3`을 늘리거나 수동으로 역할 메시지를 다시 전달한다.

```bash
# 수동 역할 재주입 (Pane 2 예시)
tmux send-keys -t team1:0.2 "너는 지훈(리서쳐)이야. Pane 2. 기술 조사 담당." Enter
```

**`set -euo pipefail`로 인해 스크립트가 중간에 종료되는 경우**

스크립트 맨 위의 `set -euo pipefail`은 오류 발생 시 즉시 종료하도록 하는 설정이다. 특정 단계에서 비정상 종료된다면, 해당 명령을 단독으로 실행해 오류 메시지를 확인한다.

```bash
# 예: 2단계만 단독 실행
SESSION="team1"
PANE_COUNT=$(tmux list-panes -t "$SESSION" | wc -l)
echo "파인 수: $PANE_COUNT"
```

<hr>

## 요약

자동복구 스크립트는 5단계(세션 확인 → 파인 수 → Claude 상태 → 파인 재기동 → 역할 주입) 순서로 팀 환경을 진단하고 복구한다. `recover` alias를 등록해 두면 어떤 상태에서든 단 한 번의 명령으로 팀을 원상복구할 수 있다. `--force` 옵션은 모든 파인을 강제 재기동하므로, 역할 혼선이나 전체 이상 시에 활용한다. 스크립트가 실패할 때는 단계별로 명령을 분리해 실행하면 원인을 빠르게 찾을 수 있다.
