## 03-4. CLI 명령과 플래그

슬래시 명령어가 세션 **안**에서 Claude Code를 제어한다면, CLI 플래그는 세션을 **시작할 때** 동작 방식을 결정합니다. `claude` 한 줄에 플래그를 붙이는 것만으로 모델을 바꾸거나, 직전 대화를 이어가거나, 결과만 뽑아내는 스크립트 모드로 실행할 수 있습니다. 이 절에서는 일상에서 가장 자주 쓰는 플래그를 익혀 **터미널 워크플로우를 자립**하는 것을 목표로 합니다.

> **이 페이지 범위**: 기본 실행 형식 · `-p`(print 모드) · `--continue`/`--resume`/`--fork-session` · `--model` · 유용한 서브커맨드(`doctor`·`update`). 권한 관련 플래그(`--permission-mode`)의 세부는 03-5에서 다룹니다. 실측 버전: Claude Code 2.1.284.

전체 플래그 목록은 언제든 터미널에서 확인할 수 있습니다.

```bash
claude --help          # 플래그 전체 목록 출력
claude --version       # 현재 버전 확인
```

<hr>

## 기본 실행 형식 세 가지

`claude`를 어떻게 부르느냐에 따라 동작 방식이 달라집니다.

**① 대화형 세션(기본)**:

```bash
claude
```

프롬프트가 열리고 Enter를 누를 때마다 Claude와 대화를 이어갑니다. 세션을 종료하기 전까지 대화 이력이 유지됩니다.

**② 초기 프롬프트와 함께 시작**:

```bash
claude "src/main.py에 있는 함수 목록을 알려줘"
```

세션을 시작하면서 첫 프롬프트를 바로 전달합니다. Claude가 응답을 마치면 프롬프트가 열려 대화를 이어갈 수 있습니다.

**③ 비대화형 print 모드 (`-p`)**:

```bash
claude -p "이 디렉터리의 Python 파일 개수를 세어줘"
```

Claude가 응답만 출력한 뒤 곧바로 종료합니다. 터미널 프롬프트로 돌아오므로 셸 스크립트나 파이프라인에 활용할 수 있습니다.

```bash
# 파이프 활용 예시
claude -p "버전 번호만 한 줄로 알려줘" | xargs echo "현재 버전:"
```

> 💡 `-p`는 `--print`의 단축형입니다. 자동화 스크립트나 반복 작업처럼 대화 없이 결과만 필요할 때 사용합니다. 대화형 승인이 필요한 파일 편집 작업에는 적합하지 않습니다.

<hr>

## 세션 연속성 플래그 — `--continue`·`--resume`·`--fork-session`

Claude Code를 닫았다가 다시 열어도 이전 대화를 이어갈 수 있습니다. 03-1에서 잠깐 소개한 세션 재개 기능의 전체 옵션을 여기서 정리합니다.

**`--continue` / `-c` — 직전 세션 바로 이어가기**:

```bash
claude --continue      # 이 디렉터리의 가장 최근 대화를 자동으로 재개
claude -c              # 단축 형태
```

별도 선택 없이 마지막으로 사용한 세션을 바로 불러옵니다. "어제 하던 작업 계속"이 필요할 때 가장 빠릅니다.

**`--resume` / `-r` — 세션 선택해서 재개**:

```bash
claude --resume        # 세션 목록 피커 열기
claude -r              # 단축 형태
claude --resume <세션ID>  # 특정 세션 바로 지정
```

`--resume`만 입력하면 최근 세션 목록이 나타납니다. 화살표 키로 원하는 세션을 고르고 Enter를 눌러 재개합니다.

```
최근 세션 목록:

  ● 2026-09-29 14:32 — src/main.py 리팩터링 (23턴)
  ○ 2026-09-28 10:15 — README 초안 작성 (8턴)
  ○ 2026-09-27 17:44 — 테스트 코드 추가 (15턴)
```

**`--fork-session` — 세션 복사본 생성**:

```bash
claude --resume <세션ID> --fork-session
```

기존 세션을 **원본을 보존**하면서 복사본에서 이어갑니다. "이 맥락은 유지하되 다른 방향을 실험해보고 싶을 때" 유용합니다.

**플래그 선택 기준 요약**:

| 상황 | 플래그 |
|---|---|
| 바로 직전 작업 이어가기 | `--continue` (`-c`) |
| 며칠 전 세션으로 돌아가기 | `--resume` (`-r`) |
| 현재 세션 맥락으로 실험 분기 | `--fork-session` |
| 완전히 새 주제 시작 | 플래그 없이 `claude` |

<hr>

## 모델 플래그 — `--model`

세션 시작 시 사용할 모델을 직접 지정합니다. 세션 중에 `/model`로 바꾸는 것과 달리, 이 플래그는 **시작 전에 모델을 고정**합니다.

```bash
claude --model opus         # Opus 5.5 — 복잡한 추론·아키텍처 분석
claude --model sonnet       # Sonnet 5.5 — 일상 코딩 (균형)
claude --model haiku        # Haiku 4.5 — 빠르고 가벼운 단순 작업
claude --model fable        # Fable 5.1 — 최고 성능
claude --model best         # Fable 5.1 (없으면 Opus 5.5)
```

전체 모델 ID 대신 **별칭**을 쓸 수 있습니다. 별칭이 실제 모델 ID에 매핑되는 방식은 버전에 따라 달라질 수 있습니다.

```bash
# 별칭과 전체 ID 모두 사용 가능
claude --model sonnet
claude --model claude-sonnet-5-5   # 동일한 결과
```

> 💡 `--model` 플래그로 시작한 세션의 모델은 해당 세션에서 기본값이 됩니다. 세션 중 `/model`로 변경하면 그 이후부터 적용됩니다. 영구 기본값을 바꾸려면 `/config`를 사용합니다.

**`--effort` 플래그**: 모델이 문제에 쏟는 노력 수준을 조정합니다.

```bash
claude --effort high    # 더 깊이 생각 (응답 느림·품질 높음)
claude --effort low     # 빠른 응답 (단순 질의·초안 작업)
# low | medium | high | xhigh | max
```

<hr>

## 자동 컴팩트 — `--autocompact`

컨텍스트 창이 지정한 임계값에 도달하면 Claude Code가 자동으로 대화를 요약합니다. 긴 작업 세션에서 수동으로 `/compact`를 실행하지 않아도 됩니다.

```bash
claude --autocompact 500k    # 500K 토큰 도달 시 자동 요약
claude --autocompact 200k    # 더 일찍 요약 (더 자주 압축)
claude --autocompact auto    # Claude Code가 자동 판단
```

> 🔀 **컨텍스트 심화(연결)**: 자동 컴팩트 임계값 조정과 컨텍스트 창의 동작 원리는 03-7(컨텍스트 관리 기초)에서 자세히 다룹니다.

<hr>

## 유용한 서브커맨드

`claude` 뒤에 오는 서브커맨드는 세션을 시작하지 않고 특정 관리 작업을 수행합니다.

**`claude doctor` — 설치 진단**:

```bash
claude doctor
```

Claude Code 설치 상태를 점검하고 문제를 자동으로 수정합니다. "뭔가 이상하게 동작하는 것 같다"는 느낌이 들 때 가장 먼저 실행해 보세요.

```
Checking Claude Code installation...

✓ Node.js version: v20.11.0
✓ API connection: OK
✓ Settings: valid
✓ No issues found
```

**`claude update` — 업데이트**:

```bash
claude update            # 최신 버전으로 업데이트
claude install stable    # 안정 채널로 재설치
claude install latest    # 최신 채널(실험적 포함)로 재설치
```

**`claude auth` — 인증 관리**:

```bash
claude auth         # 인증 상태 확인·재로그인
```

API 키 만료나 인증 오류가 생길 때 사용합니다.

**`claude agents` — 백그라운드 에이전트 목록**:

```bash
claude agents       # 실행 중인 백그라운드 세션 목록
```

> 🔀 **백그라운드 에이전트(연결)**: 에이전트를 백그라운드에서 실행하고 결과를 나중에 수집하는 패턴은 04장(네이티브 멀티에이전트)에서 다룹니다. 여기서는 목록 확인 명령이 있다는 것만 알아두면 됩니다.

<hr>

## 플래그 조합 예시

플래그는 조합해서 쓸 수 있습니다.

```bash
# 직전 세션을 Opus 모델로 이어가기
claude --continue --model opus

# print 모드 + 특정 모델
claude -p "이 함수의 복잡도를 분석해줘" --model sonnet

# 직전 세션 + 자동 컴팩트 설정
claude -c --autocompact 500k
```

<hr>

## 플래그 한눈에 보기

이 절에서 다룬 플래그를 한 표로 정리합니다.

| 플래그 | 단축 | 역할 |
|---|---|---|
| `-p` / `--print` | `-p` | 비대화형 — 응답만 출력 후 종료 |
| `--continue` | `-c` | 직전 세션 자동 재개 |
| `--resume [ID]` | `-r` | 세션 피커 또는 ID로 재개 |
| `--fork-session` | — | 세션 복사본 생성 후 재개 |
| `--model <별칭>` | — | 시작 시 모델 지정 |
| `--effort <수준>` | — | 노력 수준 조정 |
| `--autocompact <값>` | — | 자동 컴팩트 임계값 설정 |

서브커맨드:

| 명령 | 역할 |
|---|---|
| `claude doctor` | 설치 진단·자동 수정 |
| `claude update` | 버전 업데이트 |
| `claude auth` | 인증 관리 |
| `claude agents` | 백그라운드 에이전트 목록 |

<hr>

## 정리

CLI 플래그는 세션을 열기 전에 **동작 방식을 결정**하는 설정값입니다. `--continue`로 이어가기, `-p`로 스크립트 활용, `--model`로 모델 전환 — 이 세 가지만 익혀도 일상 워크플로우 대부분을 커버합니다.

다음 03-5에서는 **Plan Mode와 권한 시스템**을 다룹니다. Claude가 파일을 건드리기 전에 계획을 먼저 세우게 하거나, 어떤 도구를 허용할지 직접 제어하는 방법을 익혀서 Claude Code를 더 안전하고 예측 가능하게 사용할 수 있게 됩니다.
