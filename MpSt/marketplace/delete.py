import requests
import json
import datetime
import csv

class ozon:
    def __init__(self, client_id, api_key):
        self.url = "https://api-seller.ozon.ru"
        self.head = {
                "Client-Id": client_id,
                "Api-Key":  api_key          
        }


    def MakerResponse(self, method, body):
        body = json.dumps(body)
        response = requests.post(self.url + method, headers=self.head, data=body)
        print(response.content)
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def GetProduct(self):
        method = "/v4/product/info/prices"
        body = {
                    "filter": {
                        "product_id": [],
                        "visibility": "ALL"
                    },
                    "last_id": "",
                    "limit": 1000
                }

        response = self.MakerResponse(method, body)
        return response

    def GetProductList(self):
        method = "/v2/product/info"
        body = {
            'sku':"679665016",
                }

        response = self.MakerResponse(method, body)
        return response

fields = ['acquiring', 'product_id', 'offer_id', 
          'price', 'old_price', 'premium_price', 
          'recommended_price', 'retail_price', 'vat', 
          'min_ozon_price', 'marketing_price', 
          'marketing_seller_price', 'sales_percent',
          'fbo_fulfillment_amount', 'fbo_direct_flow_trans_min_amount',
          'fbo_direct_flow_trans_max_amount', 'fbo_deliv_to_customer_amount',
          'fbo_return_flow_amount','fbo_return_flow_trans_min_amount',
          'fbo_return_flow_trans_max_amount', 'fbs_first_mile_min_amount',
          'fbs_first_mile_max_amount', 'fbs_direct_flow_trans_min_amount',
          'fbs_direct_flow_trans_max_amount', 'fbs_deliv_to_customer_amount',
          'fbs_return_flow_amount', 'fbs_return_flow_trans_min_amount', 
          'fbs_return_flow_trans_max_amount', 'sales_percent_fbo', 'sales_percent_fbs']

client_id='175762'
api_key='43c52f9c-0329-47de-a8d8-2e5e56edd130'
data_csv = []
person = ozon(client_id, api_key)
ProdList = person.GetProductList()
print(ProdList)
for prod in ProdList['result']:
    print(prod)