## 02-1. 환경 설치 — 플랫폼 선택

Claude Code 멀티에이전트 환경은 Ubuntu Linux 기반에서 동작합니다. 사용 중인 운영체제에 맞는 가이드를 선택하세요.

<hr>

## 플랫폼별 설치 가이드

### Windows 사용자 → [02-1-W. WSL2 환경 구성 완전 가이드](02-1-windows-wsl2.md)

WSL2(Windows Subsystem for Linux 2)를 통해 Windows 위에서 Ubuntu 환경을 구성합니다.

- WSL2 활성화 → Ubuntu 설치 → Node.js/Git/TMUX → Claude Code

### macOS 사용자 → [02-2-M. macOS 설치 완전 가이드](02-2-macos.md)

Homebrew를 사용해 기본 터미널(zsh) 환경에서 바로 구성합니다.

- Homebrew → Node.js/Git/TMUX → Claude Code

### Linux 사용자 → 이 페이지에서 계속

Ubuntu 22.04 이상 또는 Debian 계열 배포판을 이미 사용 중이라면 아래 단계를 따릅니다.

<hr>

## Linux 네이티브 설치

### 패키지 목록 최신화

```bash
sudo apt update && sudo apt upgrade -y
```

### 기본 유틸리티 설치

```bash
sudo apt install -y git curl wget unzip build-essential tmux
```

### Node.js 설치 (nvm 권장)

```bash
# nvm 설치
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc

# Node.js LTS
nvm install --lts
nvm use --lts

# 확인
node --version
npm --version
```

### Claude Code 설치

```bash
npm install -g @anthropic-ai/claude-code

# 확인
claude --version
```

### 최초 인증

```bash
claude
```

1. `Yes, I trust this folder` 선택
2. `Yes, I accept` 선택
3. `Login with claude.ai (recommended)` 선택

<hr>

## 설치 확인

```bash
node --version    # v18.0.0 이상
npm --version     # 9.0.0 이상
git --version     # 2.x.x
tmux -V           # tmux 3.x
claude --version  # claude-code x.x.x
```

플랫폼별 환경이 준비되었으면 다음 챕터에서 TMUX 구조와 멀티에이전트 팀을 구성합니다.
