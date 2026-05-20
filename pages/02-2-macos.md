## 02-2. macOS: 설치 완전 가이드

macOS에서는 WSL2 없이 기본 터미널(zsh)에서 바로 Claude Code 멀티에이전트 환경을 구성할 수 있습니다. **Homebrew**를 패키지 관리자로 사용합니다.

> **이 페이지 범위**: Homebrew 설치 → Node.js/Git/TMUX 설치 → Claude Code 설치까지 macOS 사용자가 필요한 모든 단계를 다룹니다.

> **지원 버전**: macOS 12 Monterey 이상을 권장합니다. Intel Mac과 Apple Silicon(M1/M2/M3) 모두 지원됩니다.

<hr>

## 1단계: Xcode Command Line Tools 설치

Node.js, Git, TMUX를 빌드하거나 설치하기 위해 Apple의 개발 도구가 필요합니다.

```bash
xcode-select --install
```

팝업 창이 열리면 **설치** 버튼을 클릭합니다. 수 분이 소요됩니다.

설치 확인:

```bash
xcode-select -p
# 출력 예시: /Library/Developer/CommandLineTools
```

<hr>

## 2단계: Homebrew 설치

Homebrew는 macOS의 사실상 표준 패키지 관리자입니다. 터미널에서 아래 명령을 실행합니다.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

설치 중 macOS 비밀번호를 입력하라는 프롬프트가 나타납니다.

### Apple Silicon (M1/M2/M3) — PATH 설정

Apple Silicon Mac은 Homebrew 설치 경로가 `/opt/homebrew/`입니다. 설치 완료 후 아래 명령으로 PATH를 설정합니다.

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### Intel Mac — PATH 설정

Intel Mac은 `/usr/local/`에 설치됩니다. 보통 자동으로 PATH에 추가되지만, 추가되지 않은 경우:

```bash
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zprofile
source ~/.zprofile
```

### 설치 확인

```bash
brew --version
# 출력 예시: Homebrew 4.x.x
```

<hr>

## 3단계: Node.js 설치

Claude Code는 npm 패키지로 배포되므로 **Node.js 18 이상**이 필요합니다.

### nvm으로 설치 (권장)

nvm은 Node.js 버전을 자유롭게 전환할 수 있어 개발 환경에 적합합니다.

```bash
# nvm 설치
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# zsh 설정 파일에 nvm 로드 추가 (자동으로 추가되지 않은 경우)
echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.zshrc
echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.zshrc

# 셸 재로드
source ~/.zshrc

# 설치 확인
nvm --version

# Node.js LTS 설치
nvm install --lts
nvm use --lts

# 버전 확인
node --version
npm --version
```

출력 예시:
```
v22.14.0
10.9.0
```

### Homebrew로 설치 (대안)

nvm 없이 Homebrew로 바로 설치하는 방법입니다.

```bash
brew install node@22

# PATH 추가 (Apple Silicon)
echo 'export PATH="/opt/homebrew/opt/node@22/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 버전 확인
node --version
npm --version
```

<hr>

## 4단계: Git 설정

macOS에는 Git이 기본 내장되어 있습니다. 최신 버전이 필요하다면 Homebrew로 설치합니다.

```bash
# 기본 Git 버전 확인
git --version
# 출력 예시: git version 2.39.5 (Apple Git-154)

# 최신 버전 설치 (선택)
brew install git
```

### 사용자 정보 설정

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# 기본 브랜치 이름 설정 (선택)
git config --global init.defaultBranch main
```

<hr>

## 5단계: 추가 유틸리티 설치

```bash
# wget (curl은 macOS 기본 내장)
brew install wget

# 설치 확인
curl --version | head -1
wget --version | head -1
```

<hr>

## 6단계: TMUX 설치

TMUX는 하나의 터미널에서 여러 창을 동시에 실행할 수 있는 도구입니다.

```bash
brew install tmux

# 설치 확인
tmux -V
```

출력 예시:
```
tmux 3.4
```

### macOS에서 TMUX 클립보드 연동 (선택)

macOS에서 TMUX 내 복사/붙여넣기를 시스템 클립보드와 연동하려면 reattach-to-user-namespace를 설치합니다.

```bash
brew install reattach-to-user-namespace
```

`~/.tmux.conf`에 아래 설정을 추가합니다.

```bash
set-option -g default-command "reattach-to-user-namespace -l zsh"
```

<hr>

## 7단계: Claude Code 설치

```bash
npm install -g @anthropic-ai/claude-code

# 설치 확인
claude --version
```

출력 예시:
```
claude-code 2.1.71
```

### 최초 인증

```bash
claude
```

처음 실행 시 두 가지 승인 후 브라우저 로그인 화면이 열립니다.

1. **폴더 신뢰**: `Yes, I trust this folder` 선택
2. **이용 약관**: `Yes, I accept` 선택
3. **인증 방식**: `Login with claude.ai (recommended)` 선택

> **중요**: Remote Control 기능을 사용하려면 반드시 `Login with claude.ai`를 선택해야 합니다. API 키 방식으로는 Remote Control이 활성화되지 않습니다.

로그인 후 `>` 프롬프트가 나타나면 인증 완료입니다.

<hr>

## macOS 고유 설정

### zsh 셸 확인

macOS Catalina(10.15) 이후부터 기본 셸이 zsh입니다. 현재 셸을 확인합니다.

```bash
echo $SHELL
# 출력 예시: /bin/zsh
```

bash를 사용 중이라면 zsh로 전환할 수 있습니다.

```bash
chsh -s /bin/zsh
```

### nvm PATH 확인

nvm이 zsh에서 정상 로드되는지 확인합니다.

```bash
# ~/.zshrc에 nvm 설정이 있는지 확인
grep -n "nvm" ~/.zshrc
```

아래 두 줄이 있어야 합니다.

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
```

없다면 직접 추가합니다.

```bash
echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.zshrc
echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.zshrc
source ~/.zshrc
```

### macOS 방화벽 설정

Remote Control 기능 사용 시 macOS 방화벽에서 연결을 허용해야 합니다. **시스템 환경설정 → 보안 및 개인 정보 보호 → 방화벽** 에서 Claude Code를 허용 목록에 추가합니다.

<hr>

## 원클릭 설치 스크립트

위 단계를 하나의 스크립트로 실행합니다. 터미널에서 실행하세요.

```bash
#!/bin/bash
set -e

echo "=== macOS Claude Code 환경 설치 시작 ==="

# Homebrew 설치 확인 또는 설치
if ! command -v brew &>/dev/null; then
  echo "Homebrew 설치 중..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Apple Silicon PATH
  if [[ $(uname -m) == "arm64" ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
  fi
fi

# 기본 도구
brew install git wget tmux

# nvm 설치
if ! command -v nvm &>/dev/null; then
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
fi

# Node.js LTS
nvm install --lts
nvm use --lts

# Claude Code
npm install -g @anthropic-ai/claude-code

echo ""
echo "=== 설치 완료 ==="
echo "  node:   $(node --version)"
echo "  npm:    $(npm --version)"
echo "  git:    $(git --version | cut -d' ' -f3)"
echo "  tmux:   $(tmux -V | cut -d' ' -f2)"
echo "  claude: $(claude --version 2>/dev/null || echo '인증 필요')"
echo ""
echo "다음 단계: claude 명령으로 인증을 진행하세요."
```

저장 후 실행:

```bash
chmod +x install.sh
./install.sh
```

<hr>

## 설치 확인 체크리스트

```bash
brew --version    # Homebrew 4.x.x
node --version    # v18.0.0 이상
npm --version     # 9.0.0 이상
git --version     # 2.x.x
tmux -V           # tmux 3.x
claude --version  # claude-code x.x.x
```

모든 항목이 버전을 출력하면 다음 챕터로 넘어갑니다. Windows 사용자는 [02-1. Windows WSL2 설치 가이드](02-1-windows-wsl2.md)를 참고하세요.
