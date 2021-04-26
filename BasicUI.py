# -*- coding: utf-8 -*-
"""
Created on Wed Apr 14 17:04:49 2021

@author: sbhar
"""
import PySimpleGUI as sg
import check_schema as cs
import json

with open("get_products/Adelaide Bank_product_details/CHL Select Term Loan_details.json", encoding='utf-8') as f:
    chl = json.load(f)
with open("cds_full.json", encoding='utf-8') as f:
    cds = json.load(f)
s = cs.SchemaChecker(cds, debug=False)
s.check(chl, {"$ref" : "ResponseBankingProductById"})
error_tree = sg.TreeData()

d = {}
#print(s.errors)
#for error in s.errors:
#    path = error[0]
#    message = error[1]
#    for i in range(len(path)):
#        parent = str(([""]+path)[i])
#        child = str(path[i])
#        #print(parent, child)
#        if (child not in d) or (parent not in d[child]):
#            d[child] = parent
#            if i == len(path)-1:
#                print(message)
#                error_tree.Insert(parent, child, child, values=[message])
#            else:
#                error_tree.Insert(parent, child, child, values=[])
values = [['/'.join([str(i) for i in e[0]]), e[1]] for e in s.errors]

list_ADI = ['ANZ', 'UBank', 'Up', 'BDCU Alliance Bank', 'Westpac', 'RAMS', 'Adelaide Bank'] 
list_checks = ['API availability', 'Mandatory fields presense', 'Schema verification' ]
layout = [
           [sg.Text("Select ADI")], [sg.Combo(list_ADI, size = (20,4))], 
           [sg.Text("Select Check to perform")], 
           [sg.Combo(list_checks, size = (20,4))], 
           [sg.Button("Run Checks")],
           [sg.Table(values, headings=["Field", "Issue"], justification="left", vertical_scroll_only=False)]
         ]

# Create the window
window = sg.Window("Demo GUI", layout, margins=(300, 100))

# Create an event loop
while True:
    event, values = window.read()
    
    #Response to the event 
    if event == "Run Checks": 
        """
        Add a function call here
        perform_check(values[0], values[1])
        """
    # End program if user closes window     
    elif event == sg.WIN_CLOSED:
        break

window.close()