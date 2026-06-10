## 8-4. 멀티에이전트 충돌 방지

## 이 절에서 배우는 것

여러 에이전트가 동시에 같은 코드베이스를 수정하면 충돌이 발생할 수 있습니다. 이 절에서는 충돌의 종류와 원인을 이해하고, 사전 방지 전략과 발생 후 처리 방법을 단계별로 배웁니다.

<hr>

## 왜 충돌이 발생하는가?

멀티에이전트 팀에서 여러 에이전트가 동시에 작업하다 보면 **충돌(Conflict)**이 발생합니다. 충돌은 크게 두 가지로 나뉩니다.

**파일 충돌**: 두 에이전트가 같은 파일을 동시에 수정하면 git merge conflict가 발생합니다.

**로직 충돌**: 한 에이전트의 변경이 다른 에이전트가 의존하는 인터페이스를 깨뜨립니다.

사람 팀에서도 이런 문제가 발생하지만, AI 에이전트는 더 빠르게 더 많은 파일을 수정합니다. 충돌을 사전에 방지하는 설계가 필수입니다.

> 💡 **git merge conflict란?** 두 사람이 같은 문서의 같은 줄을 동시에 수정했을 때 발생하는 충돌입니다. git은 "어느 쪽 내용을 최종으로 할지" 사람이 직접 결정해 달라고 요청합니다. AI 에이전트는 초당 수십 줄을 수정할 수 있어, 사람보다 훨씬 빠르게 충돌을 만들어 냅니다.

![멀티에이전트 파일 충돌 발생 원인 도식](../assets/08-4-conflict-prevention-conflict-cause.png)

<hr>

## 충돌 방지의 기본 원칙

### 원칙 1: 역할별 파일 소유권

각 에이전트가 담당하는 파일 영역을 명확히 나눕니다. 두 에이전트가 같은 파일을 수정하지 않도록 설계합니다.

```
서연(개발자)   → src/ 디렉터리 담당
태양(리뷰어)   → 파일 수정 없음, 읽기만
민준(PM)       → docs/, PLAN.md 담당
수아(디자이너) → src/styles/, assets/ 담당
```

CLAUDE.md에 파일 소유권을 명시하면 에이전트가 자연스럽게 범위를 지킵니다.

```markdown
# CLAUDE.md (서연용)
## 담당 영역
- src/features/ — 기능 구현
- src/utils/ — 유틸리티 함수
- tests/ — 테스트 파일

## 건드리지 않는 영역
- src/styles/ — 수아 담당
- docs/ — 민준 담당
```

![역할별 파일 소유권 지도](../assets/08-4-conflict-prevention-ownership-map.png)

### 원칙 2: 순차 실행으로 의존성 관리

설계 → 구현 → 리뷰 순서를 지키면 단계 간 충돌을 원천 차단합니다.

```
민준 설계 완료 후
  → 서연 구현 시작 (민준 작업 파일 변경 없음)
      → 서연 구현 완료 후
          → 태양 리뷰 시작 (서연 작업 파일 변경 없음)
```

리뷰어가 읽는 동안 개발자가 같은 파일을 수정하면 혼란이 생깁니다. 태양이 리뷰 중에는 서연이 해당 파일에 손대지 않도록 합니다.

![설계→구현→리뷰 순차 실행 타임라인](../assets/08-4-conflict-prevention-sequential-timeline.png)

### 원칙 3: 브랜치 전략

각 Phase를 별도 브랜치에서 작업하면 main 브랜치의 안정성을 유지합니다.

```bash
# Phase별 브랜치 생성
git checkout -b feature/phase-1-ai-comparison
git checkout -b feature/phase-2-price-history
git checkout -b feature/phase-3-bulk-update
```

Phase 완료 후 리뷰 통과 시 main에 머지합니다. 여러 Phase가 동시에 진행되더라도 브랜치로 격리합니다.

> 💡 **브랜치(Branch)란?** 코드의 "작업 사본"입니다. main 브랜치는 안정적인 완성 코드, feature 브랜치는 새 기능을 개발하는 임시 공간입니다. 서로 다른 브랜치에서 같은 파일을 수정해도 main이 망가지지 않습니다. 작업이 완료되면 main에 "머지(merge)"하여 합칩니다.

![Phase별 브랜치 전략과 main 머지 흐름](../assets/07-9-conflict-Strategy.png)

위 그림은 각 Phase 브랜치가 main에서 분기되어 독립 작업 후 순서대로 머지되는 전체 흐름입니다. 아래 그림은 실제 git 그래프 형태로 커밋 분기와 머지 포인트를 상세히 표현합니다.

![Phase별 feature 브랜치 전략 git 그래프](../assets/08-4-conflict-prevention-branch-strategy.png)

<hr>

## Git 충돌 처리

사전 방지에도 불구하고 충돌이 발생하면 신속하게 해결합니다.

### 충돌 감지

```bash
# 충돌 파일 확인
git status
# both modified: src/api/client.ts

# 충돌 내용 확인
git diff --name-only --diff-filter=U
```

### 충돌 해결 절차

**1단계: 충돌 파일 열기**
```bash
code src/api/client.ts
```

**2단계: 충돌 마커 확인**

충돌이 발생한 파일에는 아래와 같은 마커가 자동으로 삽입됩니다.
```bash
<<<<<<< HEAD
  const timeout = 5000;
=======
  const timeout = 10000;
>>>>>>> feature/phase-2
```

> 💡 **충돌 마커 읽는 법** `<<<<<<< HEAD`와 `=======` 사이가 "내 브랜치(HEAD)의 내용"이고, `=======`와 `>>>>>>> feature/phase-2` 사이가 "상대 브랜치의 내용"입니다. 둘 중 하나를 선택하거나 두 내용을 합쳐서 마커를 모두 제거하면 충돌이 해결됩니다.

**3단계: 올바른 버전 선택 또는 통합**
```bash
  const timeout = 10000;  # Phase 2에서 늘린 값 유지
```

**4단계: 충돌 마커 제거 후 저장**

`<<<<<<<`, `=======`, `>>>>>>>` 줄을 모두 지우고 파일을 저장합니다.

**5단계: 스테이징**
```bash
git add src/api/client.ts
```

**6단계: 커밋**
```bash
git commit -m "resolve: api timeout 충돌 해결"
```

![git 충돌 해결 6단계 순서도](../assets/08-4-conflict-prevention-resolve-steps.png)

### 멀티에이전트 환경에서의 충돌 보고

에이전트가 충돌을 발견하면 스스로 해결하지 않고 민준에게 보고합니다.

```bash
# 서연이 충돌 발견 시
bash claude-send.sh 1 "src/api/client.ts에서 충돌 발생. 
HEAD: timeout=5000, Phase-2: timeout=10000. 
어떤 값으로 해결할까요?"
```

민준이 판단하여 지시를 내리면 서연이 해결합니다. **에이전트가 독단적으로 충돌을 해결하는 것은 위험**합니다.

<hr>

## Redis를 활용한 에이전트 간 상태 공유

에이전트들이 서로의 작업 상태를 알 수 없으면 중복 작업이나 충돌이 발생합니다. Redis를 사용하면 에이전트 간 실시간 상태를 공유할 수 있습니다.

> 💡 **Redis란?** 초고속 인메모리 데이터베이스입니다. 여러 프로그램이 공유 메모장처럼 사용할 수 있어, "서연이 client.ts를 작업 중"이라는 정보를 모든 에이전트가 실시간으로 알 수 있습니다. 파일 잠금(lock) 기능을 구현하는 데 자주 활용됩니다.

### 상태 저장 패턴

```python
import redis

r = redis.Redis()

# 서연이 작업 시작 시
r.set("lock:src/api/client.ts", "서연", ex=3600)  # 1시간 잠금

# 다른 에이전트가 파일 수정 전 확인
lock_holder = r.get("lock:src/api/client.ts")
if lock_holder:
    print(f"{lock_holder.decode()}이 작업 중. 완료 후 수정 가능.")
else:
    # 수정 진행
    r.set("lock:src/api/client.ts", "자신의 이름", ex=3600)
```

### 작업 완료 신호

```python
# 서연이 Phase 완료 시
r.publish("team:events", json.dumps({
    "type": "phase_complete",
    "agent": "서연",
    "phase": 1,
    "commit": "eaca3ba"
}))

# 태양이 이벤트 구독
pubsub = r.pubsub()
pubsub.subscribe("team:events")
for message in pubsub.listen():
    event = json.loads(message["data"])
    if event["type"] == "phase_complete":
        print(f"{event['agent']} Phase {event['phase']} 완료. 리뷰 시작.")
```

![Redis 기반 에이전트 간 파일 잠금·상태 공유 흐름](../assets/08-4-conflict-prevention-redis-flow.png)

<hr>

## 실전 충돌 사례와 해결

### 사례 1: 동시 imports 수정

**상황**: 서연이 `utils/formatter.ts`에 함수를 추가하는 동시에 수아가 같은 파일의 스타일 유틸을 수정했습니다.

**해결**: formatter.ts를 `utils/data-formatter.ts`(서연)와 `utils/style-formatter.ts`(수아)로 분리하여 파일 소유권 충돌을 원천 제거했습니다.

**교훈**: 충돌이 반복되는 파일은 역할별로 분리하는 것이 장기적으로 유리합니다.

### 사례 2: 타입 정의 변경

**상황**: 민준이 `types/Product.ts`의 인터페이스를 변경했는데, 서연이 이미 구 인터페이스로 구현을 완료한 상태였습니다.

**해결**: 민준이 타입 변경 전 서연에게 미리 알리는 규칙을 도입했습니다. 인터페이스 변경은 구현보다 반드시 먼저 공지합니다.

```bash
# 민준이 타입 변경 전 서연에게 공지
bash claude-send.sh 4 "⚠️ Product 인터페이스 변경 예정. 
price 필드가 number → PriceInfo 객체로 변경됨. 
현재 작업 완료 후 알려줘, 타입 변경 후 함께 수정하자."
```

### 사례 3: 테스트 파일 덮어쓰기

**상황**: 서연이 새 기능을 추가하면서 기존 테스트 파일을 실수로 덮어썼습니다.

**해결**: git pre-commit hook으로 테스트 파일 삭제·축소를 방지합니다.

> 💡 **pre-commit hook이란?** git commit 명령을 실행하면 실제 커밋이 이루어지기 직전에 자동으로 실행되는 스크립트입니다. "커밋 전 문지기" 역할을 합니다. 테스트 파일 삭제처럼 위험한 동작을 감지하면 커밋 자체를 막아 실수를 원천 차단합니다.

```bash
# .git/hooks/pre-commit
#!/bin/bash
# 테스트 파일이 줄었는지 확인
DELETED_TESTS=$(git diff --cached --diff-filter=D -- 'tests/*.test.ts' | wc -l)
if [ $DELETED_TESTS -gt 0 ]; then
    echo "❌ 테스트 파일이 삭제되었습니다. 커밋 차단."
    exit 1
fi
```

<hr>

## 충돌 방지 체크리스트

작업 시작 전 확인 사항입니다.

```
□ 내가 담당하는 파일 영역인가?
□ 다른 에이전트가 이 파일을 작업 중이지 않은가? (Redis 확인)
□ 최신 main/develop 브랜치를 pull 받았는가?
□ 내 브랜치가 최신 base 브랜치를 기준으로 하는가?

작업 완료 후 확인 사항:
□ 충돌 없이 merge/rebase 가능한가?
□ 테스트가 모두 통과하는가?
□ 내가 변경한 파일 목록을 민준에게 보고했는가?
```

![충돌 방지 체크리스트 분기 흐름도](../assets/08-4-conflict-prevention-checklist-flow.png)

<hr>

## 충돌 방지 자동화

GitHub Actions와 연동하여 충돌 가능성을 PR 단계에서 조기 발견합니다.

```yaml
# .github/workflows/conflict-check.yml
name: Conflict Check

on:
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Check for merge conflicts
        run: |
          git fetch origin main
          git merge-tree --write-tree HEAD origin/main | \
            grep -c "<<<<<<" && echo "충돌 발견" && exit 1 || echo "충돌 없음"
```

PR을 열기 전에 로컬에서도 확인합니다.

```bash
# main과의 충돌 사전 확인
git fetch origin
git merge --no-commit --no-ff origin/main
git merge --abort  # 확인 후 취소
```

> **핵심 요약**: 멀티에이전트 충돌 방지의 핵심은 **역할별 파일 소유권**, **순차 실행 원칙**, **브랜치 전략**입니다. 충돌이 발생했을 때는 에이전트가 독단적으로 해결하지 않고 민준에게 보고하여 판단을 받습니다. Redis 기반 상태 공유와 GitHub Actions 자동화로 충돌을 사전에 탐지하면 팀의 작업 흐름이 안정적으로 유지됩니다.

<hr>

## 팀 코딩 컨벤션으로 충돌 예방

기술적 충돌 외에도, 코딩 스타일 불일치로 인한 불필요한 변경이 충돌을 유발합니다. 팀 전체가 동일한 컨벤션을 따르면 이를 예방할 수 있습니다.

### ESLint + Prettier 공유 설정

```json
// .eslintrc.json (팀 공통)
{
  "extends": ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "prefer-const": "error",
    "no-console": "warn"
  }
}
```

```json
// .prettierrc (팀 공통)
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

이 설정을 저장소에 커밋하면 모든 에이전트가 동일한 규칙으로 코드를 작성합니다. 스타일 차이로 인한 diff가 사라져 리뷰 부담도 줄어듭니다.

> 💡 **ESLint와 Prettier란?** ESLint는 "잘못된 코드 패턴(버그 유발 가능 코드)"을 감지하는 도구, Prettier는 "코드 스타일(띄어쓰기·따옴표 등)"을 통일하는 도구입니다. 팀 전원이 같은 설정을 쓰면, 서연과 수아가 같은 파일을 수정해도 스타일 차이로 인한 불필요한 줄 변경이 사라집니다.

### Git Hooks로 컨벤션 강제

```bash
# .git/hooks/pre-commit
#!/bin/bash

# 스테이징된 TS 파일에 ESLint 실행
STAGED_TS=$(git diff --cached --name-only --diff-filter=ACM | grep '\.tsx\?$')
if [ -n "$STAGED_TS" ]; then
  npx eslint $STAGED_TS --fix
  git add $STAGED_TS
fi

# Prettier 포맷 강제
npx prettier --write $STAGED_TS
git add $STAGED_TS
```

커밋 시점에 자동으로 포맷을 통일하므로, 에이전트별 스타일 차이가 커밋에 남지 않습니다.

![ESLint·Prettier pre-commit hook 자동 적용 흐름](../assets/08-4-conflict-prevention-convention-hook.png)

<hr>

## 대규모 리팩토링 시 충돌 관리

파일명 변경, 인터페이스 대규모 변경 등 여러 파일에 걸친 리팩토링은 충돌 위험이 높습니다.

### 리팩토링 전 팀 동결 선언

**1단계: 전 팀원에게 동결 공지**
```bash
# 민준이 전 팀원에게 공지
bash claude-send.sh 4 "⛔ 리팩토링 동결 시작. 
auth 모듈 전면 재설계 예정.
src/auth/ 파일 작업 중단. 완료 후 재개 알림."

bash claude-send.sh 2 "⛔ 리팩토링 동결. auth 모듈 조사 보류."
```

**2단계: 리팩토링 진행** (동결 구간 동안 다른 팀원은 관련 파일 미수정)

**3단계: 완료 후 재동기화 공지**
```bash
bash claude-send.sh 4 "✅ auth 리팩토링 완료. 
커밋 def5678 확인 후 작업 재개.
변경된 인터페이스: AuthToken → TokenPayload
사용법: docs/auth-migration.md 참고"
```

팀원들은 최신 main을 pull 받고 자신의 브랜치를 rebase한 후 작업을 재개합니다.

### Feature Flag로 안전한 대규모 변경

```typescript
// 구 코드와 신 코드를 동시에 유지하며 점진적으로 전환
const USE_NEW_AUTH = process.env.FEATURE_NEW_AUTH === 'true';

export async function authenticate(token: string) {
  if (USE_NEW_AUTH) {
    return newAuthService.verify(token);
  }
  return legacyAuthService.verify(token);
}
```

Feature Flag를 사용하면 리팩토링 중에도 다른 팀원이 나머지 기능을 개발할 수 있습니다. 전환이 완료되면 Flag와 구 코드를 제거합니다.

> 💡 **Feature Flag란?** "기능 스위치"입니다. 환경변수 하나로 구 코드와 신 코드를 전환합니다. 리팩토링이 완성되지 않아도 안전하게 배포할 수 있고, 문제 발생 시 즉시 구 코드로 되돌릴 수 있습니다. 대규모 변경을 점진적으로 적용할 때 특히 유용합니다.

![대규모 리팩토링 동결·해제 팀 타임라인](../assets/08-4-conflict-prevention-freeze-timeline.png)
