from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field, SkipValidation


class StructuredOutputField(BaseModel):
    def model_dump(self, *args, **kwargs):
        # 기본 dump 호출
        dump_data = super().model_dump(*args, **kwargs)
        # 내부 필드가 있을 경우 처리
        if "properties" in dump_data:
            dump_data["properties"] = [
                prop.model_dump(*args, **kwargs) for prop in self.properties
            ]
        if "items" in dump_data:
            dump_data["items"] = [
                item.model_dump(*args, **kwargs) for item in self.items
            ]
        # 특정 이름으로 출력하기 위한 변경
        result = {
            self.__class__.__name__: {k: v for k, v in dump_data.items() if k != "name"}
        }
        return result  # 지정한 이름으로 출력하고 'name' 필드 제거


class StringFieldExample(StructuredOutputField):
    type: Literal["string"] = "string"
    enum: Optional[List[str]] = Field(None, description="가능한 문자열 값의 목록, 선택")
    description: Optional[str] = Field(None, description="설명, 선택적으로 포함 가능")


class BooleanFieldExample(StructuredOutputField):
    type: Literal["boolean"] = "boolean"
    description: Optional[str] = Field(None, description="설명, 선택적으로 포함 가능")


class ArrayFieldExample(StructuredOutputField):
    type: Literal["array"] = "array"
    items: List[Union[StructuredOutputField]]
    description: Optional[str] = Field(None, description="설명, 선택적으로 포함 가능")


class ObjectFieldExample(StructuredOutputField):
    type: Literal["object"] = "output"
    properties: List[Union[StructuredOutputField]]
    required: List[str]
    additionalProperties: Union[bool, SkipValidation] = Field(False)
    description: Optional[str] = Field(None, description="설명, 선택적으로 포함 가능")
