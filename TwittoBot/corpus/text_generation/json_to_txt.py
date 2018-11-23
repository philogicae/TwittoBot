#!/usr/bin/env python3
# coding: utf-8
import sys, io, json

try:
    with open("json/" + sys.argv[1], 'r') as jsonfile:
        with io.open("txt/" + sys.argv[1][:-4] + "txt", 'w', encoding="utf-8") as txtfile:
            for line in jsonfile:
                txtfile.write(json.loads(line).get("body")+'\n')
    print("Conversion json -> txt : Terminé")
    
except Exception as e: print("Erreur : " + str(e))
