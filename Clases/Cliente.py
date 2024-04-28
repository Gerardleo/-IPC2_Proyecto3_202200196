class Cliente:
    def __init__(self, nombre, nit):
        self.nombre = nombre
        self.nit = nit
        self.saldo = 0

    def getNombre(self):
        return self.nombre
    
    def getNit(self):
        return self.nit
    
    def setNombre(self, nombre):
        self.nombre = nombre

    def setNit(self, nit):
        self.nit = nit