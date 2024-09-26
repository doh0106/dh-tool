import uuid
import json
import openai


def generate_random_uuid() -> str:
    """Generate a random UUID."""
    return str(uuid.uuid4())


class BatchProcessor:
    def __init__(self, api_key) -> None:
        self.client = openai.OpenAI(api_key=api_key)

    @staticmethod
    def format_batch(custom_id, prompt, model, **gpt_params):
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
    def format_struct_batch(custom_id, body):   
        batch_format = {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": body
        }
        return batch_format
    
    @staticmethod
    def make_batch(prompts,custom_ids = None, **gpt_params):
        if isinstance(prompts, str):
            prompts = [prompts]
        if custom_ids is None:
            return [
                BatchProcessor.format_batch(generate_random_uuid(), prompt, **gpt_params)
                for  prompt in prompts
            ]
        else:
            return [
                BatchProcessor.format_batch(cid, prompt, **gpt_params) 
                for cid, prompt in zip(custom_ids, prompts)
            ]
        
    @staticmethod
    def make_struct_batch(bodies, custom_ids = None):
        if custom_ids is None:
            return [BatchProcessor.format_struct_batch(generate_random_uuid(), body)
                    for body in bodies]
        else:
            return [BatchProcessor.format_struct_batch(cid, body)
                    for cid, body in zip(custom_ids, bodies)]

    def request_batch(self, batchs, meta_data: dict):
        batch_str = "\n".join([json.dumps(b, ensure_ascii=False) for b in batchs])
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

    def list_batch(self, limit=100):
        return self.client.batches.list(limit=limit).model_dump()

    def check_batch(self, batch_id):
        retrieved = self.client.batches.retrieve(batch_id).model_dump()
        if retrieved["status"] == "completed":
            print("배치 결과 완료!")
            return retrieved
        else:
            return retrieved

    def result(self, batch_id):
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
