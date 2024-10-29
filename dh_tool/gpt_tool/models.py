from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union


class Message(BaseModel):
    role: str
    content: str


class ResponseFormat(BaseModel):
    type: str


class StructuredResponseFormat(ResponseFormat):
    type: str = "json_schema"
    json_schema: Dict[str, Any]


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0
    seed: Optional[int] = 1
    stream: Optional[bool] = False
    response_format: Optional[Union[ResponseFormat, StructuredResponseFormat]] = None

    # 다른 가능한 파라미터들...
    class Config:
        extra = "allow"  # 추가 필드 허용


class StructuredChatCompletionRequest(ChatCompletionRequest):
    response_format: StructuredResponseFormat


class BatchFormat(BaseModel):
    custom_id: str
    method: str = "POST"
    url: str = "/v1/chat/completions"
    body: Union[ChatCompletionRequest, StructuredChatCompletionRequest]
