# 8-1. Remote-Control 인증 오류 해결

Remote Control을 사용하다 보면 인증 관련 오류를 마주칠 때가 있다. 대부분의 문제는 토큰 만료, 계정 불일치, 네트워크 설정에서 발생한다. 이 절에서는 자주 발생하는 인증 오류와 해결 방법을 정리한다.

---

## 증상별 진단 가이드

### 1. "Session not found" — 세션을 찾을 수 없음

모바일에서 세션 목록이 비어있거나 연결 시 "Session not found" 오류가 표시된다.

**원인과 해결:**

| 원인 | 확인 방법 | 해결 |
|------|-----------|------|
| Claude Code가 실행 중이 아님 | `pgrep -f claude` | Claude Code 재실행 |
| 서버 모드가 아님 | 터미널에서 Remote Control 상태 확인 | `--remote-control` 플래그로 재시작 |
| 다른 Anthropic 계정 | 모바일과 서버의 계정 비교 | 동일 계정으로 로그인 |
| 세션 이름 불일치 | `claude sessions list` | 올바른 세션 이름으로 접속 |

```bash
# Claude Code 실행 상태 확인
pgrep -f claude
# 출력 없으면 실행 중이 아님

# Claude Code를 서버 모드로 재시작
claude --remote-control
```

### 2. "Authentication failed" — 인증 실패

연결 시도 시 인증 실패 오류가 발생한다.

**해결 과정:**

```bash
# 1. 현재 로그인된 계정 확인
claude auth status

# 2. 인증 토큰이 만료되었으면 재인증
claude auth login

# 3. 브라우저에서 Anthropic 계정으로 로그인 후
#    터미널에 표시되는 인증 코드 입력
```

### 3. "Connection timeout" — 연결 시간 초과

모바일에서 세션을 선택했지만 연결이 되지 않고 타임아웃이 발생한다.

**원인과 해결:**

```bash
# 네트워크 연결 확인
ping -c 3 api.anthropic.com

# DNS 확인
nslookup api.anthropic.com

# 방화벽이 HTTPS 아웃바운드를 차단하는 경우
sudo ufw allow out 443/tcp
```

WSL2 환경에서는 Windows 방화벽이 아웃바운드 연결을 차단하는 경우가 있다. Windows Defender 방화벽 설정에서 WSL2 관련 규칙을 확인한다.

### 4. "Permission denied" — 권한 거부

세션에는 연결되지만 도구 실행 시 "Permission denied"가 반복된다.

```bash
# settings.json의 deny 규칙 확인
cat ~/.claude/settings.json | grep -A 20 "deny"

# 프로젝트별 설정도 확인
cat .claude/settings.json | grep -A 20 "deny"
```

과도한 `deny` 규칙이 정상 명령어까지 차단하고 있을 수 있다. 패턴을 좁히거나 불필요한 규칙을 제거한다.

---

## 인증 토큰 관리

### 토큰 만료 주기

Anthropic 인증 토큰은 일정 기간이 지나면 만료된다. 장기간 실행 중인 Claude Code 세션에서 갑자기 인증 오류가 발생한다면 토큰 만료를 의심한다.

```bash
# 인증 상태 확인
claude auth status
# 출력 예시:
# Logged in as: user@example.com
# Token expires: 2026-05-15T00:00:00Z

# 토큰 갱신
claude auth login
```

### 여러 계정 사용 시

팀 환경에서 여러 Anthropic 계정을 사용하는 경우 계정 전환에 주의한다.

```bash
# 현재 계정 확인
claude auth whoami

# 로그아웃 후 다른 계정으로 전환
claude auth logout
claude auth login
```

---

## TMUX 팀 환경에서의 인증 문제

### 모든 파인이 동시에 인증 실패하는 경우

팀 세션의 모든 파인이 같은 계정을 사용한다면, 토큰 만료 시 전체가 동시에 실패한다.

```bash
# 모든 파인에서 재인증 (브로드캐스트)
for i in 0 1 2 3 4 5; do
  tmux send-keys -t team:0.$i "/login" Enter
done
```

### 특정 파인만 인증 실패하는 경우

하나의 파인만 문제가 있다면 해당 파인의 Claude Code 프로세스를 개별적으로 재시작한다.

```bash
# 문제 파인의 Claude Code 재시작
tmux send-keys -t team:0.3 "/exit" Enter
sleep 2
tmux send-keys -t team:0.3 "claude" Enter
```

---

## 진단 명령어 모음

빠른 진단을 위한 명령어를 정리한다.

```bash
# 1. Claude Code 프로세스 확인
pgrep -af claude

# 2. 인증 상태 확인
claude auth status

# 3. 네트워크 연결 확인
curl -s -o /dev/null -w "%{http_code}" https://api.anthropic.com/v1/messages
# 200 또는 401이면 네트워크 정상 (401은 인증만 실패)

# 4. 로그 확인
ls -lt ~/.claude/logs/ | head -5
tail -50 ~/.claude/logs/latest.log

# 5. 설정 파일 유효성 확인
python3 -c "import json; json.load(open('$HOME/.claude/settings.json'))" \
    && echo "유효한 JSON" \
    || echo "JSON 구문 오류"
```

---

## 요약

Remote Control 인증 문제의 90%는 **토큰 만료**, **계정 불일치**, **네트워크 차단** 중 하나다. `claude auth status`로 인증 상태를 확인하고, `pgrep`으로 프로세스 생존을 확인하고, `curl`로 네트워크 연결을 확인하는 세 단계 진단만으로 대부분의 문제를 해결할 수 있다.
