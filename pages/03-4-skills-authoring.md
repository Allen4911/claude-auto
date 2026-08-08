# 03-4. Skills 작성으로 작업 표준화

Claude Code에는 두 가지 성격의 "스킬"이 있습니다. 사용하는 스킬과 만드는 스킬입니다. 7장에서 다루는 gstack·superpowers는 누군가 미리 만들어 배포한 스킬을 팀이 공유해 쓰는 방식입니다. 이 절은 반대편을 다룹니다. 반복되는 작업 절차를 직접 SKILL.md 파일로 정의해 Claude Code가 자동으로 인식하게 만드는 **작성(Authoring)** 영역입니다.

## SKILL.md 구조와 작성법

### 스킬이란

**스킬 = `SKILL.md` 파일이 들어 있는 디렉토리**입니다.

Claude Code는 시작할 때 스킬 디렉토리를 스캔합니다. 각 스킬의 이름과 설명만 대화 컨텍스트에 올려 두고 지침 본문은 그 스킬이 실제로 호출될 때만 로드합니다. 이를 **지연 로딩(lazy loading)**이라고 합니다.

> **왜 지연 로딩인가?** 스킬 본문을 처음부터 모두 올려 두면 컨텍스트 창이 스킬 내용으로 가득 차버립니다. 설명만 먼저 두고 필요할 때 본문을 가져오면 수십 개의 스킬을 등록해도 실행 비용이 거의 없습니다.

스킬은 Agent Skills 오픈 표준(agentskills.io)을 구현합니다. Claude Code는 이 표준 위에 자체 필드를 얹어 확장합니다.

### SKILL.md 파일 형식

SKILL.md는 YAML 프론트매터와 마크다운 본문 두 부분으로 구성됩니다.

**최소 템플릿:**
```yaml
---
name: my-skill
description: 이 스킬이 무엇을 하는지, 언제 호출해야 하는지 설명합니다.
---

# 지침 본문

여기에 Claude가 따를 절차를 작성합니다.
```

`description`은 선택 항목이지만 꼭 채우세요. 이 필드가 없으면 Claude가 스킬을 자동으로 호출할 판단 근거를 잃습니다. 마크다운 본문은 그대로 Claude의 시스템 프롬프트가 됩니다.

**디렉토리 구조 예시:**
```
my-skill/
├── SKILL.md           # 필수 — 메인 지침 파일
├── template.md        # 선택 — 스킬에서 참조하는 보조 파일
├── examples/
│   └── sample.md
├── references/
│   └── api-docs.md
└── scripts/
    └── validate.sh
```

SKILL.md 본문에 "이 디렉토리의 `references/api-docs.md`를 참조하라"고 지시하면 Claude가 보조 파일을 필요할 때 직접 읽습니다.

### 저장 위치와 적용 범위

스킬 파일을 어느 경로에 두느냐에 따라 적용 범위가 달라집니다.

| 위치 | 경로 | 적용 범위 | 공유 가능 여부 |
|---|---|---|---|
| 엔터프라이즈(Managed) | 조직 관리자 설정 | 조직 전체 | 예(관리자 제어) |
| 개인 | `~/.claude/skills/<name>/SKILL.md` | 내 모든 프로젝트 | 아니오 |
| 프로젝트 | `.claude/skills/<name>/SKILL.md` | 이 프로젝트만 | 예(git 커밋) |
| 플러그인 | `<plugin>/skills/<name>/SKILL.md` | 플러그인 활성화 위치 | 예(플러그인 배포) |

**우선순위**: 엔터프라이즈 > 개인 > 프로젝트 순으로 적용됩니다. 같은 이름의 기본 제공 번들 스킬을 프로젝트 스킬로 덮어쓸 수 있습니다.

> **팀 공유가 목적이라면 `.claude/skills/`에 두고 git으로 커밋하세요.** 개인 스킬(`~/.claude/skills/`)은 내 컴퓨터에서만 동작하고 클라우드 세션이나 팀원의 환경에는 적용되지 않습니다.

> **레거시 경로**: `.claude/commands/<name>.md` 형식도 계속 동작합니다. 다만 지금은 스킬 디렉토리 구조로 옮기는 편을 권합니다.

### 명령어명은 디렉토리명입니다

> ⚠️ **가장 자주 헷갈리는 지점**: 슬래시 명령어의 이름은 `name` 프론트매터 필드가 **아니라** 디렉토리 이름입니다.

예시:
```
.claude/skills/my-deploy-tool/SKILL.md
```

이 스킬의 명령어는 `/my-deploy-tool`입니다. SKILL.md 안에 `name: "Deploy Application"`이라고 적혀 있어도 슬래시 명령의 이름은 바뀌지 않습니다. `name` 필드는 UI에 표시되는 레이블일 뿐입니다.

### 프론트매터 필드 전체

| 필드 | 필수 여부 | 설명 |
|---|---|---|
| `name` | 아니오 | UI 표시 레이블. 명령어명(디렉토리명)과 다릅니다 |
| `description` | 권장 | 스킬 내용과 호출 시점. Claude가 자동 호출을 판단할 때 씁니다. `when_to_use`와 합산 **1,536자** 상한 |
| `when_to_use` | 아니오 | 추가 트리거 문구. `description`에 합산됩니다 |
| `argument-hint` | 아니오 | 자동완성 UI에 표시할 힌트 (예: `[issue-number]`) |
| `arguments` | 아니오 | 명명된 위치 인수. `$name` 형식으로 본문에서 치환합니다 |
| `disable-model-invocation` | 아니오 | `true` 설정 시 Claude가 자동 호출 불가. 스킬 목록에도 미포함 |
| `user-invocable` | 아니오 | `false` 설정 시 `/` 메뉴에서 숨김. Claude는 여전히 자동 호출 가능 |
| `allowed-tools` | 아니오 | 이 스킬 호출 턴에 권한 없이 사용 가능한 도구 목록 |
| `disallowed-tools` | 아니오 | 이 스킬 활성 동안 제거할 도구 |
| `model` | 아니오 | 이 스킬 턴의 모델 오버라이드. 다음 메시지에서 초기화됩니다 |
| `effort` | 아니오 | `low`/`medium`/`high`/`xhigh`/`max`. 세션 effort 오버라이드 |
| `context` | 아니오 | `fork` 설정 시 격리된 서브에이전트 컨텍스트에서 실행 |
| `agent` | 아니오 | `context: fork` 사용 시 적용할 서브에이전트 타입 |
| `background` | 아니오 | `context: fork` 전용. `false`로 설정하면 결과를 기다립니다 |
| `hooks` | 아니오 | 이 스킬 라이프사이클 전용 훅 |
| `paths` | 아니오 | 스킬 자동 활성화를 특정 경로로 제한하는 glob 패턴 |
| `shell` | 아니오 | `!` 명령 실행에 사용할 셸. `bash`(기본) 또는 `powershell` |
| `metadata` | 아니오 | 자유형 YAML 맵. Claude Code는 내용을 무시합니다 |

> **`allowed-tools` 주의**: 스킬 호출 때 도구 권한을 사전 승인해도 그 승인은 오래가지 않습니다. 권한은 **그 호출 턴에만** 적용되고 다음 메시지에서 초기화됩니다.


## 반복 작업의 스킬화 — 표준화 사례

### 동적 컨텍스트 주입 — `!` 문법

스킬 본문에 셸 명령을 포함하면, 스킬이 호출될 때 그 명령의 실행 결과가 Claude에게 자동으로 전달됩니다.

**인라인 형식:**
```markdown
## 현재 변경 사항

!`git diff HEAD`

## 지침

위 변경 내역을 3줄 이내로 요약하고, 위험 요소가 있으면 표시하세요.
```

**블록 형식 (여러 명령을 한 번에):**
````markdown
```!
node --version
npm --version
git status --short
```
````

스킬이 호출될 때마다 최신 git diff나 빌드 상태가 자동으로 Claude에게 넘어갑니다. 매번 "현재 상태를 확인해 주세요"라고 요청할 필요가 없습니다.

> `!` 기능은 조직 Managed settings에서 `"disableSkillShellExecution": true`로 전체 비활성화할 수 있습니다.

### 문자열 치환 변수

본문에서 쓰는 치환 변수 목록입니다.

| 변수 | 설명 |
|---|---|
| `$ARGUMENTS` | `/skill-name` 뒤의 모든 텍스트 |
| `$ARGUMENTS[N]` | 0 기준 N번째 인수 |
| `$N` | `$ARGUMENTS[N]`의 단축형 |
| `$name` | `arguments` 프론트매터에 선언된 명명 인수 |
| `${CLAUDE_SKILL_DIR}` | 이 스킬의 SKILL.md가 있는 디렉토리 경로 |
| `${CLAUDE_PROJECT_DIR}` | 프로젝트 루트 디렉토리 경로 |
| `${CLAUDE_SESSION_ID}` | 현재 세션 ID |
| `${CLAUDE_EFFORT}` | 현재 effort 레벨 |

### 실전 스킬 작성 예시

**예시 1: 변경사항 자동 요약 (자동 호출 허용)**
```yaml
---
description: 커밋 전 변경 사항을 요약하고 위험 요소를 점검합니다. 사용자가 "무엇이 바뀌었나요?", "diff를 확인해 주세요", "커밋 메시지를 써 주세요"라고 할 때 사용하세요.
---

## 현재 변경 사항

!`git diff HEAD`

## 지침

위 변경 내역을 두세 줄로 요약하고, 위험할 수 있는 항목(파일 삭제, 시크릿 노출 가능성, 브레이킹 체인지 등)을 별도로 표기하세요.
```

`description`에 "언제 호출할지" 기준을 구체적으로 적으면 Claude가 대화 중 스스로 판단해 `/skill-name` 없이도 이 스킬을 로드합니다.

**예시 2: 배포 스킬 (수동 전용, 격리 실행)**
```yaml
---
name: deploy
description: 프로덕션 배포를 수행합니다.
context: fork
disable-model-invocation: true
---

애플리케이션을 배포합니다:
1. 테스트 스위트를 실행합니다
2. 프로덕션 빌드를 생성합니다
3. 배포 대상에 푸시합니다
```

`disable-model-invocation: true`는 Claude의 자동 호출을 막습니다. 사용자가 명시적으로 `/deploy`를 입력할 때만 실행됩니다. `context: fork`로 별도 서브에이전트 컨텍스트에서 격리됩니다.

**예시 3: 커밋 스킬 (도구 사전 승인)**
```yaml
---
name: commit
description: 현재 변경 사항을 스테이징하고 커밋합니다.
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---
```

`allowed-tools`로 git 관련 Bash 명령을 사전 승인해 두면 커밋 과정에서 매번 권한 확인 프롬프트가 뜨지 않습니다.

**예시 4: 리서치 스킬 (포크 서브에이전트 + Explore)**
```yaml
---
name: deep-research
description: 주제를 코드베이스에서 철저히 조사합니다.
context: fork
agent: Explore
---

$ARGUMENTS 주제를 심층 조사합니다:
1. Glob과 Grep으로 관련 파일을 탐색합니다
2. 코드를 읽고 분석합니다
3. 파일 경로를 명시해 결과를 요약합니다
```

`$ARGUMENTS`는 `/deep-research 인증 모듈`처럼 명령 뒤에 입력한 텍스트로 자동 치환됩니다.

### 스킬 작성 보조 도구 — skill-creator

복잡한 스킬을 처음부터 작성하기 어렵다면 `skill-creator`가 도와줍니다.

**플러그인 형태:**
```bash
/plugin install skill-creator@claude-plugins-official
```
테스트 케이스 작성, 격리 eval 실행, 채점, 벤치마킹, A/B 버전 비교, description 튜닝 기능을 제공합니다. 결과물은 스킬 디렉토리 내 `evals/evals.json`, `grading.json`, `benchmark.json` 파일로 저장됩니다.

**저장소 스킬 형태:**
`anthropics/skills` 저장소에도 skill-creator가 포함되어 있습니다. 대화형으로 스킬을 작성하고 eval을 실행하고 개선하는 반복 주기를 지원합니다.

> ⚠️ **`/skillify` 명령은 존재하지 않습니다.** 인터넷 검색에서 간혹 보이는 "skillify"는 공식 문서에 없는 명칭입니다. 스킬 작성 보조 도구의 올바른 이름은 `skill-creator`입니다.

## 스킬 사용 vs 스킬 작성의 경계

### SKILL.md vs CLAUDE.md — 언제 어느 것을

스킬과 CLAUDE.md는 모두 Claude에게 지침을 제공하지만 목적과 작동 방식이 다릅니다.

| 구분 | CLAUDE.md | 스킬(SKILL.md) |
|---|---|---|
| **로드 시점** | 매 세션 시작 시 자동 | 설명: 항상 / 본문: 호출 시만 |
| **토큰 비용** | 매 턴 전체 내용 소비 | 호출 전까지 사실상 0 |
| **적합한 내용** | 사실, 규칙, 짧은 설정 | 긴 절차, 체크리스트, 워크플로우 |
| **호출 방식** | 자동(항상 활성) | 수동(`/name`) 또는 Claude 자동 판단 |
| **호출 후 유지** | 해당 없음(항상 로드) | 세션 나머지 동안 유지 |

**CLAUDE.md에 넣어야 할 것**: "이 프로젝트는 TypeScript를 사용합니다", "커밋 전 반드시 `npm test`를 실행하세요" 같이 항상 적용해야 하는 짧은 규칙.

**SKILL.md에 넣어야 할 것**: 배포 절차, 코드 리뷰 체크리스트, PR 생성 워크플로우처럼 특정 상황에만 필요한 긴 지침.

### 스킬 발견과 로딩 메커니즘

Claude Code가 스킬을 처리하는 순서는 다음과 같습니다.

**1단계. 시작 시 스캔**
- 모든 스킬 디렉토리를 스캔합니다.
- 이름과 설명(`description + when_to_use`) 목록만 컨텍스트에 올립니다.
- `disable-model-invocation: true` 스킬은 목록에 포함하지 않습니다.
- 스킬 목록 전체의 문자 예산은 모델 컨텍스트 창의 약 1%이며 개별 스킬의 할당량은 1,536자입니다.

**2단계. 호출 시 로드**
- `/skill-name` 입력 또는 Claude의 자동 판단으로 스킬이 호출됩니다.
- SKILL.md 본문 전체가 대화에 삽입됩니다.
- 삽입된 본문은 **세션이 끝날 때까지 유지**됩니다. 매 턴 재로드하지 않습니다.

**3단계. 컨텍스트 압축 후**
- 컨텍스트 압축이 발생하면 각 스킬의 최근 호출 중 처음 5,000 토큰을 재첨부합니다.
- 전체 합산 예산은 25,000 토큰이며 최근 호출 우선으로 오래된 스킬은 제거될 수 있습니다.

### 자동 호출 vs 수동 전용

스킬을 만들 때 먼저 결정할 것은 Claude가 스스로 판단해 호출하게 할지, 사용자가 명시적으로 입력할 때만 실행할지입니다.

**자동 호출 허용** (기본값): `description`을 충분히 구체적으로 작성합니다. Claude는 대화 중 스킬 목록의 설명을 보고 현재 상황에 적합하면 스스로 로드합니다.

**수동 전용**: `disable-model-invocation: true`를 설정합니다. 배포, 데이터베이스 마이그레이션처럼 실수로 실행되면 안 되는 작업에 사용합니다.

**메뉴 숨김 + 자동 호출만**: `user-invocable: false`를 설정합니다. `/` 메뉴에는 보이지 않지만 Claude는 여전히 스스로 판단해 호출할 수 있습니다. 내부 보조 스킬처럼 사용자에게 직접 노출하고 싶지 않은 경우에 적합합니다.

> 🔀 **네이티브 vs 팀 (연결)**: 여기서 만든 스킬은 7-1(gstack)·7-2(superpowers)에서 팀 전체가 공유하는 방식과 대비됩니다. 개인 또는 프로젝트 단위 스킬 작성은 이 절에서, 팀 표준화 스킬 배포와 관리는 7장에서 다룹니다.

