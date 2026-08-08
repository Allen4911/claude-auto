# 03-5. Hooks로 자동 검증

이 책에서 "훅(hook)"이라는 단어는 문맥에 따라 전혀 다른 것을 가리킵니다. 이 절에서 다루는 것은 Claude Code 이벤트 훅인데, 이름만 같을 뿐 RTK 훅이나 Git hooks, Slack 웹훅과는 별개 시스템이므로 혼동하면 안 됩니다. 용어부터 구분한 뒤 본론으로 들어갑니다.

## 이벤트 훅이란 — PreToolUse/PostToolUse 등

### 먼저 용어 혼동부터 — 이 책에서 "훅"이 의미하는 것들

| 시스템 | "훅"의 의미 | 핵심 차이 |
|---|---|---|
| **Claude Code 이벤트 훅** | Claude Code가 동작하는 라이프사이클 지점에서 실행되는 셸 명령 | **Claude 자신의 도구 호출·라이프사이클을 가로챔** |
| **RTK (Rust Token Killer)** | 셸 명령을 가로채 토큰을 절약하는 도구 | RTK가 Claude Code 훅을 *이용해* 자신을 설치하는 것. RTK 자체가 훅은 아님 |
| **Git hooks** | `.git/hooks/` 안의 스크립트(pre-commit, post-commit 등). git 동작에서 트리거 | 완전히 별개 시스템. git은 Claude Code를 알지 못함 |
| **Slack 웹훅** | Slack이 이벤트 데이터를 POST하는 HTTP 엔드포인트 | Push 기반 HTTP 알림. Claude와 무관 |
| **React 훅** | `useState`, `useEffect` 같은 UI 라이프사이클 함수 | 프로그래밍 패턴. Claude Code와 무관 |

이 절에서 "훅"은 **Claude Code 이벤트 훅**만을 가리킵니다. 이하 "훅"은 모두 이 의미입니다.

### Claude Code 이벤트 훅의 정의

훅은 사용자가 정의한 셸 명령입니다. Claude Code가 라이프사이클의 특정 지점에서 이 명령을 실행하므로 **결정론적 제어**가 가능합니다. LLM의 판단에 맡기는 대신, 특정 동작이 반드시 일어나도록 보장합니다.

예를 들어 "Claude가 파일을 편집할 때마다 자동으로 코드 포매터를 실행한다"거나 "Claude가 위험한 명령어를 실행하려 하면 자동으로 차단한다"는 동작을 훅으로 구현할 수 있습니다.

> Claude Code의 훅 시스템은 터미널 세션, IDE 확장, 데스크톱 앱, 웹의 Claude Code 모든 플랫폼에서 동일하게 동작합니다.

### 이벤트 훅 전체 목록

Claude Code가 제공하는 이벤트 훅 목록입니다. 굵게 표시한 이벤트가 이 절에서 주로 다루는 핵심입니다.

| 이벤트 | 발동 시점 | 차단 가능 여부 |
|---|---|---|
| `SessionStart` | 세션 시작 또는 재개 시 | 아니오 |
| `Setup` | `--init-only`/`--init`/`--maintenance`로 시작 시 | 아니오 |
| `UserPromptSubmit` | Claude가 프롬프트를 처리하기 전 | 예(exit 2) |
| `UserPromptExpansion` | 슬래시 명령이 프롬프트로 확장될 때 | 예(exit 2) |
| **`PreToolUse`** | **도구 호출 실행 전** | **예(exit 2 또는 JSON deny)** |
| `PermissionRequest` | 도구에 권한 결정이 필요할 때 | 예 |
| `PermissionDenied` | 자동 모드 분류기가 도구 호출을 거부할 때 | 아니오 |
| **`PostToolUse`** | **도구 호출 성공 후** | **아니오(도구 이미 실행됨)** |
| `PostToolUseFailure` | 도구 호출 실패 후 | 아니오 |
| `PostToolBatch` | 병렬 도구 호출 배치 전체 완료 후 | 예(decision: "block") |
| **`Notification`** | **Claude Code가 알림을 전송할 때** | 아니오 |
| `MessageDisplay` | 어시스턴트 메시지 텍스트가 표시될 때 | 아니오 |
| `SubagentStart` | 서브에이전트가 시작될 때 | 아니오 |
| **`SubagentStop`** | **서브에이전트가 완료될 때** | **예(decision: "block")** |
| `TaskCreated` | 태스크가 생성될 때 | 예(exit 2) |
| `TaskCompleted` | 태스크가 완료될 때 | 예(exit 2) |
| **`Stop`** | **Claude 응답이 완료될 때** | **예(exit 2 또는 decision: "block")** |
| `StopFailure` | API 오류로 턴이 종료될 때 | 아니오 |
| `TeammateIdle` | 에이전트 팀 팀원이 유휴 상태 직전 | 예(exit 2) |
| `InstructionsLoaded` | CLAUDE.md 또는 `.claude/rules/*.md` 로드 시 | 아니오 |
| `ConfigChange` | 세션 중 설정 파일이 변경될 때 | 예(exit 2) |
| `CwdChanged` | 작업 디렉토리가 변경될 때 | 아니오 |
| `DirectoryAdded` | `/add-dir` 또는 SDK로 디렉토리가 추가될 때 | 아니오 |
| `FileChanged` | 감시 중인 파일이 디스크에서 변경될 때 | 아니오 |
| `WorktreeCreate` | 워크트리가 생성될 때 | 예(0 외 모든 exit) |
| `WorktreeRemove` | 워크트리가 제거될 때 | 아니오 |
| **`PreCompact`** | **컨텍스트 압축 전** | **예(exit 2 또는 decision: "block")** |
| `PostCompact` | 컨텍스트 압축 완료 후 | 아니오 |
| `Elicitation` | MCP 서버가 사용자 입력을 요청할 때 | 예(exit 2) |
| `ElicitationResult` | 사용자가 MCP elicitation에 응답할 때 | 예(exit 2) |
| `SessionEnd` | 세션이 종료될 때 | 아니오 |

> **`PostToolUse`는 차단할 수 없습니다.** 도구가 이미 실행된 뒤에 발동하기 때문입니다. 도구 호출을 막으려면 반드시 `PreToolUse`를 사용해야 합니다.


## 자동 검증·차단 구성

### settings.json 구조

훅은 `settings.json` 파일의 `"hooks"` 키 아래에 설정합니다.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-dangerous.sh",
            "timeout": 600
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs your attention\"'"
          }
        ]
      }
    ]
  }
}
```

**구조 요약:**
- `"hooks"`: settings.json 최상위 키
- 내부: 이벤트명 키(`"PreToolUse"`, `"PostToolUse"` 등)
- 각 이벤트: **훅 그룹 배열**. 그룹마다 `"matcher"`와 `"hooks"` 배열이 들어갑니다
- 각 훅 항목: `"type"`과 `"command"` (또는 `"url"`, `"prompt"`)

`settings.json`의 위치에 따라 적용 범위가 달라집니다.

| 파일 | 범위 | git 커밋 가능 여부 |
|---|---|---|
| `~/.claude/settings.json` | 내 모든 프로젝트 | 아니오(개인용) |
| `.claude/settings.json` | 이 프로젝트만 | 예(팀 공유·클라우드 세션 적용) |
| `.claude/settings.local.json` | 이 프로젝트만 | 아니오(자동 gitignore) |

> **중요**: `~/.claude/settings.json`의 훅은 클라우드 세션에 적용되지 않습니다. 팀 공유와 클라우드 세션 모두에 적용하려면 `.claude/settings.json`에 커밋해야 합니다.

> **훅 병합**: 같은 이벤트의 훅이 여러 범위 파일에 있으면 오버라이드가 아니라 **모두 병합**해 실행합니다.

### 훅 핸들러 타입 5종

**1. type: "command"** — 가장 일반적인 형태. 셸 명령을 실행합니다.
```json
{
  "type": "command",
  "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check-safety.sh",
  "timeout": 600,
  "shell": "bash"
}
```

**2. type: "http"** — HTTP 엔드포인트를 호출합니다.
```json
{
  "type": "http",
  "url": "http://localhost:8080/hooks/pre-tool-use",
  "timeout": 30
}
```

**3. type: "prompt"** — 단일 LLM 호출로 판단을 위임합니다.
```json
{
  "type": "prompt",
  "prompt": "이 도구 호출을 허용해야 합니까? $ARGUMENTS",
  "model": "claude-haiku",
  "timeout": 30
}
```

**4. type: "agent"** — 도구를 쓸 수 있는 다중 턴 LLM을 실행합니다. (실험적)
```json
{
  "type": "agent",
  "prompt": "모든 단위 테스트가 통과하는지 확인하세요.",
  "timeout": 120
}
```

**5. type: "mcp_tool"** — MCP 서버의 도구를 호출합니다.
```json
{
  "type": "mcp_tool",
  "server": "my_server",
  "tool": "security_scan"
}
```

### 훅이 받는 입력 — stdin JSON

> ⚠️ **흔한 실수**: `CLAUDE_TOOL_NAME` 같은 환경변수는 **존재하지 않습니다.** 도구명과 입력값은 모두 **stdin으로 넘어오는 JSON** 안에 들어 있습니다.

훅 스크립트가 실행될 때 Claude Code는 다음 JSON을 stdin으로 넘겨줍니다.

```json
{
  "session_id": "abc123",
  "cwd": "/home/user/myproject",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test"
  },
  "prompt_id": "550e8400-...",
  "transcript_path": "/home/user/.claude/projects/.../transcript.jsonl",
  "permission_mode": "default",
  "agent_id": "subagent-123",
  "agent_type": "security-reviewer",
  "tool_use_id": "toolu_01ABC123..."
}
```

스크립트 안에서 `cat`으로 stdin을 읽고 `jq`로 필요한 필드를 추출합니다.

### 사용 가능한 환경변수

stdin JSON 외에 다음 환경변수도 훅 스크립트에서 씁니다.

| 변수 | 용도 |
|---|---|
| `CLAUDE_PROJECT_DIR` | 프로젝트 루트 디렉토리 경로 |
| `CLAUDE_PLUGIN_ROOT` | 플러그인 설치 디렉토리 |
| `CLAUDE_PLUGIN_DATA` | 플러그인 영속 데이터 디렉토리 |
| `CLAUDE_CODE_REMOTE` | 웹 환경에서 `"true"` |
| `CLAUDE_EFFORT` | 현재 effort 레벨 |
| `CLAUDE_ENV_FILE` | Bash 프리앰블로 소싱할 파일 경로 |
| `CLAUDECODE` | 모든 Claude Code 하위 프로세스에서 `1` |
| `ANTHROPIC_API_KEY` | 환경에서 상속 |


### 도구 호출 차단 방법

훅 스크립트가 차단 의사를 전달하는 방법은 두 가지입니다.

**방법 1: exit code 2 (간단)**

exit code의 의미:

| exit 코드 | 결과 |
|---|---|
| **0** | 이의 없음. 정상 권한 흐름으로 진행 |
| **2** | Claude Code가 해당 동작을 차단. stderr 내용이 Claude에게 피드백으로 표시됨 |
| 기타(1, 3 등) | 비차단 오류. 동작은 진행되고 경고만 표시됨 |

```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q "drop table"; then
  echo "차단: DROP TABLE 명령은 허용되지 않습니다." >&2  # Claude에게 피드백
  exit 2                                                  # 2 = 차단
fi

exit 0  # 0 = 이의 없음, 정상 진행
```

**방법 2: exit 0 + JSON 출력 (구조화된 제어)**

`PreToolUse`에서는 JSON을 내보내 더 세밀하게 제어할 수 있습니다.

```bash
#!/bin/bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "위험한 명령어가 훅에 의해 차단되었습니다."
    }
  }'
else
  exit 0
fi
```

`PreToolUse`의 `permissionDecision` 값과 의미:

| 값 | 의미 |
|---|---|
| `"allow"` | 권한 프롬프트 없이 즉시 허용 |
| `"deny"` | 도구 호출 취소, 이유를 Claude에게 전달 |
| `"ask"` | 사용자에게 권한 프롬프트를 표시 |
| `"defer"` | SDK 헤드리스 모드용: 래퍼가 입력을 수집하도록 프로세스 종료 |

> **주의**: exit 2와 JSON 출력을 혼용하지 마세요. exit 2로 종료하면 JSON 출력은 무시됩니다.

### 매처(Matcher) 패턴

어떤 도구 호출에 훅을 적용할지 `"matcher"` 필드로 제어합니다.

```json
"matcher": "Bash"           // Bash 도구만
"matcher": "Edit|Write"     // 파이프(|)로 OR 조건
"matcher": "Edit, Write"    // 쉼표도 OR로 처리됩니다(v2.1.191+)
"matcher": "mcp__memory__.*" // 정규식: memory 서버의 모든 도구
"matcher": ""               // 빈 문자열 = 모든 발동에서 실행
```

`"if"` 필드를 쓰면 적용 조건을 한 번 더 좁힐 수 있습니다.
```json
{
  "type": "command",
  "if": "Bash(git *)",
  "command": "/path/to/check-git-policy.sh"
}
```

### 실전 예시

**민감 파일 보호 (PreToolUse, Edit|Write):**
```bash
#!/bin/bash
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

PROTECTED_PATTERNS=(".env" "package-lock.json" ".git/")

for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "차단: $FILE_PATH 는 보호된 파일 패턴 '$pattern' 에 해당합니다." >&2
    exit 2
  fi
done
exit 0
```

**편집 후 자동 포맷 (PostToolUse, Edit|Write):**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

**Stop 훅 무한루프 방지:**

Stop 훅 안에서 Claude에게 피드백을 주면 Claude가 다시 응답하고 그 응답이 또 Stop 훅을 발동시켜 무한루프가 생깁니다. `stop_hook_active` 필드를 확인해 루프를 끊습니다.

```bash
#!/bin/bash
INPUT=$(cat)
if [ "$(echo "$INPUT" | jq -r '.stop_hook_active')" = "true" ]; then
  exit 0  # Claude가 멈출 수 있도록 허용
fi
# ... 나머지 검증 로직
```


## 용어 정리 — RTK훅·Git hooks·Slack웹훅과의 차이

혼동이 잦은 세 가지 "훅"의 차이를 한 번 더 정리합니다.

### Claude Code 이벤트 훅 — 이 절의 주제

Claude 자신의 동작(도구 호출, 세션 종료 등)을 가로채는 셸 명령입니다. `settings.json`에 등록하며, Claude Code가 직접 실행합니다. PreToolUse로 도구 호출을 막거나, PostToolUse로 편집 후 포매터를 자동 실행하는 식입니다.

### RTK (Rust Token Killer)

이 책의 개발 환경에서 사용하는 토큰 절약 도구입니다. RTK 자체는 "훅"이 아닙니다. RTK는 Claude Code 이벤트 훅 시스템을 이용해 셸 명령을 가로채도록 자신을 설치합니다. Claude Code 훅을 *쓰는* 쪽이지, 훅 자체는 아닙니다.

### Git hooks

`.git/hooks/` 디렉토리 안의 스크립트입니다. `pre-commit`, `post-commit` 같은 이름으로 git 동작 시점에 트리거됩니다. git이 실행하므로 Claude Code는 이 시스템을 알지 못합니다. 두 시스템이 같은 이름의 도구(예: Prettier)를 실행하기도 하지만 서로 독립적으로 동작합니다.

### Slack 웹훅

Slack이 이벤트 발생 시 지정한 URL로 HTTP POST를 보내는 구조입니다. "웹훅"이라는 이름을 공유하지만, Claude Code와 아무런 관계가 없습니다.

> 실무에서는 세 시스템을 함께 쓰는 일이 많습니다. 예를 들어 Claude Code가 코드를 편집하면(`PostToolUse` Claude Code 훅) → 파일을 `git commit`할 때 서식 검사(`pre-commit` Git hook) → 커밋 완료 후 Slack 채널에 알림(Slack 웹훅)까지 하나로 이어집니다. 각각 별개 시스템이 순서대로 움직일 뿐입니다.


