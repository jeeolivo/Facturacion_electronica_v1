import xml.etree.ElementTree as ET
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
directorio_actual = os.getcwd()
mymodule_dir = os.path.join(directorio_actual, 'Facturacion_electronica\\dtesv\\xml\\')
 



def xml_to_dict(xml_file):    
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Crea un diccionario vacío
    data = {}

    # Recorre todos los nodos del archivo XML
    for node in root:
        # Obtiene el nombre del nodo
        node_name = node.tag

        # Crea un diccionario para almacenar los datos del nodo
        node_data = {}

        # Recorre los elementos hijos del nodo y agrega sus valores al diccionario
        for element in node:
            node_data[element.tag] = element.text

        # Agrega el diccionario del nodo al diccionario principal
        data[node_name] = node_data

    return data

def conexion_server(): 
    xml_file = mymodule_dir + 'conexion.xml'
    data_dict = xml_to_dict(xml_file)
    return data_dict
 

    