## 4-5. Stream JSON 제어

Remote Control이 사람이 다른 기기에서 직접 접속하는 방식이라면, **Stream JSON**은 프로그램이 Claude Code를 자동으로 제어하는 방식입니다. 스크립트, 파이프라인, 다른 애플리케이션에서 Claude와 구조화된 방식으로 통신할 수 있습니다.

<hr>

## Stream JSON 모드의 두 가지 방향

| 방향 | 플래그 | 용도 |
|------|--------|------|
| 출력 스트리밍 | `--output-format stream-json` | Claude 응답을 JSON 스트림으로 받기 |
| 입력 스트리밍 | `--input-format stream-json` | JSON으로 메시지를 Claude에게 전송 |

<hr>

## 출력: Stream JSON

### 기본 사용법

```bash
claude -p "파이썬으로 피보나치 함수를 작성해줘" \
    --output-format stream-json \
    --verbose \
    --include-partial-messages
```

`-p` 플래그는 프롬프트를 직접 전달하고 비대화형 모드로 실행합니다.

### 출력 형식 (NDJSON)

각 줄이 하나의 JSON 객체인 NDJSON(Newline Delimited JSON) 형식입니다.

```json
{"type":"stream_event","event":{"type":"message_start","message":{"id":"msg_01...","type":"message","role":"assistant","content":[]}},"session_id":"uuid","uuid":"event-uuid"}
{"type":"stream_event","event":{"type":"content_block_delta","delta":{"type":"text_delta","text":"def "}},"session_id":"uuid","uuid":"event-uuid"}
{"type":"stream_event","event":{"type":"content_block_delta","delta":{"type":"text_delta","text":"fibonacci"}},"session_id":"uuid","uuid":"event-uuid"}
...
{"type":"result","subtype":"success","result":"def fibonacci(n):\n    ...","session_id":"uuid"}
```

### jq로 텍스트만 추출

```bash
claude -p "간단한 인사말 작성해줘" \
    --output-format stream-json \
    --verbose \
    --include-partial-messages | \
    jq -rj 'select(
        .type == "stream_event" and
        .event.delta.type? == "text_delta"
    ) | .event.delta.text'
```

출력:
```
안녕하세요! 반갑습니다.
```

### 최종 결과만 추출

```bash
claude -p "2 + 2는?" \
    --output-format stream-json | \
    jq -r 'select(.type == "result") | .result'
```

<hr>

## 단일 JSON 출력 (`--output-format json`)

스트리밍이 필요 없고 최종 결과만 필요하다면 단일 JSON 출력을 사용합니다.

```bash
claude -p "Node.js 버전 확인 방법" --output-format json
```

응답:
```json
{
  "result": "node --version 명령을 실행하면 됩니다.",
  "session_id": "uuid-abc123",
  "usage": {
    "input_tokens": 15,
    "output_tokens": 12,
    "cache_read_tokens": 0,
    "cache_creation_tokens": 0
  }
}
```

### JSON Schema로 구조화된 출력

```bash
claude -p "다음 텍스트에서 이름 목록을 추출해줘: 앨런, 민준, 서연이 회의에 참석했다" \
    --output-format json \
    --json-schema '{
        "type": "object",
        "properties": {
            "names": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }'
```

응답:
```json
{
  "result": {"names": ["앨런", "민준", "서연"]},
  "session_id": "uuid",
  "usage": {...}
}
```

<hr>

## 입력: Stream JSON

입력도 JSON 형식으로 보낼 수 있습니다. 복잡한 메시지 구조나 자동화 파이프라인에 유용합니다.

```bash
claude -p \
    --input-format stream-json \
    --output-format stream-json \
    --replay-user-messages
```

이 명령을 실행하면 stdin에서 JSON을 읽습니다. 아래 형식으로 입력합니다.

```bash
echo '{"type":"user_message","content":"안녕하세요!","uuid":"msg-001"}' | \
    claude -p --input-format stream-json --output-format stream-json
```

입력 메시지 구조:
```json
{
  "type": "user_message",
  "content": "메시지 내용",
  "uuid": "고유-이벤트-id"
}
```

| 플래그 | 설명 |
|--------|------|
| `--input-format stream-json` | stdin에서 NDJSON으로 입력 받기 |
| `--replay-user-messages` | 수신한 사용자 메시지를 stdout에 에코 (수신 확인용) |
| `--include-partial-messages` | 부분 토큰 스트림 이벤트 포함 |

<hr>

## 실용 예제: 파이프라인에서 활용

### 파일 내용을 Claude에게 분석 요청

```bash
cat main.py | \
    claude -p "이 코드의 버그를 찾아줘" \
    --output-format json | \
    jq -r '.result'
```

### 여러 질문을 순차 처리

```bash
#!/bin/bash
questions=(
    "파이썬이란 무엇인가?"
    "Node.js의 장점은?"
    "Rust가 인기 있는 이유는?"
)

for q in "${questions[@]}"; do
    echo "=== $q ==="
    claude -p "$q" --output-format json | jq -r '.result'
    echo ""
done
```

### 응답을 파일로 저장

```bash
claude -p "README.md 초안 작성해줘" \
    --output-format json | \
    jq -r '.result' > README.md

echo "README.md 생성 완료"
```

<hr>

## Remote Control과 Stream JSON 비교

| 비교 | Remote Control | Stream JSON |
|------|----------------|-------------|
| 사용자 | 사람 (모바일/웹) | 프로그램/스크립트 |
| 입력 방식 | 인터랙티브 대화 | CLI 플래그, stdin |
| 출력 방식 | 실시간 UI | NDJSON, JSON |
| 세션 유지 | 영구 세션 | 요청별 실행 |
| 자동화 | 어려움 | 쉬움 |

<hr>

## 요약

Stream JSON은 Claude를 자동화 도구로 활용할 때 핵심 기능입니다. 쉘 스크립트, CI/CD 파이프라인, 배치 처리에서 Claude의 응답을 구조화된 데이터로 처리할 수 있습니다. 다음 챕터에서는 Remote Control 사용 시 중요한 **보안 설정**을 설명합니다.
