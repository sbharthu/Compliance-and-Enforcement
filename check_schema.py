# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 15:54:02 2021

@author: sesle
"""

import json
from check_cds_type import CDSTypeChecker

def debug(f):
    """
    Decorator function used in SchemaChecker methods to indent debug output.
    """
    def g(ref, *args, **kwargs):
        ref.indent += 2
        temp = f(ref, *args, **kwargs)
        ref.indent -= 2
        return temp
    return g

class SchemaChecker:
    def __init__(self, cds, debug=False):
        self.indent = 0
        self.debug = debug # switch debug log on/off
        self.stack = [] # traces our path through the object tree
        self.errors = []
        self.cds = cds # a JSON encoding of the Consumer Data Standards
        self.ctc = CDSTypeChecker()
    
    def pprint(self, *args, **kwargs):
        """
        Prints debug output, at an indent determined by the debug decorator,
        or not at all if self.debug is False."
        """
        if self.debug:
            print(' '*self.indent, *args, **kwargs)
    
    def log_error(self, error_string):
        """
        Records an instance of noncompliance with the schema as well as where
        in the response it occurred.
        """
        self.errors.append((self.stack[:], error_string))
    
    def print_errors(self):
        """
        Prints errors recorded in self.errors in a readable format.
        """
        print("Found {} errors:".format(len(self.errors)))
        def format_path(path):
            s = []
            for i in path:
                if type(i) == str:
                    s.append('/' + i)
                elif type(i) == int:
                    s.append("[{}]".format(i))
            return ''.join(s)
        
        for path, error_string in self.errors:
            print("In {}:\n\t{}".format(format_path(path), error_string))
    
    def get_errors(self):
        e = []
        def format_path(path):
            s = []
            for i in path:
                if type(i) == str:
                    s.append('/' + i)
                elif type(i) == int:
                    s.append("[{}]".format(i))
            return ''.join(s)
        
        for path, error_string in self.errors:
            e.append([format_path(path), error_string])
        
        return e
    
    def get_schema(self, sch_type):
        definitions = self.cds["definitions"]
        return definitions[sch_type]
    
    @debug
    def check(self, obj, sch):
        """
        Takes in a JSON object obj, and sch, which can be a JSON schema or a
        reference to one. If it is a reference (its only field will be "$ref"),
        it looks up referenced schema. The object is then checked against the
        schema using check_object.
        """
        if "$ref" in sch:
            sch_type = sch["$ref"].split('/')[-1] # trim the relevant part
            sch = self.get_schema(sch_type)
        self.check_object(obj, sch)
    
    @debug
    def check_object(self, obj, sch):
        """
        Takes in a JSON object obj, and a JSON object sch, the latter of which
        is a schema of the former. This function checks whether obj is a simple
        object (e.g. integer, string), an array of objects, or a complex object.
        Arrays and complex objects are recursively reduced to simple objects.
        """
        if "type" not in sch or sch["type"] == "object":
            self.check_complex_object(obj, sch)
        elif sch["type"] == "array":
            self.check_array(obj, sch["items"])
        elif sch["type"] in ["string", "boolean", "integer", "number"]:
            self.check_simple_object(obj, sch)
        else:
            self.pprint("### UNHANDLED TYPE: {} ###".format(sch["type"]))
            return False
        return
    
    @debug
    def check_type(self, obj, sch_type):
        """
        Checks that obj has the simple type specified in sch_type. Objects of
        type 'array' and 'object' are checked in their own methods.
        """
        if sch_type == "string":
            return type(obj) == str
        elif sch_type == "boolean":
            return type(obj) == bool
        elif sch_type == "integer":
            return type(obj) == int
        elif sch_type == "number":
            return type(obj) == int or type(obj) == float
        else:
            self.pprint("### ERROR: unhandled type {}".format(sch_type))
            return False
    
    @debug
    def check_x_cds_type(self, obj, cds_type):
        """
        Checks that a simple object conforms to an aditional type specified in
        the 'x-cds-type' field. Details on these CDS types can be found here:
        https://consumerdatastandardsaustralia.github.io/standards/#common-field-types
        """
        return self.ctc.check(obj, cds_type)
    
    # TODO: see if there are further checking requirements, e.g. ones written in the description
    # TODO: optional fields are ALLOWED to be null
    @debug
    def check_simple_object(self, obj, sch):
        """
        Takes in a JSON object obj, and a JSON schema sch. The schema contains
        fields detailing basic type (e.g. string, integer), sometimes an
        enumeration of restricted values, sometimes an extra CDS type (e.g. 
        DateTime string on top of being a basic string). This function ensures
        that the object complies with the schema.
        """
        # check type
        self.pprint("Checking that field is of type '{}'...".format(sch["type"]))
        if not self.check_type(obj, sch["type"]):
            # record type noncompliance
            self.log_error("Invalid type: {} where {} was expected".format(type(obj).__name__, sch["type"]))
        self.pprint("Valid.".format())
        
        # check enum
        if "enum" in sch:
            self.pprint("Field is an enumerated type. Checking if valid...")
            if obj not in sch["enum"]:
                # record enum noncompliance
                self.errors.append((self.stack[:], "Invalid enumerated value '{}': value must be one of {}".format(obj, sch["enum"])))
            else:
                self.pprint("Valid.")
        
        # check CDS type
        if "x-cds-type" in sch:
            self.pprint("Field has additional CDS type '{}'. Checking...".format(sch["x-cds-type"]))
            if not self.check_x_cds_type(obj, sch["x-cds-type"]):
                pass
                # TODO: record CDS type noncompliance
            self.pprint("Valid.")
        return
    
    @debug
    def check_array(self, obj, items, indent=0):
        """
        Takes in an array of objects "obj" and checks that they are all
        compliant with the schema "items".
        """
        self.pprint("Checking array:")
        if not type(obj) == list:
            self.log_error("Invalid array: object is actually of type {}".format(type(obj).__name__))
        for i, element in enumerate(obj):
            self.stack.append(i)
            self.check(element, items)
            self.stack.pop()
        return
    
    @debug
    def check_complex_object(self, obj, sch):
        """
        Takes in a complex object that could be made up of simple objects and
        complex objects and checks it against its schema.
        """
        # if there is an allOf clause,
        # we combine the required fields list and properties list of the objects
        # in the allOf clause into one combined schema, and verify the object
        # against that
        if "allOf" in sch:
            self.pprint("allOf clause: combining...")
            combined_sch = {"type" : "object", "required" : [], "properties" : {}}
            for sub_sch in sch["allOf"]:
                if "$ref" in sub_sch:
                    sub_sch_type = sub_sch["$ref"].split('/')[-1]
                    sub_sch = self.get_schema(sub_sch_type) # replace $ref by actual schema
                # add required fields and properties to the combined schema
                if "required" in sub_sch:
                    combined_sch["required"] += sub_sch["required"]
                combined_sch["properties"].update(sub_sch["properties"])
            sch = combined_sch

        # check that all mandatory fields are present        
        if "required" in sch:
            self.pprint("Checking mandatory fields (if any):")
            for m_field in sch["required"]:
                self.pprint("Mandatory field: '{}'".format(m_field))
                if m_field not in obj:
                    # record missing mandatory field noncompliance
                    self.log_error("Invalid object: mandatory field {} missing".format(m_field))
                else:
                    self.pprint("Mandatory field '{}' is present. Verifying...".format(m_field))
                    self.stack.append(m_field)
                    self.check(obj[m_field], sch["properties"][m_field])
                    self.stack.pop()
            self.pprint("Finished mandatory fields.")
        
        # check that optional fields, if present, are correctly formatted
        # TODO: optional fields are ALLOWED to be null
        self.pprint("Checking optional fields (if any):")
        for field in obj:
            if "required" in sch and field in sch["required"]:
                continue # we've already checked required fields
            if field not in sch["properties"]:
                # record unexpected field noncompliance
                self.log_error("Invalid object: unexpected field {}".format(field))
            else:
                self.stack.append(field)
                self.check(obj[field], sch["properties"][field])
                self.stack.pop()
        self.pprint("Finished optional fields.")
        return

if __name__ == "__main__":
    with open("get_products/Adelaide Bank_product_details/CHL Select Term Loan_details.json", encoding='utf-8') as f:
        chl = json.load(f)
    with open("cds_full.json", encoding='utf-8') as f:
        cds = json.load(f)
    s = SchemaChecker(cds)
    s.check(chl, {"$ref" : "ResponseBankingProductById"})
    s.print_errors()
