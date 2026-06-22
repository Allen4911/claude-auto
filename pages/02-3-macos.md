## 02-3. macOS: 설치 완전 가이드 + Docker Desktop

macOS에서는 기본 터미널(zsh)에서 바로 호스트 환경을 구성하고, **Docker Desktop**을 설치한 뒤 컨테이너 안에서 Claude Code·tmux를 운영합니다.

> **이 페이지 범위**: Homebrew 설치 → Git·기본 유틸리티 설치 → **Docker Desktop 설치**까지. Claude Code·tmux 등 실제 개발 도구는 **Docker 컨테이너 내부**(02-5·02-6)에서 설치합니다.

> **지원 버전**: macOS 12 Monterey 이상을 권장합니다. Intel Mac과 Apple Silicon(M1/M2/M3) 모두 지원됩니다.

> **Homebrew를 쉽게 말하면?** macOS용 "앱 설치 도우미"입니다. 평소 앱은 App Store에서 받지만, 개발 도구는 터미널에서 `brew install 도구이름` 한 줄로 깔 수 있게 해 줍니다. 이 페이지는 Homebrew로 필요한 도구들을 차례로 설치합니다.

> 아래는 이 페이지에서 진행할 전체 흐름입니다. 1→5단계를 순서대로 따라가면 됩니다.

**개발 토대(Xcode 도구·Homebrew)를 깔고**(1~2단계), **Git과 기본 유틸리티를 설치**(3~4단계)한 뒤 **Docker Desktop을 설치**합니다(5단계). Claude Code·tmux는 02-5·02-6에서 컨테이너 내부에 설치합니다.

<hr>

## 1단계: Xcode Command Line Tools 설치

Git·curl 등 기본 개발 도구를 쓰기 위해 Apple의 커맨드라인 툴이 필요합니다.

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

> **내 맥이 Apple Silicon인지 Intel인지 확인하는 법:** 화면 왼쪽 위 사과(🍎) 메뉴 → `이 Mac에 관하여`를 엽니다. "칩(Chip)"에 `Apple M1/M2/M3...`라고 적혀 있으면 Apple Silicon, "프로세서(Processor)"에 `Intel...`이라고 적혀 있으면 Intel Mac입니다. 둘은 아래 설치 경로가 다르므로 자기 기종에 맞는 항목을 따르세요.

다음 단계는 칩 종류에 따라 갈립니다. Apple Silicon은 Homebrew가 `/opt/homebrew/`에, Intel Mac은 `/usr/local/`에 설치되어 PATH 설정 명령이 서로 다릅니다. 아래 두 갈래 중 자기 기종에 맞는 쪽을 따라가면 됩니다.

### Apple Silicon (M1/M2/M3) — PATH 설정

Apple Silicon Mac은 Homebrew 설치 경로가 `/opt/homebrew/`입니다. 설치 완료 후 아래 명령으로 PATH를 설정합니다.

> **PATH란?** 터미널이 "어느 폴더에서 명령어를 찾을지" 적어 둔 목록입니다. 방금 설치한 `brew`가 있는 폴더를 이 목록에 등록해야, 어느 위치에서든 `brew` 명령이 동작합니다.

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

## 3단계: Git 설정

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

## 4단계: 추가 유틸리티 설치

```bash
# wget (curl은 macOS 기본 내장)
brew install wget

# 설치 확인
curl --version | head -1
wget --version | head -1
```

<hr>

## 5단계: Docker Desktop 설치

macOS에서 Docker를 쓰는 표준 방법은 **Docker Desktop**입니다. Intel Mac과 Apple Silicon 모두 지원하며, GUI 관리 도구를 포함합니다.

### 5-1. 설치 방법 선택

**방법 A — Homebrew (권장)**

```bash
brew install --cask docker
```

설치 후 애플리케이션 폴더에서 **Docker** 앱을 실행합니다.

**방법 B — 직접 다운로드**

[docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) 에서 자신의 칩에 맞는 설치 파일을 내려받습니다.

| 기종 | 다운로드 선택 |
|------|-------------|
| Apple Silicon (M1/M2/M3) | **Mac with Apple Chip** |
| Intel Mac | **Mac with Intel Chip** |

`.dmg` 파일을 열고 Docker 아이콘을 Applications 폴더로 드래그합니다.

> **주의 — Apple Silicon 유의사항**: 이 책에서 사용하는 `ubuntu:22.04` 이미지는 x86(amd64) 아키텍처입니다. Apple Silicon에서는 **QEMU 에뮬레이션**으로 실행되며 실행 속도가 네이티브 대비 느릴 수 있습니다. 기능 자체는 동작합니다.

### 5-2. Docker Desktop 최초 실행

설치 후 **Docker Desktop 앱을 실행**합니다. 메뉴바(상단 우측)에 고래 🐳 아이콘이 나타나면 Docker 엔진이 시작된 것입니다.

처음 실행 시 이용 약관 동의 화면이 나타납니다. **Accept** 를 선택합니다.

### 5-3. 터미널에서 확인

```bash
docker --version
```

출력 예시:
```
Docker version 29.3.1, build ...
```

```bash
docker run hello-world
```

`Hello from Docker!` 메시지가 출력되면 설치 완료입니다.

> `docker: command not found` 오류가 나면 Docker Desktop 앱이 실행 중인지 확인하세요. 메뉴바 고래 아이콘이 회전 중이면 엔진이 시작 중입니다. 완전히 멈출 때까지 기다린 뒤 다시 시도하세요.

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

### macOS 방화벽 설정

Remote Control 기능 사용 시 macOS 방화벽에서 연결을 허용해야 합니다. **시스템 환경설정 → 보안 및 개인 정보 보호 → 방화벽** 에서 Docker를 허용 목록에 추가합니다.

<hr>

## 원클릭 설치 스크립트

macOS 호스트 환경 기본 설정을 한 번에 처리합니다. Node.js·tmux·Claude Code는 02-5 컨테이너 단계에서 설치합니다.

```bash
#!/bin/bash
set -e

echo "=== macOS 호스트 환경 설치 시작 ==="

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

# 기본 도구 (컨테이너 내부 도구는 02-5에서 설치)
brew install git wget

# Docker Desktop
if ! command -v docker &>/dev/null; then
  echo "Docker Desktop 설치 중 (cask)..."
  brew install --cask docker
  echo "Docker Desktop 앱을 Applications에서 한 번 실행한 뒤 다시 확인하세요."
fi

echo ""
echo "=== 호스트 기본 설치 완료 ==="
echo "  git:  $(git --version | cut -d' ' -f3)"
echo "  brew: $(brew --version | head -1)"
echo ""
echo "다음 단계:"
echo "  1. Docker Desktop 앱을 실행하여 메뉴바 고래 아이콘을 확인"
echo "  2. docker run hello-world 로 연동 확인"
echo "  3. 02-4 Docker 이해로 이동"
```

저장 후 실행:

```bash
chmod +x install-host.sh
./install-host.sh
```

<hr>

## 설치 확인 체크리스트

```bash
brew --version    # Homebrew 4.x.x
git --version     # 2.x.x
docker --version  # Docker version 29.x.x 이상
docker run hello-world  # Hello from Docker! 출력
```

모든 항목이 정상이면 다음 단계로 넘어갑니다.

<hr>

## 다음 단계: 02-4 Docker 이해

호스트(macOS + Docker Desktop) 준비가 완료됐습니다. 이제 Docker의 개념을 익힌 뒤, 컨테이너를 기동해 Claude Code·tmux를 설치합니다.

[02-4. Docker 이해](02-4-docker-concept.md)로 이동하세요.
