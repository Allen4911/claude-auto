## 9-4. 자동복구 스크립트

## 이 절에서 배우는 것

[09-2절](09-2-tmux-recovery.md)에서는 상황별 수동 복구 방법을 배웠다. 이 절에서는 수동 절차를 스크립트로 자동화하여, 문제 발생 시 단 한 번의 명령으로 팀 환경 전체를 복구하는 방법을 다룬다.

> 💡 **자동복구 vs 수동복구** 수동 복구는 상황을 이해하는 데 유리하고, 자동복구는 속도와 일관성이 강점입니다. 처음에는 수동 절차를 익히고, 익숙해지면 자동복구 스크립트로 전환하는 것을 권장합니다.

<hr>

## 자동복구가 필요한 상황

| 상황 | 수동 복구 시간 | 자동복구 시간 |
|------|--------------|-------------|
| SSH 재접속 후 세션 재연결 | 1분 미만 | 즉시 (alias) |
| 파인 1~2개 Claude 종료 | 3~5분 | 30초 |
| TMUX 세션 전체 소실 | 10~15분 | 1~2분 |
| 시스템 재부팅 후 전체 재구성 | 20분 이상 | 2~3분 |

<hr>

## 원스톱 복구 스크립트

아래 스크립트를 `~/team-recover.sh`로 저장하면, 어떤 상태에서든 팀 환경을 자동으로 점검하고 복구한다.

```bash
#!/usr/bin/env bash
# team-recover.sh — 팀 환경 원스톱 자동복구 스크립트
# 사용법: bash ~/team-recover.sh [--force]
#   --force : 세션이 살아있어도 파인을 전부 재기동

set -euo pipefail

SESSION="team1"
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
  bash /mnt/c/work/Team/setup-team.sh
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
  bash /mnt/c/work/Team/setup-team.sh
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
  bash /mnt/c/work/Team/reboot-pane.sh "$PANE_IDX" 2>/dev/null || {
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

## 스크립트 설치 및 사용

**1. 스크립트 저장 및 실행 권한 부여**

```bash
# 스크립트 저장
curl -o ~/team-recover.sh \
  https://raw.githubusercontent.com/Allen4911/Team/main/team-recover.sh
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
| TMUX 세션 자체 소실 | `bash /mnt/c/work/Team/setup-team.sh` |
| 시스템 재부팅 후 | `bash /mnt/c/work/Team/setup-team.sh` |

> 💡 세션 자체가 소실된 경우는 스크립트가 자동으로 `setup-team.sh`를 호출하므로, 항상 `team-recover.sh` 하나만 기억해도 충분합니다.
