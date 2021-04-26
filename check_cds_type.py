# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 15:41:31 2021

@author: sesle
"""

class CDSTypeChecker:
    
    def check(self, o, type_string):
        if type_string == "ASCIIString" : 
            return self.check_ASCIIString(o)
        elif type_string == "Boolean": 
            return self.check_Boolean(o)
        elif type_string == "NaturalNumber":
            return self.check_NaturalNumber(o)
        elif type_string == "PositiveInteger":
            return self.check_PositiveInteger(o)
        elif type_string == "NegativeInteger":
            return self.check_NegativeInteger(o)
        elif type_string == "Integer":
            return self.check_Integer(o)
        elif type_string == "Number":
            return self.check_Number(o)
        elif type_string == "Base64":
            return self.check_Base64(o)
        elif type_string == "DateTimeString":
            return self.check_DateTimeString(o)
        elif type_string == "DateString":
            return self.check_DateString(o)
        elif type_string == "TimeString":
            return self.check_TimeString(o)
        elif type_string == "CurrencyString":
            return self.check_CurrencyString(o)
        elif type_string == "RateString":
            return self.check_RateString(o)
        elif type_string == "AmountString":
            return self.check_AmountString(o)
        elif type_string == "MaskedPANString":
            return self.check_MaskedPANString(o)
        elif type_string == "MaskedAccountString":
            return self.check_MaskedAccountString(o)
        elif type_string == "URIString":
            return self.check_URIString(o)
        elif type_string == "ExternalRef":
            return self.check_ExternalRef(o)
        else:
            print("### UNSUPPORTED TYPE {} ###".format(type_string))
            return False

    def check_ASCIIString(self, o):
        return True
    
    def check_Boolean(self, o):
        return type(o) == bool
    
    def check_NaturalNumber(self, o):
        return True
    
    def check_PositiveInteger(self, o):
        return True
        
    def check_NegativeInteger(self, o):
        return True
    
    def check_Integer(self, o):
        return True
    
    def check_Number(self, o):
        return True
    
    def check_Base64(self, o):
        return True
    
    def check_DateTimeString(self, o):
        return True
    
    def check_DateString(self, o):
        return True
    
    def check_TimeString(self, o):
        return True
    
    def check_CurrencyString(self, o):
        return True
    
    def check_RateString(self, o):
        return True
    
    def check_AmountString(self, o):
        return True
    
    def check_MaskedPANString(self, o):
        return True
    
    def check_MaskedAccountString(self, o):
        return True
    
    def check_URIString(self, o):
        return True
    
    def check_ExternalRef(self, o):
        return True