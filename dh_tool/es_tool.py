# Example usage
# est = ESTool("http://localhost:9200", "id", "pwd")
# est.set_index_name("my_index")
# result = est.search(return_all=True, name="example")
# delete_res = est.delete_by_query(name="example")
# pattern_res = est.search_with_pattern(field="name", pattern="*example*")
# nested_res = est.search_nested(path="nested_path", name="example")
# agg_res = est.search_with_aggregation(agg_field="example_field")
# multi_match_res = est.multi_match_search(query="example query", fields=["field1", "field2"])
# bulk_res = est.bulk_insert([{"_id": 1, "_source": {"name": "example"}}])
# scroll_res = est.scroll_search(name="example")


import urllib3, logging

from elasticsearch import Elasticsearch, helpers

urllib3.disable_warnings()
logging.captureWarnings(True)


class ESTool:
    def __init__(self, url, id, pwd) -> None:
        self.es = Elasticsearch(
            url,
            http_auth=(id, pwd),
            verify_certs=False,
            timeout=10,
            ssl_show_warn=False,
        )
        self.index_name = None
        self.size = 1000

    def set_index_name(self, index_name):
        self.index_name = index_name

    def set_size(self, size):
        self.size = size

    def create_index(self, settings=None, mappings=None):
        if not self.index_name:
            raise ValueError("인덱스 이름이 설정되지 않았음. set_index_name() 실행")

        body = {}
        if settings:
            body["settings"] = settings
        if mappings:
            body["mappings"] = mappings

        response = self.es.indices.create(index=self.index_name, body=body, ignore=400)
        return response

    def make_body(self, **kwargs):
        must_clauses = []
        for key, value in kwargs.items():
            must_clauses.append({"match": {key: value}})
        body = {
            "_source": [],
            "query": {
                "bool": {
                    "must": must_clauses,
                }
            },
            "size": self.size,
        }
        return body

    def search(self, return_all=False, verbose=True, **kwargs):
        if not self.index_name:
            raise ValueError("인덱스 이름이 설정되지 않았음. set_index_name() 실행")

        body = self.make_body(**kwargs)
        res = self.es.search(index=self.index_name, body=body)
        hits = res["hits"]["hits"]
        if hits:
            if verbose:
                print("Data Num :", len(hits))
            if return_all:
                return hits
            return hits[0]
        else:
            print(f"{kwargs} Nodata")

    def index(self, data, id):
        if not self.index_name:
            raise ValueError("인덱스 이름이 설정되지 않았음. set_index_name() 실행")
        response = self.es.index(index=self.index_name, body=data, id=id)
        return response

    def delete_by_query(self, **kwargs):
        if not self.index_name:
            raise ValueError("인덱스 이름이 설정되지 않았음. set_index_name() 실행")

        body = self.make_body(**kwargs)
        res = self.es.delete_by_query(index=self.index_name, body=body)
        return res

    def search_with_pattern(self, field, pattern, return_all=False, verbose=True):
        if not self.index_name:
            raise ValueError("인덱스 이름이 설정되지 않았음. set_index_name() 실행")

        body = {
            "query": {"wildcard": {field: {"value": pattern}}},
            "size": self.size,
        }
        res = self.es.search(index=self.index_name, body=body)
        hits = res["hits"]["hits"]
        if hits:
            if verbose:
                print("Data Num :", len(hits))
            if return_all:
                return hits
            return hits[0]
        else:
            print(f"{field} with pattern {pattern} Nodata")

    def search_nested(self, path, **kwargs):
        if not self.index_name:
            raise ValueError("인덱스 이름이 설정되지 않았음. set_index_name() 실행")

        must_clauses = []
        for key, value in kwargs.items():
            must_clauses.append({"match": {f"{path}.{key}": value}})

        body = {
            "query": {
                "nested": {"path": path, "query": {"bool": {"must": must_clauses}}}
            },
            "size": self.size,
        }
        res = self.es.search(index=self.index_name, body=body)
        hits = res["hits"]["hits"]
        if hits:
            print("Data Num :", len(hits))
            return hits
        else:
            print(f"{kwargs} in nested path {path} Nodata")

    def search_with_aggregation(self, agg_field, agg_type="terms", **kwargs):
        if not self.index_name:
            raise ValueError("인덱스 이름이 설정되지 않았음. set_index_name() 실행")

        body = self.make_body(**kwargs)
        body["aggs"] = {"agg_results": {agg_type: {"field": agg_field}}}

        res = self.es.search(index=self.index_name, body=body)
        agg_results = res["aggregations"]["agg_results"]
        return agg_results

    def multi_match_search(self, query, fields, return_all=False, verbose=True):
        if not self.index_name:
            raise ValueError("인덱스 이름이 설정되지 않았음. set_index_name() 실행")

        body = {
            "query": {"multi_match": {"query": query, "fields": fields}},
            "size": 10000,
        }

        res = self.es.search(index=self.index_name, body=body)
        hits = res["hits"]["hits"]
        if hits:
            if verbose:
                print("Data Num :", len(hits))
            if return_all:
                return hits
            return hits[0]
        else:
            print(f"Query {query} with fields {fields} Nodata")

    def bulk_insert(self, actions):
        if not self.index_name:
            raise ValueError("인덱스 이름이 설정되지 않았음. set_index_name() 실행")

        for action in actions:
            action["_index"] = self.index_name

        response = helpers.bulk(self.es, actions)
        return response

    def scroll_search(self, scroll="2m", **kwargs):
        if not self.index_name:
            raise ValueError("인덱스 이름이 설정되지 않았음. set_index_name() 실행")

        body = self.make_body(**kwargs)
        response = self.es.search(index=self.index_name, body=body, scroll=scroll)
        hits = response["hits"]["hits"]
        scroll_id = response["_scroll_id"]

        all_hits = []
        while len(hits):
            all_hits.extend(hits)
            response = self.es.scroll(scroll_id=scroll_id, scroll=scroll)
            scroll_id = response["_scroll_id"]
            hits = response["hits"]["hits"]

        return all_hits
