## 03-2. 팀 에이전트 레이아웃 설계

TMUX 구조를 이해했다면 이제 실제로 6명의 Claude 에이전트가 배치될 팀 레이아웃을 설계합니다. 좋은 레이아웃은 각 에이전트의 역할을 명확하게 하고, 시각적으로 팀 전체 상태를 한눈에 파악할 수 있게 합니다.

> 💡 **레이아웃이 단순한 화면 꾸미기가 아닌 이유:** 어떤 파인이 어디에 있는지를 한눈에 알 수 있으면, 문제가 생겼을 때 시선이 바로 해당 파인으로 향합니다. 반대로 파인이 뒤죽박죽이면 "지금 서연이 어느 칸이지?" 찾느라 시간을 씁니다. 레이아웃은 팀 운영 효율에 직접 영향을 줍니다.

<hr>

## 팀 구성 설계

이 책에서 사용하는 팀 구성은 실제 소프트웨어 개발팀을 모델로 합니다.

| 파인 | 이름 | 역할 | 모델 |
|------|------|------|------|
| Pane 0 | 쭌 | 팀장 — 지시 수령, 작업 배분, 결과 보고 | Sonnet |
| Pane 1 | 민준 | 아키텍트 — 시스템 설계, 기술 방향 결정 | Opus |
| Pane 2 | 지훈 | 리서쳐 — 정보 수집, 기술 조사 | Sonnet |
| Pane 3 | 수아 | 디자이너 — UI/UX, 사용자 경험 설계 | Sonnet |
| Pane 4 | 서연 | 개발자 — 기능 구현, 코드 작성 | Sonnet |
| Pane 5 | 태양 | 리뷰어 — 코드 리뷰, 품질 검토 | Sonnet |

> 민준(아키텍트)은 복잡한 설계 판단이 많아 Claude Opus를 사용합니다. 나머지는 속도와 비용이 균형 잡힌 Claude Sonnet을 사용합니다.

> 💡 **모델을 왜 다르게 쓸까요?** Opus는 더 깊이 생각하지만 느리고 비쌉니다. Sonnet은 빠르고 저렴합니다. 깊은 판단이 필요한 설계(민준)에는 Opus, 정해진 작업을 빠르게 처리하는 역할에는 Sonnet을 배정해 "성능과 비용의 균형"을 맞추는 것입니다. 팀장(쭌)은 판단보다 라우팅이 주 역할이라 Sonnet으로 충분합니다.

### 역할 분담의 논리

각 역할이 왜 이렇게 나뉘었는지 이해하면 나중에 팀 구성을 변형할 때 기준이 됩니다.

| 역할 | 핵심 역량 | 모델 선택 이유 |
|------|-----------|----------------|
| 팀장(쭌) | 지시 파싱, 작업 분배 | 빠른 라우팅 → Sonnet |
| 아키텍트(민준) | 트레이드오프 판단, 설계 문서 | 깊은 추론 필요 → Opus |
| 리서쳐(지훈) | 정보 수집, 요약 | 검색·요약은 Sonnet 충분 |
| 디자이너(수아) | UI 구조·흐름 설계 | 창의·경험 설계 → Sonnet |
| 개발자(서연) | 코드 구현, 테스트 | 실행 중심 → Sonnet |
| 리뷰어(태양) | 코드 검토, 품질 체크 | 패턴 인식 → Sonnet |

<hr>

## 레이아웃 구성

main-vertical 레이아웃으로 팀장(Pane 0)이 왼쪽 넓은 공간을 차지하고, 팀원 5명(Pane 1~5)이 오른쪽에 세로로 배열됩니다.

| Pane | 이름 | 역할 | 비고 |
|------|------|------|------|
| 0 | 쭌 | 팀장 | 왼쪽 메인, 너비 158 |
| 1 | 민준 | 아키텍트 | 오른쪽 상단 |
| 2 | 지훈 | 리서쳐 | |
| 3 | 수아 | UI/UX 디자이너 | |
| 4 | 서연 | 개발자 | |
| 5 | 태양 | QA·리뷰어 | 오른쪽 하단 |

`tmux list-panes -t team`을 실행하면 위 표의 여섯 칸이 `0:`, `1:`…처럼 번호와 함께 한 줄씩 찍혀 나옵니다. 화면상 위치(좌·우, 위·아래)와 무관하게 **번호는 만들어진 순서대로 0번부터** 매겨지므로, 어떤 명령을 어느 파인에 보낼지는 이 번호로 지목합니다.

> 💡 **파인 번호를 빠르게 확인하는 방법:** TMUX 내부에서 `Ctrl+B q`를 누르면 각 파인에 번호가 잠깐 표시됩니다. 이 숫자를 누르면 해당 파인으로 이동합니다. 번호가 눈에 익을 때까지 처음 며칠은 이 단축키를 자주 쓰게 됩니다.

<hr>

## 레이아웃 구성 스크립트

```bash
#!/bin/bash
SESSION="team"

# 1. 세션 생성 (백그라운드)
TERM_WIDTH=$(tput cols 2>/dev/null || echo 317)
TERM_HEIGHT=$(tput lines 2>/dev/null || echo 85)
tmux new-session -d -s "$SESSION" -x "$TERM_WIDTH" -y "$TERM_HEIGHT"

# 2. 파인 5개 분할 (좌우, even-horizontal 먼저 적용)
tmux split-window -t "$SESSION:0.0" -h
tmux split-window -t "$SESSION:0.1" -h
tmux split-window -t "$SESSION:0.2" -h
tmux split-window -t "$SESSION:0.3" -h
tmux split-window -t "$SESSION:0.4" -h

# 3. 균등 배치 후 main-vertical로 전환
tmux select-layout -t "$SESSION:0" even-horizontal
tmux select-layout -t "$SESSION:0" main-vertical
tmux set-option -t "$SESSION" main-pane-width 158

# 4. 파인 제목 표시
tmux set-option -t "$SESSION" pane-border-status top
tmux set-option -t "$SESSION" pane-border-format " #{pane_title} "
tmux set-option -t "$SESSION" allow-rename off

# 5. 각 파인에 이름 설정
tmux select-pane -t "$SESSION:0.0" -T "쭌"
tmux select-pane -t "$SESSION:0.1" -T "민준 아키텍트"
tmux select-pane -t "$SESSION:0.2" -T "지훈 리서쳐"
tmux select-pane -t "$SESSION:0.3" -T "수아 UI/UX디자이너"
tmux select-pane -t "$SESSION:0.4" -T "서연 개발자"
tmux select-pane -t "$SESSION:0.5" -T "태양 QA·리뷰어"

echo "✅ 레이아웃 구성 완료"
```

스크립트가 하는 일을 순서로 풀면 다섯 단계입니다.

1. **세션 생성** — 백그라운드(`-d`)로 팀 세션을 만든다. 터미널 실제 크기를 먼저 읽고, 실패하면 기본값(317×85)을 쓴다
2. **파인 분할** — Pane 0에서 시작해 오른쪽으로 5번 분할해 6칸을 만든다
3. **레이아웃 정렬** — `even-horizontal`로 먼저 균등 배분한 뒤 `main-vertical`로 전환해 왼쪽 팀장 칸을 넓힌다. 두 단계로 나누는 이유는 `main-vertical` 직접 적용 시 칸 배열이 불규칙해질 수 있기 때문이다
4. **제목 표시** — 파인 위쪽 테두리에 제목줄을 켠다
5. **이름 붙이기** — 각 파인에 담당자 이름을 설정한다

> 💡 **`allow-rename off`란?** TMUX는 기본적으로 파인에서 실행 중인 프로그램 이름으로 파인 제목을 자동 변경합니다. 예를 들어 `claude`가 실행되면 제목이 "claude"로 바뀌어 방금 붙인 이름이 사라집니다. `allow-rename off`로 자동 변경을 막아 항상 담당자 이름이 유지되게 합니다.

<hr>

## 레이아웃 설계 원칙

### 파인 크기 배분

팀장(Pane 0)은 지시를 받고 팀에 전달하는 주 통신 창구이므로 화면을 넓게 사용합니다. `main-pane-width 158`은 전체 화면(약 317 컬럼)의 절반입니다.

```bash
# 파인 너비 조정
tmux set-option -t team main-pane-width 158

# 더 넓게 (팀장 중심)
tmux set-option -t team main-pane-width 200
```

> 💡 **너비를 바꾸고 싶을 때:** 화면이 좁다면 `main-pane-width`를 줄이고, 팀원 파인이 너무 좁아 내용이 잘린다면 세션 전체 너비(`-x` 값)를 늘리는 것이 근본적인 해결책입니다.

### 균등 배분 레이아웃

팀원 간 역할이 비슷하고 모든 파인을 동등하게 모니터링하려면 `even-horizontal`을 사용합니다.

```bash
tmux select-layout -t team:0 even-horizontal
```

두 레이아웃의 쓰임새를 정리하면 이렇습니다.

| 레이아웃 | 구조 | 적합한 상황 |
|----------|------|------------|
| `main-vertical` | 왼쪽 1칸 크게 + 나머지 세로 배열 | 팀장 중심 지휘·지시 흐름 |
| `even-horizontal` | 모든 칸 균등 좌우 분할 | 팀원 전체 모니터링·감시 |

**지휘 중심이면 main-vertical, 균등 감시면 even-horizontal**입니다.

<hr>

## 레이아웃 저장 및 복원

TMUX는 기본적으로 레이아웃을 저장하지 않습니다. 세션을 종료하면 레이아웃이 사라집니다. 셋업 스크립트를 사용해 언제든지 동일한 레이아웃을 재현합니다.

```bash
# 현재 레이아웃 값 확인 (저장용)
tmux list-windows -t team -F "#{window_layout}"

# 출력 예시:
# main-vertical,317x85,158,0[317x16,158,0,0,317x16,158,17,1,...]
```

이 값을 저장해두면 나중에 파인 크기까지 정확하게 복원할 수 있습니다.

```bash
# 저장된 레이아웃 값으로 복원
SAVED_LAYOUT="main-vertical,317x85,158,0[...]"
tmux select-layout -t team:0 "$SAVED_LAYOUT"
```

> 💡 **현실적인 복원 방법:** 레이아웃 문자열이 길고 파인 위치가 조금 달라져도 무방하다면, 셋업 스크립트를 다시 실행하는 것이 가장 간단합니다. 정확한 픽셀 단위 복원이 필요한 경우에만 위의 레이아웃 값을 저장해 사용하세요.

<hr>

## 요약

레이아웃 설계의 핵심은 **역할에 맞는 공간 배분**과 **팀 전체를 한눈에 볼 수 있는 배치**입니다. 다음 챕터에서는 이 레이아웃 위에 Claude Code를 자동으로 실행하는 방법을 설명합니다.
