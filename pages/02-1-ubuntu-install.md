## 02-1. 환경 설치 — 플랫폼 선택

Claude Code 멀티에이전트 환경은 Ubuntu Linux 기반에서 동작합니다. 사용 중인 운영체제에 맞는 가이드를 선택하세요.

처음 개발 환경을 구성한다면 낯선 용어가 많이 보일 수 있습니다. 하지만 걱정하지 마세요. 이 책은 명령어 한 줄마다 "무엇을, 왜" 하는지 함께 설명합니다. 순서대로 따라 하기만 하면 됩니다.

> 💡 **운영체제(OS)란?** 컴퓨터를 움직이는 기본 소프트웨어입니다. Windows, macOS, Linux가 대표적입니다. Claude Code는 Linux 환경에서 가장 안정적으로 동작하기 때문에, Windows·macOS 사용자도 각자 환경 위에 Linux와 비슷한 환경을 얹어 사용합니다.

출발점은 Windows·macOS·Linux로 셋이지만, 도착점은 모두 같은 **Ubuntu Linux 환경** 하나입니다. Windows는 WSL2로, macOS는 Homebrew 터미널로 각자 다른 길을 거칠 뿐, 그 길들은 결국 한 지점에서 만납니다. 일단 Ubuntu 환경에 올라서면 3장부터의 과정은 OS와 상관없이 똑같아집니다. 그러니 지금은 자신의 OS에 맞는 한 갈래만 고르면 됩니다.

> 💡 **왜 Ubuntu인가?** Ubuntu는 Linux 배포판 중 사용자 수가 가장 많고, 공식 문서와 커뮤니티가 활발합니다. 새로운 개발 도구가 출시되면 Ubuntu 지원이 가장 먼저, 가장 안정적으로 제공됩니다. Claude Code 역시 Ubuntu 환경을 기준으로 배포·테스트됩니다.

<hr>

## 플랫폼별 설치 가이드

자신의 컴퓨터 운영체제에 해당하는 길을 따라가세요. 아래 세 갈래 중 하나만 선택하면 됩니다.

### Windows 사용자 → [02-2. WSL2 환경 구성 완전 가이드](02-2-windows-wsl2.md)

WSL2(Windows Subsystem for Linux 2)를 통해 Windows 위에서 Ubuntu 환경을 구성합니다. 쉽게 말해, Windows를 끄지 않고도 그 안에서 진짜 Linux를 함께 돌리는 기능입니다.

- WSL2 활성화 → Ubuntu 설치 → Node.js/Git/TMUX → Claude Code

> 💡 **WSL2는 가상머신과 다릅니다.** 가상머신(VM)은 하드웨어를 통째로 흉내 내기 때문에 느립니다. WSL2는 Windows 커널과 직접 통합되어 진짜 Linux처럼 빠르고, 파일 시스템도 Windows와 공유됩니다. Windows 10 버전 2004 이상, Windows 11에 기본 탑재되어 별도 비용 없이 사용할 수 있습니다.

### macOS 사용자 → [02-3. macOS 설치 완전 가이드](02-3-macos.md)

Homebrew를 사용해 기본 터미널(zsh) 환경에서 바로 구성합니다. Homebrew는 macOS에서 개발 도구를 손쉽게 설치해 주는 "앱 설치 도우미"라고 생각하면 됩니다.

- Homebrew → Node.js/Git/TMUX → Claude Code

> 💡 **macOS는 이미 Unix 기반입니다.** macOS는 내부적으로 Unix 운영체제 위에서 동작합니다. 그래서 Linux 명령어 대부분이 macOS 터미널에서도 그대로 작동합니다. Homebrew는 Linux의 `apt`와 비슷한 역할을 macOS에서 담당합니다.

### Linux 사용자 → 이 페이지에서 계속

Ubuntu 22.04 이상 또는 Debian 계열 배포판을 이미 사용 중이라면 아래 단계를 따릅니다.

<hr>

## Linux 네이티브 설치

아래 5단계를 순서대로 진행합니다. 각 명령은 터미널(검은 화면의 명령 입력 창)에 붙여 넣고 Enter를 누르면 실행됩니다. 한 단계가 끝난 뒤 다음 단계로 넘어가세요.

아래로 이어지는 다섯 단계는 ① 패키지 목록 최신화 → ② 기본 유틸리티 설치 → ③ Node.js 설치 → ④ Claude Code 설치 → ⑤ 최초 인증 순서입니다. 앞 단계가 끝나야 다음 단계가 의미를 가지므로, 건너뛰지 말고 위에서 아래로 하나씩 실행하세요.

### 1단계. 패키지 목록 최신화

설치를 시작하기 전에, 시스템이 알고 있는 프로그램 목록을 최신 상태로 새로고침합니다. 오래된 목록으로 설치하면 옛 버전이 깔리거나 오류가 날 수 있습니다.

```bash
sudo apt update && sudo apt upgrade -y
```

> 💡 `sudo`는 "관리자 권한으로 실행"이라는 뜻이고, `apt`는 우분투의 프로그램 설치 도구입니다. `update`는 목록 새로고침, `upgrade -y`는 설치된 프로그램들을 최신 버전으로 올리는 명령입니다(`-y`는 "예"를 미리 답해 자동 진행).

> 💡 **apt를 "앱스토어 카탈로그"로 생각하세요.** `apt update`는 카탈로그를 새로고침하는 것이고, `apt upgrade`는 이미 설치된 앱들을 최신 버전으로 업데이트하는 것입니다. 카탈로그를 새로고침해야 최신 버전을 받을 수 있기 때문에, 이 두 명령은 항상 세트로 함께 씁니다.

이 명령을 실행하면 화면에 여러 줄이 스크롤됩니다. 마지막에 `0 upgraded, 0 newly installed` 같은 메시지가 나오면 완료입니다. 중간에 비밀번호를 물어볼 수 있는데, 계정 비밀번호를 입력하면 됩니다. 입력 중 화면에 아무것도 표시되지 않는 것이 정상입니다 — 보안상 일부러 숨기는 것입니다.

### 2단계. 기본 유틸리티 설치

이후 작업에 필요한 기본 도구들을 한 번에 설치합니다.

```bash
sudo apt install -y git curl wget unzip build-essential tmux
```

> 💡 `git`은 버전 관리, `curl`·`wget`은 인터넷에서 파일 받기, `unzip`은 압축 풀기, `build-essential`은 프로그램을 빌드할 때 필요한 도구 모음, `tmux`는 화면을 여러 칸으로 나누는 도구입니다(멀티에이전트 팀 구성의 핵심).

각 도구의 역할을 좀 더 구체적으로 살펴보면 다음과 같습니다.

| 도구 | 역할 | 비유 |
|------|------|------|
| `git` | 코드 버전 관리 | 파일의 "무한 되돌리기" 기록장 |
| `curl` | URL로 파일 다운로드 | 주소를 입력하면 파일을 가져오는 택배 |
| `wget` | URL로 파일 다운로드 (이어받기 지원) | 중단 후 재시작이 되는 택배 |
| `unzip` | ZIP 파일 압축 해제 | 파일 압축 풀기 도구 |
| `build-essential` | C/C++ 컴파일러 모음 | 프로그램을 직접 빌드할 때 필요한 공구함 |
| `tmux` | 터미널 화면 분할 및 세션 관리 | 하나의 모니터를 여러 칸으로 나누는 리모컨 |

`build-essential`은 당장 직접 쓸 일이 없더라도, Node.js 패키지 중 일부는 설치 중 C++ 코드를 직접 컴파일하는 경우가 있습니다. 미리 설치해 두지 않으면 그 순간 오류가 납니다.

### 3단계. Node.js 설치 (nvm 권장)

Claude Code는 Node.js라는 실행 환경 위에서 동작합니다. 버전 관리가 편한 nvm으로 설치하는 것을 권장합니다.

```bash
# nvm 설치
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.5/install.sh | bash
source ~/.bashrc

# Node.js LTS
nvm install --lts
nvm use --lts

# 확인
node --version
npm --version
```

> 💡 nvm(Node Version Manager)은 Node.js 버전을 자유롭게 바꿔 쓰게 해 줍니다. `LTS`는 "오래 안정적으로 지원되는 버전(Long Term Support)"이라는 뜻으로, 초보자에게 가장 안전한 선택입니다. `source ~/.bashrc`는 방금 설치한 nvm을 현재 터미널에 즉시 적용하는 명령입니다.

> 💡 **왜 `apt`가 아닌 nvm으로 설치하나요?** `sudo apt install nodejs`로 설치하면 Ubuntu 기본 저장소의 오래된 버전이 설치되는 경우가 많습니다. Claude Code는 Node.js 18 이상이 필요한데, 기본 저장소에는 그보다 낮은 버전이 있을 수 있습니다. nvm은 항상 최신 LTS를 정확히 설치해 주고, 나중에 버전을 바꾸거나 여러 버전을 나란히 관리하기도 쉽습니다.

`source ~/.bashrc`는 셸(터미널)의 설정 파일을 현재 창에 다시 불러오는 명령입니다. nvm은 설치 시 `~/.bashrc` 파일에 자신의 경로를 추가하는데, 새 터미널을 열면 자동으로 읽히지만 지금처럼 같은 창에서 계속 진행할 때는 이 명령으로 즉시 적용해야 `nvm` 명령이 바로 인식됩니다.

### 4단계. Claude Code 설치

이제 핵심인 Claude Code를 설치합니다.

```bash
npm install -g @anthropic-ai/claude-code

# 확인
claude --version
```

> 💡 `npm`은 Node.js의 패키지 설치 도구이고, `-g`는 "global(전역)"의 약자로 어느 폴더에서든 `claude` 명령을 쓸 수 있게 설치한다는 뜻입니다. 설치 후 `claude --version`으로 버전 번호가 출력되면 성공입니다.

> 💡 **`@anthropic-ai/claude-code` 이름의 의미**: `@anthropic-ai`는 이 패키지를 만든 조직(Anthropic)을 나타내고, `claude-code`가 패키지 이름입니다. npm에서 `@조직명/패키지명` 형태를 "스코프 패키지"라고 부르며, Anthropic이 공식 배포한 Claude Code임을 식별하는 방법입니다.

### 5단계. 최초 인증

설치가 끝나면 Claude Code를 처음 실행해 로그인합니다.

```bash
claude
```

처음 실행하면 몇 가지 확인 질문이 차례로 나옵니다. 순서대로 선택하세요.

1. `Yes, I trust this folder` 선택 — 현재 폴더를 신뢰할지 묻는 질문
2. `Yes, I accept` 선택 — 이용 약관 동의
3. `Login with claude.ai (recommended)` 선택 — 브라우저가 열리며 로그인 진행

세 질문 모두 화면에 나온 순서대로 선택하면 됩니다 — 신뢰(trust) → 동의(accept) → 로그인(login)으로 이어지는 한 방향 흐름이라 되돌아갈 일은 없습니다. 마지막 로그인 단계에서 브라우저가 자동으로 열리니, 평소 쓰는 claude.ai 계정으로 로그인하면 터미널로 돌아와 인증이 마무리됩니다.

> 💡 **브라우저가 없는 서버 환경이라면**: SSH로 접속한 서버처럼 화면이 없는 환경에서는 브라우저가 열리지 않고, 인증 URL이 터미널에 텍스트로 출력됩니다. 그 URL을 로컬 PC의 브라우저에서 열어 로그인하면 됩니다.

<hr>

## 설치 확인

모든 설치가 끝났다면, 아래 명령으로 각 도구가 제대로 깔렸는지 한 번에 확인합니다. 버전 번호가 출력되면 정상입니다.

```bash
node --version    # v18.0.0 이상
npm --version     # 9.0.0 이상
git --version     # 2.x.x
tmux -V           # tmux 3.x
claude --version  # claude-code x.x.x
```

> 💡 만약 `command not found`가 나온다면 해당 도구가 설치되지 않았거나, 터미널을 새로 열어야 PATH가 적용되는 경우입니다. 터미널을 닫았다 다시 연 뒤 다시 확인해 보세요.

### 자주 겪는 문제와 해결법

| 증상 | 원인 | 해결 |
|------|------|------|
| `nvm: command not found` | `source ~/.bashrc` 미실행 | `source ~/.bashrc` 후 재시도 |
| `claude: command not found` | npm 전역 경로 미등록 | 터미널 재시작 후 재시도 |
| `npm ERR! code EACCES` | sudo로 npm 실행한 흔적 | nvm 통해 Node.js 재설치 |
| `node --version`이 구버전 | 시스템 Node와 nvm Node 충돌 | `nvm use --lts` 실행 |

> 💡 `npm install -g`에서 권한 오류가 나더라도 절대 `sudo npm install -g`를 쓰지 마세요. sudo로 설치하면 파일 소유권이 꼬여서 이후에도 계속 오류가 납니다. nvm으로 Node.js를 새로 설치하면 권한 문제 없이 해결됩니다.

플랫폼별 환경이 준비되었으면 다음 챕터에서 TMUX 구조와 멀티에이전트 팀을 구성합니다.
