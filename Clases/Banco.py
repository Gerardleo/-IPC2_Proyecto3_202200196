class Banco:
    def __init__(self,codigo,nombre):
        self.codigo = codigo
        self.nombre = nombre
        self.Clientes = []

    def getCodigo(self):
        return self.codigo
    
    def getNombre(self):
        return self.nombre
    
    def setCodigo(self, codigo):
        self.codigo = codigo

    def setNombre(self, nombre):
        self.nombre = nombre

        