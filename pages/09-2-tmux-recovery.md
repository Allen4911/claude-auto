## 09-2. TMUX 세션 복구 및 재연결

## 이 절에서 배우는 것

TMUX 기반 팀 환경을 운용하다 보면 세션이 끊기거나, 파인이 사라지거나, 레이아웃이 깨지는 상황이 발생한다. 이 절에서는 상황별 원인을 파악하고 팀 세션을 빠르게 복구하는 단계별 방법을 다룬다.

> 💡 **TMUX 세션이 SSH와 독립적인 이유** TMUX는 "터미널 멀티플렉서"로, 서버 위에서 독자적으로 실행됩니다. SSH는 사용자 PC와 서버를 연결하는 통로일 뿐입니다. SSH 연결이 끊겨도 서버 위의 TMUX는 계속 살아있으므로, 재접속하면 그대로 이어서 작업할 수 있습니다.

> 💡 **열차 비유** SSH는 탑승객(사용자)과 열차(서버)를 잇는 출입문입니다. TMUX는 열차 안에서 독립적으로 돌아가는 엔진입니다. 출입문이 닫혀도(SSH 끊김) 엔진은 계속 돌고 있으므로, 다시 탑승하면(SSH 재접속) 그대로 여행을 이어갈 수 있습니다.

<hr>

## 흔한 문제 상황

| 상황 | 원인 | 위험도 |
|------|------|--------|
| SSH 연결 끊김 | 네트워크 불안정 | 낮음 — 세션은 살아있음 |
| 특정 파인의 Claude 종료 | OOM, 수동 종료 | 중간 — 해당 파인만 복구 |
| TMUX 서버 크래시 | 시스템 리소스 부족 | 높음 — 전체 재구성 필요 |
| 시스템 재부팅 | 업데이트, 정전 | 높음 — 전체 재구성 필요 |

> 💡 **OOM(Out of Memory)이란?** 프로그램이 필요한 메모리보다 시스템 여유 메모리가 부족할 때, 운영체제가 강제로 프로세스를 종료하는 현상입니다. Claude Code는 6개가 동시에 실행되면 상당한 메모리를 소모하므로, 메모리가 부족한 환경에서 갑작스럽게 종료될 수 있습니다.

위험도별로 복구 난이도가 다르다. **낮음**은 재연결만 하면 되고, **중간**은 해당 파인만 재시작하면 되며, **높음**은 셋업 스크립트로 전체를 처음부터 다시 구성해야 한다.

![TMUX 복구 상황 분류 트리 — 문제 발생에서 SSH 연결 끊김(낮은 위험)/Claude만 종료(중간 위험)/TMUX 서버 크래시(높은 위험)/시스템 재부팅(높은 위험) 4가지로 분기, 각 분기에 복구 명령(tmux attach·claude 재실행·setup-team.sh)](https://raw.githubusercontent.com/Allen4911/claude-auto/main/assets/09-2-tmux-recovery-situation-tree.png)

<hr>

## 상황 1: SSH 연결이 끊어졌을 때

가장 흔하고 가장 안전한 상황이다. TMUX 세션은 SSH 연결과 독립적으로 유지된다.

**1단계: SSH 재접속 후 세션 목록 확인**
```bash
tmux ls
# 출력: team: 1 windows (created Mon Apr 28 10:00:00 2026)
```

세션 이름(`team`)과 생성 시각이 표시되면 세션이 살아있는 것이다. 아무것도 출력되지 않으면 세션이 없는 것이므로 상황 4(전체 재구성)로 넘어간다.

**2단계: 세션에 재연결**
```bash
tmux attach -t team
```

연결만 끊어진 것이므로 모든 파인의 Claude Code는 그대로 실행 중이다. 아무런 데이터 손실 없이 그대로 이어서 작업할 수 있다.

위 두 단계처럼 SSH는 끊겨도 서버의 TMUX 세션은 살아있으므로, `tmux attach`로 재연결하면 데이터 손실 없이 그대로 이어진다.

<hr>

**자동 재연결 alias 설정 (선택 사항)**

SSH 재접속 후 바로 세션에 붙는 alias를 `~/.bashrc`에 추가하면 편리하다.

```bash
echo "alias team='tmux attach -t team || tmux new-session -s team'" >> ~/.bashrc
source ~/.bashrc
```

이후 SSH 재접속 시 `team` 한 단어로 바로 세션에 복귀할 수 있다.

<hr>

## 상황 2: 특정 파인의 Claude가 종료되었을 때

한 팀원의 Claude Code가 종료되었지만 파인 자체는 살아있는 경우이다.

### 진단

파인에서 Claude Code가 종료되면 일반 쉘 프롬프트(`$`)가 표시된다.

```bash
# 각 파인 존재 여부 및 현재 실행 프로세스 확인
for i in 0 1 2 3 4 5; do
  CMD=$(tmux list-panes -t team:0 -F "#{pane_index} #{pane_current_command}" 2>/dev/null \
    | awk -v idx="$i" '$1==idx {print $2}')
  if [ -z "$CMD" ]; then
    echo "Pane $i: 파인 없음"
  elif [ "$CMD" = "claude" ] || [ "$CMD" = "node" ]; then
    echo "Pane $i: Claude 실행 중 ($CMD)"
  else
    echo "Pane $i: Claude 미실행 (현재: $CMD)"
  fi
done
```

파인 화면을 직접 확인하는 방법도 있다:
```bash
# Pane 3 화면 내용 마지막 5줄 확인
tmux capture-pane -t team:0.3 -p | tail -5
```

출력에 `$` 프롬프트가 보이면 Claude Code가 종료된 상태, `❯` 또는 `claude>` 프롬프트가 보이면 정상 실행 중이다.

> 💡 **왜 Claude가 갑자기 종료되나?** 세 가지가 주된 원인입니다. ①메모리 부족(OOM)으로 OS가 강제 종료, ②네트워크 오류로 API 연결이 끊겨 프로세스 자체 종료, ③팀원이 실수로 `/exit` 명령을 실행. OOM은 메모리 여유를 확보하거나 동시 파인 수를 줄여 예방할 수 있습니다.

### 복구

**1단계: 해당 파인에서 Claude Code 재실행**
```bash
tmux send-keys -t team:0.3 "claude" Enter
```

**2단계: 이전 세션 복구 (히스토리가 있는 경우)**

Claude Code는 이전 대화 히스토리를 로컬에 저장하므로, 재실행 후 `/resume` 명령으로 이전 세션을 이어갈 수 있다.

```bash
tmux send-keys -t team:0.3 "/resume" Enter
```

> 💡 **/resume의 동작 원리** Claude Code는 모든 대화를 `~/.claude/projects/` 아래에 JSON 파일로 저장합니다. `/resume`을 실행하면 가장 최근 세션 파일을 읽어 대화 맥락을 복원합니다. 단, 복원 후에는 이전 맥락이 입력 토큰으로 그대로 포함되므로, 오래된 세션일수록 토큰 비용이 높을 수 있습니다.

즉 진단 반복문으로 비활성 파인을 찾은 뒤 해당 파인에서 claude를 재실행(필요 시 `/resume`)하면 복구된다.

<hr>

## 상황 3: 파인 자체가 사라졌을 때

TMUX 파인이 닫히면 복구할 수 없다. 새 파인을 생성하고 재설정해야 한다.

### 현재 파인 구조 확인

```bash
tmux list-panes -t team:0 -F "#{pane_index}: #{pane_title} (#{pane_pid})"
# 출력 예시:
# 0: 쭌 (1234)
# 1: 민준 PM·아키텍트 (1235)
# 2: 지훈 리서쳐 (1236)
# 4: 서연 개발자 (1238)
# 5: 태양 리뷰어 (1239)
# → 파인 3(수아)이 없음
```

인덱스 번호가 0, 1, 2, 4, 5로 건너뛰면 3번 파인이 사라진 것이다.

### 파인 재생성 절차

**1단계: 기존 파인 옆에 새 파인 분할**
```bash
tmux split-window -v -t team:0.2
```

> 💡 **`split-window -v`란?** TMUX 파인을 **수직으로** 분할하는 옵션입니다. `-v`는 "vertical split"이 아닌 "horizontal line을 그어 위·아래로 분리"를 의미합니다. 직관과 반대처럼 느껴지지만, TMUX 용어에서 `-v`는 위아래 분할, `-h`는 좌우 분할입니다.

**2단계: 새 파인에 타이틀 설정**
```bash
tmux select-pane -t team:0.3 -T "디자이너 수아"
```

**3단계: Claude Code 실행**
```bash
tmux send-keys -t team:0.3 "claude" Enter
```

**4단계: 레이아웃 재정렬**
```bash
tmux select-layout -t team:0 main-vertical
```

파인을 새로 나누고 타이틀을 붙인 뒤 claude를 띄우고 레이아웃을 정리하면 된다.

<hr>

**파인 2개 이상 사라진 경우**

파인이 2개 이상 사라지면 레이아웃이 복잡하게 엉킬 수 있다. 이 경우는 아래 상황 4(전체 재구성)의 셋업 스크립트를 사용하는 것이 더 빠르다.

```bash
# 현재 파인 수 빠른 확인
tmux list-panes -t team:0 | wc -l
# 6 미만이면 전체 재구성 고려
```

<hr>

## 상황 4: TMUX 세션 전체가 소실되었을 때

시스템 재부팅이나 TMUX 서버 크래시로 세션이 완전히 사라진 경우이다. 셋업 스크립트로 전체를 재구성한다.

**1단계: 세션 존재 여부 확인**
```bash
tmux ls 2>/dev/null || echo "세션 없음"
```

출력이 "세션 없음"이거나 빈 줄이면 전체 재구성이 필요하다.

**2단계: 셋업 스크립트로 전체 재구성**
```bash
bash /path/to/setup-team.sh  # 본인 프로젝트의 setup 스크립트 경로로 수정
```

> 💡 **setup-team.sh가 하는 일** 이 스크립트는 ①새 TMUX 세션 생성 ②6개 파인으로 분할 ③각 파인에 역할 이름(타이틀) 설정 ④각 파인에서 올바른 모델로 Claude Code 실행 ⑤레이아웃·너비 조정을 한 번에 수행합니다. 수동으로 하면 20분이 걸리는 작업을 2~3분 안에 완료합니다.

**3단계: 새로 생성된 세션에 접속**
```bash
tmux attach -t team
```

셋업 스크립트는 TMUX 세션 생성, 파인 분할, 타이틀 설정, Claude Code 실행을 자동으로 수행한다.

tmux ls로 소실을 확인하고 setup-team.sh를 돌린 뒤 세션에 접속하면 된다. 스크립트가 세션·파인·역할을 한 번에 재구성한다.

<hr>

**재구성 완료 확인**

```bash
# 세션 생성 확인
tmux ls

# 6개 파인 모두 생성 확인
tmux list-panes -t team:0 | wc -l

# 각 파인 타이틀 확인
tmux list-panes -t team:0 -F "#{pane_index}: #{pane_title}"
```

<hr>

## 자동 복구 스크립트

수동 복구가 번거롭다면 상태를 점검하고 자동 복구하는 스크립트를 작성할 수 있다.

```bash
#!/bin/bash
# check-team.sh — 팀 세션 상태 점검 및 복구

SESSION="team"
EXPECTED_PANES=6
TITLES=("쭌" "민준 PM·아키텍트" "지훈 리서쳐" "디자이너 수아" "서연 개발자" "태양 리뷰어")

# 1. 세션 존재 확인
if ! tmux has-session -t $SESSION 2>/dev/null; then
  echo "세션이 없습니다. 재구성합니다..."
  bash /path/to/setup-team.sh  # 본인 프로젝트의 setup 스크립트 경로로 수정
  exit 0
fi

# 2. 파인 수 확인
CURRENT_PANES=$(tmux list-panes -t $SESSION:0 | wc -l)
if [ "$CURRENT_PANES" -ne "$EXPECTED_PANES" ]; then
  echo "파인 수 불일치: $CURRENT_PANES / $EXPECTED_PANES"
  echo "전체 재구성을 권장합니다."
  exit 1
fi

# 3. 각 파인에서 Claude 실행 상태 확인
for i in 0 1 2 3 4 5; do
  PANE_CMD=$(tmux list-panes -t $SESSION:0 -F "#{pane_index} #{pane_current_command}" \
    | grep "^$i " | awk '{print $2}')
  
  if [ "$PANE_CMD" != "claude" ] && [ "$PANE_CMD" != "node" ]; then
    echo "Pane $i (${TITLES[$i]}): Claude 미실행 — 재시작합니다"
    tmux send-keys -t $SESSION:0.$i "claude" Enter
  else
    echo "Pane $i (${TITLES[$i]}): 정상"
  fi
done

echo "점검 완료"
```

위 스크립트는 ①세션 존재 → ②파인 수 → ③각 파인의 Claude 실행 상태를 차례로 점검하고, 빠진 부분만 자동으로 복구한다.

<hr>

**스크립트 설치 및 주기적 실행**

```bash
# 스크립트 저장 및 실행 권한
chmod +x ~/check-team.sh

# 수동 실행
~/check-team.sh
```

이 스크립트를 cron에 등록하면 주기적으로 팀 상태를 점검할 수 있다.

```bash
# 매 10분마다 팀 상태 점검
crontab -e
# 추가:
# */10 * * * * /home/user/check-team.sh >> /tmp/team-check.log 2>&1
```

> 💡 **cron이란?** 리눅스의 예약 작업 시스템입니다. `*/10 * * * *`는 "매 10분마다 실행"을 의미합니다. `crontab -e`로 편집기를 열어 위 줄을 추가하면, 10분마다 check-team.sh가 자동으로 실행되어 팀 상태를 점검하고 이상이 있으면 자동 복구합니다.

**로그 확인:**
```bash
tail -f /tmp/team-check.log
```

<hr>

## 레이아웃 복구

파인 수는 맞지만 레이아웃이 깨진 경우이다. 파인이 겹치거나 크기가 이상해진 경우에 적용한다.

**main-vertical 레이아웃 재적용:**
```bash
tmux select-layout -t team:0 main-vertical
```

> 💡 **main-vertical 레이아웃이란?** 왼쪽에 큰 메인 파인 하나(Pane 0), 오른쪽에 나머지 파인들이 세로로 쌓이는 배치입니다. 팀 환경에서 Pane 0(쭌)을 넓게 두고 오른쪽에 팀원들이 줄지어 있는 구조입니다.

**Pane 0 너비를 158로 고정:**
```bash
tmux resize-pane -t team:0.0 -x 158
```

**파인 테두리에 타이틀 표시 재설정:**
```bash
tmux set-option -t team pane-border-status top
```

위 명령들로 main-vertical 레이아웃을 다시 적용하고 Pane 0 너비·타이틀 표시를 복원하면 깨진 배치가 정상으로 돌아온다.

<hr>

**레이아웃 복구 한 번에 실행:**

```bash
# 레이아웃 복구 원스톱
tmux select-layout -t team:0 main-vertical && \
tmux resize-pane -t team:0.0 -x 158 && \
tmux set-option -t team pane-border-status top && \
echo "레이아웃 복구 완료"
```

<hr>

## 예방 조치

### TMUX 자동 저장 플러그인

tmux-resurrect 플러그인을 사용하면 세션 상태를 파일로 저장하고 복원할 수 있다.

**설치:**
```bash
git clone https://github.com/tmux-plugins/tmux-resurrect \
    ~/.tmux/plugins/tmux-resurrect
```

**~/.tmux.conf에 추가:**
```bash
# ~/.tmux.conf
run-shell ~/.tmux/plugins/tmux-resurrect/resurrect.tmux
```

설정 적용:
```bash
tmux source-file ~/.tmux.conf
```

> 💡 **~/.tmux.conf란?** TMUX의 설정 파일입니다. 이 파일에 옵션을 추가하면 TMUX를 시작할 때마다 자동으로 적용됩니다. `run-shell` 명령으로 플러그인을 로드합니다.

| 키 바인딩 | 동작 |
|-----------|------|
| `Ctrl-b` + `Ctrl-s` | 현재 세션 상태 저장 |
| `Ctrl-b` + `Ctrl-r` | 마지막 저장된 상태 복원 |

> 💡 **tmux-resurrect의 한계** 이 플러그인은 TMUX 세션 구조(파인 레이아웃, 작업 디렉터리)는 저장하지만, 각 파인에서 실행 중인 프로세스(Claude Code)를 재시작해 주지는 않습니다. 복원 후 각 파인에서 `claude` 명령을 수동으로 실행해야 합니다. 전체 자동화는 setup-team.sh와 함께 사용하세요.

<hr>

### 시스템 리소스 모니터링

Claude Code는 메모리를 꽤 먹는다. 여섯 개를 한꺼번에 돌리면 부담이 만만치 않다.

**Claude Code 프로세스별 메모리 사용량 확인:**
```bash
ps aux | grep claude | grep -v grep | awk '{print $6/1024 "MB", $0}' | sort -rn
```

출력 예시:
```
512MB  user  12453 ... node /usr/local/bin/claude
489MB  user  12454 ... node /usr/local/bin/claude
...
```

각 Claude 인스턴스가 500MB 안팎을 사용한다면, 6개를 동시 실행하면 약 3GB가 필요하다. 시스템 총 RAM이 8GB 이하라면 OOM 위험이 있다.

메모리가 모자라 Claude가 OOM으로 죽는 걸 막으려면 RAM을 충분히 확보하거나(16GB 이상 권장), 동시 실행 파인 수를 줄이는 것을 고려한다.

**현재 메모리 여유량 확인:**
```bash
free -h
# 출력 예시:
#               total  used  free  available
# Mem:           16Gi  9Gi   2Gi   6Gi
# available이 전체 Claude 프로세스 합산보다 많아야 안전
```

정리하면 예방은 두 갈래다. ①앞서 설치한 tmux-resurrect 플러그인으로 세션 상태를 저장·복원해 두고(`Ctrl-b`+`Ctrl-s`로 저장, `Ctrl-b`+`Ctrl-r`로 복원), ②위 `ps aux` 명령으로 Claude 프로세스의 메모리 사용량을 주기적으로 점검해 OOM 종료를 미리 막는다.

<hr>

## 요약

TMUX 세션 복구의 핵심은 **단계별 진단**이다. SSH가 끊기면 다시 붙고, Claude만 죽으면 재실행하고, 파인이 사라지면 새로 만들고, 세션이 통째 날아가면 셋업 스크립트로 다시 짠다. `check-team.sh` 같은 자동 점검 스크립트와 tmux-resurrect 플러그인을 활용하면 복구 시간이 확 줄어든다. OOM을 방지하려면 `free -h`와 `ps aux`로 메모리 여유량을 주기적으로 확인하는 습관이 중요하다.
