# Claude Code 팀 에이전트 운용 가이드
## Remote-Control로 멀티에이전트를 원격에서 지휘하다

---

## 1장. 들어가며
- [1-1. 이 책의 목적과 대상 독자](pages/01-1-purpose.md)
- [1-2. Remote-Control 팀 에이전트란 무엇인가](pages/01-2-what-is-remote-control.md)
- [1-3. 전체 아키텍처 미리 보기](pages/01-3-architecture-overview.md)

---

## 2장. Ubuntu 환경에서 Claude & TMUX 설치
- [2-1. Ubuntu 설치: WSL2 또는 네이티브](pages/02-1-ubuntu-install.md)
- [2-2. 필수 패키지 설치](pages/02-2-prerequisites.md)
- [2-3. Claude Code 설치 및 인증](pages/02-3-claude-install.md)
- [2-4. TMUX 설치 및 기본 명령어](pages/02-4-tmux-install.md)

---

## 3장. Claude Code와 TMUX로 멀티에이전트 구성
- [3-1. TMUX 세션·윈도우·파인 구조](pages/03-1-tmux-structure.md)
- [3-2. 팀 에이전트 레이아웃 설계](pages/03-2-team-layout.md)
- [3-3. 각 파인에 Claude Code 자동 실행](pages/03-3-auto-launch.md)
- [3-4. CLAUDE.md로 팀원 역할 정의](pages/03-4-claude-md-roles.md)
- [3-5. 팀 셋업 스크립트 작성](pages/03-5-setup-script.md)

---

## 4장. Claude Code Remote-Control 기능 설정 및 사용
- [4-1. Remote-Control 개요](pages/04-1-remote-control-overview.md)
- [4-2. Remote Control 활성화 방법 3가지](pages/04-2-activation.md)
- [4-3. 서버 모드 및 Spawn 모드](pages/04-3-server-mode.md)
- [4-4. 세션 이름 설정](pages/04-4-session-naming.md)
- [4-5. Stream JSON 제어](pages/04-5-stream-json.md)
- [4-6. 보안 설정 및 인증 요구사항](pages/04-6-security.md)

---

## 5장. 휴대폰 Claude 앱에서 Remote-Control 사용
- [5-1. Claude 모바일 앱 설치 및 계정 연결](pages/05-1-mobile-install.md)
- [5-2. QR 코드로 세션 연결하기](pages/05-2-qr-connect.md)
- [5-3. 세션 목록에서 팀 에이전트 선택](pages/05-3-session-list.md)
- [5-4. 모바일에서 지시 전달 및 도구 승인](pages/05-4-mobile-control.md)
- [5-5. 푸시 알림으로 작업 완료 확인](pages/05-5-push-notification.md)

---

## 6장. 핵심 도구 설치 및 활용
- [6-1. gstack — Claude Code 플러그인 스택 관리](pages/06-1-gstack.md)
  - 설치 방법
  - 플러그인 추가/제거
  - 주요 명령어
- [6-2. superpowers — 스킬 기반 워크플로우 자동화](pages/06-2-superpowers.md)
  - 설치 방법
  - 스킬 목록 확인 및 호출
  - 커스텀 스킬 작성
- [6-3. gsd — Get Stuff Done 프로젝트 관리](pages/06-3-gsd.md)
  - 설치 방법
  - 프로젝트 초기화 및 마일스톤 관리
  - 페이즈 계획 및 실행
- [6-4. RTK — Rust Token Killer 토큰 최적화](pages/06-4-rtk.md)
  - 설치 방법
  - 토큰 절약 분석 (`rtk gain`)
  - Hook 기반 자동 적용

---

## 7장. 실전 팀 에이전트 운용
- [7-1. 팀 지시 흐름 설계](pages/07-1-team-flow.md)
- [7-2. Bot Mode 활용](pages/07-2-bot-mode.md)
- [7-3. 업무 분담 전략](pages/07-3-task-distribution.md)
- [7-4. Triple Crown 전략 — gstack + GSD + Superpowers 통합 워크플로우](pages/07-4-triple-crown.md)
- [7-5. 자동화 워크플로우 예시](pages/07-5-workflow-examples.md)

---

## 8장. 운영 및 문제 해결
- [8-1. Remote-Control 인증 오류 해결](pages/08-1-auth-troubleshooting.md)
- [8-2. TMUX 세션 복구 및 재연결](pages/08-2-tmux-recovery.md)
- [8-3. 토큰 최적화 심화](pages/08-3-token-optimization.md)
- [8-4. 멀티에이전트 충돌 방지](pages/08-4-conflict-prevention.md)

---

## 9장. 마치며
- [9-1. 앞으로의 발전 방향](pages/09-1-future.md)
- [9-2. 커뮤니티 참여](pages/09-2-community.md)
