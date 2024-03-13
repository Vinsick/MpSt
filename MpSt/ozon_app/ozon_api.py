import json
import requests

class OzonAPI:
    def __init__(self, client_id, api_key):
        self.client_id = client_id
        self.api_key = api_key
        self.base_url = 'https://api-seller.ozon.ru'
        self.headers = {
            'Client-Id': self.client_id,
            'Api-Key': self.api_key,
        }

    def MakerResponse(self, method, body):
        print(f"Делаем запрос OZON meth: {method} \n telo: {body}")
        body = json.dumps(body)
        response = requests.post(self.base_url + method, headers=self.headers, data=body)
        if response.status_code == 200:
            print(f"Запрос Верен")
            return response.json()
        else:
            print(f"Ошибка запроса {response.content}")
            return None
        
    def GetWarehouseList(self):
        method = "/v1/warehouse/list"
        body = {

                }

        response = self.MakerResponse(method, body)
        if response:
            return response
        else:
            return None
        

    def GetDeliveryMethodList(self, warehouse_id):
        method = "/v1/delivery-method/list"
        body = {
                'filter': {
                'warehouse_id': warehouse_id
                },
                'limit': 50,
                'offset': 0
                }

        response = self.MakerResponse(method, body)
        if response:
            return response
        else:
            return None
        

    def GetProductList(self):
        all_products = []
        last_id = None

        while True:
            method = "/v2/product/list"
            body = {
                "last_id": last_id
            }

            response = self.MakerResponse(method, body)
            if response:
                all_products.extend(response['result']['items'])
                last_id = response['result']['last_id']
                if last_id == '':
                    break
            else:
                break

        return all_products
    
    def GetFBOPostingList(self, date_from, date_to):
        method = "/v2/posting/fbo/list"
        body = {
                    "dir": "desc",
                    "filter": {
                        "since": date_from+"T00:00:00.000Z",
                        "to": date_to+"T23:59:59.000Z"
                    },
                    "limit": 1000,
                    "offset": 0,
                    "translit": True,
                    "with": {
                        "analytics_data": True,
                        "financial_data": True
                    }
                    }

        response = self.MakerResponse(method, body)
        if response:
            return response
        else:
            return None
        
    def GetFBSPostingList(self, date_from, date_to):
        all_postings = []
        method = "/v3/posting/fbs/list"
        body = {
                    "dir": "desc",
                    "filter": {
                        "since": date_from+"T00:00:00.000Z",
                        "to": date_to+"T23:59:59.000Z"
                    },
                    "limit": 1000,
                    "offset": 0,
                    "translit": True,
                    "with": {
                        "analytics_data": True,
                        "financial_data": True
                    }
                    }
        it = 1
        while True:
            response = self.MakerResponse(method, body)
            if response['result']['has_next'] == True:
                all_postings.extend(response['result']['postings'])
                body = {
                            "dir": "desc",
                            "filter": {
                                "since": date_from+"T00:00:00.000Z",
                                "to": date_to+"T23:59:59.000Z"
                            },
                            "limit": 1000,
                            "offset": 1000*it,
                            "translit": True,
                            "with": {
                                "analytics_data": True,
                                "financial_data": True
                            }
                            }
                it = it + 1
            else:
                all_postings.extend(response['result']['postings'])
                break

        if response:
            return all_postings
        else:
            return None
        