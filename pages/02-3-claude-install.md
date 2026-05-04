# 2-3. Claude Code 설치 및 인증

Claude Code는 Anthropic이 만든 AI 코딩 어시스턴트 CLI 도구입니다. 터미널에서 직접 Claude와 대화하며 코드를 작성하고, 파일을 편집하고, 명령을 실행할 수 있습니다. 멀티에이전트 환경에서는 각 TMUX 파인마다 Claude Code 인스턴스가 독립적으로 동작합니다.

---

## 설치

npm을 통해 전역 설치합니다.

```bash
npm install -g @anthropic-ai/claude-code
```

설치 후 버전을 확인합니다.

```bash
claude --version
```

출력 예시:
```
claude-code 2.1.71
```

```bash
$ npm install -g @anthropic-ai/claude-code 2>&1 | tail -5 && echo '✅ 설치 완료'

changed 2 packages in 2s
✅ 설치 완료
```

---

## 인증

Claude Code를 처음 실행하면 Anthropic 계정 인증이 필요합니다.

```bash
claude
```

처음 실행 시 아래 두 가지 다이얼로그가 순서대로 나타납니다.

### 다이얼로그 1: 폴더 신뢰

```
Do you trust the files in this folder?
> Yes, I trust this folder (proceed)
  No, exit
```

Enter를 눌러 신뢰를 승인합니다.

### 다이얼로그 2: 이용 약관

```
Do you accept the terms of service?
  No, exit
> Yes, I accept
```

아래 방향키로 "Yes, I accept"를 선택 후 Enter를 누릅니다.

### 로그인 방식 선택

```
How would you like to authenticate?
> Login with claude.ai (recommended)
  Use an API key
```

`Login with claude.ai`를 선택하면 브라우저가 열리고 Anthropic 계정으로 OAuth 로그인을 진행합니다.

> **중요**: Remote Control 기능을 사용하려면 반드시 `claude.ai`를 통한 OAuth 로그인이 필요합니다. API 키 방식으로는 Remote Control이 활성화되지 않습니다.

---

## 인증 확인

로그인 후 Claude 프롬프트(❯)가 나타나면 인증이 완료된 것입니다.

```
❯ Hello! What can I help you with?
```

현재 인증 상태는 `/status` 명령으로 확인할 수 있습니다.

```
❯ /status
```

---

## 모델 설정

기본 모델은 Claude Sonnet입니다. 다른 모델로 시작하려면 `--model` 플래그를 사용합니다.

```bash
# Sonnet (기본, 속도·비용 균형)
claude --model claude-sonnet-4-6

# Opus (고성능, 복잡한 작업)
claude --model claude-opus-4-6

# Haiku (경량, 빠른 응답)
claude --model claude-haiku-4-5-20251001
```

---

## 권한 설정 (멀티에이전트용)

여러 파인에서 자동으로 실행할 때는 권한 다이얼로그를 건너뛰는 플래그를 사용합니다.

```bash
claude --dangerously-skip-permissions
```

이 플래그는 파일 읽기/쓰기, 명령 실행 등의 권한 승인 절차를 자동으로 허용합니다. 신뢰할 수 있는 환경에서만 사용하세요.

---

## 업데이트

새 버전이 출시되면 동일한 npm 명령으로 업데이트합니다.

```bash
npm update -g @anthropic-ai/claude-code

# 또는
npm install -g @anthropic-ai/claude-code@latest
```

---

## 요약

```bash
# 설치
npm install -g @anthropic-ai/claude-code

# 최초 실행 및 인증
claude

# 인증 후 정상 동작 확인
claude --version   # 버전 출력
claude             # ❯ 프롬프트 확인
```

다음 챕터에서는 멀티에이전트 환경의 핵심인 TMUX를 설치하고 기본 사용법을 익힙니다.
