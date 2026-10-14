import xmltodict
import sys
import os
script_dir = os.getcwd()

class xmlread(object):
    """Lector de Archivo XML"""
    def read_xml():
        with open('xml/CORRECTXPRS.xml', 'r', encoding='utf-8') as file:
          my_xml = file.read()
        my_dict = xmltodict.parse(my_xml)
        return my_dict
