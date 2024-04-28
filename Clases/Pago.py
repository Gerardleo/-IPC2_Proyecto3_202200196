class Pago:
    def __init__(self, codigoBanco, fecha, nit, valor):
        self.codigoBanco = codigoBanco
        self.fecha = fecha
        self.nit = nit
        self.valor = valor

    def getCodigoBanco(self):
        return self.codigoBanco

    def getFecha(self):
        return self.fecha
    
    def getNit(self):
        return self.nit
    
    def getValor(self):
        return self.valor
    
    def setCodigoBanco(self, codigoBanco):
        self.codigoBanco = codigoBanco

    def setFecha(self, fecha):
        self.fecha = fecha

    def setNit(self, nit):
        self.nit = nit

    def setValor(self, valor):
        self.valor = valor
        
        