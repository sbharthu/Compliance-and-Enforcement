# -*- coding: utf-8 -*-
"""
Created on Thu Apr 15 15:49:00 2021

@author: sesle
"""

from get_products import ResponseFetcher
from check_schema import SchemaChecker
import json
import requests

ADIs = ["ANZ", "Ubank", "Up", "BDCU Alliance Bank", "Westpac", "RAMS", "Adelaide Bank"]
product_urls = {"ANZ" : "https://api.anz/cds-au/v1/banking/products",
                "Ubank" : "https://openbank.api.ubank.com.au/cds-au/v1/banking/products",
                "Up" : "https://api.up.com.au/cds-au/v1/banking/products",
                "BDCU Alliance Bank" : "https://api.cdr.bdcualliancebank.com.au/cds-au/v1/banking/products",
                "Westpac" : "https://digital-api.westpac.com.au/cds-au/v1/banking/products",
                "RAMS" : "https://digital-api.westpac.com.au/cds-au/v1/banking/products",
                "Adelaide Bank" : "https://api.cdr.adelaidebank.com.au/cds-au/v1/banking/products"}

class MainController:
    
    cds_copy = "cds_full.json"
    cds_url = "https://consumerdatastandardsaustralia.github.io/standards/includes/swagger/cds_full.json"
    products_copy = "get_products/{}_products.json"
    product_detail_copy = "get_products/{}_product_details/{}_details.json"
        
    def __init__(self, adis, urls, from_copy=True):
        self.adis = adis
        self.urls = urls
        self.from_copy = from_copy
        self.rf = ResponseFetcher(ADIs, product_urls)
        
        # get CDS
        cds = None
        if self.from_copy:
            with open(self.cds_copy, encoding='utf-8') as f:
                cds = json.load(f)
        else:
            r = requests.get(self.cds_url)
            cds =  r.json()
        self.sc = SchemaChecker(cds)
    
    def save_local_copy(self, adi):
        """
        Saves an ADI's product and product details responses into local files
        that can be used instead of making further API calls using the
        from_copy flag.
        """
        temp = self.from_copy
        self.from_copy = False
        products = self.get_products(adi)
        print("Saving products from {}...".format(adi))
        self.rf.dump_json(products, self.products_copy.format(adi))
        for product in products["data"]["products"]:
            print("Saving {}...".format(product["name"].translate({ord(c): None for c in "\\/:*\"<>|"})))
            product_detail = self.get_product_detail(adi, product["productId"], product["name"])
            self.rf.dump_json(product_detail, self.product_detail_copy.format(adi, product["name"].translate({ord(c): None for c in "\\/:*\"<>|"})))
        self.from_copy = temp

    def get_products(self, adi):
        """
        Calls Get Products on an ADI. If from_copy is true, this function reads
        from a local backup instead of actually making the call.
        """
        obj = None
        if self.from_copy:
            with open(self.products_copy.format(adi), encoding='utf-8') as f:
                    obj = json.load(f)
            return obj
        else:
            return self.rf.get_products(self.urls[adi])
    
    def get_product_detail(self, adi, product_id=None, product_name=None):
        """
        Calls Get Product Details on an ADI and one of its products. If
        from_copy is true, this function reads from a local backup instead of 
        actually making the call. Note that to specify a product, the product_id
        is needed when making an API call, but the name is required to read
        from backup.
        """
        obj = None
        if self.from_copy:
            if product_name is None:
                print("Need product_name to load from copy")
                return
            with open(self.product_detail_copy.format(adi, product_name.translate({ord(c): None for c in "\\/:*\"<>|"})), encoding='utf-8') as f:
                    obj = json.load(f)
            return obj
        else:
            if product_id is None:
                print("Need product_id to call API")
                return
            return self.rf.get_product_detail(self.urls[adi], product_id)
    
    def check_products(self, adi):
        """
        Checks Get Product Detail APIs work for all products in Get Products.
        """
        results = []
        products = self.get_products(adi)
        for product in products["data"]["products"]:
            print("Checking product '{}'... ".format(product["name"]), end='')
            detail = self.get_product_detail(adi, product_id=product["productId"], product_name=product["name"])
            if self.rf.valid_product_detail(detail):
                print("Valid.")
                result = "Available"
            else:
                print("INVALID.")
                result = "Not available"
            results.append([product["name"], result])
        return results
        
    def check_product_schema(self, adi):
        """
        Checks the schema of the Get Product response is correct.
        """
        products = self.get_products(adi)
        self.sc.check(products, {"$ref" : "ResponseBankingProductList"})
    
    def check_product_detail_schema(self, adi, product_id=None, product_name=None):
        """
        Checks the schema of the Get Product Detail response is correct.
        """
        product_detail = self.get_product_detail(adi, product_id, product_name)
        if product_detail is None:
            return
        self.sc.check(product_detail, {"$ref" : "ResponseBankingProductById"})
    
    def one_click(self, adi):
        """
        Checks the schema of the Get Product response and of all listed
        Product Details are correct for a given ADI.
        """
        products = self.get_products(adi)
        self.sc.stack = [adi]
        self.sc.check(products, {"$ref" : "ResponseBankingProductList"})
        for product in products["data"]["products"]:
            self.sc.stack = [adi, product["name"]]
            self.check_product_detail_schema(adi, product["productId"], product["name"])

if __name__ == "__main__":
    mc = MainController(ADIs, product_urls)
    mc.one_click("BDCU Alliance Bank")
    mc.sc.print_errors()