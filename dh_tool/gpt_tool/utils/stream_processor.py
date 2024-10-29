from box import Box
from typing import Iterator, Dict, Any


class StreamProcessor:
    @staticmethod
    def process_stream(stream_output: Iterator[Dict[str, Any]], verbose: bool) -> Box:
        collected_messages = []
        full_response = []
        usage_info = None
        model = None
        created = None

        for chunk in stream_output:
            full_response.append(chunk)
            if chunk.choices:
                chunk_message = chunk.choices[0].delta.content
                if chunk_message:
                    collected_messages.append(chunk_message)
                    if verbose:
                        print(chunk_message, end="", flush=True)
            else:
                usage_info = chunk.usage
                model = chunk.model
                created = chunk.created

        full_message = "".join(collected_messages)

        complete_response = {
            "id": full_response[0].id,
            "object": full_response[0].object,
            "created": created,
            "model": model,
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": full_message,
                    },
                    "finish_reason": "stop",
                    "index": 0,
                }
            ],
            "usage": usage_info,
        }
        return Box(complete_response)


def process_and_convert_stream(
    stream_output: Iterator[Dict[str, Any]], verbose: bool
) -> Box:
    return StreamProcessor.process_stream(stream_output, verbose)
