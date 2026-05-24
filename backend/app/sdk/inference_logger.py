import time
import requests
from datetime import datetime


class InferenceLogger:
    def __init__(self, provider, model, ingestion_url):
        self.provider = provider
        self.model = model
        self.ingestion_url = ingestion_url

    def run(self, conversation_id, messages, llm_function):
        started_at = datetime.utcnow()
        start_time = time.time()

        status = "success"
        error_message = None
        output_text = ""

        try:
            output_text = llm_function(messages)
            return output_text

        except Exception as e:
            status = "error"
            error_message = str(e)
            raise e

        finally:
            completed_at = datetime.utcnow()
            latency_ms = int((time.time() - start_time) * 1000)

            input_text = " ".join([m.get("content", "") for m in messages])
            input_tokens = estimate_tokens(input_text)
            output_tokens = estimate_tokens(output_text)
            total_tokens = input_tokens + output_tokens

            payload = {
                "event_type": "llm.inference.completed",
                "conversation_id": conversation_id,
                "provider": self.provider,
                "model": self.model,
                "status": status,
                "error_message": error_message,
                "latency_ms": latency_ms,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "input_preview": input_text[:300],
                "output_preview": output_text[:300],
                "request_started_at": started_at.isoformat(),
                "request_completed_at": completed_at.isoformat()
            }

            try:
                requests.post(
                    self.ingestion_url,
                    json=payload,
                    timeout=2
                )
            except Exception:
                pass


def estimate_tokens(text):
    if not text:
        return 0

    return max(1, len(text.split()))