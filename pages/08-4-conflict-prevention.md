## 8-4. 멀티에이전트 충돌 방지

여러 Claude Code 인스턴스가 동시에 같은 코드베이스에서 작업하면 충돌이 발생할 수 있다. 두 팀원이 같은 파일을 동시에 수정하거나, 한 팀원의 변경이 다른 팀원의 작업을 무효화하는 상황이다. 이 절에서는 멀티에이전트 환경에서 충돌을 예방하고 관리하는 전략을 다룬다.

<hr>

## 충돌이 발생하는 유형

### 유형 1: 파일 동시 수정

```
서연 (Pane 4): src/api/users.ts 수정 중
    ↕ 동시에
태양 (Pane 5): src/api/users.ts 리뷰 후 직접 수정
    → 한쪽의 변경이 덮어씌워짐
```

### 유형 2: 의존성 충돌

```
서연: 새 패키지 추가 (npm install axios)
    ↕ 동시에
민준: package.json 수동 수정 중
    → package.json / package-lock.json 충돌
```

### 유형 3: Git 충돌

```
서연: feature/notification 브랜치에서 커밋
    ↕ 동시에
지훈: 같은 브랜치에서 다른 파일 커밋
    → push 실패 또는 머지 충돌
```

<hr>

## 전략 1: 영역 분리

가장 효과적인 충돌 방지 방법은 **작업 영역을 물리적으로 분리**하는 것이다.

### 디렉토리 기반 분리

각 팀원에게 담당 디렉토리를 배정한다.

```
프로젝트 구조:
├── src/
│   ├── api/          ← 서연 담당
│   ├── components/   ← 수아 담당
│   ├── services/     ← 민준 담당
│   └── utils/        ← 공용 (팀장 승인 후 수정)
├── tests/            ← 태양 담당
└── docs/             ← 지훈 담당
```

팀장이 지시를 내릴 때 담당 영역을 명시한다.

```bash
# 명확한 영역 지정
tmux send-keys -t team:0.4 \
  "src/api/ 디렉토리에서 알림 API 엔드포인트를 구현해줘. \
  다른 디렉토리의 파일은 수정하지 마." Enter
```

### 브랜치 기반 분리

각 팀원이 독립된 Git 브랜치에서 작업한다.

```bash
# 팀원별 브랜치 생성
tmux send-keys -t team:0.4 \
  "git checkout -b feature/notification-api 에서 작업해줘" Enter

tmux send-keys -t team:0.3 \
  "git checkout -b feature/notification-ui 에서 작업해줘" Enter
```

브랜치가 분리되면 파일 수준의 충돌이 커밋 시점에서는 발생하지 않는다. 충돌은 머지 시점에만 발생하며, 팀장이 통제할 수 있다.

### Git Worktree 활용

같은 저장소의 다른 브랜치를 별도 디렉토리로 체크아웃하는 Git Worktree를 사용하면 브랜치 전환 없이 병렬 작업이 가능하다.

```bash
# 팀원별 worktree 생성
git worktree add ../project-suyeon feature/notification-api
git worktree add ../project-sua feature/notification-ui

# 서연은 ../project-suyeon/ 에서 작업
# 수아는 ../project-sua/ 에서 작업
```

각 팀원의 Claude Code가 다른 디렉토리에서 실행되므로 파일 시스템 수준에서 완전히 격리된다.

<hr>

## 전략 2: 잠금 규칙

영역 분리가 불가능한 경우 **잠금 규칙**을 도입한다.

### 파일 잠금 컨벤션

```bash
# 잠금 파일 생성
echo "서연 작업중 $(date)" > src/api/users.ts.lock

# 작업 완료 후 잠금 해제
rm src/api/users.ts.lock
```

이 컨벤션을 CLAUDE.md에 명시한다.

```markdown
# CLAUDE.md 잠금 규칙
## 파일 잠금
- 파일 수정 전 `.lock` 파일 존재 여부 확인
- `.lock` 파일이 있으면 해당 파일 수정 금지
- 수정 시작 시 `.lock` 파일 생성, 완료 시 삭제
```

### 공유 파일 수정 프로토콜

여러 팀원이 수정할 수 있는 공유 파일(라우터 설정, 타입 정의 등)은 팀장을 통해 순차적으로 수정한다.

```bash
# 나쁜 예: 두 팀원이 동시에 routes.ts 수정
# → 충돌 발생

# 좋은 예: 순차 실행
# 1단계: 서연이 API 라우트 추가
tmux send-keys -t team:0.4 \
  "src/routes.ts에 알림 API 라우트를 추가해줘" Enter
# 서연 완료 확인 후...

# 2단계: 수아가 UI 라우트 추가
tmux send-keys -t team:0.3 \
  "src/routes.ts에 알림 설정 페이지 라우트를 추가해줘" Enter
```

<hr>

## 전략 3: 충돌 감지 및 해소

예방에도 불구하고 충돌이 발생할 수 있다. 빠른 감지와 해소가 중요하다.

### 정기적 상태 점검

```bash
# 팀장이 주기적으로 실행하는 충돌 점검
#!/bin/bash

# 수정 중인 파일 목록 수집
echo "=== 현재 수정 중인 파일 ==="
git diff --name-only
echo ""

echo "=== 스테이지되지 않은 변경 ==="
git status --short
echo ""

# 같은 파일을 여러 곳에서 수정했는지 확인
MODIFIED=$(git diff --name-only)
for file in $MODIFIED; do
  COUNT=$(echo "$MODIFIED" | grep -c "$file")
  if [ "$COUNT" -gt 1 ]; then
    echo "⚠️ 충돌 위험: $file ($COUNT곳에서 수정)"
  fi
done
```

### Git 충돌 해소

머지 시 충돌이 발생하면 팀장이 판단하여 해소한다.

```bash
# 브랜치 머지 시도
git merge feature/notification-api
# CONFLICT: src/routes.ts

# 충돌 내용 확인
git diff --name-only --diff-filter=U
# src/routes.ts

# 팀원에게 충돌 해소 지시
tmux send-keys -t team:0.4 \
  "src/routes.ts에서 머지 충돌이 발생했어. \
  두 브랜치의 변경을 모두 유지하는 방향으로 해소해줘." Enter
```

<hr>

## 전략 4: 작업 순서 설계

팀장이 작업을 배분할 때 충돌 가능성을 고려하여 순서를 설계한다.

### 의존성 그래프 기반 배분

```
작업 A (지훈: 조사) ──→ 작업 C (민준: 설계) ──→ 작업 E (서연: 구현)
                                              ↘
작업 B (수아: UI 설계) ─────────────────────────→ 작업 F (서연: UI 구현)
                                                       ↘
                                                   작업 G (태양: 리뷰)
```

병렬 작업(A와 B)은 서로 다른 영역을 다루도록 설계하고, 의존성이 있는 작업(C→E, B→F)은 순차 실행한다.

### 페이즈 기반 실행

```bash
# Phase 1: 병렬 (서로 영역이 다름)
# 지훈 → 기술 조사
# 수아 → UI 설계
# (동시 실행 가능, 충돌 없음)

# Phase 2: 순차 (이전 결과에 의존)
# 민준 → 아키텍처 설계 (지훈+수아의 결과 필요)

# Phase 3: 병렬 (브랜치로 분리)
# 서연 → API 구현 (feature/api 브랜치)
# 수아 → UI 구현 (feature/ui 브랜치)

# Phase 4: 순차 (머지 후 리뷰)
# 팀장 → 브랜치 머지
# 태양 → 통합 리뷰
```

<hr>

## CLAUDE.md에 충돌 방지 규칙 명시

팀 전체에 적용되는 충돌 방지 규칙을 CLAUDE.md에 기록한다.

```markdown
## 충돌 방지 규칙
1. 지시받은 디렉토리/파일 범위 안에서만 작업할 것
2. 공유 파일(routes.ts, types.ts) 수정 전 팀장에게 보고
3. 새 패키지 설치는 팀장 승인 후 진행
4. 작업 완료 후 반드시 git add + commit
5. 다른 팀원의 브랜치를 직접 수정하지 않을 것
```

<hr>

## 요약

멀티에이전트 충돌 방지의 핵심은 **영역 분리**와 **순서 설계**다. 디렉토리, 브랜치, 또는 Git Worktree로 작업 영역을 물리적으로 분리하고, 공유 리소스는 순차적으로 접근하도록 설계한다. CLAUDE.md에 충돌 방지 규칙을 명시하고, 팀장이 작업 배분 시 의존성 그래프를 고려하면 대부분의 충돌을 사전에 예방할 수 있다.
