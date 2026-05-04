# 2-1. Ubuntu 설치: WSL2 또는 네이티브

이 책에서 구성하는 Claude 멀티에이전트 환경은 **Ubuntu Linux** 위에서 동작합니다. Windows 사용자라면 WSL2(Windows Subsystem for Linux 2)를 통해, 리눅스/Mac 사용자라면 네이티브 환경을 그대로 사용할 수 있습니다.

---

## WSL2로 Ubuntu 설치하기 (Windows)

WSL2는 Windows 10/11에서 완전한 Linux 커널을 실행할 수 있는 Microsoft 공식 솔루션입니다. 성능과 호환성 모두 네이티브에 가깝습니다.

### 1단계: WSL2 활성화

PowerShell을 **관리자 권한**으로 열고 아래 명령을 실행합니다.

```powershell
wsl --install
```

이 명령 하나로 WSL2 기능 활성화, 가상 머신 플랫폼 설치, Ubuntu 최신 LTS 다운로드까지 자동으로 처리됩니다. 설치 완료 후 PC를 재시작하세요.

재시작 후 Ubuntu 초기 설정 창이 자동으로 열립니다.

```
Enter new UNIX username: allen          # 원하는 사용자명 입력
New password: ****                       # 비밀번호 설정
```

### 2단계: WSL 버전 확인

```powershell
wsl --list --verbose
```

출력 결과에서 Ubuntu 행의 VERSION이 `2`인지 확인합니다.

```
  NAME      STATE    VERSION
* Ubuntu    Running  2
```

VERSION이 `1`이라면 다음 명령으로 업그레이드합니다.

```powershell
wsl --set-version Ubuntu 2
```

### 3단계: Ubuntu 터미널 열기

시작 메뉴에서 **Ubuntu** 앱을 실행하거나, Windows Terminal에서 Ubuntu 탭을 선택합니다. 이후 모든 작업은 이 Ubuntu 터미널에서 진행합니다.

---

## 네이티브 Ubuntu 설치 (리눅스/Mac)

이미 Ubuntu 22.04 이상 또는 Debian 계열 배포판을 사용 중이라면 별도 설치 없이 다음 챕터로 넘어가도 됩니다. macOS는 Homebrew 환경을 그대로 활용할 수 있습니다.

---

## 패키지 목록 최신화

설치 후 반드시 패키지 목록을 업데이트합니다.

```bash
sudo apt update && sudo apt upgrade -y
```

---

## WSL2 네트워크 정보 확인

WSL2는 Windows 호스트와 별도의 가상 IP를 가집니다. 나중에 SSH나 포트 접근이 필요할 때 유용합니다.

```bash
# WSL2 IP 확인
ip addr show eth0 | grep 'inet '

# Windows 호스트 IP 확인 (WSL 내부에서)
cat /etc/resolv.conf | grep nameserver
```

---

## 요약

| 환경 | 방법 |
|------|------|
| Windows | `wsl --install` → 재부팅 → Ubuntu 앱 실행 |
| 기존 Ubuntu/Debian | 그대로 진행 |
| macOS | Homebrew 환경 유지, bash/zsh 터미널 사용 |

Ubuntu 환경이 준비되었으면 다음 챕터에서 Claude Code 실행에 필요한 패키지들을 설치합니다.
