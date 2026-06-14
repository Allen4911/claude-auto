## 08-5. Redis 에이전트 상태공유

## 이 절에서 배우는 것

[08-4절](08-4-conflict-prevention.md)에서는 파일 충돌 방지를 위해 Redis 락과 Pub/Sub를 간략히 소개했다. 이 절에서는 Redis 자체를 집중적으로 다룬다 — 키 스키마 설계, 하트비트 아키텍처, Pub/Sub와 폴링의 혼합 전략, 그리고 메시지 유실 없이 상태를 보존하는 Streams 패턴까지 심화한다.

> 💡 **Redis란?** Redis(레디스)는 메모리에 데이터를 저장하는 고속 데이터베이스입니다. 디스크 대신 RAM을 사용하기 때문에 읽고 쓰는 속도가 매우 빠릅니다. AI 팀에서는 에이전트 상태("서연: 작업 중"), 파일 잠금("이 파일은 서연이 편집 중"), 팀원 간 메시지 전달 등에 사용합니다.

> 💡 **08-4와의 관계** 08-4에서 소개한 `lock:파일경로` 패턴과 `team:events` pub/sub가 이 절에서 정규화·확장됩니다. 08-4 충돌 체크리스트의 "Redis 확인" 항목을 실제로 구현하는 방법이 바로 여기에 있습니다.

이 절에서 다루는 내용:

- **Pub/Sub vs 폴링**: 언제 무엇을 선택하는가
- **키 스키마**: 팀 전체가 공유하는 이름 규칙
- **하트비트**: 에이전트 생존 감지 구조
- **Redis Streams**: 메시지 유실 없는 내구성 확보
- **전체 흐름**: Phase 완료부터 리뷰 요청까지

<hr>

## Pub/Sub와 폴링 — 언제 무엇을 쓸까

두 방식은 서로 대체재가 아니라 상호 보완재다.

| 방식 | 특징 | 팀에서 쓰는 상황 |
|------|------|----------------|
| **Pub/Sub** | 이벤트 발생 즉시 구독자에게 푸시. 저지연. | 서연 Phase 완료 → 태양 즉시 리뷰 알림 |
| **Key 폴링** | 주기적으로 상태 키를 직접 조회. 에이전트 다운 내성. | 쭌 5분 체크루프, 전체 팀 상태 대시보드 |

> 💡 **비유: Pub/Sub는 카톡 알림, 폴링은 게시판 새로고침** Pub/Sub는 "서연이 완료했다"는 메시지를 태양에게 즉시 푸시합니다. 태양이 잠깐 오프라인이었다면 메시지를 못 받습니다. 폴링은 쭌이 5분마다 Redis를 열어 "지금 서연 상태가 뭐야?" 하고 직접 조회하는 방식입니다. 오프라인이어도 나중에 확인할 수 있습니다.

**혼합 전략**: 이벤트 알림은 Pub/Sub으로 보내고, 상태 조회는 폴링으로 읽는다.

```
서연(서연) ─── PUBLISH channel:team:events "phase:8:done" ──→ 태양(즉시 수신)
                                                               ↓
쭌(5분 루프) ─── GET agent:서연:status ─────────────────→ "idle"
```

> ⚠️ **Pub/Sub의 함정** Redis 기본 Pub/Sub는 구독자가 오프라인 상태일 때 메시지가 소실됩니다. 신뢰성이 필요한 이벤트는 뒤에서 다루는 Redis Streams를 사용하세요.

### 따라하기: Pub/Sub 기본 동작 확인

Redis가 설치되어 있다면 터미널 두 개를 열어 실습할 수 있습니다.

```bash
# 터미널 1: 구독자 (태양 역할)
redis-cli SUBSCRIBE channel:team:events
# 이 상태에서 기다립니다

# 터미널 2: 발행자 (서연 역할)
redis-cli PUBLISH channel:team:events "phase:8:done"

# 터미널 1에 즉시 출력됩니다:
# 1) "message"
# 2) "channel:team:events"
# 3) "phase:8:done"
```

<hr>

## 키 스키마 설계

팀 전체가 일관된 키 이름을 사용해야 충돌과 혼선을 막을 수 있다. 아래는 표준 스키마다.

> 💡 **키 스키마(Key Schema)란?** Redis에 저장할 데이터의 이름 규칙입니다. `agent:서연:status`처럼 `대분류:이름:속성` 형태로 정하면, 서연의 모든 상태 키를 `agent:서연:*` 패턴으로 한 번에 조회할 수 있습니다. 규칙 없이 쓰면 "서연상태", "seoyeon_status", "s_stat" 같이 중구난방이 되어 자동화가 불가능해집니다.

### 에이전트 상태 키

```
agent:{이름}:status       # 현재 상태 (working | idle | blocked | rate_limited)
agent:{이름}:heartbeat    # Unix 타임스탬프 (TTL 120s — 만료 시 hang 판단)
agent:{이름}:context_pct  # 컨텍스트 사용률 0~100
agent:{이름}:task         # 현재 작업 한 줄 설명
```

> 💡 **TTL(Time To Live)이란?** 키의 유효 기간입니다. `EX 120`은 "120초 후 자동 삭제"를 의미합니다. 하트비트 키에 TTL을 설정하면, 에이전트가 갑자기 다운되어 갱신을 못 해도 120초 후 키가 사라집니다. 쭌이 "키가 없다 = 에이전트가 죽었다"로 판단할 수 있게 됩니다.

**예시**

```bash
# 서연이 작업 시작 시
redis-cli SET agent:서연:status "working"
redis-cli SET agent:서연:task "08-5 페이지 작성"
redis-cli SET agent:서연:context_pct 42

# 하트비트 갱신 (15초마다)
redis-cli SET agent:서연:heartbeat $(date +%s) EX 120
```

### 락 키

```
lock:file:{경로}    # 파일 작업 점유 (담당자명, TTL 3600s)
lock:phase:{번호}   # Phase 단위 작업 점유 (담당자명)
```

> 💡 **NX 옵션이란?** `SET key value NX`는 "키가 없을 때만 설정"입니다. 이미 서연이 락을 잡고 있으면 수아가 같은 파일에 `SET lock:file:... NX`를 해도 실패합니다. 이것이 "원자적 락 획득"입니다 — 두 에이전트가 동시에 시도해도 딱 한 명만 성공합니다.

**예시**

```bash
# 서연이 파일 편집 전 락 획득
redis-cli SET lock:file:pages/08-5-redis-state-sharing.md "서연" EX 3600 NX
# NX: 이미 락이 있으면 실패 → 충돌 방지

# 락 획득 성공 여부 확인
RESULT=$(redis-cli SET lock:file:pages/08-5.md "서연" EX 3600 NX)
if [ "$RESULT" = "OK" ]; then
  echo "락 획득 성공 — 편집 시작"
else
  echo "락 획득 실패 — 다른 에이전트 작업 중"
fi
```

### 팀 Phase 키

```
team:phase:{n}:status   # planned | in_progress | review | done
team:phase:{n}:owner    # 담당 팀원 이름
team:phase:{n}:commit   # 완료 커밋 해시 (done 상태에서 기록)
```

**예시**

```bash
redis-cli SET team:phase:8:status "in_progress"
redis-cli SET team:phase:8:owner  "서연"

# Phase 완료 시
redis-cli SET team:phase:8:status "done"
redis-cli SET team:phase:8:commit "a1b2c3d"
```

### 큐 키

```
queue:review   # 리뷰 대기 목록 (LPUSH로 추가, RPOP으로 꺼냄)
```

> 💡 **LPUSH/RPOP으로 큐를 구현하는 이유** LPUSH는 리스트 왼쪽(앞)에 항목을 추가하고, RPOP은 오른쪽(뒤)에서 꺼냅니다. 먼저 들어온 것이 먼저 나오는 FIFO(선입선출) 큐가 됩니다. 서연이 먼저 완료한 파일을 태양이 먼저 리뷰하게 됩니다.

**예시**

```bash
# 서연이 리뷰 요청 추가
redis-cli LPUSH queue:review "pages/08-5-redis-state-sharing.md"

# 태양이 다음 리뷰 대상 꺼내기
redis-cli RPOP queue:review
```

### 채널 키

```
channel:team:events    # 팀 전체 이벤트 브로드캐스트
channel:agent:{이름}   # 특정 에이전트 개인 채널 (DM)
```

### 따라하기: 팀 상태 한 번에 조회하기

```bash
# 모든 에이전트 상태를 한 번에 조회
for AGENT in 쭌 민준 지훈 수아 서연 태양; do
  STATUS=$(redis-cli GET "agent:${AGENT}:status" 2>/dev/null || echo "미설정")
  TASK=$(redis-cli GET "agent:${AGENT}:task" 2>/dev/null || echo "-")
  CTX=$(redis-cli GET "agent:${AGENT}:context_pct" 2>/dev/null || echo "0")
  echo "[${AGENT}] status=${STATUS} ctx=${CTX}% task=${TASK}"
done

# 리뷰 큐 잔량 확인
echo "리뷰 대기: $(redis-cli LLEN queue:review)개"
```

<hr>

## 하트비트 아키텍처

하트비트는 에이전트가 살아있음을 증명하는 신호다. TTL과 함께 설계하면 에이전트가 비정상 종료되어도 자동으로 "응답 없음" 상태가 된다.

```
[에이전트 루프]                    [쭌 5분 체크루프]
  매 15초:                           매 5분:
  SET agent:서연:heartbeat           KEYS agent:*:heartbeat 조회
      $(date +%s) EX 120     →       TTL 남은 키 = 정상
                                     만료된 키   = hang/rate-limit 의심
                                                  → reboot-pane.sh 호출
```

> 💡 **비유: 생존 신호등** 잠수함은 주기적으로 신호를 보내 "우리 살아있다"를 알립니다. 하트비트도 마찬가지입니다. 서연이 15초마다 Redis에 "나 살아있어요"(하트비트 갱신)를 보냅니다. 쭌이 5분 후 확인했을 때 신호가 없으면(키 만료) "서연이 뭔가 문제가 생겼다"고 판단합니다.

**TTL 설계 근거**

| 항목 | TTL | 이유 |
|------|-----|------|
| 하트비트 | 120s | 15s 갱신 주기 × 8배 여유 |
| 파일 락 | 3600s | 크래시 시 자동 해제, 장시간 작업 허용 |
| Phase 상태 | 없음 | 소실 방지 — 수동 삭제만 |
| 리뷰 큐 | 없음 | 항목 유실 방지 |

> 💡 **갱신 주기 × 8배 여유를 두는 이유** 15초마다 갱신하는데 TTL을 20초로 설정하면, 한 번이라도 갱신이 지연되면 키가 만료됩니다. 8배(120초)를 주면 갱신이 7번 연속 실패해도 키가 살아있습니다. 일시적 처리 지연으로 잘못된 경보가 울리는 상황을 방지합니다.

### 따라하기: 하트비트 시뮬레이션

```bash
# 에이전트 하트비트 시작 (백그라운드 루프)
(while true; do
  redis-cli SET agent:서연:heartbeat $(date +%s) EX 120 > /dev/null
  sleep 15
done) &
HEARTBEAT_PID=$!

echo "하트비트 시작 (PID: $HEARTBEAT_PID)"

# 5초 후 TTL 확인
sleep 5
echo "하트비트 TTL: $(redis-cli TTL agent:서연:heartbeat)초"

# 시뮬레이션 종료
kill $HEARTBEAT_PID 2>/dev/null
```

<hr>

## Redis Streams — 메시지 유실 없는 내구성

기본 Pub/Sub는 오프라인 구독자에게 메시지를 전달하지 못한다. **Redis Streams**를 사용하면 메시지가 로그처럼 쌓여 나중에도 읽을 수 있다.

> 💡 **Redis Streams란?** 메시지를 시간 순서대로 로그처럼 저장하는 구조입니다. 태양이 잠깐 오프라인이었더라도 나중에 연결하면 그동안 쌓인 이벤트를 처음부터 다시 읽을 수 있습니다. 일반 Pub/Sub이 "라디오 방송"(실시간에 없으면 못 들음)이라면, Streams는 "팟캐스트"(언제든 다시 들을 수 있음)입니다.

```bash
# 서연이 이벤트 발행 (Streams에 기록)
redis-cli XADD stream:team:events '*' \
  type "phase_done" \
  phase "8" \
  owner "서연" \
  commit "a1b2c3d"

# 태양이 구독 (마지막으로 읽은 ID 이후부터)
redis-cli XREAD COUNT 10 BLOCK 5000 \
  STREAMS stream:team:events $LAST_ID
```

> 💡 **`*`와 `$LAST_ID`의 의미** `XADD stream:... '*'`에서 `*`는 "타임스탬프 기반 ID를 자동 생성해줘"입니다. `XREAD ... $LAST_ID`에서 `$LAST_ID`는 "내가 마지막으로 읽은 메시지 ID 이후부터 읽어줘"입니다. 처음 읽을 때는 `0`을 사용하면 전체 기록을 읽습니다.

**Pub/Sub vs Streams 선택 기준**

| 기준 | Pub/Sub | Streams |
|------|---------|---------|
| 구독자 오프라인 내성 | ✗ 메시지 소실 | ✓ 나중에 재생 가능 |
| 전달 보장 | ✗ | ✓ (ACK 패턴) |
| 이벤트 이력 조회 | ✗ | ✓ |
| 구현 복잡도 | 낮음 | 중간 |
| 권장 사용처 | 실시간 알림 (소실 허용) | Phase 완료·커밋 이벤트 |

> **결정 규칙**: 이벤트가 유실되면 다음 단계 작업이 시작되지 않는가? → Streams. 유실돼도 폴링으로 보완 가능한가? → Pub/Sub.

### 따라하기: Streams로 Phase 이벤트 기록하기

```bash
# Phase 완료 이벤트 기록
redis-cli XADD stream:team:events '*' \
  type "phase_done" phase "8" owner "서연" commit "a1b2c3d"

# 전체 이벤트 이력 조회 (처음부터)
redis-cli XREAD COUNT 100 STREAMS stream:team:events 0

# 최근 5개 이벤트 조회
redis-cli XREVRANGE stream:team:events + - COUNT 5
```

<hr>

## 전체 흐름 예시

서연이 Phase 8을 완료하고 태양에게 리뷰를 요청하는 흐름을 Redis로 구현한다.

```bash
# ── 서연: 작업 완료 처리 ──────────────────────────────

# 1. 파일 락 해제
redis-cli DEL lock:file:pages/08-5-redis-state-sharing.md

# 2. 에이전트 상태 업데이트
redis-cli SET agent:서연:status "idle"
redis-cli SET agent:서연:task   "대기 중"

# 3. Phase 상태 → review
redis-cli SET team:phase:8:status "review"

# 4. 리뷰 큐에 추가
redis-cli LPUSH queue:review "pages/08-5-redis-state-sharing.md"

# 5. Streams에 이벤트 기록 + Pub/Sub 동시 발행
redis-cli XADD stream:team:events '*' type "review_requested" file "pages/08-5-redis-state-sharing.md" from "서연"
redis-cli PUBLISH channel:agent:태양 "리뷰 요청: pages/08-5-redis-state-sharing.md"


# ── 태양: 리뷰 수신 ──────────────────────────────────

# Pub/Sub 구독 중 → 즉시 알림 수신
# (오프라인이었어도 XREAD로 Streams 재생 가능)
NEXT=$(redis-cli RPOP queue:review)
echo "리뷰 대상: $NEXT"
```

> 💡 **Streams + Pub/Sub를 동시에 쓰는 이유** Pub/Sub는 태양이 온라인이면 즉시 알립니다. Streams는 태양이 오프라인이었더라도 나중에 이벤트를 복구합니다. 두 가지를 동시에 쓰면 "빠름 + 내구성"을 모두 얻습니다. 리뷰 큐(LPUSH)는 중복 수신 방지 역할도 합니다 — 태양이 RPOP으로 꺼내면 다른 에이전트가 같은 파일을 또 리뷰하지 않습니다.

<hr>

## 장애 감지 패턴

쭌의 5분 체크 루프에서 하트비트 만료를 감지하는 스크립트 예시다.

```bash
#!/usr/bin/env bash
# heartbeat-check.sh — 쭌 5분 루프에서 호출

AGENTS=(쭌 민준 지훈 수아 서연 태양)

for AGENT in "${AGENTS[@]}"; do
  TTL=$(redis-cli TTL "agent:${AGENT}:heartbeat")
  STATUS=$(redis-cli GET "agent:${AGENT}:status")

  if [[ "$TTL" == "-2" ]]; then
    echo "[!!] ${AGENT}: 하트비트 키 없음 — 미초기화 또는 장기 다운"
  elif [[ "$TTL" -lt 30 ]]; then
    echo "[??] ${AGENT}: 하트비트 곧 만료 (남은 TTL: ${TTL}s) — hang 의심"
    # reboot-pane.sh 호출 또는 쭌에게 경고 전달
  else
    echo "[OK] ${AGENT}: 정상 (상태=${STATUS}, TTL=${TTL}s)"
  fi
done
```

> 💡 **TTL 값이 `-2`인 경우** Redis에서 `TTL` 명령은 키가 없으면 `-2`를 반환하고, TTL이 설정되지 않은 키(만료 없음)면 `-1`을 반환합니다. `-2`는 에이전트가 한 번도 하트비트를 등록하지 않았거나, 이미 키가 만료되어 사라진 경우입니다.

**장애 유형별 대응**

| TTL 값 | 의미 | 쭌의 대응 |
|--------|------|----------|
| 60~120 | 정상 | 이상 없음 |
| 1~29 | 갱신 지연 의심 | 경고 로그, 다음 체크까지 관찰 |
| -2 (키 없음) | 미초기화 또는 다운 | reboot-pane.sh 실행 |
| -1 (TTL 없음) | 하트비트 키 설정 오류 | TTL 재설정 지시 |

<hr>

## 핵심 정리

| 주제 | 핵심 규칙 |
|------|----------|
| 알림 방식 | 이벤트 → Pub/Sub, 상태 조회 → 폴링 |
| 내구성 필요 시 | Streams 사용 (소실 불가 이벤트) |
| 하트비트 TTL | 120s (갱신 주기 15s × 8배) |
| 파일 락 TTL | 3600s + NX 옵션으로 원자적 획득 |
| Phase·큐 키 | TTL 없음 (소실 방지) |
| 08-4 연계 | 08-4 락 패턴의 정규화·확장판이 이 절 |
| Streams vs Pub/Sub | 소실 허용 → Pub/Sub, 소실 불가 → Streams |

> **이 절의 핵심 한 줄**: Redis는 에이전트 팀의 중앙 신경계 — 누가 살아있고, 누가 무엇을 하고, 어떤 이벤트가 발생했는지를 모두 기록하고 전달합니다.
