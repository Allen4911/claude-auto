# Claude Code 멀티에이전트 & AI 팀 자동화 실전 가이드
## TMUX + Remote-Control로 AI 개발팀을 구성하고 스마트폰으로 어디서든 지휘한다

---

## 01장. 들어가며
* [01-1. 이 책의 목적과 대상 독자](pages/01-1-purpose.md)
* [01-2. Remote-Control 팀 에이전트란 무엇인가](pages/01-2-what-is-remote-control.md)
* [01-3. 전체 아키텍처 미리 보기](pages/01-3-architecture-overview.md)
* [01-4. 개발 환경 및 최소 사양](pages/01-4-requirements.md)

---

## 02장. 환경 설치 및 기반 구성
* [02-1. 플랫폼별 설치 안내](pages/02-1-ubuntu-install.md)
* [02-2. Windows: WSL2 환경 구성 완전 가이드](pages/02-2-windows-wsl2.md)
* [02-3. macOS: 설치 완전 가이드](pages/02-3-macos.md)
* [02-4. Claude Code 설치 및 인증](pages/02-4-claude-install.md)
* [02-5. TMUX 기본 명령어 및 활용](pages/02-5-tmux-install.md)

---

## 03장. Claude Code와 TMUX로 멀티에이전트 구성
* [03-1. TMUX 세션·윈도우·파인 구조](pages/03-1-tmux-structure.md)
* [03-2. 팀 에이전트 레이아웃 설계](pages/03-2-team-layout.md)
* [03-3. 각 파인에 Claude Code 자동 실행](pages/03-3-auto-launch.md)
* [03-4. CLAUDE.md로 팀원 역할 정의](pages/03-4-claude-md-roles.md)
* [03-5. 팀 셋업 스크립트 작성](pages/03-5-setup-script.md)

---

## 04장. Claude Code Remote-Control 기능 설정 및 사용
* [04-1. Remote-Control 개요](pages/04-1-remote-control-overview.md)
* [04-2. Remote Control 활성화 방법 3가지](pages/04-2-activation.md)
* [04-3. 서버 모드 및 Spawn 모드](pages/04-3-server-mode.md)
* [04-4. 세션 이름 설정](pages/04-4-session-naming.md)
* [04-5. Stream JSON 제어](pages/04-5-stream-json.md)
* [04-6. 보안 설정 및 인증 요구사항](pages/04-6-security.md)

---

## 05장. 휴대폰 Claude 앱에서 Remote-Control 사용
* [05-1. Claude 모바일 앱 설치 및 계정 연결](pages/05-1-mobile-install.md)
* [05-2. QR 코드로 세션 연결하기](pages/05-2-qr-connect.md)
* [05-3. 세션 목록에서 팀 에이전트 선택](pages/05-3-session-list.md)
* [05-4. 모바일에서 지시 전달 및 도구 승인](pages/05-4-mobile-control.md)
* [05-5. 푸시 알림으로 작업 완료 확인](pages/05-5-push-notification.md)

---

## 06장. 핵심 도구 설치 및 활용
* [06-1. gstack — Claude Code 플러그인 스택 관리](pages/06-1-gstack.md)
* [06-2. superpowers — 스킬 기반 워크플로우 자동화](pages/06-2-superpowers.md)
* [06-3. gsd — Get Shit Done 프로젝트 관리](pages/06-3-gsd.md)
* [06-4. RTK — Rust Token Killer 토큰 최적화](pages/06-4-rtk.md)
* [06-5. MCP 연동 및 외부 도구 연결](pages/06-5-mcp.md)

---

## 07장. 실전 팀 에이전트 운용
* [07-1. 팀 지시 흐름 설계](pages/07-1-team-flow.md)
* [07-2. Bot Mode 활용](pages/07-2-bot-mode.md)
* [07-3. 업무 분담 전략](pages/07-3-task-distribution.md)
* [07-4. Triple Crown 전략 — gstack + GSD + Superpowers 통합 워크플로우](pages/07-4-triple-crown.md)
* [07-5. 자동화 워크플로우 예시](pages/07-5-workflow-examples.md)

---

## 08장. 고급 운용 기법
* [08-1. 실제 멀티에이전트 운영 사례](pages/08-1-real-world.md)
* [08-2. GitHub Actions 기반 자동화](pages/08-2-github-actions.md)
* [08-3. 컨텍스트 관리 기법](pages/08-3-context-management.md)
* [08-4. 멀티에이전트 충돌 방지](pages/08-4-conflict-prevention.md)

---

## 09장. 운영 및 문제 해결
* [09-1. Remote-Control 인증 오류 해결](pages/09-1-auth-troubleshooting.md)
* [09-2. TMUX 세션 복구 및 재연결](pages/09-2-tmux-recovery.md)
* [09-3. 토큰 최적화 심화](pages/09-3-token-optimization.md)

---

## 10장. 마치며
* [10-1. 앞으로의 발전 방향](pages/10-1-future.md)
* [10-2. 커뮤니티 참여](pages/10-2-community.md)

---
