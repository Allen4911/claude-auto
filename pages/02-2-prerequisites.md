## 02-2. 필수 패키지 설치

Claude Code와 TMUX 기반 멀티에이전트 환경을 구성하려면 Node.js, npm, 그리고 몇 가지 유틸리티가 필요합니다. 이 챕터에서는 순서대로 설치합니다.

> **Windows 사용자**: 아래 명령은 모두 **Ubuntu 터미널(WSL2)** 안에서 실행합니다. PowerShell이나 CMD가 아닌 WSL2 Ubuntu 창을 열어 진행하세요.

<hr>

## Node.js 설치

Claude Code는 npm 패키지로 배포됩니다. **Node.js 18 이상**이 필요하며, 최신 LTS 버전을 권장합니다.

### nvm으로 설치 (권장 — Windows/Linux/macOS 공통)

nvm(Node Version Manager)은 모든 플랫폼에서 동일하게 사용할 수 있어 권장합니다.

```bash
# nvm 설치
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# 셸 재로드
source ~/.bashrc   # Linux / WSL2
# source ~/.zshrc  # macOS (zsh 기본 셸인 경우)

# nvm 설치 확인
nvm --version

# Node.js LTS 설치
nvm install --lts

# 버전 확인
node --version
npm --version
```

출력 예시:
```
v22.14.0
10.9.0
```

### apt로 직접 설치 (Linux / WSL2 전용)

```bash
# NodeSource 저장소 추가 (Node.js 22.x)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -

# 설치
sudo apt install -y nodejs

# 확인
node --version
npm --version
```

### Homebrew로 설치 (macOS 전용)

```bash
# Homebrew가 없다면 먼저 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Node.js LTS 설치
brew install node@22

# 확인
node --version
npm --version
```

<hr>

## Git 설치

Git은 Claude Code의 프로젝트 관리와 설정 파일 버전 관리에 활용됩니다.

### Linux / WSL2

```bash
sudo apt install -y git

# 설치 확인
git --version
```

### macOS

macOS에는 Git이 기본 포함되어 있습니다. 최신 버전이 필요하다면 Homebrew로 설치합니다.

```bash
# 기본 Git 확인
git --version

# 최신 버전 설치 (선택)
brew install git
```

### 공통 — 초기 사용자 설정

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

<hr>

## curl, wget, unzip

### Linux / WSL2

```bash
sudo apt install -y curl wget unzip
```

### macOS

`curl`은 기본 내장되어 있습니다. `wget`이 필요하다면 Homebrew로 설치합니다.

```bash
brew install wget
# curl, unzip은 기본 포함
```

<hr>

## build-essential (선택)

일부 npm 패키지가 네이티브 빌드를 요구할 수 있습니다.

### Linux / WSL2

```bash
sudo apt install -y build-essential
```

### macOS

```bash
# Xcode Command Line Tools 설치
xcode-select --install
```

<hr>

## 전체 설치 요약 스크립트

### Linux / WSL2

```bash
#!/bin/bash
set -e

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 기본 도구
sudo apt install -y git curl wget unzip build-essential

# nvm & Node.js LTS
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install --lts

echo "✅ 설치 완료"
echo "  node: $(node --version)"
echo "  npm:  $(npm --version)"
echo "  git:  $(git --version)"
```

### macOS

```bash
#!/bin/bash
set -e

# Homebrew 설치 (없는 경우)
which brew || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 기본 도구
brew install git wget

# nvm & Node.js LTS
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.zshrc
nvm install --lts

echo "✅ 설치 완료"
echo "  node: $(node --version)"
echo "  npm:  $(npm --version)"
echo "  git:  $(git --version)"
```

<hr>

## 설치 확인 체크리스트

```bash
node --version    # v18.0.0 이상
npm --version     # 9.0.0 이상
git --version     # 2.x.x
curl --version    # 설치 확인
```

모든 명령이 오류 없이 버전을 출력하면 다음 단계로 넘어갑니다.
