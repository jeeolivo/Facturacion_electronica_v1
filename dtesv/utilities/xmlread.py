import xmltodict

 


class xmlreadDB(object):
   def read_xml():
        with open('/configuracion.xml', 'r', encoding='utf-8') as file:
          my_xml = file.read()
        my_dict = xmltodict.parse(my_xml)
        return my_dict