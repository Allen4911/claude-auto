## 6-1. gstack — Claude Code 플러그인 스택 관리

## gstack이란?

**gstack**은 Claude Code를 위한 전문화 워크플로우 스킬 시스템입니다. 단순한 AI 어시스턴트 사용을 넘어, 소프트웨어 개발 사이클 전반을 체계적으로 지원하는 역할 기반 명령어 모음을 제공합니다. `/ship`, `/qa`, `/review`, `/investigate`, `/health` 등 개발 현장에서 바로 쓸 수 있는 슬래시 커맨드를 Claude Code에 추가해줍니다.

gstack의 핵심 철학은 세 가지입니다.

- **역할 기반 의사결정**: 코드를 작성하기 전에 CEO(비즈니스 가치)나 CTO(아키텍처)의 관점에서 먼저 문제를 검토합니다.
- **자동화된 계획 수립**: 복잡한 작업을 단계별로 쪼개고 각 단계마다 검증을 거칩니다.
- **그라운딩(Grounding)**: 프로젝트의 현재 상태와 요구사항에 에이전트를 강력하게 고정시켜 맥락을 잃지 않게 합니다.

<hr>

## 설치 방법

gstack은 Claude Code의 스킬 시스템을 통해 설치됩니다. 터미널에서 Claude Code를 실행한 뒤 다음 명령어를 입력합니다.

```bash
/gstack
```

처음 `/gstack` 을 실행하면 설치 과정이 자동으로 진행됩니다. 설치가 완료되면 스킬이 `~/.claude/skills/gstack` 경로에 저장됩니다.

설치 확인:

```bash
# Claude Code 세션 내에서
/gstack-upgrade
```

현재 버전과 최신 버전을 비교하여 업데이트가 필요하면 자동으로 수행합니다. 자동 업데이트를 항상 활성화하려면 다음 명령어를 실행합니다.

```bash
~/.claude/skills/gstack/bin/gstack-config set auto_upgrade true
```

<hr>

## 주요 명령어

| 커맨드 | 역할 | 용도 |
|:---|:---|:---|
| `/cso` | Chief Security Officer | 보안 감사 (secrets, OWASP Top 10, CI/CD 취약점) |
| `/autoplan` | Planner | 요구사항 분석 및 개발 로드맵 자동 생성 |
| `/review` | Peer Reviewer | 코드 논리 오류, 스타일, 잠재 버그 검토 |
| `/qa` | QA Engineer | 구현 기능이 요구사항을 충족하는지 검증 |
| `/ship` | Release Manager | 작업 마무리 및 배포 준비 |
| `/investigate` | Detective | 버그 및 코드베이스 특정 부분 심층 조사 |
| `/learn` | Learner | 새 라이브러리나 스택 도입 전 선행 학습 |
| `/careful` | Senior Dev | 중요한 코드 수정 시 극도로 신중하게 접근 |
| `/context-save` | Checkpoint | 현재 작업 상태 저장 |
| `/context-restore` | Restorer | 저장된 작업 상태 복원 |

<hr>

## 실전 활용 예시

### 새 기능 개발 흐름

새로운 기능을 개발할 때 gstack 커맨드를 순서대로 활용하면 체계적인 개발이 가능합니다.

```
1단계: /autoplan
   → "사용자 인증 기능을 추가하려 합니다. 개발 계획을 수립해주세요."
   → 세부 태스크 목록과 예상 구현 순서를 자동 생성합니다.

2단계: /review
   → "작성한 auth.py 파일을 리뷰해주세요."
   → 코드 품질, 보안 취약점, 스타일 일관성을 점검합니다.

3단계: (코드 구현 후) /cso
   → "보안 취약점을 점검해주세요."
   → secrets 노출, OWASP Top 10, 의존성 취약점을 감사합니다.

4단계: /qa
   → "인증 기능이 요구사항을 모두 만족하는지 검증해주세요."
   → 테스트 시나리오를 실행하고 결과를 보고합니다.

5단계: /ship
   → "기능 구현이 완료되었습니다. 배포 준비를 해주세요."
   → 브랜치 정리, 변경사항 요약, 배포 체크리스트를 제공합니다.
```

### 컨텍스트 저장 및 복원

긴 세션에서 작업 상태를 저장하고 이어서 작업할 때 유용합니다.

```bash
# 현재 작업 상태 저장
/context-save 인증기능-구현중

# 목록 확인
/context-save list

# 저장된 상태 복원
/context-restore 인증기능-구현중
```

<hr>

## Triple Crown 전략 (권장 워크플로우)

gstack 단독으로도 강력하지만, GSD(프로젝트 관리)와 Superpowers(품질 관리)를 함께 사용하면 더욱 강력한 워크플로우를 구성할 수 있습니다.

```
gstack (전략·검증)  →  GSD (구조·실행)  →  Superpowers (품질·방법론)
 "무엇을 왜"          "어떤 순서로"         "어떻게 잘"
```

이 세 도구를 파이프라인으로 연결하는 것이 Triple Crown 전략입니다. 구체적인 5단계 사이클, 팀 환경 배분 방법, 실전 예시는 [7-4. Triple Crown 전략](07-4-triple-crown.md)에서 자세히 다룹니다.

<hr>

## 버전 이력

| 버전 | 주요 변경사항 |
|:---|:---|
| 1.51.0.0 | 최신 업데이트 |
| 1.48.0.0 | 안정 릴리스 |
| 1.27.0.0 | artifacts 동기화 시스템 도입 |
| 1.0.0.0 | V1 프롬프트 스타일 개선, `/plan-tune` 추가 |

> **현재 최신 버전**: 1.51.0.0 (2026-05 기준) — `/gstack-upgrade`로 업그레이드 가능
