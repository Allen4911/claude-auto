## 09-1. Remote-Control 인증 오류 해결

## 이 절에서 배우는 것

Remote Control을 사용하다 보면 인증 관련 오류를 마주칠 때가 있다. 대부분의 문제는 토큰 만료, 계정 불일치, 네트워크 설정에서 발생한다. 이 절에서는 자주 발생하는 인증 오류와 해결 방법을 증상별로 단계적으로 정리한다.

> 💡 **인증 토큰(Auth Token)이란?** 비밀번호를 매번 입력하는 대신, 로그인 후 발급받은 "임시 열쇠"입니다. 이 열쇠로 서버에 접속하는데, 일정 기간이 지나면 만료되어 새 열쇠를 발급받아야 합니다. 토큰이 만료되면 갑자기 연결이 거부되는 것처럼 보일 수 있습니다.

![Remote Control 인증 오류 진단 트리 — Session not found / Authentication failed / Connection timeout / Permission denied 4가지 분기 결정 트리](https://raw.githubusercontent.com/Allen4911/claude-auto/main/assets/09-1-auth-troubleshooting-diagnosis-tree.png)

<hr>

## 왜 인증 오류가 갑자기 생기는가?

처음에는 잘 동작하던 Remote Control이 어느 날 갑자기 연결을 거부하기도 한다. 대부분은 사용자 실수가 아니라 **시간이 지나 저절로 만료**된 것이다.

> 💡 **지하철 1일권 비유** 인증 토큰은 지하철 1일권과 비슷합니다. 처음 발급할 때는 아무 문제 없이 게이트를 통과하지만, 유효 기간이 지나면 동일한 카드라도 "사용 불가" 오류가 납니다. 새 1일권을 발급받아야 하듯, 토큰도 재발급(`auth login`)이 필요합니다.

원인 세 가지만 알아 두면 진단이 빨라진다:

| 원인 | 비유 | 해결 방향 |
|------|------|---------|
| 토큰 만료 | 지하철 1일권 기간 초과 | `auth login`으로 재발급 |
| 계정 불일치 | 다른 열쇠로 문 열기 | 서버와 모바일 계정 통일 |
| 네트워크 차단 | 전화선 끊김 | 방화벽·DNS 점검 |

<hr>

## 증상별 진단 가이드

### 1. "Session not found" — 세션을 찾을 수 없음

모바일에서 세션 목록이 비어있거나 연결 시 "Session not found" 오류가 표시된다.

**원인과 해결:**

| 원인                    | 확인 방법                      | 해결                          |
| --------------------- | -------------------------- | --------------------------- |
| Claude Code가 실행 중이 아님 | `pgrep -f claude`          | Claude Code 재실행             |
| 서버 모드가 아님             | 터미널에서 Remote Control 상태 확인 | `--remote-control` 플래그로 재시작 |
| 다른 Anthropic 계정       | 모바일과 서버의 계정 비교             | 동일 계정으로 로그인                 |
| 세션 이름 불일치             | `claude --resume`          | 올바른 세션 이름으로 접속              |

**확인 절차:**

**1단계: Claude Code 실행 여부 확인**
```bash
pgrep -f claude
# 숫자(프로세스 ID)가 출력되면 실행 중, 아무것도 안 나오면 실행 중이 아님
```

출력 예시:
```
12453
12891
```
두 개의 숫자가 나온다면, 프로세스가 2개 실행 중임을 의미한다. 아무것도 출력되지 않으면 Claude Code가 완전히 종료된 상태다.

**2단계: 서버 모드로 재시작**
```bash
claude --remote-control
```

> 💡 **`pgrep -f`란?** 현재 실행 중인 프로세스 중에서 이름에 특정 단어가 포함된 것을 찾는 명령어입니다. `pgrep -f claude`는 "claude"라는 단어가 포함된 프로세스 번호를 출력합니다. 번호가 나오면 실행 중, 아무것도 나오지 않으면 종료된 것입니다.

> 💡 **`--remote-control` 플래그란?** Claude Code를 모바일 앱이나 외부 클라이언트가 접속할 수 있는 "서버 모드"로 시작하는 옵션입니다. 이 플래그 없이 실행하면 로컬 터미널 전용 모드로 동작하여 Remote Control에서 세션을 찾을 수 없습니다.

**3단계: 계정 일치 확인**
```bash
claude auth status
# 출력 예시:
# Logged in as: user@example.com
```
모바일 앱에서 로그인된 계정과 이메일이 동일한지 확인한다. 다르면 어느 한쪽에서 로그아웃 후 같은 계정으로 재로그인한다.

<hr>

### 2. "Authentication failed" — 인증 실패

연결 시도 시 인증 실패 오류가 발생한다. 가장 흔한 원인은 토큰 만료다.

**해결 과정:**

**1단계: 현재 로그인된 계정 확인**
```bash
claude auth status
```

출력 예시:
```
Logged in as: user@example.com
Token expires: 2026-07-01T00:00:00Z
```
`Token expires` 날짜가 오늘보다 이전이라면 만료된 것이다.

**2단계: 인증 토큰이 만료되었으면 재인증**
```bash
claude auth login
```

**3단계: 브라우저 인증 완료**

브라우저가 자동으로 열리며 Anthropic 계정으로 로그인한다. 로그인 후 터미널에 표시되는 인증 코드를 입력하면 새 토큰이 발급된다.

정리하면 계정 확인, 재인증, 브라우저 로그인 순서다.

> 💡 **왜 브라우저가 열리는가?** Claude Code는 OAuth 2.0 방식으로 인증합니다. "구글로 로그인" 버튼처럼, Anthropic 서버에서 신원을 확인한 뒤 터미널에 임시 코드를 전달하는 방식입니다. 이 방식 덕분에 비밀번호를 터미널에 직접 입력할 필요 없이 안전하게 인증할 수 있습니다.

<hr>

### 3. "Connection timeout" — 연결 시간 초과

모바일에서 세션을 선택했지만 연결이 되지 않고 타임아웃이 발생한다. 인증 자체보다 **네트워크 경로** 문제인 경우가 많다.

**원인과 해결:**

**1단계: 네트워크 연결 확인**
```bash
ping -c 3 api.anthropic.com
```

출력 예시 (정상):
```
PING api.anthropic.com (104.18.x.x): 56 data bytes
64 bytes from 104.18.x.x: icmp_seq=0 ttl=60 time=12.4 ms
```
타임아웃이 계속 나오면 DNS 또는 방화벽 문제다.

**2단계: DNS 확인**
```bash
nslookup api.anthropic.com
```

출력 예시 (정상):
```
Server: 8.8.8.8
Address: 8.8.8.8#53
Non-authoritative answer:
Name: api.anthropic.com
Address: 104.18.x.x
```
`Address`가 출력되면 DNS는 정상이다. 아무것도 나오지 않으면 DNS 서버에 문제가 있다.

**3단계: 방화벽이 HTTPS 아웃바운드를 차단하는 경우 허용**
```bash
sudo ufw allow out 443/tcp
```

WSL2 환경에서는 Windows 방화벽이 아웃바운드 연결을 막기도 한다. Windows Defender 방화벽 설정에서 WSL2 관련 규칙을 확인한다.

> 💡 **포트 443이란?** 인터넷에서 HTTPS(암호화된 웹 통신)가 사용하는 문 번호입니다. `ufw allow out 443/tcp`는 "이 포트를 통한 외부 연결을 허용하라"는 뜻입니다. Claude Code는 Anthropic 서버와 HTTPS로 통신하므로, 이 포트가 막히면 연결 자체가 불가능합니다.

**4단계: WSL2 전용 — Windows IP 경유 확인**

WSL2에서는 Windows 호스트를 경유해 외부와 통신하므로, Windows 방화벽이 추가 차단을 할 수 있다.

```bash
# WSL2에서 Windows 호스트 IP 확인
cat /etc/resolv.conf | grep nameserver
# 예시: nameserver 172.23.64.1

# 해당 IP로 ping 확인
ping -c 2 172.23.64.1
```

<hr>

### 4. "Permission denied" — 권한 거부

세션에는 연결되지만 도구 실행 시 "Permission denied"가 반복된다. 이는 인증 자체가 아니라 **Claude Code의 권한 설정** 문제다.

**1단계: 사용자 설정 파일의 deny 규칙 확인**
```bash
cat ~/.claude/settings.json | grep -A 20 "deny"
```

**2단계: 프로젝트별 설정도 확인**
```bash
cat .claude/settings.json | grep -A 20 "deny"
```

출력 예시:
```json
"deny": [
  "rm -rf *",
  "git push --force",
  "npm run *"
]
```

"npm run *" 처럼 와일드카드를 과도하게 사용하면 `npm run test` 같은 무해한 명령어도 차단될 수 있다.

**3단계: 규칙 수정**

`deny` 배열에서 지나치게 광범위한 패턴을 찾아 구체적으로 수정한다.

수정 전 — 와일드카드로 과도하게 차단하는 예:

```json
"deny": ["npm run *"]
```

수정 후 — 실제로 위험한 명령만 지정하는 예:

```json
"deny": ["npm run deploy", "npm run publish"]
```

> 💡 **settings.json의 deny 규칙이란?** Claude Code가 실행할 수 있는 명령어를 제한하는 목록입니다. 보안을 위해 위험한 명령어를 차단하는 데 유용하지만, 너무 광범위하게 설정하면 정상적인 개발 명령어까지 막힐 수 있습니다. `grep -A 20 "deny"`는 "deny" 단어 이후 20줄을 출력해 규칙을 확인합니다.

<hr>

## 인증 토큰 관리

### 토큰 만료 주기

Anthropic 인증 토큰은 일정 기간이 지나면 만료된다. 장기간 실행 중인 Claude Code 세션에서 갑자기 인증 오류가 발생한다면 토큰 만료를 의심한다.

> 💡 **토큰은 왜 만료되는가?** 영구적인 인증 열쇠를 사용하면, 해당 열쇠가 탈취되었을 때 무기한으로 악용될 수 있습니다. 일정 기간마다 갱신을 강제하면 탈취된 토큰의 유효 시간을 제한할 수 있습니다. 불편하지만 보안을 위한 설계입니다.

**인증 상태 확인:**
```bash
claude auth status
# 출력 예시:
# Logged in as: user@example.com
# Token expires: 2026-05-15T00:00:00Z
```

**토큰 갱신:**
```bash
claude auth login
```

즉 로그인 시 발급된 토큰이 만료되면 인증 오류가 나고, `auth login`으로 재발급하면 다시 정상화되는 순환 구조다.

<hr>

### 여러 계정 사용 시

팀 환경에서 여러 Anthropic 계정을 사용하는 경우 계정 전환에 주의한다.

> 💡 **계정 불일치 함정** 모바일 앱은 계정 A로 로그인되어 있고, 서버의 Claude Code는 계정 B로 실행 중이라면, 두 계정의 "채널"이 달라서 연결이 절대 이루어지지 않습니다. 두 개의 다른 라디오 주파수로 통신하려는 것과 같습니다.

**현재 계정 확인:**
```bash
claude auth status
```

**로그아웃 후 다른 계정으로 전환:**
```bash
claude auth logout
claude auth login
```

<hr>

## TMUX 팀 환경에서의 인증 문제

### 모든 파인이 동시에 인증 실패하는 경우

팀 세션의 모든 파인이 같은 계정을 사용한다면, 토큰 만료 시 전체가 동시에 실패한다.

> 💡 **파인(Pane)이란?** TMUX 화면을 여러 구역으로 나눈 각각의 창입니다. 6명 팀을 운용할 때는 화면을 6개 파인으로 분할하여 각 파인에서 Claude Code가 실행됩니다. 모든 파인이 같은 계정을 쓰므로, 토큰이 만료되면 6개 파인이 동시에 인증 오류를 냅니다.

> 💡 **도미노 인증 실패 비유** 모든 파인이 같은 계정 토큰을 공유하므로, 토큰이 만료되는 순간 도미노처럼 6개 파인이 동시에 인증 오류를 냅니다. 한 명이 재인증하면 동일 토큰 파일이 갱신되어 나머지도 자동으로 복구됩니다.

**모든 파인 일괄 재시작:**
```bash
for i in 0 1 2 3 4 5; do
  tmux send-keys -t team:0.$i "/exit" Enter
  sleep 1
  tmux send-keys -t team:0.$i "claude" Enter
done
```

위 반복문처럼 토큰이 만료되면 P0~P5 파인이 동시에 실패하므로, 모든 파인을 순차로 재시작해 한꺼번에 복구한다.

**재인증만 먼저 하는 방법 (빠른 복구):**

별도 터미널에서 재인증하면 토큰 파일이 즉시 갱신된다. 실행 중인 Claude Code는 새 토큰을 자동으로 읽으므로, 재시작 없이 복구된다.

```bash
# 새 터미널 창에서
claude auth login
# 브라우저 인증 완료 후 모든 파인이 자동 복구
```

<hr>

### 특정 파인만 인증 실패하는 경우

하나의 파인만 문제가 있다면 해당 파인의 Claude Code 프로세스를 개별적으로 재시작한다.

**문제 파인(예: Pane 3) 개별 재시작:**
```bash
tmux send-keys -t team:0.3 "/exit" Enter
sleep 2
tmux send-keys -t team:0.3 "claude" Enter
```

특정 파인만 실패하는 경우, 해당 파인에서 임의로 `claude auth logout`이 실행되었거나 프로세스가 비정상 종료된 경우가 많다. 우선 해당 파인의 상태를 화면에서 직접 확인한다.

```bash
# 파인 화면 내용 캡처로 오류 메시지 확인
tmux capture-pane -t team:0.3 -p | tail -20
```

<hr>

## 진단 명령어 모음

문제 발생 시 아래 5단계 순서로 진단하면 원인을 빠르게 찾을 수 있다.

**1단계: Claude Code 프로세스 확인**
```bash
pgrep -af claude
# 예시 출력:
# 12453 node /usr/local/bin/claude --remote-control
# 실행 중이면 PID와 실행 옵션이 출력됨
```

**2단계: 인증 상태 확인**
```bash
claude auth status
# 예시 출력:
# Logged in as: user@example.com
# Token expires: 2026-07-01T00:00:00Z
```

**3단계: 네트워크 연결 확인**
```bash
curl -s -o /dev/null -w "%{http_code}" https://api.anthropic.com/v1/messages
# 200 또는 401이면 네트워크 정상 (401은 인증만 실패)
```

> 💡 **curl 응답 코드 읽는 법** `200`은 "정상", `401`은 "인증 실패(네트워크는 됨)", `000`은 "서버에 도달 자체가 안 됨"을 의미합니다. 401이 나오면 네트워크는 정상이고 인증 토큰만 갱신하면 됩니다.

**4단계: 로그 확인**
```bash
ls -lt ~/.claude/logs/ | head -5
tail -50 ~/.claude/logs/latest.log
```

로그에서 자주 보이는 오류 패턴:
- `TokenExpiredError` → `auth login`으로 재발급
- `NetworkError: ETIMEDOUT` → 네트워크 또는 방화벽 문제
- `PermissionDeniedError` → settings.json deny 규칙 확인

**5단계: 설정 파일 유효성 확인**
```bash
python3 -c "import json; json.load(open('$HOME/.claude/settings.json'))" \
    && echo "유효한 JSON" \
    || echo "JSON 구문 오류"
```

> 💡 **JSON 구문 오류가 왜 생기나?** settings.json을 수동으로 편집하다가 쉼표 하나를 빠뜨리거나 따옴표를 닫지 않으면 Claude Code가 설정 파일을 읽지 못합니다. Python으로 파싱을 시도하면 어느 줄에 오류가 있는지 즉시 알 수 있습니다.

프로세스, 인증, 네트워크, 로그, 설정 파일을 차례로 확인하며 원인을 좁혀간다.

<hr>

## 빠른 점검 스크립트

매번 5단계를 수동으로 실행하는 대신, 아래 스크립트를 `~/auth-check.sh`로 저장해 두면 한 번에 전체 상태를 확인할 수 있다.

```bash
#!/bin/bash
# auth-check.sh — Claude Code 인증 상태 빠른 점검

echo "=== 1. 프로세스 확인 ==="
pgrep -af claude || echo "[없음] Claude Code가 실행 중이 아닙니다"

echo ""
echo "=== 2. 인증 상태 ==="
claude auth status 2>/dev/null || echo "[오류] auth status 실행 실패"

echo ""
echo "=== 3. 네트워크 (api.anthropic.com) ==="
CODE=$(curl -s -o /dev/null -w "%{http_code}" https://api.anthropic.com/v1/messages)
echo "HTTP 응답 코드: $CODE"
case "$CODE" in
  200|401) echo "[정상] 네트워크 연결 OK (401=인증만 실패)" ;;
  000)     echo "[오류] 서버에 도달 불가 — 방화벽 또는 DNS 확인 필요" ;;
  *)       echo "[경고] 예상치 못한 코드: $CODE" ;;
esac

echo ""
echo "=== 4. 설정 파일 유효성 ==="
python3 -c "import json; json.load(open('$HOME/.claude/settings.json'))" \
  && echo "[정상] JSON 유효" \
  || echo "[오류] JSON 구문 오류 — settings.json 점검 필요"
```

사용법:
```bash
chmod +x ~/auth-check.sh
~/auth-check.sh
```

<hr>

## 요약

Remote Control 인증 문제의 90%는 **토큰 만료**, **계정 불일치**, **네트워크 차단** 중 하나다. `claude auth status`로 인증을, `pgrep`으로 프로세스를, `curl`로 연결을 확인하면 대부분 잡힌다. 반복 발생한다면 `auth-check.sh` 스크립트로 한 번에 전체 상태를 점검하는 습관을 들이면 진단 시간이 확 줄어든다.
