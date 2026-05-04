# 2-2. 필수 패키지 설치

Claude Code와 TMUX 기반 멀티에이전트 환경을 구성하려면 Node.js, npm, 그리고 몇 가지 유틸리티가 필요합니다. 이 챕터에서는 순서대로 설치합니다.

---

## Node.js 설치

Claude Code는 npm 패키지로 배포됩니다. **Node.js 18 이상**이 필요하며, 최신 LTS 버전을 권장합니다.

### nvm으로 설치 (권장)

nvm(Node Version Manager)을 사용하면 Node.js 버전을 유연하게 관리할 수 있습니다.

```bash
# nvm 설치
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

# 셸 재로드
source ~/.bashrc

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

### apt로 직접 설치 (대안)

```bash
# NodeSource 저장소 추가 (Node.js 22.x)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -

# 설치
sudo apt install -y nodejs

# 확인
node --version
npm --version
```

---

## Git 설치

Git은 Claude Code의 프로젝트 관리와 설정 파일 버전 관리에 활용됩니다.

```bash
sudo apt install -y git

# 설치 확인
git --version
```

초기 사용자 설정도 함께 진행합니다.

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

---

## curl, wget, unzip

네트워크 도구와 압축 해제 유틸리티입니다.

```bash
sudo apt install -y curl wget unzip
```

---

## build-essential (선택)

일부 npm 패키지가 네이티브 빌드를 요구할 수 있습니다.

```bash
sudo apt install -y build-essential
```

---

## 전체 설치 요약 스크립트

위 단계를 한 번에 실행하려면 아래 스크립트를 사용하세요.

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

---

## 설치 확인 체크리스트

```bash
node --version    # v18.0.0 이상
npm --version     # 9.0.0 이상
git --version     # 2.x.x
curl --version    # 설치 확인
```

모든 명령이 오류 없이 버전을 출력하면 다음 단계로 넘어갑니다.
