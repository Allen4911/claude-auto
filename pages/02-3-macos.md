## 02-3. macOS: 설치 완전 가이드

macOS에서는 기본 터미널(zsh)에서 바로 호스트 환경을 구성하고, Claude Code를 호스트에 직접 설치해 운영합니다.

> **이 페이지 범위**: Homebrew 설치 → Git·기본 유틸리티 설치까지. Claude Code·tmux는 호스트에 직접 설치합니다(02-4·02-5).

> **지원 버전**: macOS 13 Ventura 이상을 권장합니다. Intel Mac과 Apple Silicon(M1/M2/M3) 모두 지원됩니다.

> **Homebrew를 쉽게 말하면?** macOS용 "앱 설치 도우미"입니다. 평소 앱은 App Store에서 받지만, 개발 도구는 터미널에서 `brew install 도구이름` 한 줄로 깔 수 있게 해 줍니다. 이 페이지는 Homebrew로 필요한 도구들을 차례로 설치합니다.

> 아래는 이 페이지에서 진행할 전체 흐름입니다. 1→4단계를 순서대로 따라가면 됩니다.

**개발 토대(Xcode 도구·Homebrew)를 깔고**(1~2단계), **Git과 기본 유틸리티를 설치**합니다(3~4단계). 이후 Claude Code·tmux는 02-4·02-5에서 호스트에 직접 설치합니다.

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

Remote Control 기능 사용 시 macOS 방화벽에서 연결을 허용해야 합니다. **시스템 환경설정 → 보안 및 개인 정보 보호 → 방화벽** 에서 해당 포트를 허용 목록에 추가합니다.

<hr>

## 원클릭 설치 스크립트

macOS 호스트 환경 기본 설정을 한 번에 처리합니다.

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

# 기본 도구
brew install git wget

echo ""
echo "=== 호스트 기본 설치 완료 ==="
echo "  git:  $(git --version | cut -d' ' -f3)"
echo "  brew: $(brew --version | head -1)"
echo ""
echo "다음 단계: 02-4로 이동하여 Claude Code를 설치하고 인증하세요."
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
```

모든 항목이 정상이면 다음 단계로 넘어갑니다.

<hr>

## 다음 단계: 02-4 호스트에 Claude Code 설치

macOS 호스트 준비가 완료됐습니다. 이제 Claude Code를 직접 설치하고 인증합니다.

[02-4. 호스트에 Claude Code 설치·인증](02-4-host-claude-install.md)으로 이동하세요.
