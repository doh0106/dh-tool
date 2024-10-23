from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
import json
import uuid

from openai import OpenAI

from ..models import (
    BatchFormat,
    ChatCompletionRequest,
    StructuredChatCompletionRequest,
    Message,
    StructuredResponseFormat,
)


class IDGenerator(ABC):
    """ID 생성을 위한 추상 기본 클래스"""

    @abstractmethod
    def generate(self) -> str:
        pass


class UUIDGenerator(IDGenerator):
    """UUID를 생성하는 구체적인 클래스"""

    @staticmethod
    def generate() -> str:
        return str(uuid.uuid4())


class BatchFormatter:
    """배치 요청 형식을 만드는 클래스"""

    @staticmethod
    def create_simple_batch_format(
        custom_id: str, prompt: str, model: str, **gpt_params
    ) -> BatchFormat:
        """단일 프롬프트에 대한 일반 배치 형식을 생성"""
        chat_request = ChatCompletionRequest(
            model=model, messages=[Message(role="user", content=prompt)], **gpt_params
        )
        return BatchFormat(custom_id=custom_id, body=chat_request)

    @staticmethod
    def create_structured_batch_format(
        custom_id: str,
        prompt: str,
        model: str,
        response_format: Dict[str, Any],
        **gpt_params,
    ) -> BatchFormat:
        """구조화된 응답을 위한 배치 형식을 생성"""
        chat_request = StructuredChatCompletionRequest(
            model=model,
            messages=[Message(role="user", content=prompt)],
            response_format=StructuredResponseFormat(**response_format),
            **gpt_params,
        )
        return BatchFormat(custom_id=custom_id, body=chat_request)


class BatchCreator:
    """배치 생성을 담당하는 클래스"""

    def __init__(self, formatter: BatchFormatter, id_generator: IDGenerator):
        self.formatter = formatter
        self.id_generator = id_generator

    def make_batch(
        self,
        prompts: Union[str, List[str]],
        model,
        custom_ids: List[str] = None,
        **gpt_params,
    ) -> List[BatchFormat]:
        """프롬프트 목록에 대한 배치를 생성"""
        if isinstance(prompts, str):
            prompts = [prompts]
        if custom_ids is None:
            return [
                self.formatter.create_simple_batch_format(
                    self.id_generator.generate(), prompt, model, **gpt_params
                )
                for prompt in prompts
            ]
        else:
            return [
                self.formatter.create_simple_batch_format(
                    custom_id, prompt, model, **gpt_params
                )
                for custom_id, prompt in zip(custom_ids, prompts)
            ]

    def make_structured_batch(
        self,
        prompts: Union[str, List[str]],
        model,
        response_format,
        custom_ids: List[str] = None,
        **gpt_params,
    ) -> List[BatchFormat]:
        """구조화된 본문 목록에 대한 배치를 생성"""
        if isinstance(prompts, str):
            prompts = [prompts]
        if custom_ids is None:
            return [
                self.formatter.create_structured_batch_format(
                    self.id_generator.generate(),
                    prompt,
                    model,
                    response_format,
                    **gpt_params,
                )
                for prompt in prompts
            ]
        else:
            return [
                self.formatter.create_structured_batch_format(
                    custom_id, prompt, model, response_format, **gpt_params
                )
                for custom_id, prompt in zip(custom_ids, prompts)
            ]


class BatchProcessor:
    """배치 처리를 담당하는 클래스"""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.batch_creator = BatchCreator(BatchFormatter(), UUIDGenerator())

    def create_and_submit_batch(
        self, batches: List[BatchFormat], meta_data: Dict[str, Any]
    ):
        """배치를 생성하고 제출"""
        batch_str = "\n".join(
            [json.dumps(batch.model_dump(), ensure_ascii=False) for batch in batches]
        )
        gpt_batch_file = self.client.files.create(
            file=batch_str.encode("utf-8"), purpose="batch"
        )
        response = self.client.batches.create(
            input_file_id=gpt_batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata=meta_data,
        )
        return response

    def list_batches(self, limit: int = 100):
        """배치 목록 조회"""
        return self.client.batches.list(limit=limit).model_dump()

    def get_batch_status(self, batch_id: str):
        """배치 상태 확인"""
        retrieved = self.client.batches.retrieve(batch_id).model_dump()
        if retrieved["status"] == "completed":
            print("배치 결과 완료!")
        return retrieved

    def get_batch_results(self, batch_id: str):
        """배치 결과 조회"""
        retrieved = self.client.batches.retrieve(batch_id).model_dump()
        if retrieved["status"] != "completed":
            raise ValueError("아직 완료되지 않았습니다.")
        output_file_id = retrieved["output_file_id"]

        contents = self.get_file_contents(output_file_id)
        return contents

    def get_file_contents(self, file_id):
        try:
            contents = [
                json.loads(line)
                for line in self.client.files.content(file_id)
                .read()
                .decode("utf-8")
                .splitlines()
            ]
            return contents
        except:
            raise ValueError("해당 file_id를 가져오는 데 실패했습니다.")

    def make_batch(
        self,
        prompts: Union[str, List[str]],
        model,
        custom_ids: List[str] = None,
        **gpt_params,
    ) -> List[BatchFormat]:
        """BatchCreator를 통해 배치 생성"""
        return self.batch_creator.make_batch(prompts, model, custom_ids, **gpt_params)

    def make_structured_batch(
        self,
        prompts: Union[str, List[str]],
        model,
        response_format,
        custom_ids: List[str] = None,
        **gpt_params,
    ) -> List[BatchFormat]:
        """BatchCreator를 통해 구조화된 배치 생성"""
        return self.batch_creator.make_structured_batch(
            prompts, model, response_format, custom_ids, **gpt_params
        )
