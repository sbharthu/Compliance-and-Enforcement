# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 14:44:55 2021

@author: sesle
"""
import requests
import json

class ResponseFetcher:
    def __init__(self, adis, urls):
        self.adis = adis
        self.urls = urls

    def get_products(self, url):
        headers = {"x-v" : '3'}
        r = requests.get(url, headers=headers)
        return r.json()

    def get_product_detail(self, url, productId):
        headers = {"x-v" : '3', "productId" : productId}
        r = requests.get(url + '/' + productId, headers=headers)
        return r.json()

    def valid_product_detail(self, detail):
        return "name" in detail["data"]
    
    def dump_json(self, j, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(j, f, ensure_ascii=False, indent=4)

    def check_products(self, adi):
        results = []
        print("Checking products for {}...".format(adi))
        url = self.urls[adi]
        print("Requesting products from {}...".format(url))
        products = self.get_products(url)
        print("Done: found {} products.".format(len(products["data"]["products"])))
        for product in products["data"]["products"]:
            print("Checking product '{}'... ".format(product["name"]), end='')
            detail = self.get_product_detail(url, product["productId"])
            if self.valid_product_detail(detail):
                print("Valid.")
                result = "Available"
            else:
                print("INVALID.")
                result = "Not available"
            results.append([product["name"], result])
