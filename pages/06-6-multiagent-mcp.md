## 06-6. 멀티에이전트에 유용한 추가 MCP 도구

앞에서 살펴본 Filesystem·GitHub·Redis MCP 외에, 멀티에이전트 팀 구성에서 실질적으로 쓸 수 있는 도구들이 더 있습니다. 공유 기억, 추론 구조화, 브라우저 자동화, 문서 수집, 시간 정규화, 버전 관리까지 — 역할별로 적합한 도구를 골라 팀에 추가하면 에이전트 간 협업의 폭이 넓어집니다.

> **런타임 패턴 사전 안내**
> - Node 계열: `.mcp.json`에서 `"command": "npx"` 사용
> - Python 계열: `"command": "uvx"` 또는 `"command": "uv"` 사용 — npm 패키지 없음

| 도구 | 패키지 | 공식 여부 | 상태 |
|---|---|---|---|
| Memory | `@modelcontextprotocol/server-memory` | ✅ Anthropic 공식 | 활성 |
| Sequential Thinking | `@modelcontextprotocol/server-sequential-thinking` | ✅ Anthropic 공식 | 활성 |
| Playwright | `@playwright/mcp` | ✅ Microsoft 공식 | 활성 |
| Puppeteer | `@modelcontextprotocol/server-puppeteer` | ✅ Anthropic 공식 | 활성 |
| Context7 | `@upstash/context7-mcp` | 커뮤니티 (Upstash) | 사실상 표준 |
| Fetch | `mcp-server-fetch` | ✅ Anthropic 공식 | 활성 |
| Time | `mcp-server-time` | ✅ Anthropic 공식 | 활성 |
| Git | `mcp-server-git` | ✅ Anthropic 공식 | ⚠️ 초기 개발 단계 |

---

### Memory MCP — 에이전트 간 공유 장기기억

**패키지:** `@modelcontextprotocol/server-memory` (Anthropic 공식, 활성)

에이전트는 기본적으로 상태가 없습니다. 세션이 끊기면 직전 대화에서 쌓인 맥락은 사라집니다. Memory MCP는 **지식 그래프** 형태의 영속 저장소로 이 문제를 해결합니다. 데이터는 로컬 `memory.json`에 저장되고, 모든 에이전트가 동일한 MCP 서버를 통해 접근합니다.

**데이터 모델:** Entity(노드) → Relation(방향성 엣지) → Observation(엔티티에 붙은 사실 목록)

**노출 도구:**

| 도구 | 기능 |
|---|---|
| `create_entities` | 엔티티 노드 생성 |
| `create_relations` | 엔티티 간 방향성 관계 추가 |
| `add_observations` | 엔티티에 사실 추가 |
| `search_nodes` | 이름·타입·내용 퍼지 검색 |
| `open_nodes` | 특정 노드 이름으로 직접 조회 |
| `read_graph` | 전체 지식 그래프 읽기 |
| `delete_entities` / `delete_observations` / `delete_relations` | 항목 삭제 |

**멀티에이전트 활용:**
리서처 에이전트(지훈)가 조사 완료 후 `create_entities`로 결과를 그래프에 저장합니다. 이후 작성 에이전트(서연)가 `search_nodes`로 필요한 항목을 꺼내 씁니다. 컨텍스트 창을 직접 전달할 필요가 없고, 작업 순서도 강제되지 않습니다. 역할이 다른 에이전트들이 같은 정보 기반 위에서 비동기로 협업하는 토대가 됩니다.

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

> Redis MCP(앞 절 참고)와 역할이 다릅니다. Redis는 에이전트 간 KV 상태·태스크 큐·Pub/Sub IPC에 쓰고, Memory는 지식 그래프 형태의 장기 사실 저장에 씁니다.

---

### Sequential Thinking MCP — 플래너 에이전트의 추론 구조화

**패키지:** `@modelcontextprotocol/server-sequential-thinking` (Anthropic 공식, 활성)

단일 도구 `sequentialthinking`을 노출합니다. 일반적인 순차 추론과 달리 **트리 구조**로 사고를 전개할 수 있습니다. 중간 가정이 틀렸을 때 처음부터 다시 시작하는 대신, 해당 단계에서 분기하거나 수정 표시를 달고 이어갈 수 있습니다.

**주요 파라미터:**

| 파라미터 | 설명 |
|---|---|
| `thought` / `thoughtNumber` / `totalThoughts` | 이번 사고 내용·단계 번호·전체 단계 수 |
| `nextThoughtNeeded` | 추론을 계속할지 여부 |
| `isRevision` / `revisesThought` | 이전 단계 수정 여부·수정 대상 단계 |
| `branchFromThought` / `branchId` | 분기 시작 단계·분기 식별자 |

**멀티에이전트 활용:**
플래너 에이전트(민준 역할)가 복잡한 태스크를 검증 가능한 서브스텝으로 분해하는 데 씁니다. 초기 계획에서 가정 오류가 발견되면 `isRevision: true`와 `branchFromThought`로 해당 지점부터 대안 경로를 전개합니다. 분해된 각 스텝은 실행 에이전트에게 단위 작업으로 넘깁니다.

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

---

### Playwright MCP — 브라우저 자동화 및 렌더 검증 ★팀 실사용

**패키지:** `@playwright/mcp` (Microsoft 공식, 활성)

브라우저를 코드 없이 MCP 도구 호출만으로 제어합니다. `browser_snapshot`이 페이지를 **접근성 트리(ARIA 구조)**로 돌려준다는 점이 특징입니다. 스크린샷 이미지가 아니므로 비전 모델 없이 구조를 검증할 수 있고 토큰도 아낄 수 있습니다.

**노출 도구:**

| 도구 | 기능 |
|---|---|
| `browser_navigate` | URL 이동 |
| `browser_snapshot` | 접근성 트리(ARIA) 스냅샷 — 비전 모델 불필요 |
| `browser_take_screenshot` | PNG 스크린샷 캡처 |
| `browser_click` / `browser_type` | 요소 클릭·텍스트 입력 |
| `browser_evaluate` | 페이지 내 JavaScript 실행 |
| `browser_console_messages` | 브라우저 콘솔 로그 읽기 |
| `browser_wait_for` | 셀렉터·조건 충족까지 대기 |

**팀 실경험 — 블로그 렌더 검증:**
배포 후 QA 에이전트(수아)가 `browser_navigate`로 발행된 포스트 URL에 접근하고, `browser_snapshot`으로 제목·본문·이미지 렌더 구조를 확인합니다. 이후 `browser_take_screenshot`으로 시각 캡처를 남기고 팀장(쭌)에게 pass/fail을 보고합니다. 개발자가 브라우저를 직접 열지 않아도 에이전트가 렌더 이상을 감지합니다.

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

---

### Puppeteer MCP — 비주얼 캡처 및 JS 렌더 스크래핑

**패키지:** `@modelcontextprotocol/server-puppeteer` (Anthropic 공식, 활성 / v2025.5.12)

**노출 도구:** `puppeteer_navigate`, `puppeteer_screenshot`(base64 반환), `puppeteer_click`, `puppeteer_fill`, `puppeteer_evaluate`, `puppeteer_console`

`puppeteer_screenshot`은 페이지를 base64 이미지로 반환합니다. 텍스트 구조 분석보다 **시각적 레이아웃 확인**이 목적인 경우, 또는 스크린샷을 비전 모델 에이전트에게 전달해 레이아웃 이상을 탐지하는 파이프라인에 적합합니다.

**Playwright와의 역할 분담:**
- Playwright: 접근성 스냅샷 우선 → 비전 모델 없이 구조 검증, 토큰 절약
- Puppeteer: 스크린샷 우선 → 비주얼 비교·비전 모델 파이프라인

```json
{
  "mcpServers": {
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

---

### Context7 MCP — 최신 라이브러리 문서 실시간 조회

**패키지:** `@upstash/context7-mcp` (Upstash 커뮤니티, 사실상 표준)
**대안 연결:** `https://mcp.context7.com/mcp` (Streamable HTTP, API 키 선택)

> **공식 여부 참고:** Upstash 커뮤니티 패키지로, Anthropic 공식 패키지가 아닙니다. 다만 동일 기능의 Anthropic 공식 대안이 없어 현재 사실상 표준으로 자리잡았습니다.

LLM의 학습 데이터 컷오프 이후 출시되거나 크게 변경된 라이브러리를 다룰 때, 에이전트가 구버전 API를 그대로 쓰는 실수가 생깁니다. Context7은 이 문제를 잡아주는 전용 도구입니다.

**노출 도구:**

| 도구 | 기능 |
|---|---|
| `resolve-library-id` | 라이브러리명 → Context7 내부 ID 변환 |
| `get-library-docs` | 버전별 최신 공식 문서 및 코드 예제 반환 |

프롬프트에 `use context7`을 포함하면 자동 호출 체인이 작동합니다.

**멀티에이전트 활용:**
코딩 에이전트(서연)가 라이브러리를 사용하기 전 Context7 에이전트에 문서 조회를 위임합니다. 최신 API를 확인하고 코드를 작성하므로 구버전 문법 오용과 할루시네이션을 예방합니다. 예: Next.js 12 문법을 Next.js 15 프로젝트에 적용하는 실수 방지.

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

---

### Fetch MCP — 경량 HTTP 문서 수집

**패키지:** `mcp-server-fetch` (PyPI, Anthropic 공식, 활성) — **npm 없음, Python 전용**

단일 도구 `fetch`를 노출합니다. URL을 가져와 Markdown으로 변환해 반환하며, `robots.txt`를 기본으로 준수합니다.

**주요 파라미터:**

| 파라미터 | 설명 |
|---|---|
| `url` | 가져올 URL |
| `max_length` | 반환 최대 길이 |
| `start_index` | 청크 단위 읽기 시작 위치 |
| `raw` | Markdown 변환 없이 HTML 원문 반환 |

**멀티에이전트 활용:**
JavaScript 렌더링이 불필요한 HTTP 문서 수집에 씁니다. `start_index`를 활용하면 긴 문서를 여러 에이전트가 청크 단위로 나눠 읽을 수 있습니다. 단순 문서 수집은 Fetch, JS 렌더링이 필요한 경우는 Playwright로 역할을 나누면 토큰을 절약할 수 있습니다.

```json
{
  "mcpServers": {
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    }
  }
}
```

---

### Time MCP — 타임존 정규화 및 시간 게이팅

**패키지:** `mcp-server-time` (PyPI, Anthropic 공식, 활성) — **npm 없음, Python 전용**

**노출 도구:**

| 도구 | 기능 |
|---|---|
| `get_current_time` | IANA 타임존 기준 현재 시각 반환 |
| `convert_time` | 두 타임존 간 시각 변환 |

`--local-timezone Asia/Seoul` 플래그로 기본 타임존을 지정합니다.

**멀티에이전트 활용:**
발행 에이전트와 로깅 에이전트 간 타임스탬프를 정규화합니다. 비즈니스 로직으로 시간 게이팅이 필요한 경우(예: "KST 오전 9시~오후 6시에만 발행 허용")에 판단 기준을 제공합니다. 에이전트 간 스케줄 이벤트를 생성할 때 타임존 오산으로 인한 오류를 방지합니다.

```json
{
  "mcpServers": {
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone", "Asia/Seoul"]
    }
  }
}
```

---

### Git MCP — 버전 관리 작업의 MCP 레이어 통합

**패키지:** `mcp-server-git` (PyPI, Anthropic 공식) — **npm 없음, Python 전용**

> ⚠️ **초기 개발 단계:** 공식 README에 "Currently in early development; functionality and available tools are subject to change"라고 명시되어 있습니다. 기능과 도구 목록이 변경될 수 있으므로 프로덕션 파이프라인 적용 시 주의가 필요합니다.

의존성: `gitpython`, `mcp`, `click`, `pydantic`

**노출 도구:**

| 도구 | 기능 |
|---|---|
| `git_status` | 작업 트리 상태 확인 |
| `git_diff_unstaged` / `git_diff_staged` | 스테이지 전후 diff |
| `git_diff` | 브랜치·커밋 간 diff |
| `git_add` / `git_commit` | 파일 스테이징 및 커밋 |
| `git_reset` | 스테이징 취소 |
| `git_log` | 커밋 히스토리 (`max_count`, `since`/`until` ISO 8601 지원) |
| `git_create_branch` / `git_checkout` | 브랜치 생성 및 전환 |
| `git_search_commits` | 커밋 메시지 패턴 검색 |
| `git_show` | 특정 커밋 내용 표시 |
| `git_init` | 저장소 초기화 |

**멀티에이전트 활용:**
코딩 에이전트(서연)가 파일 수정 후 `git_add` + `git_commit`을 직접 호출합니다. 리뷰어 에이전트(태양)가 `git_diff`로 변경사항을 감사하고, 최종 push는 팀장(쭌)이 결정합니다. 버전 관리 작업이 MCP 레이어 안에서 이루어지므로, 변경 이력을 감사하고(auditable) 재현하기(reproducible) 좋은 형태로 기록됩니다.

```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "/path/to/repo"]
    }
  }
}
```

---

### 도구 선택 가이드 (기존 도구 포함 전체)

기존 챕터에서 다룬 도구와 이번 신규 도구를 합쳐 역할별로 정리합니다.

| 필요한 기능 | 권장 도구 | 비고 |
|---|---|---|
| 파일시스템 읽기·쓰기 | Filesystem MCP | 기존 수록 |
| GitHub PR·이슈·코드 탐색 | GitHub MCP | 기존 수록 |
| 에이전트 간 KV 상태·태스크 큐·IPC | Redis MCP | 기존 수록 |
| 에이전트 간 장기 지식 그래프 공유 | Memory MCP | 이번 추가 |
| 복잡한 태스크 트리 구조 분해 | Sequential Thinking MCP | 이번 추가 |
| 브라우저 구조 검증 (토큰 절약) | Playwright MCP | 이번 추가 ★팀 실사용 |
| 비주얼 스크린샷·비전 모델 파이프라인 | Puppeteer MCP | 이번 추가 |
| 최신 라이브러리 API 문서 조회 | Context7 MCP | 이번 추가 |
| 경량 HTTP 문서 수집 | Fetch MCP | 이번 추가 |
| 타임존 정규화·시간 게이팅 | Time MCP | 이번 추가 |
| 버전 관리 감사·브랜치 분기 | Git MCP | 이번 추가 ⚠️ 초기개발 |
