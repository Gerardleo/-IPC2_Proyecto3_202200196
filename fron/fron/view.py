import json
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from requests import post,get
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

url = 'http://localhost:5000/'


def index(request):
    return render(request, 'index.html')

def archivoConfig(request):
    return render(request, 'archivoConfig.html')

def transacciones(request):
    return render(request, 'archivoTransacciones.html')

def borrarDatos(request):
    return render(request, 'borrarDatos.html')

def estado_cuenta(request):
    return render(request, 'EstadosCuenta.html')

def resumenBancos(request):
    return render(request, 'general.html')

def inicio(request):
    return render(request, 'inicio.html')
# def datosPersonales(request):
#     return render(request, 'datosPersonales.html')

# def borrar_Datos(request):
#     return render(request, 'borrarDatos.html')

@csrf_exempt
def cargarArchivoConfig(request):
    global url
    mensaje = None  # Mensaje de respuesta inicialmente vacío

    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        if archivo:
            # Crear una solicitud POST al backend de Flask
            url_flask = url + '/grabarConfiguracion'
            files = {'archivo': archivo}
            response = post(url_flask, files=files)

            if response.status_code == 200:
                mensaje = 'Archivo cargado correctamente'
            else:
                mensaje = 'Error al cargar el archivo'

    return render(request, 'archivoConfig.html', {'mensaje': mensaje})
    
@csrf_exempt  # Agrega csrf_exempt para evitar el token CSRF en esta vista
def cargaArchivoTranscciones(request):
    global url
    mensaje = None

    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        if archivo:
            url_flask = url + '/grabarTransaccion'
            files = {'archivo': archivo}
            response = post(url_flask, files=files)
            if response.status_code == 200:
                print(response.text)
                mensaje = 'Archivo procesado correctamente'
            else:
                mensaje = 'Error al obtener la respuesta de la API Flask'

    # Renderizar la plantilla con el resultado y el botón
    return render(request, 'archivoTransacciones.html', {'mensaje': mensaje})

@csrf_exempt
def eliminarDatos(request):
    global url
    mensaje = None

    if request.method == 'POST':
        url_flask = url + '/limpiarDatos'
        response = post(url_flask)
        if response.status_code == 200:
            mensaje = 'Datos borrados correctamente'
        else:
            mensaje = 'Error al borrar los datos'
    
    return render(request, 'borrarDatos.html', {'mensaje': mensaje})

@csrf_exempt
def obtenerEstadoCuenta(request):
    global url
    if request.method == 'GET':
        nit = request.GET.get('nit')
        url_flask = url + '/devolverEstadoCuenta'
        data = {'nit': nit}  # Los datos deben ir en el parámetro 'data' para una solicitud POST
        response = get(url_flask, data=data)  # Utiliza 'data=data' en lugar de 'nit=nit'
        if response.status_code == 200:
            mensaje = 'Datos obtenidos correctamente'
            datos = response.json()  # Convierte la respuesta a JSON
        else:
            mensaje = 'Error al obtener los datos'
            datos = None
        estado = response.status_code
    else:
        estado = response.status_code
    
    return render(request, 'EstadosCuenta.html', {'json': datos, 'mensaje': mensaje})

@csrf_exempt
def obtenerResumenBancos(request):
    global url
    if request.method == 'GET':
        fecha_str = request.GET.get('fecha')
        # Convertir la fecha de formato '2024-04-30' a '30/04/2024'
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').strftime('%d/%m/%Y')
        url_flask = url + '/resumenBanco'
        data = {'fecha': fecha}  # Los datos deben ir en el parámetro 'data' para una solicitud POST
        response = get(url_flask, data=data)  # Utiliza 'data=data' en lugar de 'nit=nit'
        if response.status_code == 200:
            mensaje = 'Datos obtenidos correctamente'
            datos = response.json()  # Convierte la respuesta a JSON
        else:
            mensaje = 'Error al obtener los datos'
            datos = None
        estado = response.status_code
    else:
        estado = response.status_code
    
    resumen_json = json.dumps(datos)

    
    return render(request, 'general.html', {'json': resumen_json, 'mensaje': mensaje})