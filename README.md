# Chat Mirror

A lightweight, OpenAI API-compatible HTTP server that echoes chat completion requests. Useful for debugging AI prompts and client payloads.

## Features

- **OpenAI Compatible:** Supports `/v1/models` and `/v1/chat/completions`.
- **Dynamic Mirroring:** Include `[tag: N]` in your last message to return only the last `N` messages. Use `0` for an empty response or `-1` to return the raw JSON payload.
- **Log Redaction:** Set `REDACT_LOGS=true` to prevent logging sensitive payload content to the console.

## Usage

### Docker

`docker run -d -p 8080:8080 -e REDACT_LOGS=true --name chat-mirror ulcdia/chat-mirror:latest`

or

```bash
git clone https://github.com/uLcdia/chat-mirror
cd chat-mirror
docker-compose up -d
```

### Local

```bash
python app.py
```

*Listens on `http://0.0.0.0:8080`.*

## In-Chat Example

**User**: `Example usage for chat-mirror`

**Assistant**: Returns last user message.

```json
[
  {
    "role": "user",
    "content": "Example usage for `chat-mirror`"
  }
]
```

**User**: `This is the second user message.`

**Assistant**: Returns last user message.

```json
[
  {
    "role": "user",
    "content": "This is the second user message."
  }
]
```

**User**:

```
[tag:2]
This is the third user message
```

**Assistant**: Returns last user message + last assistant message.

```json
[
  {
    "role": "assistant",
    "content": "[\n  {\n    \"role\": \"user\",\n    \"content\": \"This is the second user message.\"\n  }\n]"
  },
  {
    "role": "user",
    "content": "[tag:2]\nThis is the third user message"
  }
]
```

**User**:

```
[tag:-1]
This is the fourth user message.
```

**Assistant**: Returns the full raw JSON payload.

```json
{
    "stream": true,
    "model": "mirror",
    "messages": [
        {
            "role": "user",
            "content": "Example usage for `chat-mirror`"
        },
        {
            "role": "assistant",
            "content": "[\n  {\n    \"role\": \"user\",\n    \"content\": \"Example usage for `chat-mirror`\"\n  }\n]"
        },
        {
            "role": "user",
            "content": "This is the second user message."
        },
        {
            "role": "assistant",
            "content": "[\n  {\n    \"role\": \"user\",\n    \"content\": \"This is the second user message.\"\n  }\n]"
        },
        {
            "role": "user",
            "content": "[tag:2]\nThis is the third user message"
        },
        {
            "role": "assistant",
            "content": "[\n  {\n    \"role\": \"assistant\",\n    \"content\": \"[\\n  {\\n    \\\"role\\\": \\\"user\\\",\\n    \\\"content\\\": \\\"This is the second user message.\\\"\\n  }\\n]\"\n  },\n  {\n    \"role\": \"user\",\n    \"content\": \"[tag:2]\\nThis is the third user message\"\n  }\n]"
        },
        {
            "role": "user",
            "content": "[tag:-1]\nThis is the fourth user message."
        }
    ]
}
```
