class Factura:
    def __init__(self,numFactura,nit,fecha,valor):
        self.numFactura = numFactura
        self.fecha = fecha
        self.nit = nit
        self.valor = valor

    def getNumFactura(self):
        return self.numFactura
    
    def getFecha(self):
        return self.fecha
    
    def getNit(self):
        return self.nit
    
    def getValor(self):
        return self.valor
    
    def setNumFactura(self, numFactura):
        self.numFactura = numFactura

    def setFecha(self, fecha):
        self.fecha = fecha

    def setNit(self, nit):
        self.nit = nit

    def setValor(self, valor):
        self.valor = valor

        
         