import uuid
import json
from openai import OpenAI
from typing import List, Dict, Any, Union


class UUIDGenerator:
    @staticmethod
    def generate() -> str:
        return str(uuid.uuid4())


class BatchFormatter:
    @staticmethod
    def format_batch(
        custom_id: str, prompt: str, model: str, **gpt_params
    ) -> Dict[str, Any]:
        batch_format = {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 4096,
                "temperature": 0,
                "seed": 1,
            },
        }
        if gpt_params:
            batch_format["body"].update(gpt_params)
        return batch_format

    @staticmethod
    def format_struct_batch(custom_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": body,
        }


class BatchCreator:
    def __init__(self, formatter: BatchFormatter, uuid_generator: UUIDGenerator):
        self.formatter = formatter
        self.uuid_generator = uuid_generator

    def make_batch(
        self, prompts: Union[str, List[str]], custom_ids: List[str] = None, **gpt_params
    ) -> List[Dict[str, Any]]:
        if isinstance(prompts, str):
            prompts = [prompts]
        if custom_ids is None:
            return [
                self.formatter.format_batch(
                    self.uuid_generator.generate(), prompt, **gpt_params
                )
                for prompt in prompts
            ]
        else:
            return [
                self.formatter.format_batch(cid, prompt, **gpt_params)
                for cid, prompt in zip(custom_ids, prompts)
            ]

    def make_struct_batch(
        self, bodies: List[Dict[str, Any]], custom_ids: List[str] = None
    ) -> List[Dict[str, Any]]:
        if custom_ids is None:
            return [
                self.formatter.format_struct_batch(self.uuid_generator.generate(), body)
                for body in bodies
            ]
        else:
            return [
                self.formatter.format_struct_batch(cid, body)
                for cid, body in zip(custom_ids, bodies)
            ]


class BatchProcessor:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.batch_creator = BatchCreator(BatchFormatter(), UUIDGenerator())

    # request_batch를 create_and_submit_batch로 변경
    def create_and_submit_batch(
        self, batches: List[Dict[str, Any]], meta_data: Dict[str, Any]
    ):
        batch_str = "\n".join([json.dumps(b, ensure_ascii=False) for b in batches])
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

    # list_batch를 list_batches로 변경 (복수형이 더 적절)
    def list_batches(self, limit: int = 100):
        return self.client.batches.list(limit=limit).model_dump()

    # check_batch를 get_batch_status로 변경
    def get_batch_status(self, batch_id: str):
        retrieved = self.client.batches.retrieve(batch_id).model_dump()
        if retrieved["status"] == "completed":
            print("배치 결과 완료!")
        return retrieved

    # result를 get_batch_results로 변경
    def get_batch_results(self, batch_id: str):
        retrieved = self.client.batches.retrieve(batch_id).model_dump()
        if retrieved["status"] != "completed":
            raise ValueError("아직 완료안되었습니다.")
        output_file_id = retrieved["output_file_id"]
        contents = [
            json.loads(i)
            for i in self.client.files.content(output_file_id)
            .read()
            .decode("utf-8")
            .splitlines()
        ]
        return contents

    def make_batch(
        self, prompts: Union[str, List[str]], custom_ids: List[str] = None, **gpt_params
    ) -> List[Dict[str, Any]]:
        return self.batch_creator.make_batch(prompts, custom_ids, **gpt_params)

    def make_struct_batch(
        self, bodies: List[Dict[str, Any]], custom_ids: List[str] = None
    ) -> List[Dict[str, Any]]:
        return self.batch_creator.make_struct_batch(bodies, custom_ids)
