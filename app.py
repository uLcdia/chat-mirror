#!/usr/bin/env python3

import json
import re
import time
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

# Load configuration from environment variables
REDACT_LOGS = os.getenv("REDACT_LOGS", "false").lower() == "true"


class ChatDebugHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Clean up standard HTTP logs to keep console readable
        super().log_message(format, *args)

    def do_GET(self):
        if self.path == "/v1/models":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "object": "list",
                "data": [
                    {
                        "id": "mirror",
                        "object": "model",
                        "created": int(time.time()),
                        "owned_by": "debug",
                    }
                ],
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/v1/chat/completions":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            decoded_input = post_data.decode("utf-8", errors="replace")

            # --- LOGGING: RECEIVED PAYLOAD ---
            print("\n--- Received Payload ---")
            if REDACT_LOGS:
                print(f"[REDACTED] ({content_length} bytes)")
            else:
                print(decoded_input)
            print("------------------------\n")

            output_text = decoded_input
            n_messages = 1

            try:
                payload = json.loads(post_data)
                messages = payload.get("messages", [])

                # Mirror Tag Detection (always processed even if logs are redacted)
                last_user_msg = next(
                    (m for m in reversed(messages) if m.get("role") == "user"), None
                )
                if last_user_msg:
                    content = last_user_msg.get("content", "")
                    text_to_search = (
                        content[0].get("text", "")
                        if isinstance(content, list)
                        else content
                    )

                    match = re.match(
                        r"^\s*[\[<]tag:\s*(-?\d+)\s*[\]>]",
                        text_to_search,
                        re.IGNORECASE,
                    )
                    if match:
                        n_messages = int(match.group(1))

                if n_messages == 0:
                    output_text = ""
                elif n_messages == -1:
                    output_text = decoded_input
                else:
                    count = max(1, n_messages)
                    selected_messages = messages[-count:]
                    output_text = json.dumps(selected_messages, indent=2)

            except Exception:
                output_text = decoded_input

            # Wrap in OpenAI format
            openai_response = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "mirror",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": output_text},
                        "finish_reason": "stop",
                    }
                ],
            }

            response_body = json.dumps(openai_response, indent=2)

            # --- LOGGING: SENT RESPONSE ---
            print("--- Sent Response ---")
            if REDACT_LOGS:
                print(f"[REDACTED] (Mirror Result: {n_messages} msgs)")
            else:
                print(response_body)
            print("---------------------\n")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response_body.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    port = 8080
    status = "ENABLED" if REDACT_LOGS else "DISABLED"
    print(f"Chatbot debug endpoint listening on http://0.0.0.0:{port}")
    print(f"Log Redaction: {status}")
    HTTPServer(("0.0.0.0", port), ChatDebugHandler).serve_forever()
