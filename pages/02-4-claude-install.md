## 02-4. Claude Code 설치 및 인증

Claude Code는 Anthropic이 만든 AI 코딩 어시스턴트 CLI 도구입니다. 터미널에서 직접 Claude와 대화하며 코드를 작성하고, 파일을 편집하고, 명령을 실행할 수 있습니다. 멀티에이전트 환경에서는 각 TMUX 파인마다 Claude Code 인스턴스가 독립적으로 동작합니다.

> 💡 **CLI란?** Command Line Interface, 즉 "명령줄 도구"입니다. 마우스로 클릭하는 화면 대신, 터미널에 명령어를 입력해 프로그램을 사용하는 방식입니다. 처음엔 낯설지만, 한 번 익히면 훨씬 빠르고 자동화하기 좋습니다.

<hr>

## 설치

아래 2단계로 설치하고 정상 설치 여부를 확인합니다.

### 1단계. npm으로 전역 설치

npm을 통해 전역(컴퓨터 전체에서 사용 가능) 설치합니다.

```bash
npm install -g @anthropic-ai/claude-code
```

> 💡 `-g`는 "global(전역)"의 약자로, 어느 폴더에서든 `claude` 명령을 쓸 수 있게 설치한다는 뜻입니다.

### 2단계. 버전 확인

설치가 끝나면 버전을 확인해 정상 설치를 검증합니다.

```bash
claude --version
```

출력 예시:
```
claude-code 2.1.170
```

위처럼 버전 번호가 보이면 설치 성공입니다.

정리하면 검증은 간단합니다 — npm으로 설치한 뒤 `claude --version` 한 줄을 쳤을 때 위처럼 버전 번호가 돌아오면 끝입니다. 만약 `command not found` 같은 메시지가 나온다면 설치가 안 됐거나 PATH 등록이 빠진 것이니, 앞 단계를 다시 확인하세요.

<hr>

## 인증

Claude Code를 처음 실행하면 Anthropic 계정 인증이 필요합니다. 아래 명령으로 실행을 시작합니다.

```bash
claude
```

처음 실행 시 아래 세 가지 화면이 순서대로 나타납니다. 각 화면에서 안내대로 선택하면 됩니다.

세 화면은 **폴더 신뢰 → 이용 약관 동의 → 로그인 방식 선택**의 한 방향 순서로 흘러가며, 마지막에서 로그인을 고르면 브라우저가 열려 OAuth 인증으로 마무리됩니다. 되돌아가는 분기는 없으니 안내대로 차례차례 선택하면 됩니다. 아래에서 각 화면을 하나씩 짚어 보겠습니다.

### 1단계. 폴더 신뢰

```
Do you trust the files in this folder?
> Yes, I trust this folder (proceed)
  No, exit
```

Enter를 눌러 신뢰를 승인합니다.

> 💡 Claude Code는 현재 작업 폴더의 파일을 읽고 쓸 수 있으므로, 처음 들어온 폴더가 안전한지 한 번 확인하는 절차입니다.

### 2단계. 이용 약관 동의

```
Do you accept the terms of service?
  No, exit
> Yes, I accept
```

아래 방향키(↓)로 `Yes, I accept`를 선택한 뒤 Enter를 누릅니다.

### 3단계. 로그인 방식 선택

```
How would you like to authenticate?
> Login with claude.ai (recommended)
  Use an API key
```

`Login with claude.ai`를 선택하면 브라우저가 열리고 Anthropic 계정으로 OAuth 로그인을 진행합니다.

> 💡 **OAuth란?** 비밀번호를 직접 입력하지 않고, 이미 로그인된 웹사이트(claude.ai)를 통해 안전하게 권한을 넘겨받는 방식입니다. 브라우저에서 "허용"만 누르면 됩니다.

> **중요**: Remote Control 기능을 사용하려면 반드시 `claude.ai`를 통한 OAuth 로그인이 필요합니다. API 키 방식으로는 Remote Control이 활성화되지 않습니다.

<hr>

## 인증 확인

로그인 후 Claude 프롬프트(>)가 나타나면 인증이 완료된 것입니다.

```
> Hello! What can I help you with?
```

현재 인증 상태는 `/status` 명령으로 확인할 수 있습니다.

```
> /status
```

<hr>

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

> 💡 처음에는 기본값인 Sonnet으로 시작하길 권합니다. 더 복잡하고 어려운 작업이 필요해지면 Opus로, 빠르고 가벼운 응답이 필요하면 Haiku로 바꾸면 됩니다.

<hr>

## 권한 설정 (멀티에이전트용)

여러 파인에서 자동으로 실행할 때는 권한 다이얼로그를 건너뛰는 플래그를 사용합니다.

```bash
claude --dangerously-skip-permissions
```

이 플래그는 파일 읽기/쓰기, 명령 실행 등의 권한 승인 절차를 자동으로 허용합니다. 신뢰할 수 있는 환경에서만 사용하세요.

> ⚠️ 이름 그대로 "위험할 수 있으니 권한 확인을 건너뛴다"는 옵션입니다. 내 컴퓨터처럼 믿을 수 있는 환경에서만 쓰고, 잘 모르는 코드를 다룰 때는 사용하지 마세요.

<hr>

## 업데이트

새 버전이 출시되면 동일한 npm 명령으로 업데이트합니다.

```bash
npm update -g @anthropic-ai/claude-code

# 또는
npm install -g @anthropic-ai/claude-code@latest
```

<hr>

## 요약

```bash
# 설치
npm install -g @anthropic-ai/claude-code

# 최초 실행 및 인증
claude

# 인증 후 정상 동작 확인
claude --version   # 버전 출력
claude             # > 프롬프트 확인
```

다음 챕터에서는 멀티에이전트 환경의 핵심인 TMUX를 설치하고 기본 사용법을 익힙니다.
