def structured_body(content, response_format, **kwargs):
    format = {
        "model": "gpt-4o-mini-2024-07-18",
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 2048,
        "temperature": 0,
        "response_format": response_format,
    }
    if kwargs:
        format.update(kwargs)
    return format
