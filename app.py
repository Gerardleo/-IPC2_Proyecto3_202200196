from collections import defaultdict
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from xml.dom.minidom import Document, parseString
from flask import Flask, request, jsonify
from Clases.Cliente import Cliente as C
from Clases.Banco import Banco as B
from Clases.Factura import Factura as F
from Clases.Pago import Pago as P
from datetime import datetime
from flask import send_file
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape
from reportlab.platypus import Table, TableStyle, PageBreak
from io import BytesIO
import os
import webbrowser

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

def agregarSaldo(nit, valor):
    for cliente in Clientes:
        if cliente.getNit() == nit:
            cliente.setSaldo(valor)
            break

def restarSaldo(nit, valor):
    for cliente in Clientes:
        if cliente.getNit() == nit:
            cliente.setSaldo(-valor)
            break
        
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

def buscar_Pago(codigoBanco, fecha, nit):
    for pago in Pagos:
        if pago.getCodigoBanco() == codigoBanco and pago.getFecha() == fecha and pago.getNit() == nit:
            return True
    return False

def retornarFacturas(nit):
    facturas = []
    for factura in Facturas:
        if factura.getNit() == nit:
            facturas.append(factura)
    return facturas

def retornarPagos(nit):
    pagos = []
    for pago in Pagos:
        if pago.getNit() == nit:
            pagos.append(pago)
    return pagos

def retornarCliente(nit):
    for cliente in Clientes:
        if cliente.getNit() == nit:
            return cliente
    return None

def nombreBanco(codigo):
    for banco in Bancos:
        if banco.getCodigo() == codigo:
            return banco.getNombre()
    return None

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
    global  contadorFacturasNuevas, contadorPagosNuevos, contadorFacturasDuplicadas, contadorPagosDuplicados, contadorPagosConError, contadorFacturasConError
    archivo = request.files.get('archivo')
    try:
        if archivo.filename == '':
            return jsonify({"error": "No se ha proporcionado ningún archivo"}), 400

        tree = ET.parse(archivo)
        root = tree.getroot()

        for factura in root.findall('.//factura'):
            numFactura = factura.find('numeroFactura').text.strip()
            nit = factura.find('NITcliente').text.strip()
            fechaString = factura.find('fecha').text.strip()
            validador = re.search(r"([0-2][0-9]|3[0-1])(/)(0[1-9]|1[0-2])\2(\d{4})", fechaString)
            if validador is None:
                contadorFacturasConError += 1
            else:
                fecha_str = validador.group()
                dia, mes, anio = map(int, fecha_str.split('/'))
                fecha = datetime(anio, mes, dia)
                valor = float(factura.find('valor').text.strip())
                nueva_factura = F(numFactura, nit, fecha, valor)
                if buscar_Cliente(nit) == False or valor < 0:
                    contadorFacturasConError += 1
                else:
                    if buscar_Factura(numFactura):
                        contadorFacturasDuplicadas += 1
                    else:
                        contadorFacturasNuevas += 1
                        agregarSaldo(nit, valor)
                        Facturas.append(nueva_factura)    
            

        for pago in root.findall('.//pago'):
            codigoBanco = pago.find('codigoBanco').text.strip()
            fechaString = pago.find('fecha').text.strip()
            validador = re.search(r"([0-2][0-9]|3[0-1])(/)(0[1-9]|1[0-2])\2(\d{4})", fechaString)
            if validador is None:
                contadorPagosConError += 1
            else:
                fecha_str = validador.group()
                dia, mes, anio = map(int, fecha_str.split('/'))
                fecha = datetime(anio, mes, dia)
                valor = float(factura.find('valor').text.strip())
                nueva_factura = F(numFactura, nit, fecha, valor)
                nit = pago.find('NITcliente').text.strip()
                valor = float(pago.find('valor').text.strip())
                if buscar_Cliente(nit) == False or buscar_Banco(codigoBanco) == False or valor < 0:
                    contadorPagosConError += 1
                else:
                    nuevo_pago = P(codigoBanco, fecha, nit, valor)
                    if buscar_Pago(codigoBanco, fecha, nit):
                        contadorPagosDuplicados += 1
                    else:
                        contadorPagosNuevos += 1
                        Pagos.append(nuevo_pago)
                        restarSaldo(nit, valor)


        for factura in Facturas:
            print(factura.getNumFactura(), factura.getNit(), factura.getFecha(), factura.getValor())

        for pago in Pagos:
            print(pago.getCodigoBanco(), pago.getFecha(), pago.getNit(), pago.getValor())

        print(f"Facturas nuevas: {contadorFacturasNuevas}")
        print(f"Facturas duplicadas: {contadorFacturasDuplicadas}")
        print(f"Facturas con error: {contadorFacturasConError}")
        print(f"Pagos nuevos: {contadorPagosNuevos}")
        print(f"Pagos duplicados: {contadorPagosDuplicados}")
        print(f"Pagos con error: {contadorPagosConError}")


        crear_xml_respuesta_transac()
    except Exception as e:
        print(e)

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

def ordenar_por_fecha_descendente(objetos):
    return sorted(objetos, key=lambda x: x['fecha'], reverse=False)

# Función para unificar y ordenar créditos y débitos en un solo estado de cuenta
def unificar_y_ordenar_estado_cuenta(debitos, creditos):
    estado_cuenta = {
        "cliente": "",
        "nit": "",
        "saldo": 0,
        "movimientos": []
    }

    # Agregar débitos al estado de cuenta
    for debito in debitos:
        estado_cuenta["movimientos"].append({
            "tipo": "debito",
            "num_factura": debito['num_factura'],
            "fecha": debito['fecha'],
            "valor": debito['valor'],
        })

    # Agregar créditos al estado de cuenta
    for credito in creditos:
        estado_cuenta["movimientos"].append({
            "tipo": "credito",
            "codigo_banco": credito['codigo_banco'],
            "fecha": credito['fecha'],
            "valor": credito['valor'],
            "banco": credito['banco']
        })

    # Ordenar el estado de cuenta combinado por fecha de manera descendente
    estado_cuenta["movimientos"] = ordenar_por_fecha_descendente(estado_cuenta["movimientos"])

    return estado_cuenta

# Ruta para obtener el estado de cuenta unificado y ordenado
@app.route('/devolverEstadoCuenta', methods=['GET'])
def devolverEstadoCuenta():
    try:
        nit = request.form.get('nit')

        debitos = []
        creditos = []
        lista_movimientos = []
        if nit == '':
            # Todos los clientes
            lista_movimientos = []
            for cliente in Clientes:
                debitos = []
                creditos = []
                facturas = retornarFacturas(cliente.getNit())
                pagos = retornarPagos(cliente.getNit())

                for factura in facturas:
                    debitos.append({
                        "num_factura": factura.getNumFactura(),
                        "fecha": factura.getFecha().strftime("%d/%m/%Y"),
                        "valor": factura.getValor(),
                    })

                for pago in pagos:
                    creditos.append({
                        "codigo_banco": pago.getCodigoBanco(),
                        "fecha": pago.getFecha().strftime("%d/%m/%Y"),
                        "valor": pago.getValor(),
                        "banco": nombreBanco(pago.getCodigoBanco())
                    })
                
                estado_cuenta = unificar_y_ordenar_estado_cuenta(debitos, creditos)
                estado_cuenta["cliente"] = cliente.getNombre()
                estado_cuenta["nit"] = cliente.getNit()
                estado_cuenta["saldo"] = cliente.getSaldo()
                lista_movimientos.append(estado_cuenta)

            lista_movimientos.sort(key=lambda x: x['nit'], reverse=True)
            descargar_pdf(lista_movimientos)
            return jsonify(lista_movimientos)

            
        else:
            # cliente con nit específico
            if buscar_Cliente(nit):
                lista_movimientos = []
                cliente = retornarCliente(nit)
                facturas = retornarFacturas(nit)
                pagos = retornarPagos(nit)

                for factura in facturas:
                    debitos.append({
                        "num_factura": factura.getNumFactura(),
                        "fecha": factura.getFecha().strftime("%d/%m/%Y"),
                        "valor": factura.getValor(),
                    })

                for pago in pagos:
                    creditos.append({
                        "codigo_banco": pago.getCodigoBanco(),
                        "fecha": pago.getFecha().strftime("%d/%m/%Y"),
                        "valor": pago.getValor(),
                        "banco": nombreBanco(pago.getCodigoBanco())
                    })

                estado_cuenta = unificar_y_ordenar_estado_cuenta(debitos, creditos)
                estado_cuenta["cliente"] = cliente.getNombre()
                estado_cuenta["nit"] = cliente.getNit()
                estado_cuenta["saldo"] = cliente.getSaldo()
                lista_movimientos.append(estado_cuenta)
                descargar_pdf(lista_movimientos)
                return jsonify(lista_movimientos)
            else:
                return jsonify({"error": "El cliente no existe"}), 404

    except Exception as e:
        print(e)
        return jsonify({"error": "Ha ocurrido un error"}), 500
    

def obtener_tercer_mes_anterior(fecha):
    # Obtener el mes y el año de la fecha proporcionada
    mes_actual = fecha.month
    anio_actual = fecha.year

    # Calcular el tercer mes anterior
    tercer_mes_anterior = mes_actual - 2  # Tercer mes anterior
    anio_tercer_mes_anterior = anio_actual
    if tercer_mes_anterior <= 0:
        tercer_mes_anterior += 12
        anio_tercer_mes_anterior -= 1

    return datetime(anio_tercer_mes_anterior, tercer_mes_anterior, 1)
    
@app.route("/resumenBanco", methods=["GET"])
def resumenBanco():
    global Pagos, Bancos
    lista_bancos = []
    strFecha = request.form.get('fecha')  # Usamos args en lugar de form para GET
    dia, mes, anio = map(int, strFecha.split('/'))
    fecha = datetime(anio, mes, dia)
    
    # Obtener el tercer mes anterior a la fecha proporcionada
    tercer_mes_anterior = obtener_tercer_mes_anterior(fecha)
    
    for banco in Bancos:
        for i in range(3):
            # Calcular el mes correspondiente
            mes_actual = tercer_mes_anterior.month + i
            anio_actual = tercer_mes_anterior.year
            if mes_actual <= 0:
                mes_actual += 12
                anio_actual -= 1
            mes_actual_str = f'{mes_actual:02d}'  # Formatear mes a dos dígitos
            
            # Calcular el total de pagos para este banco en este mes
            total_mes = 0
            for pago in Pagos:
                if pago.getCodigoBanco() == banco.getCodigo() and pago.getFecha().month == mes_actual and pago.getFecha().year == anio_actual:
                    total_mes += pago.getValor()            
            # Agregar el resumen a la lista de bancos
            lista_bancos.append({
                "banco": banco.getNombre(),
                "mes": mes_actual_str,
                "total": total_mes
            })

    # Ordenar la lista de bancos por nombre y mes
    lista_bancos.sort(key=lambda x: (x["banco"], x["mes"]))
    
    # Agrupar los datos por mes
    resumen_por_mes = {}
    for resumen in lista_bancos:
        mes = resumen['mes']
        if mes not in resumen_por_mes:
            resumen_por_mes[mes] = []
        resumen_por_mes[mes].append({
            "banco": resumen['banco'],
            "total": resumen['total']
        })

    return jsonify(resumen_por_mes)



    
def generarPdf(listaMovimientos):
    buffer = BytesIO()
    doc = canvas.Canvas(buffer, pagesize=landscape(letter))

    for idx, movimiento in enumerate(listaMovimientos):
        if idx > 0:
            doc.showPage()  # Nueva página para cada cliente después del primero

        # Encabezado
        doc.setFont("Helvetica-Bold", 16)
        doc.drawCentredString(400, 750, "Estado de Cuenta")

        y_position = 500  # Posición inicial más abajo

        # Datos del cliente
        doc.setFont("Helvetica-Bold", 12)
        doc.drawString(50, y_position, f"Cliente: {movimiento['cliente']}")
        doc.drawString(50, y_position - 20, f"NIT: {movimiento['nit']}")
        doc.drawString(50, y_position - 40, f"Saldo: Q{movimiento['saldo']}")

        y_position -= 70

        # Movimientos
        movimientos_data = [['Tipo', 'Fecha', 'Valor', 'Detalles']]
        for m in movimiento['movimientos']:
            tipo = m['tipo']
            fecha = m['fecha']
            valor = f"Q{m['valor']}"
            detalles = ""

            if tipo == 'debito':
                detalles = f"Núm. Factura: {m['num_factura']}"
            elif tipo == 'credito':
                detalles = f"Código Banco: {m['codigo_banco']}, Banco: {m['banco']}"

            movimientos_data.append([tipo, fecha, valor, detalles])

        table = Table(movimientos_data, colWidths=[80, 80, 80, 300])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table.wrapOn(doc, 800, 600)
        table.drawOn(doc, 50, y_position - table._height - 20)  # Ajuste de posición de la tabla
        y_position -= table._height + 120  # Ajuste de posición vertical

    doc.save()

    # Obtener el contenido del buffer como bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()

    ruta_archivo = os.path.join('Salidas', 'estado_cuenta.pdf')  # Ruta de salida del archivo
    with open(ruta_archivo, 'wb') as f:
        f.write(pdf_bytes)

    return ruta_archivo

def descargar_pdf(lista_movimientos):

     ruta_archivo = generarPdf(lista_movimientos)
     webbrowser.open_new_tab(ruta_archivo)
     return send_file(ruta_archivo, as_attachment=True)

app.run(debug=True, port=5000)