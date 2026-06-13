## 8-5. Redis 에이전트 상태공유

## 이 절에서 배우는 것

[08-4절](08-4-conflict-prevention.md)에서는 파일 충돌 방지를 위해 Redis 락과 Pub/Sub를 간략히 소개했다. 이 절에서는 Redis 자체를 집중적으로 다룬다 — 키 스키마 설계, 하트비트 아키텍처, Pub/Sub와 폴링의 혼합 전략, 그리고 메시지 유실 없이 상태를 보존하는 Streams 패턴까지 심화한다.

> 💡 **08-4와의 관계** 08-4에서 소개한 `lock:파일경로` 패턴과 `team:events` pub/sub가 이 절에서 정규화·확장됩니다. 08-4 충돌 체크리스트의 "Redis 확인" 항목을 실제로 구현하는 방법이 바로 여기에 있습니다.

<hr>

## Pub/Sub와 폴링 — 언제 무엇을 쓸까

두 방식은 서로 대체재가 아니라 상호 보완재다.

| 방식 | 특징 | 팀에서 쓰는 상황 |
|------|------|----------------|
| **Pub/Sub** | 이벤트 발생 즉시 구독자에게 푸시. 저지연. | 서연 Phase 완료 → 태양 즉시 리뷰 알림 |
| **Key 폴링** | 주기적으로 상태 키를 직접 조회. 에이전트 다운 내성. | 쭌 5분 체크루프, 전체 팀 상태 대시보드 |

**혼합 전략**: 이벤트 알림은 Pub/Sub으로 보내고, 상태 조회는 폴링으로 읽는다.

```
서연(서연) ─── PUBLISH channel:team:events "phase:8:done" ──→ 태양(즉시 수신)
                                                               ↓
쭌(5분 루프) ─── GET agent:서연:status ─────────────────→ "idle"
```

> ⚠️ **Pub/Sub의 함정** Redis 기본 Pub/Sub는 구독자가 오프라인 상태일 때 메시지가 소실됩니다. 신뢰성이 필요한 이벤트는 뒤에서 다루는 Redis Streams를 사용하세요.

<hr>

## 키 스키마 설계

팀 전체가 일관된 키 이름을 사용해야 충돌과 혼선을 막을 수 있다. 아래는 표준 스키마다.

### 에이전트 상태 키

```
agent:{이름}:status       # 현재 상태 (working | idle | blocked | rate_limited)
agent:{이름}:heartbeat    # Unix 타임스탬프 (TTL 120s — 만료 시 hang 판단)
agent:{이름}:context_pct  # 컨텍스트 사용률 0~100
agent:{이름}:task         # 현재 작업 한 줄 설명
```

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

**예시**

```bash
# 서연이 파일 편집 전 락 획득
redis-cli SET lock:file:pages/08-5-redis-state-sharing.md "서연" EX 3600 NX
# NX: 이미 락이 있으면 실패 → 충돌 방지
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

**TTL 설계 근거**

| 항목 | TTL | 이유 |
|------|-----|------|
| 하트비트 | 120s | 15s 갱신 주기 × 8배 여유 |
| 파일 락 | 3600s | 크래시 시 자동 해제, 장시간 작업 허용 |
| Phase 상태 | 없음 | 소실 방지 — 수동 삭제만 |
| 리뷰 큐 | 없음 | 항목 유실 방지 |

<hr>

## Redis Streams — 메시지 유실 없는 내구성

기본 Pub/Sub는 오프라인 구독자에게 메시지를 전달하지 못한다. **Redis Streams**를 사용하면 메시지가 로그처럼 쌓여 나중에도 읽을 수 있다.

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

**Pub/Sub vs Streams 선택 기준**

| 기준 | Pub/Sub | Streams |
|------|---------|---------|
| 구독자 오프라인 내성 | ✗ 메시지 소실 | ✓ 나중에 재생 가능 |
| 전달 보장 | ✗ | ✓ (ACK 패턴) |
| 이벤트 이력 조회 | ✗ | ✓ |
| 구현 복잡도 | 낮음 | 중간 |
| 권장 사용처 | 실시간 알림 (소실 허용) | Phase 완료·커밋 이벤트 |

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
