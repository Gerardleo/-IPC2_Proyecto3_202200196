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
