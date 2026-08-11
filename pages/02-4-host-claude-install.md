## 02-4. 호스트에 Claude Code 설치·인증

앞 절까지 플랫폼별(Ubuntu·WSL2·macOS) 환경을 준비했습니다. 이제 모든 플랫폼에서 동일한 경로로 Claude Code를 설치하고 인증을 마칩니다. 설치는 curl 네이티브 스크립트가 1순위이며, Node.js 없이도 곧바로 실행됩니다.

<hr>

## 설치

### 네이티브 설치 (권장)

공식 설치 스크립트 한 줄로 설치가 끝납니다. macOS·Linux·WSL2 모두 동일합니다.

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Node.js가 없어도 됩니다. 스크립트가 플랫폼에 맞는 네이티브 바이너리를 `~/.local/bin/claude`에 직접 내려받으므로 별도 런타임이 필요 없습니다. 설치 후 백그라운드 자동 업데이트도 지원합니다.

설치 확인:

```bash
claude --version   # 예: 2.1.211 (Claude Code)
claude doctor      # 설치 상태 진단 (세션 시작하지 않음)
```

### npm 글로벌 설치 (고급 옵션)

Node.js 기반 프로젝트 환경이라 npm 설치를 선호하는 경우에만 사용합니다. Node.js **22 이상**이 필요하며, `sudo npm install -g`는 절대 사용하지 않습니다. root 권한을 동반한 전역 설치는 권한 문제와 보안 위험을 일으킬 수 있다고 공식 문서가 명시합니다. nvm으로 Node.js를 설치하면 `~/.nvm` 경로에 설치되어 sudo 없이도 전역 설치가 정상 동작합니다.

```bash
npm install -g @anthropic-ai/claude-code
```

업그레이드할 때는 `npm update -g`가 아니라 아래 명령을 사용합니다.

```bash
npm install -g @anthropic-ai/claude-code@latest
```

npm 설치 방식은 자동 업데이트를 지원하지 않습니다. 쓰기 권한이 있는 npm 전역 디렉터리가 필요하므로, nvm 없이 apt로 Node.js를 설치한 환경이라면 자동 업데이트가 작동하지 않을 수 있습니다.

<hr>

## 인증

Claude Code를 처음 실행하면 자동으로 로그인 프롬프트가 표시됩니다. 인증을 마쳐야 프롬프트(`>`)로 진입합니다.

**계정 요건**: Claude Pro·Max·Team·Enterprise 구독 또는 Anthropic Console(API 크레딧). 무료 플랜으로는 Claude Code를 사용할 수 없습니다.

### 브라우저 OAuth (기본)

```bash
claude
```

실행하면 로그인 화면이 표시되고, 호스트 환경에서는 시스템 브라우저가 자동으로 열립니다. `claude.ai` 계정으로 로그인·승인하면 터미널로 돌아와 인증이 완료됩니다.

Remote Control 기능을 사용하려면 반드시 이 OAuth 방식으로 인증해야 합니다. API 키 방식으로는 Remote Control이 활성화되지 않습니다.

**WSL2 환경**: 브라우저가 자동으로 열리지 않는 경우가 있습니다. 이때는 두 가지 방법 중 하나를 사용합니다.

```
  Browser didn't open? Use the url below to sign in (c to copy)

  https://claude.com/cai/oauth/authorize?...

  Paste code here if prompted >
```

- `c`를 눌러 로그인 URL을 클립보드에 복사한 뒤, Windows 브라우저에 붙여넣어 로그인합니다.
- 로그인 후 브라우저 화면에 인증 코드가 표시되면, 그 코드를 터미널의 `Paste code here if prompted >` 자리에 붙여넣고 Enter를 누릅니다.

세션 도중 재인증이나 계정 전환이 필요할 때는 Claude 프롬프트 안에서 `/login`을 입력합니다.

### API 키

Anthropic Console(`console.anthropic.com`)에서 발급한 API 키를 환경 변수로 설정하면 브라우저 로그인 없이 인증됩니다.

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

키가 설정된 상태에서 `claude`를 실행하면 키 승인 여부를 한 번 묻고 바로 진입합니다. 셸 재시작 이후에도 유지하려면 `~/.bashrc` 또는 `~/.zshrc`에 추가합니다.

### 장기 토큰 (CI/CD)

자동화 파이프라인처럼 브라우저 없는 환경에서 반복 실행이 필요할 때는 `setup-token`으로 1년 유효 토큰을 생성합니다.

```bash
claude setup-token
# 브라우저 승인 후 토큰 출력
export CLAUDE_CODE_OAUTH_TOKEN=your-token
```

### 자격증명 저장 위치

| 플랫폼 | 저장 위치 |
|--------|----------|
| macOS | 시스템 키체인 (암호화) |
| Linux·WSL2 | `~/.claude/.credentials.json` (파일 모드 0600) |

<hr>

## 실행

```bash
claude
```

처음 실행 시 폴더 신뢰 확인과 이용 약관 동의 화면이 차례로 나타납니다. Enter(폴더 신뢰) → 방향키 ↓로 `Yes, I accept` 선택 후 Enter(약관 동의) 순서로 통과하면 `>` 프롬프트가 나타납니다.

멀티에이전트 자동화 환경에서 에이전트가 확인 없이 파일 쓰기·명령 실행을 자동 처리해야 할 때는 `--dangerously-skip-permissions` 플래그를 씁니다. 신뢰할 수 있는 프로젝트 디렉터리에서만 사용합니다.

```bash
claude --dangerously-skip-permissions
```

종료는 `/exit` 또는 `Ctrl+C` 두 번입니다.

<hr>

## 모델 설정

기본 모델은 Claude Sonnet입니다. `--model` 플래그로 다른 모델을 지정할 수 있습니다.

```bash
claude --model claude-sonnet-4-6    # 기본 (속도·비용 균형)
claude --model claude-opus-4-8      # 고성능, 복잡한 설계
claude --model claude-haiku-4-5-20251001  # 경량, 빠른 응답
```

| 모델 | 특성 | 적합한 작업 |
|------|------|------------|
| Sonnet | 속도와 품질의 균형 | 일반 코딩, 파일 편집, 대화 |
| Opus | 최고 성능, 느리고 비용 높음 | 복잡한 설계, 다단계 추론 |
| Haiku | 가장 빠르고 저렴 | 단순 질문, 반복 작업 |

멀티에이전트 팀에서는 역할에 따라 모델을 다르게 배정합니다. 팀장·PM처럼 설계·판단이 많은 역할에는 Opus를, 실행 중심 팀원에는 Sonnet을 사용하면 비용과 성능을 함께 잡을 수 있습니다.

<hr>

## 요약

```bash
# 1. 네이티브 설치 (권장)
curl -fsSL https://claude.ai/install.sh | bash

# 또는 npm 고급 옵션 (Node.js 22 이상, sudo 금지)
npm install -g @anthropic-ai/claude-code

# 2. 설치 확인
claude --version
claude doctor

# 3. 실행 및 인증 (최초 1회 브라우저 OAuth 자동)
claude
# WSL2: 브라우저 미열림 시 → c키로 URL 복사 → Windows 브라우저 로그인 → 코드 붙여넣기

# 또는 API 키 방식
export ANTHROPIC_API_KEY="sk-ant-..."
claude
```

다음 챕터에서는 TMUX를 설치하고 멀티에이전트 팀 레이아웃을 구성합니다.
