## 02-4. Docker 컨테이너 기동 + 내부 Claude Code 설치

플랫폼별 Docker 준비(02-1~02-3)가 끝났습니다. 이제부터는 **모든 플랫폼이 동일한 경로**를 걷습니다. `ubuntu:22.04` 컨테이너를 띄우고, 그 안에 Node.js와 Claude Code를 설치합니다.

> **컨테이너가 호스트와 분리되는 이유**: 컨테이너는 호스트 OS와 격리된 독립 공간입니다. Node.js, Claude Code를 호스트에 직접 설치하면 버전 충돌이나 경로 문제가 생길 수 있지만, 컨테이너 안에서는 항상 깨끗한 Ubuntu 22.04 환경에서 시작합니다. 여러 사람이 같은 이미지로 동일한 환경을 재현합니다.

<hr>

## 컨테이너 기동

### 즉시 체험 (1회성)

Docker가 정상 설치됐는지 확인하면서 Ubuntu 22.04 환경을 바로 체험할 수 있습니다.

```bash
docker run --rm -it ubuntu:22.04 bash
```

처음 실행하면 이미지를 자동으로 내려받습니다.

```
Unable to find image 'ubuntu:22.04' locally
22.04: Pulling from library/ubuntu
...
PRETTY_NAME="Ubuntu 22.04.5 LTS"
```

> `--rm`은 컨테이너 종료 시 자동 삭제, `-it`는 인터랙티브 터미널 연결입니다. 이 방식은 실험용이며, `exit`로 나오면 컨테이너와 내부에 설치한 모든 것이 사라집니다.

### 지속 실행 (실전)

작업이 유지되는 지속 컨테이너를 만듭니다. 이 방식으로 Claude Code를 설치하고 운영합니다.

```bash
# 컨테이너 생성 (백그라운드 실행)
docker run -d --name claude-env \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -v "$HOME/project":/workspace \
  ubuntu:22.04 sleep infinity

# 컨테이너 내부로 진입
docker exec -it claude-env bash
```

각 옵션이 하는 일을 살펴봅니다.

| 옵션 | 의미 |
|------|------|
| `-d` | 백그라운드(detached)로 실행 — 터미널을 점유하지 않음 |
| `--name claude-env` | 컨테이너에 이름 부여 — 이후 `docker exec`로 재진입 가능 |
| `-e ANTHROPIC_API_KEY=...` | 환경변수로 API 키 주입 — 컨테이너 인증의 핵심 |
| `-v "$HOME/project":/workspace` | 호스트 폴더를 컨테이너 `/workspace`에 연결 |
| `sleep infinity` | 컨테이너가 종료되지 않고 대기하도록 유지 |

> **주의** **`-v` 없이 작업하면 파일을 잃습니다.** `-v` 볼륨 마운트 없이 컨테이너 안에서 파일을 만들면, `docker rm`으로 컨테이너를 삭제하는 순간 내부 파일이 전량 소실됩니다. 작업물은 반드시 `/workspace` (호스트 볼륨)에 저장하세요.

> **`$HOME/project` 폴더가 없다면** 먼저 `mkdir -p ~/project`로 만들어 두세요. 마운트 대상 폴더가 없으면 Docker가 빈 디렉터리를 자동 생성하지만, 미리 만들어 두는 것이 안전합니다.

<hr>

## 컨테이너 내부 설치

`docker exec -it claude-env bash`로 컨테이너에 진입한 상태에서 아래 명령을 순서대로 실행합니다.

### 1단계. 기본 도구 설치

```bash
apt-get update
apt-get install -y curl ca-certificates git
```

> `ubuntu:22.04` 이미지는 최소 구성으로 배포됩니다. `curl`, `git` 등 익숙한 도구들이 기본으로 들어있지 않아 먼저 설치해야 합니다. tmux는 다음 챕터(02-5)에서 멀티파인 환경과 함께 설치합니다.

### 2단계. Node.js 22 설치 (nodesource 경유)

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs
```

설치 확인:
```bash
node --version   # v22.22.3
npm --version    # 10.9.8
```

> **왜 `apt-get install nodejs`를 직접 쓰지 않나요?** Ubuntu 22.04 기본 저장소의 Node.js는 오래된 버전(12.x)입니다. Claude Code는 Node.js 18 이상이 필요합니다. nodesource 스크립트는 Node.js 공식 팀이 관리하는 저장소를 등록해 현재 안정 버전(22.x)을 설치해 줍니다.

### 3단계. Claude Code 설치

```bash
npm install -g @anthropic-ai/claude-code
```

설치 확인:
```bash
claude --version   # 2.1.181 (Claude Code)
```

> 컨테이너 내부는 root 사용자로 실행되므로 `-g` 전역 설치에 `sudo`가 필요 없습니다. `npm ERR! code EACCES` 오류가 나지 않는 것이 정상입니다.

<hr>

## 인증 — API 키 주입 방식

> **주의** **컨테이너 안에서 `/login` 브라우저 인증은 불가능합니다.** 컨테이너에는 브라우저가 없기 때문에 `claude` 실행 시 `/login`을 선택해도 인증이 완료되지 않습니다. 컨테이너에서 Claude Code를 인증하는 **유일한 실용적 방법은 `ANTHROPIC_API_KEY` 환경변수 주입**입니다.

API 키는 컨테이너 기동 시 `-e` 옵션으로 주입합니다.

```bash
docker run -d --name claude-env \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  ...
```

컨테이너 내부에서 환경변수가 제대로 들어왔는지 확인합니다.

```bash
echo $ANTHROPIC_API_KEY
```

`sk-ant-...`로 시작하는 키 값이 출력되면 주입 성공입니다. API 키가 없거나 잘못된 경우 Claude Code 실행 시 아래 메시지가 나타납니다.

```
Not logged in · Please run /login
```

> **API 키 발급 위치**: Anthropic Console(`console.anthropic.com`) → API Keys 탭 → Create Key. 키는 `sk-ant-`로 시작합니다.

### Dockerfile에 API 키를 하드코딩하지 마세요

```dockerfile
# ❌ 절대 이렇게 하지 마세요
ENV ANTHROPIC_API_KEY="sk-ant-..."

# ✅ 올바른 방법: docker run 시 -e로 주입
```

Dockerfile에 키를 박으면 `docker build`로 생성된 이미지에 키가 영구적으로 포함됩니다. 이미지를 Docker Hub에 push하거나 공유하는 순간 키가 유출됩니다. 키는 항상 실행 시점에 `-e`로 전달하세요.

<hr>

## Claude Code 실행

컨테이너 내부에서 Claude Code를 시작합니다.

```bash
claude --dangerously-skip-permissions
```

> **`--dangerously-skip-permissions` 플래그**: Claude Code는 파일 쓰기·명령 실행 등 위험한 작업 전 사용자에게 확인을 요청합니다. 멀티에이전트 자동화 환경에서는 6개의 에이전트가 자동으로 동작하므로 매번 사람이 확인하면 자동화가 불가능합니다. 신뢰하는 컨테이너 환경에서만 이 플래그를 사용하세요.

처음 실행하면 아래 두 가지 화면이 차례로 나타납니다.

**폴더 신뢰 확인:**
```
Do you trust the files in this folder?
> Yes, I trust this folder (proceed)
  No, exit
```
Enter를 눌러 진행합니다.

**이용 약관 동의:**
```
Do you accept the terms of service?
  No, exit
> Yes, I accept
```
방향키 ↓로 `Yes, I accept`를 선택한 뒤 Enter를 누릅니다.

두 화면을 통과하면 Claude 프롬프트(`>`)가 나타납니다.

```
> Hello! What can I help you with?
```

`>` 프롬프트가 보이면 인증 및 실행 완료입니다. `/exit` 또는 `Ctrl+C` 두 번으로 종료합니다.

<hr>

## 모델 설정

기본 모델은 Claude Sonnet입니다. 다른 모델로 시작하려면 `--model` 플래그를 사용합니다.

```bash
# Sonnet (기본, 속도·비용 균형)
claude --model claude-sonnet-4-6

# Opus (고성능, 복잡한 작업)
claude --model claude-opus-4-8

# Haiku (경량, 빠른 응답)
claude --model claude-haiku-4-5-20251001
```

모델별 특성을 정리하면 다음과 같습니다.

| 모델 | 특성 | 적합한 작업 |
|------|------|------------|
| Sonnet | 속도와 품질의 균형 | 일반 코딩, 파일 편집, 대화 |
| Opus | 최고 성능, 느리고 비용 높음 | 복잡한 설계, 다단계 추론 |
| Haiku | 가장 빠르고 저렴 | 단순 질문, 반복 작업 |

멀티에이전트 팀에서는 역할별로 모델을 다르게 배정합니다. 팀장(쭌)·PM(민준)처럼 설계·판단·조율이 많은 역할에는 Opus를, 실행 중심 팀원(지훈·수아·서연·태양)에는 Sonnet을 사용합니다. 역할별로 모델을 섞어 쓰면 비용과 성능을 함께 잡습니다.

<hr>

## 파일 영속성 요약

컨테이너 환경에서 데이터가 어떻게 유지되는지 한눈에 정리합니다.

| 데이터 | 보존 방법 | `docker rm` 시 |
|--------|----------|--------------|
| 프로젝트 코드 | `-v ~/project:/workspace` 볼륨 | 보존 |
| API 키 | `-e ANTHROPIC_API_KEY=...` 환경변수 | 매번 재주입 필요 |
| tmux 세션 | 없음 (컨테이너 내부) | 소실 |
| 설치 도구 | Dockerfile `RUN npm install -g ...` | 이미지에 포함 |

<hr>

## 업데이트

새 버전이 출시되면 컨테이너 내부에서 동일한 npm 명령으로 업데이트합니다.

```bash
npm install -g @anthropic-ai/claude-code@latest
```

현재 설치된 버전과 최신 버전을 비교하려면 다음 명령을 씁니다.

```bash
npm outdated -g @anthropic-ai/claude-code
```

`Wanted`와 `Latest` 컬럼에 다른 버전이 보이면 업데이트가 있다는 뜻입니다.

<hr>

## 요약

```bash
# 지속 컨테이너 생성
docker run -d --name claude-env \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -v "$HOME/project":/workspace \
  ubuntu:22.04 sleep infinity

# 컨테이너 진입
docker exec -it claude-env bash

# 내부 설치 (한 번만)
apt-get update && apt-get install -y curl ca-certificates git
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs
npm install -g @anthropic-ai/claude-code

# 실행 확인
claude --version   # 2.1.181
claude --dangerously-skip-permissions
```

다음 챕터에서는 컨테이너 내부에서 TMUX를 설치하고 멀티에이전트 팀 레이아웃을 구성합니다.
