## 02-1. 환경 설치 — 플랫폼 선택

Claude Code 멀티에이전트 환경은 Ubuntu Linux 기반에서 동작합니다. 사용 중인 운영체제에 맞는 가이드를 선택하세요.

처음 개발 환경을 구성한다면 낯선 용어가 많이 보일 수 있습니다. 이 책은 명령어 한 줄마다 "무엇을, 왜" 하는지 함께 설명합니다. 순서대로 따라가면 됩니다.

> **운영체제(OS)란?** 컴퓨터를 움직이는 기본 소프트웨어입니다. Windows, macOS, Linux가 대표적입니다. Claude Code는 Linux 환경에서 가장 안정적으로 동작하기 때문에, Windows·macOS 사용자도 각자 환경 위에 Linux와 비슷한 환경을 얹어 사용합니다.

출발점은 Windows·macOS·Linux로 셋이지만, 도착점은 모두 같은 **Docker 컨테이너 안의 Ubuntu 22.04** 하나입니다. 플랫폼마다 Docker를 준비하는 방법이 조금씩 다를 뿐, 컨테이너 안에서 Node.js·Claude Code를 설치하는 단계부터는 모두 동일합니다.

> **왜 Docker인가?** Docker는 OS와 무관하게 동일한 Ubuntu 22.04 환경을 재현합니다. 호스트 OS에 직접 설치하면 플랫폼마다 경로·버전·권한 문제가 달라지지만, 컨테이너 안에서는 어디서나 같은 명령이 같은 결과를 냅니다. 팀 전원이 동일한 이미지를 쓰므로 "내 컴퓨터에서는 됐는데"라는 말이 나오지 않습니다.

<hr>

## 플랫폼별 설치 가이드

자신의 컴퓨터 운영체제에 해당하는 길을 따라가세요. 아래 세 갈래 중 하나만 선택하면 됩니다.

### Windows 사용자 → [02-2. WSL2 환경 구성 완전 가이드](02-2-windows-wsl2.md)

WSL2(Windows Subsystem for Linux 2)를 통해 Docker Desktop을 설치합니다.

- WSL2 활성화 → Docker Desktop(WSL2 backend) 설치 → 02-4 Docker 이해·컨테이너 기동 → 02-5 Claude Code 설치

> **WSL2는 가상머신과 다릅니다.** 가상머신(VM)은 하드웨어를 통째로 흉내 내기 때문에 느립니다. WSL2는 Windows 커널과 직접 통합되어 진짜 Linux처럼 빠르고, 파일 시스템도 Windows와 공유됩니다. Windows 10 버전 2004 이상, Windows 11에 기본 탑재되어 별도 비용 없이 사용할 수 있습니다.

### macOS 사용자 → [02-3. macOS 설치 완전 가이드](02-3-macos.md)

Docker Desktop(Intel/Apple Silicon 공통)을 설치합니다.

- Docker Desktop 설치 → 02-4 Docker 이해·컨테이너 기동 → 02-5 Claude Code 설치

> **macOS는 이미 Unix 기반입니다.** macOS는 내부적으로 Unix 운영체제 위에서 동작합니다. Docker Desktop for Mac은 Apple Silicon(M1/M2)과 Intel 모두 지원하며, 설치 후 바로 `docker` 명령을 사용할 수 있습니다.

### Linux(Ubuntu) 사용자 → 이 페이지에서 계속

Ubuntu 22.04 이상 또는 Debian 계열 배포판을 이미 사용 중이라면 아래 단계를 따릅니다.

<hr>

## Linux 호스트 준비

아래 3단계를 순서대로 진행합니다. 이 단계는 **호스트(Ubuntu 본체)를 준비하는 과정**입니다. Node.js와 Claude Code는 이후 Docker 컨테이너 안에서 설치하므로 여기서는 다루지 않습니다.

순서는 ① 패키지 목록 최신화 → ② 기본 유틸리티 설치 → ③ Docker Engine 설치입니다.

### 1단계. 패키지 목록 최신화

설치를 시작하기 전에, 시스템이 알고 있는 프로그램 목록을 최신 상태로 새로고침합니다. 오래된 목록으로 설치하면 옛 버전이 깔리거나 오류가 날 수 있습니다.

```bash
sudo apt update && sudo apt upgrade -y
```

> `sudo`는 "관리자 권한으로 실행"이라는 뜻이고, `apt`는 우분투의 프로그램 설치 도구입니다. `update`는 목록 새로고침, `upgrade -y`는 설치된 프로그램들을 최신 버전으로 올리는 명령입니다(`-y`는 "예"를 미리 답해 자동 진행).

이 명령을 실행하면 화면에 여러 줄이 스크롤됩니다. 마지막에 `0 upgraded, 0 newly installed` 같은 메시지가 나오면 완료입니다. 중간에 비밀번호를 물어볼 수 있는데, 계정 비밀번호를 입력하면 됩니다. 입력 중 화면에 아무것도 표시되지 않는 것이 정상입니다 — 보안상 일부러 숨기는 것입니다.

### 2단계. 기본 유틸리티 설치

이후 Docker 설치와 작업에 필요한 기본 도구들을 한 번에 설치합니다.

```bash
sudo apt install -y git curl wget unzip build-essential tmux
```

> `git`은 버전 관리, `curl`·`wget`은 인터넷에서 파일 받기, `unzip`은 압축 풀기, `build-essential`은 프로그램을 빌드할 때 필요한 도구 모음, `tmux`는 화면을 여러 칸으로 나누는 도구입니다.

각 도구의 역할을 좀 더 구체적으로 살펴보면 다음과 같습니다.

| 도구 | 역할 | 비유 |
|------|------|------|
| `git` | 코드 버전 관리 | 파일의 "무한 되돌리기" 기록장 |
| `curl` | URL로 파일 다운로드 | 주소를 입력하면 파일을 가져오는 택배 |
| `wget` | URL로 파일 다운로드 (이어받기 지원) | 중단 후 재시작이 되는 택배 |
| `unzip` | ZIP 파일 압축 해제 | 파일 압축 풀기 도구 |
| `build-essential` | C/C++ 컴파일러 모음 | 프로그램을 직접 빌드할 때 필요한 공구함 |
| `tmux` | 터미널 화면 분할 및 세션 관리 | 하나의 모니터를 여러 칸으로 나누는 리모컨 |

> **호스트에도 tmux를 설치하는 이유**: 컨테이너 안에서도 tmux를 별도로 설치하지만, 호스트 tmux는 `docker exec` 세션을 여러 창으로 나눠 관리하거나 Docker 명령을 나란히 실행할 때 유용합니다.

### 3단계. Docker Engine 설치

공식 Docker apt 저장소를 통해 Docker Engine을 설치합니다.

> **`curl | sh` 편의 스크립트는 쓰지 않습니다.** `curl -fsSL https://get.docker.com | sh` 형태의 원라이너 스크립트가 있지만, Docker 공식 문서에서 "프로덕션 환경에 비권장"으로 명시합니다. 아래 수동 절차가 더 안전하고 문제가 생겼을 때 원인을 파악하기 쉽습니다.

```bash
# 1. 기존 충돌 패키지 제거 (없으면 무시)
sudo apt remove docker.io docker-compose docker-compose-v2 \
    docker-doc podman-docker containerd runc 2>/dev/null || true

# 2. Docker 공식 GPG 키 + apt 저장소 등록
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 3. Docker Engine 설치
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

# 4. sudo 없이 사용 (로그아웃 후 재로그인 필요)
sudo usermod -aG docker $USER
newgrp docker
```

각 단계가 하는 일을 순서대로 설명합니다.

| 단계 | 설명 |
|------|------|
| 충돌 패키지 제거 | 오래된 비공식 Docker 패키지가 있으면 먼저 지웁니다. 없어도 오류 없이 넘어갑니다. |
| GPG 키 등록 | Docker의 공식 서명 키를 내려받아 `keyrings` 폴더에 저장합니다. apt가 이 키로 패키지 출처를 검증합니다. |
| apt 저장소 등록 | Docker 공식 저장소 주소를 시스템에 추가합니다. `$VERSION_CODENAME`은 Ubuntu 버전 코드명(jammy 등)으로 자동 치환됩니다. |
| Docker Engine 설치 | `docker-ce`(컨테이너 엔진), `docker-ce-cli`(명령줄 도구), `containerd.io`(런타임), `buildx`(빌드 확장), `compose`(다중 컨테이너)를 한 번에 설치합니다. |
| docker 그룹 추가 | 매번 `sudo docker` 대신 `docker`만 입력하도록 현재 사용자를 docker 그룹에 추가합니다. `newgrp docker`로 재로그인 없이 즉시 적용합니다. |

> **`newgrp docker`란?** 사용자를 docker 그룹에 추가한 뒤 그 변경을 현재 터미널 세션에 즉시 반영하는 명령입니다. 로그아웃 후 재로그인과 동일한 효과를 냅니다. 이 명령 없이는 새 터미널을 열거나 재로그인해야 `sudo` 없는 `docker` 명령이 작동합니다.

<hr>

## Docker 설치 확인

설치가 끝났으면 아래 명령으로 Docker가 정상 동작하는지 확인합니다.

```bash
docker run hello-world
```

출력 예시:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

`Hello from Docker!` 메시지가 보이면 설치 성공입니다. 이 명령은 `hello-world` 이미지를 내려받아 컨테이너를 실행하고 메시지를 출력한 뒤 자동으로 종료합니다.

### 자주 겪는 문제와 해결법

| 증상 | 원인 | 해결 |
|------|------|------|
| `permission denied while trying to connect` | docker 그룹 미적용 | `newgrp docker` 또는 터미널 재시작 |
| `Cannot connect to the Docker daemon` | dockerd 서비스 미실행 | `sudo systemctl start docker` |
| `docker: command not found` | 설치 미완료 | 3단계 재실행 |

> `sudo systemctl enable docker`를 한 번 실행해 두면 재부팅 시 Docker 데몬이 자동으로 시작됩니다.

<hr>

## 다음 단계

Ubuntu 호스트에 Docker Engine 설치가 완료되었습니다. 이제부터 **모든 작업은 이 호스트 위에서 Docker로 `ubuntu:22.04` 컨테이너를 띄운 뒤 그 안에서** 진행합니다. Node.js와 Claude Code는 컨테이너 내부에 설치하므로 호스트에 따로 설치할 필요가 없습니다. tmux는 호스트와 컨테이너 양쪽에 두되, 호스트에서는 `docker exec` 세션 관리용으로, 컨테이너 안에서는 멀티에이전트 파인 분할용으로 각각 사용합니다.

**[02-4. Docker 이해 →](02-4-docker-concept.md)**
