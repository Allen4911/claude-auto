# 2-4. TMUX 설치 및 기본 명령어

TMUX(Terminal Multiplexer)는 하나의 터미널 창 안에서 여러 개의 터미널을 동시에 실행하고 관리할 수 있는 강력한 도구입니다. Claude 멀티에이전트 환경에서는 TMUX의 파인(Pane) 기능을 활용해 6명의 에이전트를 동시에 운영합니다.

---

## 설치

```bash
sudo apt install -y tmux

# 설치 확인
tmux -V
```

출력 예시:
```
tmux 3.4
```

```bash
$ tmux -V

tmux 3.4
```

---

## 핵심 개념

TMUX는 세 가지 계층 구조로 구성됩니다.

```
세션(Session)
  └── 윈도우(Window)
        └── 파인(Pane)
```

- **세션**: TMUX의 최상위 단위. 여러 윈도우를 포함. 터미널을 닫아도 세션은 백그라운드에서 유지됩니다.
- **윈도우**: 세션 내의 탭. 하나의 전체 화면을 차지합니다.
- **파인**: 윈도우를 분할한 공간. 각 파인은 독립적인 쉘을 실행합니다.

---

## 기본 명령어

### 세션 관리

```bash
# 새 세션 생성
tmux new-session -s team

# 세션 목록 확인
tmux ls

# 세션 접속 (attach)
tmux attach -t team
tmux a -t team        # 단축 형식

# 세션 분리 (detach, 세션은 백그라운드 유지)
# 단축키: Ctrl+B, D

# 세션 종료
tmux kill-session -t team
```

### 윈도우 관리

TMUX 세션 안에서 사용하는 단축키입니다. 모든 단축키는 `Ctrl+B`를 먼저 누른 후 키를 입력합니다.

| 단축키 | 동작 |
|--------|------|
| `Ctrl+B c` | 새 윈도우 생성 |
| `Ctrl+B n` | 다음 윈도우로 이동 |
| `Ctrl+B p` | 이전 윈도우로 이동 |
| `Ctrl+B 0~9` | 번호로 윈도우 이동 |
| `Ctrl+B &` | 현재 윈도우 종료 |

### 파인 관리

| 단축키 | 동작 |
|--------|------|
| `Ctrl+B %` | 세로로 분할 (좌우) |
| `Ctrl+B "` | 가로로 분할 (상하) |
| `Ctrl+B 방향키` | 파인 간 이동 |
| `Ctrl+B x` | 현재 파인 종료 |
| `Ctrl+B z` | 현재 파인 전체 화면 토글 |
| `Ctrl+B Ctrl+방향키` | 파인 크기 조절 |

---

## 명령으로 파인 제어하기

스크립트에서 특정 파인에 명령을 전송하는 방법입니다.

```bash
# 특정 파인에 텍스트 전송 (Enter 없이)
tmux send-keys -t team:0.1 "echo hello"

# 특정 파인에 명령 실행 (Enter 포함)
tmux send-keys -t team:0.1 "echo hello" Enter

# 파인 내용 캡처 (현재 화면 텍스트 읽기)
tmux capture-pane -t team:0.1 -p
```

형식: `세션이름:윈도우번호.파인번호`

---

## 레이아웃 설정

TMUX는 파인 배치를 자동으로 정렬하는 레이아웃 기능을 제공합니다.

```bash
# 레이아웃 적용
tmux select-layout -t team:0 even-horizontal   # 좌우 균등
tmux select-layout -t team:0 even-vertical     # 상하 균등
tmux select-layout -t team:0 main-vertical     # 왼쪽 크게, 나머지 세로 배열
tmux select-layout -t team:0 main-horizontal   # 위 크게, 나머지 가로 배열
tmux select-layout -t team:0 tiled             # 격자 배열
```

---

## 파인 제목 설정

각 파인에 이름(제목)을 붙여 누가 어떤 파인인지 한눈에 알 수 있게 합니다.

```bash
# 파인 상단 제목 표시 활성화
tmux set-option -t team pane-border-status top
tmux set-option -t team pane-border-format " #{pane_title} "

# 파인 이름 설정
tmux select-pane -t team:0.0 -T "쭌 (팀장)"
tmux select-pane -t team:0.1 -T "민준 아키텍트"
```

---

## 실습: 간단한 멀티파인 세션

```bash
# 1. 새 세션 생성 (백그라운드)
tmux new-session -d -s practice

# 2. 파인 분할 (좌우 2개)
tmux split-window -t practice:0.0 -h

# 3. 각 파인에 명령 실행
tmux send-keys -t practice:0.0 "echo 'Pane 0 작동 중'" Enter
tmux send-keys -t practice:0.1 "echo 'Pane 1 작동 중'" Enter

# 4. 세션 접속하여 확인
tmux attach -t practice
```

---

## 요약

TMUX의 핵심 흐름은 **세션 생성 → 파인 분할 → 각 파인에 명령 전송**입니다. 다음 챕터에서는 이 구조를 활용해 6명의 Claude 에이전트가 동시에 동작하는 팀 환경을 구성합니다.
