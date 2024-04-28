import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from xml.dom.minidom import Document, parseString
from flask import Flask, request, jsonify
from Clases.Cliente import Cliente as C
from Clases.Banco import Banco as B
from Clases.Factura import Factura as F
from Clases.Pago import Pago as P
#from unidecode import unidecode
#from datetime import datetime
#from collections import defaultdict
from flask import send_file
#import re



app = Flask(__name__)

# Listas
Clientes = []
Bancos = []
Facturas = []
Pagos = []

#Contadores 
contadorClientesActualizados = 0
contadorBancosActualizados = 0
contadorClientesNuevos = 0
contadorBancosNuevos = 0

contadorFacturasNuevas = 0
contadorPagosNuevos = 0
contadorFacturasDuplicadas = 0
contadorPagosDuplicados = 0
contadorPagosConError = 0
contadorFacturasConError = 0



# Funciones
def buscar_Banco(codigo):
    for banco in Bancos:
        if banco.getCodigo() == codigo:
            return True
    return False
        
def buscar_Cliente(nit):
    for cliente in Clientes:
        if cliente.getNit() == nit:
            return True
    return False

def buscar_Factura(numFactura):
    for factura in Facturas:
        if factura.getNumFactura() == numFactura:
            return True
    return False

def buscar_Pago(codigoBanco, fecha, nit, valor):
    for pago in Pagos:
        if pago.getCodigoBanco() == codigoBanco and pago.getFecha() == fecha and pago.getNit() == nit and pago.getValor() == valor:
            return True
    return False

# Rutas
@app.route('/grabarConfiguracion', methods=['POST'])
def procesar_archivo_Config():
    global contadorClientesActualizados, contadorBancosActualizados, contadorClientesNuevos, contadorBancosNuevos
    archivo = request.files.get('archivo')

    if archivo.filename == '':
        return jsonify({"error": "No se ha proporcionado ningún archivo"}), 400

    # Parsear el XML
    tree = ET.parse(archivo)
    root = tree.getroot()

    # Procesar los datos
    for cliente in root.findall('.//cliente'):
        nit = cliente.find('NIT').text.strip()
        nombre = cliente.find('nombre').text.strip()
        nuevo_cliente = C(nombre, nit)
        if buscar_Cliente(nit):
            for c in Clientes:
                if c.getNit() == nit:
                    Clientes.remove(c)
                    contadorClientesActualizados += 1
                    break
        else:
            contadorClientesNuevos += 1
        Clientes.append(nuevo_cliente)
    for banco in root.findall('.//banco'):
        codigo = banco.find('codigo').text.strip()
        nombre_banco = banco.find('nombre').text.strip()
        nuevo_banco = B(codigo, nombre_banco)
        if buscar_Banco(codigo):
            for b in Bancos:
                if b.getCodigo() == codigo:
                    Bancos.remove(b)
                    contadorBancosActualizados += 1
                    break
        else:
            contadorBancosNuevos += 1
        Bancos.append(nuevo_banco)


    for cliente in Clientes:
        print(cliente.getNombre(), cliente.getNit())

    for banco in Bancos:
        print(banco.getCodigo(), banco.getNombre())

    print(f"Clientes actualizados: {contadorClientesActualizados}")
    print(f"Clientes nuevos: {contadorClientesNuevos}")
    print(f"Bancos actualizados: {contadorBancosActualizados}")
    print(f"Bancos nuevos: {contadorBancosNuevos}")

    crear_xml_config()
    return 'Datos procesados correctamente'

  


@app.route('/generarSalidaConfig', methods=['GET'])
def crear_xml_config():
    global contadorClientesActualizados, contadorBancosActualizados, contadorClientesNuevos, contadorBancosNuevos
    # Crear el elemento raíz <respuesta>
    root = ET.Element("respuesta")

    # Elemento <clientes> con subelementos <creados> y <actualizados>
    clientes_element = ET.SubElement(root, "clientes")
    creados_element = ET.SubElement(clientes_element, "creados")
    creados_element.text = str(contadorClientesNuevos)
    actualizados_element = ET.SubElement(clientes_element, "actualizados")
    actualizados_element.text = str(contadorClientesActualizados)

    # Elemento <bancos> con subelementos <creados> y <actualizados>
    bancos_element = ET.SubElement(root, "bancos")
    creados_bancos_element = ET.SubElement(bancos_element, "creados")
    creados_bancos_element.text = str(contadorBancosNuevos)
    actualizados_bancos_element = ET.SubElement(bancos_element, "actualizados")
    actualizados_bancos_element.text = str(contadorBancosActualizados)  

    # Crear el árbol XML y escribirlo en un archivo
    tree = ET.ElementTree(root)
    tree.write("Salidas/respuestaConfig.xml")


    return "Archivo de salida generado con éxito"

@app.route('/grabarTransaccion', methods=['POST'])
def grabarTransaccion():
    global  contadorFacturasNuevas, contadorPagosNuevos, contadorFacturasDuplicadas, contadorPagosDuplicados
    archivo = request.files.get('archivo')
    
    if archivo.filename == '':
        return jsonify({"error": "No se ha proporcionado ningún archivo"}), 400

    tree = ET.parse(archivo)
    root = tree.getroot()

    for factura in root.findall('.//factura'):
        numFactura = factura.find('numeroFactura').text.strip()
        nit = factura.find('NITcliente').text.strip()
        fecha = factura.find('fecha').text.strip()
        valor = factura.find('valor').text.strip()
        nueva_factura = F(numFactura, nit, fecha, valor)
        if buscar_Factura(numFactura):
            contadorFacturasDuplicadas += 1
        else:
            contadorFacturasNuevas += 1
            Facturas.append(nueva_factura)

    for pago in root.findall('.//pago'):
        codigoBanco = pago.find('codigoBanco').text.strip()
        fecha = pago.find('fecha').text.strip()
        nit = pago.find('NITcliente').text.strip()
        valor = pago.find('valor').text.strip()
        nuevo_pago = P(codigoBanco, fecha, nit, valor)
        if buscar_Pago(codigoBanco, fecha, nit, valor):
            contadorPagosDuplicados += 1
        else:
            contadorPagosNuevos += 1
            Pagos.append(nuevo_pago)


    for factura in Facturas:
        print(factura.getNumFactura(), factura.getNit(), factura.getFecha(), factura.getValor())

    for pago in Pagos:
        print(pago.getCodigoBanco(), pago.getFecha(), pago.getNit(), pago.getValor())

    print(f"Facturas nuevas: {contadorFacturasNuevas}")
    print(f"Facturas duplicadas: {contadorFacturasDuplicadas}")
    print(f"Pagos nuevos: {contadorPagosNuevos}")
    print(f"Pagos duplicados: {contadorPagosDuplicados}")


    return 'Datos procesados correctamente'

@app.route('/generarSalidaTransac', methods=['GET'])
def crear_xml_respuesta_transac():
    global contadorFacturasNuevas, contadorPagosNuevos, contadorFacturasDuplicadas, contadorPagosDuplicados, contadorPagosConError, contadorFacturasConError
    root = ET.Element("transacciones")

    facturas_element = ET.SubElement(root, "facturas")
    creadas_element = ET.SubElement(facturas_element, "nuevasFacturas")
    creadas_element.text = str(contadorFacturasNuevas)
    duplicadas_element = ET.SubElement(facturas_element, "facturasDuplicadas")
    duplicadas_element.text = str(contadorFacturasDuplicadas)
    errores_element = ET.SubElement(facturas_element, "facturasConError")
    errores_element.text = str(contadorFacturasConError)

    pagos_element = ET.SubElement(root, "pagos")
    creados_pagos_element = ET.SubElement(pagos_element, "nuevosPagos")
    creados_pagos_element.text = str(contadorPagosNuevos)
    duplicados_pagos_element = ET.SubElement(pagos_element, "pagosDuplicados")
    duplicados_pagos_element.text = str(contadorPagosDuplicados)
    errores_pagos_element = ET.SubElement(pagos_element, "pagosConError")
    errores_pagos_element.text = str(contadorPagosConError)

    tree = ET.ElementTree(root)
    tree.write("Salidas/respuestaTransac.xml")


    return "Archivo de salida generado con éxito"


@app.route('/limpiarDatos', methods=['POST'])
def limpiarDatos():
    global contadorClientesActualizados, contadorBancosActualizados, contadorClientesNuevos, contadorBancosNuevos
    global contadorFacturasNuevas, contadorPagosNuevos, contadorFacturasDuplicadas, contadorPagosDuplicados
    global contadorPagosConError, contadorFacturasConError

    Clientes.clear()
    Bancos.clear()
    Facturas.clear()
    Pagos.clear()

    contadorClientesActualizados = 0
    contadorBancosActualizados = 0
    contadorClientesNuevos = 0
    contadorBancosNuevos = 0

    contadorFacturasNuevas = 0
    contadorPagosNuevos = 0
    contadorFacturasDuplicadas = 0
    contadorPagosDuplicados = 0
    contadorPagosConError = 0
    contadorFacturasConError = 0

    print(len(Clientes), len(Bancos), len(Facturas), len(Pagos))
    print(contadorClientesActualizados, contadorBancosActualizados, contadorClientesNuevos, contadorBancosNuevos)
    print(contadorFacturasNuevas, contadorPagosNuevos, contadorFacturasDuplicadas, contadorPagosDuplicados)
    print(contadorPagosConError, contadorFacturasConError)

    return 'Datos limpiados correctamente'

# @app.route('/obtenerHistorialConfiguraciones', methods=['GET'])
# def obtener_historial_configuraciones():
#     return jsonify({"historial_configuraciones": historial_configuraciones})


# @app.route('/generarSalidaTransac', methods=['GET'])
# def generar_archivo_resumen_config():
#     global palabras_positivas, palabras_negativas, palabras_negativas_rechazadas, palabras_positivas_rechazadas, historial_configuraciones,palabras_neutras

#     archivo_salida = "resumenConfig.xml"

#     # Crear el documento XML de salida
#     doc = Document()
#     config_recibida = doc.createElement('CONFIG_RECIBIDA')
#     doc.appendChild(config_recibida)

#     for configuracion in historial_configuraciones:
#         configuracion_element = doc.createElement('CONFIGURACION')
#         config_recibida.appendChild(configuracion_element)

#         fecha_element = doc.createElement('FECHA')
#         fecha_element.appendChild(doc.createTextNode(configuracion['fecha']))
#         configuracion_element.appendChild(fecha_element)  # Adjuntado dentro de configuracion_element

#         hora_element = doc.createElement('HORA')
#         hora_element.appendChild(doc.createTextNode(configuracion['hora']))
#         configuracion_element.appendChild(hora_element)  # Adjuntado dentro de configuracion_element

#         palabras_positivas_element = doc.createElement('PALABRAS_POSITIVAS')
#         palabras_positivas_element.appendChild(doc.createTextNode(str(configuracion['palabras_positivas'])))
#         configuracion_element.appendChild(palabras_positivas_element)  # Adjuntado dentro de configuracion_element

#         # Agregar el número de palabras positivas rechazadas
#         palabras_positivas_rechazadas_element = doc.createElement('PALABRAS_POSITIVAS_RECHAZADAS')
#         palabras_positivas_rechazadas_element.appendChild(doc.createTextNode(str(configuracion['palabras_positivas_rechazadas'])))
#         configuracion_element.appendChild(palabras_positivas_rechazadas_element)  # Adjuntado dentro de configuracion_element

#         # Agregar el número de palabras negativas acumuladas
#         palabras_negativas_element = doc.createElement('PALABRAS_NEGATIVAS')
#         palabras_negativas_element.appendChild(doc.createTextNode(str(configuracion['palabras_negativas'])))
#         configuracion_element.appendChild(palabras_negativas_element)  # Adjuntado dentro de configuracion_element

#         # Agregar el número de palabras negativas rechazadas
#         palabras_negativas_rechazadas_element = doc.createElement('PALABRAS_NEGATIVAS_RECHAZADAS')
#         palabras_negativas_rechazadas_element.appendChild(doc.createTextNode(str(configuracion['palabras_negativas_rechazadas'])))
#         configuracion_element.appendChild(palabras_negativas_rechazadas_element)  # Adjuntado dentro de configuracion_element

#         palabras_neutras_element = doc.createElement('PALABRAS_NEUTRAS')
#         palabras_neutras_element.appendChild(doc.createTextNode(str(configuracion['palabras_neutras'])))
#         configuracion_element.appendChild(palabras_neutras_element)  # Adjuntado dentro de configuracion_element

#         # Agregar los demás datos de configuración (palabras positivas, negativas, rechazadas, etc.)

#     # Generar el archivo de salida en el formato deseado
#     with open(archivo_salida, 'w', encoding='utf-8') as output_file:
#         output_file.write(doc.toprettyxml(indent=" "))
    
#     return "Archivo de salida generado con éxito"

# @app.route('/limpiarDatos', methods=['POST'])
# def reiniciar_datos_globales():
#     global mensajes_recibidos, usuarios_mencionados, hashtags_incluidos, palabras_positivas, palabras_negativas, palabras_negativas_rechazadas, palabras_positivas_rechazadas, historial_configuraciones
#     mensajes_recibidos = {}
#     usuarios_mencionados = set()
#     hashtags_incluidos = set()
#     palabras_positivas = 0
#     palabras_negativas = 0
#     palabras_neutras = 0
#     palabras_negativas_rechazadas = 0
#     palabras_positivas_rechazadas = 0
#     historial_configuraciones = []

#     return json.dumps({
#         "mensajes_recibidos": mensajes_recibidos,
#         "usuarios_mencionados": list(usuarios_mencionados),
#         "hashtags_incluidos": list(hashtags_incluidos),
#         "palabras_positivas": palabras_positivas,
#         "palabras_negativas": palabras_negativas,
#         "palabras_neutras": palabras_neutras,
#         "palabras_negativas_rechazadas": palabras_negativas_rechazadas,
#         "palabras_positivas_rechazadas": palabras_positivas_rechazadas,
#         "configuracion_por_fecha": historial_configuraciones
#     }, indent=4)

# @app.route('/devolverHashtags', methods=['GET'])
# def contar_hashtags():
#     global mensajes_recibidos
#     codigoRespuesta = 1

#     hashtags_contados = {}  # Diccionario para almacenar los hashtags y sus cantidades

#     for mensajes in mensajes_recibidos.values():
#         for mensaje in mensajes:
#             for hashtag in mensaje['HASH_INCLUIDOS']:
#                 if hashtag in hashtags_contados:
#                     hashtags_contados[hashtag] += 1
#                 else:
#                     hashtags_contados[hashtag] = 1

#     if not hashtags_contados:
#         codigoRespuesta = 0
#         return jsonify({"codigo":codigoRespuesta,"mensaje":"No se encontraron hashtags en los mensajes."}), 404
#     else:
#         return jsonify({"codigo":codigoRespuesta,"hashtags_contados": hashtags_contados})

# @app.route('/devolverMenciones', methods=['GET'])
# def contar_menciones():
#     global mensajes_recibidos
#     codigoRespuesta = 1
#     menciones_contadas = {}  # Diccionario para almacenar las menciones y sus cantidades

#     for mensajes in mensajes_recibidos.values():
#         for mensaje in mensajes:
#             for mencion in mensaje['USR_MENCIONADOS']:
#                 if mencion in menciones_contadas:
#                     menciones_contadas[mencion] += 1
#                 else:
#                     menciones_contadas[mencion] = 1

#     if not menciones_contadas:
#         codigoRespuesta = 0
#         return jsonify({"codigo":codigoRespuesta,"mensaje":"No se encontraron menciones en los mensajes."}), 404
#     else:
#         return jsonify({"codigo":codigoRespuesta,"menciones_usuario": menciones_contadas})

# @app.route('/grabarDatos', methods=['POST'])
# def grabarDatos():
#     # Tu código para procesar los mensajes

#     # Guardar los datos en un archivo JSON
#     with open('datos.json', 'w') as json_file:
#         data = {
#             "mensajes_recibidos": mensajes_recibidos,
#             "usuarios_mencionados": list(usuarios_mencionados),
#             "hashtags_incluidos": list(hashtags_incluidos),
#             "menciones_usuario": menciones_usuario,
#             "menciones_hashtag": menciones_hashtag,
#             "palabras_positivas": palabras_positivas,
#             "palabras_negativas": palabras_negativas,
#             "palabras_negativas_rechazadas": palabras_negativas_rechazadas,
#             "palabras_positivas_rechazadas": palabras_positivas_rechazadas,
#             "configuracion_por_fecha": historial_configuraciones
#         }
#         json.dump(data, json_file)
        
#     return 'Datos guardados con éxito'



# @app.route('/obtenerHashtagsPorRango', methods=['GET'])
# def contar_hashtags_por_rango():
#     codigoRespuesta = 1
#     fecha_inicio = request.form.get('fecha_inicio')
#     fecha_fin = request.form.get('fecha_fin')
    
#     if fecha_inicio is None or fecha_fin is None:
#         return jsonify({"error": "Las fechas de inicio y fin son requeridas"}), 400

#     hashtags_por_fecha = defaultdict(lambda: defaultdict(int))  # Diccionario para contar hashtags por fecha

#     # Iterar a través de las fechas dentro del rango
#     for fecha in mensajes_recibidos:
#         if fecha_inicio <= fecha <= fecha_fin:
#             for mensaje in mensajes_recibidos[fecha]:
#                 hashtags = mensaje['HASH_INCLUIDOS']
#                 for hashtag in hashtags:
#                     hashtags_por_fecha[fecha][hashtag] += 1

#     if not hashtags_por_fecha:
#         codigoRespuesta = 0
#         return jsonify({"codigo": codigoRespuesta, "mensaje": "No se encontraron hashtags en el rango de fechas proporcionado."}), 404

#     # Organizar los hashtags por fecha
#     resultado = {
#         "codigo": codigoRespuesta,
#         "hashtags_por_fecha": dict(hashtags_por_fecha),
#         "hashtags_totales": defaultdict(int)
#     }

#     # Calcular el contador total
#     for fecha, hashtags in hashtags_por_fecha.items():
#         for hashtag, conteo in hashtags.items():
#             resultado["hashtags_totales"][hashtag] += conteo

#     return jsonify(resultado)


# @app.route('/obtenerMencionesPorRango', methods=['GET'])
# def contar_menciones_por_rango():
#     codigoRespuesta = 1
#     fecha_inicio = request.form.get('fecha_inicio')
#     fecha_fin = request.form.get('fecha_fin')

#     if fecha_inicio is None or fecha_fin is None:
#         return jsonify({"Las fechas de inicio y fin son requeridas"}), 400

#     menciones_por_fecha = defaultdict(lambda: defaultdict(int))  # Diccionario para contar menciones por fecha

#     # Iterar a través de las fechas dentro del rango
#     for fecha in mensajes_recibidos:
#         if fecha_inicio <= fecha <= fecha_fin:
#             for mensaje in mensajes_recibidos[fecha]:
#                 menciones = mensaje['USR_MENCIONADOS']
#                 for mencion in menciones:
#                     menciones_por_fecha[fecha][mencion] += 1

#     if not menciones_por_fecha:
#         codigoRespuesta = 0
#         return jsonify({"codigo": codigoRespuesta, "mensaje": "No se encontraron menciones en el rango de fechas proporcionado."}), 404

#     # Organizar las menciones por fecha
#     resultado = {
#         "codigo": codigoRespuesta,
#         "menciones_por_fecha": dict(menciones_por_fecha),
#         "menciones_usuario_totales": defaultdict(int)
#     }

#     # Calcular el contador total
#     for fecha, menciones in menciones_por_fecha.items():
#         for mencion, conteo in menciones.items():
#             resultado["menciones_usuario_totales"][mencion] += conteo

#     return jsonify(resultado)

# @app.route('/consultarSentimientos', methods=['GET'])
# def consultar_sentimientos():
#     codigoRespuesta = 1
#     fecha_inicio_str = request.form.get('fecha_inicio')
#     fecha_fin_str = request.form.get('fecha_fin')

#     if not fecha_inicio_str or not fecha_fin_str:
#         # Si falta alguno de los parámetros, devuelve un mensaje de error
#         return jsonify({"Mensaje": "Los parámetros 'fecha_inicio' y 'fecha_fin' son obligatorios."}), 400

#     # Convierte las fechas de cadena a objetos datetime
#     fecha_inicio = datetime.strptime(fecha_inicio_str, "%d-%m-%Y")
#     fecha_fin = datetime.strptime(fecha_fin_str, "%d-%m-%Y")

#     # Inicializar un diccionario para almacenar las menciones de palabras por fecha y hora, incluyendo segundos
#     menciones_por_fecha_hora = defaultdict(dict)

#     # Calcular el total de palabras en todas las configuraciones dentro del rango de fechas
#     total_palabras_positivas = 0
#     total_palabras_negativas = 0
#     total_palabras_positivas_rechazadas = 0
#     total_palabras_negativas_rechazadas = 0
#     total_palabras_neutras = 0

#     for configuracion in historial_configuraciones:
#         fecha_configuracion = datetime.strptime(configuracion["fecha"], "%d/%m/%Y")
#         hora_configuracion = configuracion.get("hora", "")
        
#         if fecha_inicio <= fecha_configuracion <= fecha_fin:
#             palabras_positivas = configuracion.get("palabras_positivas", 0)
#             palabras_negativas = configuracion.get("palabras_negativas", 0)
#             palabras_neutras = configuracion.get("palabras_neutras", 0)
#             palabras_positivas_rechazadas = configuracion.get("palabras_positivas_rechazadas", 0)
#             palabras_negativas_rechazadas = configuracion.get("palabras_negativas_rechazadas", 0)

#             # Actualizar los totales de palabras
#             total_palabras_positivas += palabras_positivas
#             total_palabras_negativas += palabras_negativas
#             total_palabras_neutras += palabras_neutras
#             total_palabras_positivas_rechazadas += palabras_positivas_rechazadas
#             total_palabras_negativas_rechazadas += palabras_negativas_rechazadas

#             # Construir la clave para la fecha y hora, incluyendo segundos
#             fecha_hora_str = f"{fecha_configuracion.strftime('%d/%m/%Y')} {hora_configuracion}"

#             # Actualizar las menciones de palabras por fecha y hora
#             menciones_por_fecha_hora[fecha_hora_str]["palabras_positivas"] = palabras_positivas
#             menciones_por_fecha_hora[fecha_hora_str]["palabras_negativas"] = palabras_negativas
#             menciones_por_fecha_hora[fecha_hora_str]["palabras_positivas_rechazadas"] = palabras_positivas_rechazadas
#             menciones_por_fecha_hora[fecha_hora_str]["palabras_negativas_rechazadas"] = palabras_negativas_rechazadas
#             menciones_por_fecha_hora[fecha_hora_str]["palabras_neutras"] = palabras_neutras
            
#     if not menciones_por_fecha_hora:
#         codigoRespuesta = 0
#         return jsonify({"codigo": codigoRespuesta, "mensaje": "No se encontraron sentimientos en el rango de fechas proporcionado."}), 404

#     return jsonify({
#         "codigo": codigoRespuesta,
#         "menciones_por_fecha_hora": menciones_por_fecha_hora,
#         "total_palabras": {
#             "positivas": total_palabras_positivas,
#             "negativas": total_palabras_negativas,
#             "neutras": total_palabras_neutras,
#             "positivas_rechazadas": total_palabras_positivas_rechazadas,
#             "negativas_rechazadas": total_palabras_negativas_rechazadas
#         }
#     })

# if __name__ == "__main__":
#     # try:
#     #     with open('datos.json', 'r') as json_file:
#     #         data = json.load(json_file)
#     #         mensajes_recibidos = data.get("mensajes_recibidos", {})
#     #         usuarios_mencionados = set(data.get("usuarios_mencionados", []))
#     #         hashtags_incluidos = set(data.get("hashtags_incluidos", []))
#     #         menciones_usuario = data.get("menciones_usuario", {})
#     #         menciones_hashtag = data.get("menciones_hashtag", {})
#     #         palabras_positivas = data.get("palabras_positivas", 0)
#     #         palabras_negativas = data.get("palabras_negativas", 0)
#     #         palabras_neutras = data.get("palabras_neutras", 0)  
#     #         palabras_negativas_rechazadas = data.get("palabras_negativas_rechazadas", 0) 
#     #         palabras_positivas_rechazadas = data.get("palabras_positivas_rechazadas", 0)
#     #         historial_configuraciones = data.get("configuracion_por_fecha", [])

#     # except FileNotFoundError:
#     #     mensajes_recibidos = {}
#     #     usuarios_mencionados = set()
#     #     hashtags_incluidos = set()
#     #     menciones_usuario = {}
#     #     menciones_hashtag = {}
#     #     palabras_positivas = 0
#     #     palabras_negativas = 0
#     #     palabras_neutras = 0
#     #     palabras_negativas_rechazadas = 0
#     #     palabras_positivas_rechazadas = 0
#     #     historial_configuraciones = []



app.run(debug=True, port=5000)





