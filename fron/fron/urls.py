import fron.view as view

"""
URL configuration for fron project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('', view.inicio, name='inicio'),
    path('Configuraccion', view.archivoConfig, name='Configuraccion'),
    path('transacciones', view.transacciones, name='transacciones'),
    path('borrarDatos', view.borrarDatos, name='borrarDatos'),
    path('cargaArchivoTranscciones', view.cargaArchivoTranscciones, name='cargaArchivoTranscciones'),
    path('cargarArchivoConfig', view.cargarArchivoConfig, name='cargarArchivoConfig'),
    path('EliminarDatos', view.eliminarDatos, name='EliminarDatos'),
    path('estado_cuenta', view.estado_cuenta, name='estado_cuenta'),
    path('obtenerEstadoCuenta', view.obtenerEstadoCuenta, name='obtenerEstadoCuenta'),
    path('resumenBancos', view.resumenBancos, name='resumenBancos'),
    path('obtenerResumenBancos', view.obtenerResumenBancos, name='obtenerResumenBancos'),
]
