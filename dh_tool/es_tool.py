import urllib3, logging
from elasticsearch import Elasticsearch, helpers
from abc import ABC, abstractmethod

urllib3.disable_warnings()
logging.captureWarnings(True)


class ElasticsearchClient:
    def __init__(self, url, username, password):
        self.es = Elasticsearch(
            url,
            http_auth=(username, password),
            verify_certs=False,
            timeout=10,
            ssl_show_warn=False,
        )


class ElasticsearchOperation(ABC):
    def __init__(self, client: ElasticsearchClient, index_name: str):
        self.client = client
        self.index_name = index_name

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass


class ElasticsearchSearch(ElasticsearchOperation):
    def execute(self, query, size=1000):
        body = {"query": query, "size": size}
        return self.client.es.search(index=self.index_name, body=body)


class ElasticsearchDelete(ElasticsearchOperation):
    def execute(self, query):
        body = {"query": query}
        return self.client.es.delete_by_query(index=self.index_name, body=body)


class ElasticsearchBulkInsert(ElasticsearchOperation):
    def execute(self, actions):
        for action in actions:
            action["_index"] = self.index_name
        return helpers.bulk(self.client.es, actions)


class ElasticsearchScroll(ElasticsearchOperation):
    def execute(self, query, scroll="2m"):
        body = {"query": query, "size": 1000}
        response = self.client.es.search(
            index=self.index_name, body=body, scroll=scroll
        )
        scroll_id = response["_scroll_id"]
        hits = response["hits"]["hits"]

        while len(hits):
            yield from hits
            response = self.client.es.scroll(scroll_id=scroll_id, scroll=scroll)
            scroll_id = response["_scroll_id"]
            hits = response["hits"]["hits"]


class ElasticsearchService:
    def __init__(self, url, username, password):
        self.client = ElasticsearchClient(url, username, password)

    def search(self, index_name, query, size=1000):
        operation = ElasticsearchSearch(self.client, index_name)
        return operation.execute(query, size)

    def delete(self, index_name, query):
        operation = ElasticsearchDelete(self.client, index_name)
        return operation.execute(query)

    def bulk_insert(self, index_name, actions):
        operation = ElasticsearchBulkInsert(self.client, index_name)
        return operation.execute(actions)

    def scroll_search(self, index_name, query, scroll="2m"):
        operation = ElasticsearchScroll(self.client, index_name)
        return operation.execute(query, scroll)


__all__ = [
    "ElasticsearchService",
    "ElasticsearchClient",
    "ElasticsearchOperation",
    "ElasticsearchSearch",
    "ElasticsearchDelete",
    "ElasticsearchBulkInsert",
    "ElasticsearchScroll",
]

# 사용 예:
# es_service = ElasticsearchService("http://localhost:9200", "username", "password")
# search_result = es_service.search("my_index", {"match": {"field": "value"}})
# delete_result = es_service.delete("my_index", {"match": {"field": "value"}})
# bulk_result = es_service.bulk_insert("my_index", [{"_id": 1, "_source": {"field": "value"}}])
# for hit in es_service.scroll_search("my_index", {"match_all": {}}):
#     print(hit)
