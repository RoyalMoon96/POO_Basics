from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


#Enums
class Periodicidad(Enum):
    MENSUAL = "MENSUAL"
    ANUAL = "ANUAL"


class Moneda(Enum):
    MXN = "MXN"
    USD = "USD"
    EUR = "EUR"

#Clases
@dataclass(frozen=True)
class Usuario:
    id: str
    nombre: str

@dataclass(frozen=True)
class Plan:
    id: str
    nombre: str
    precio_mxn: float
    periodicidad: Periodicidad

@dataclass
class Suscripcion:
    id: str
    usuario: Usuario
    plan: Plan
    activa: bool = False

    def activar(self) -> None:
        if self.activa:
            print("La suscripción ya está activa")
        self.activa = True

    def cancelar(self) -> None:
        if not self.activa:
            print("La suscripción ya está cancelada")
        self.activa = False

@dataclass(frozen=True)
class Money:
    monto: float
    moneda: Moneda

    def convertir(self, moneda: Moneda) -> "Money":
        if moneda == self.moneda:
            return self
        print("Conversión entre monedas invalida")

#clase abstracta
class MetodoPago(ABC):
    def __init__(self, id: str, tipo: str):
        self.id = id
        self.tipo = tipo

    @abstractmethod
    def pagar(self, monto: Money) -> bool:
        pass

class Tarjeta(MetodoPago):
    def __init__(self, id: str, numero: str, titular: str, vencimiento: str):
        super().__init__(id, "TARJETA")
        self.numero = numero
        self.titular = titular
        self.vencimiento = vencimiento

    def pagar(self, monto: Money) -> bool:
        print(f"Pagando con tarjeta {self.numero} a nombre de {self.titular}")
        return True

class Transferencia(MetodoPago):
    def __init__(self, id: str, clabe: str):
        super().__init__(id, "TRANSFERENCIA")
        self.clabe = clabe

    def pagar(self, monto: Money) -> bool:
        print(f"Pagando con transferencia a CLABE {self.clabe}")
        return True

class Paypal(MetodoPago):
    def __init__(self, id: str, email: str):
        super().__init__(id, "PAYPAL")
        self.email = email

    def pagar(self, monto: Money) -> bool:
        print(f"Pagando con PayPal {self.email}")
        return True

class ApplePay(MetodoPago):
    def __init__(self, id: str, cuentaApple: str):
        super().__init__(id, "APPLEPAY")
        self.cuentaApple = cuentaApple

    def pagar(self, monto: Money) -> bool:
        print(f"Pagando con ApplePay {self.cuentaApple}")
        return True

@dataclass
class Factura:
    id: str
    suscripcion: Suscripcion
    metodoPago: MetodoPago
    total: Money

    def pagar(self) -> None:
        if not self.metodoPago.pagar(self.total):
            print("Error en el pago de la factura")
        elif not self.suscripcion.activa:
            print("Error al pagar: suscripcion desactivada")
        else :
            print("Factura pagada correctamente")

#Clase abstracta
class PoliticaPrecio(ABC):
    def __init__(self, id: str, nombre: str):
        self.id = id
        self.nombre = nombre

    @abstractmethod
    def aplicar(self, monto: Money) -> Money:
        pass

class PrecioFull(PoliticaPrecio):
    def aplicar(self, monto: Money) -> Money:
        return monto

class CuponPorcentaje(PoliticaPrecio):
    def __init__(self, id: str, nombre: str, porcentaje: float):
        super().__init__(id, nombre)
        self.porcentaje = porcentaje

    def aplicar(self, monto: Money) -> Money:
        descuento = monto.monto * (self.porcentaje / 100)
        return Money(monto.monto - descuento, monto.moneda)

class CuponMonto(PoliticaPrecio):
    def __init__(self, id: str, nombre: str, descuento: float):
        super().__init__(id, nombre)
        self.descuento = descuento

    def aplicar(self, monto: Money) -> Money:
        return Money(max(monto.monto - self.descuento, 0), monto.moneda)

#Clase abstracta
class CalculadoraImpuestos(ABC):
    @abstractmethod
    def aplicar(self, precio: Money) -> Money:
        pass

class ImpuestosMX(CalculadoraImpuestos):
    def __init__(self, tasaIVA: float = 0.16, tasaISR: float = 0.30):
        self.tasaIVA = tasaIVA
        self.tasaISR = tasaISR

    def aplicar(self, precio: Money) -> Money:
        impuestos = precio.monto * self.tasaIVA
        return Money(precio.monto + impuestos, precio.moneda)

class ImpuestosUS(CalculadoraImpuestos):
    def __init__(self, tasaFederal: float = 0.10, tasaEstatal: float = 0.08):
        self.tasaFederal = tasaFederal
        self.tasaEstatal = tasaEstatal

    def aplicar(self, precio: Money) -> Money:
        impuestos = precio.monto * (self.tasaFederal + self.tasaEstatal)
        return Money(precio.monto + impuestos, precio.moneda)

@dataclass
class ServicioCobro:
    politica: PoliticaPrecio
    calcImpuestos: CalculadoraImpuestos

    def calcularTotal(self, subtotal: Money) -> Money:
        con_descuento = self.politica.aplicar(subtotal)
        con_impuestos = self.calcImpuestos.aplicar(con_descuento)
        return con_impuestos


def probar_clases():
    # probar crear usuario y plan
    inputNombre = input("Ingresa tu nombre de usuario: ")
    userID=1
    usuario = Usuario(id=userID, nombre=inputNombre)
    plan = Plan(id=userID, nombre="Plan Prueba", precio_mxn=1000.0, periodicidad=Periodicidad.MENSUAL)
    print(f"{usuario.id}: {usuario.nombre}")
    print(f"Plan: {plan.nombre} ${plan.precio_mxn}")

    # probar crear suscripción 
    suscripcionID=1
    suscripcion = Suscripcion(id=suscripcionID, usuario=usuario, plan=plan)
    Activar = input("Activar suscripcion? (Y/N): ")
    tempFlag = Activar.strip().upper()[0]=="Y"
    while tempFlag:
        suscripcion.activar()
        print(f"Suscripción activa: {suscripcion.activa}")
        Activar = input("Volver a activar suscripcion? (Y/N): ")
        tempFlag = Activar.strip().upper()[0]=="Y"

    #probar crear Money con precio del plan 
    subtotal = Money(monto=plan.precio_mxn, moneda=Moneda.MXN)
    print(f"Precio base: {subtotal.monto} {subtotal.moneda.value}")

    #probar Definir política de precio y calculadora de impuestos 
    cupon = CuponPorcentaje(id="CP001", nombre="Descuento del 10%", porcentaje=10)
    impuestos = ImpuestosMX(tasaIVA=0.16)
    cobro = ServicioCobro(politica=cupon, calcImpuestos=impuestos)
    print(f"Se aplico un cupon: {cobro.politica.nombre}, impuesto aplicado {cobro.calcImpuestos.tasaIVA}")

    #probar calcular total
    total = cobro.calcularTotal(subtotal)
    print(f"Total con cupón e impuestos: {total.monto:.2f} {total.moneda.value}")

    # probar elegir método de pago 
    def elegir_metodo_pago():
        print("Elige un método de pago:")
        print("1 - Tarjeta")
        print("2 - Transferencia")
        print("3 - PayPal")
        print("4 - ApplePay")
        opcion = input("Ingresa el número de tu opción: ")
        match opcion:
            case "1":
                numero = input("Número de tarjeta: ")
                titular = input("Nombre del titular: ")
                vencimiento = input("Fecha de vencimiento: ")
                return Tarjeta(id="MP001", numero=numero, titular=titular, vencimiento=vencimiento)

            case "2":
                clabe = input("CLABE de la cuenta: ")
                return Transferencia(id="MP002", clabe=clabe)

            case "3":
                email = input("Correo PayPal: ")
                return Paypal(id="MP003", email=email)

            case "4":
                cuenta = input("Cuenta ApplePay: ")
                return ApplePay(id="MP004", cuentaApple=cuenta)

            case _:
                print("Opción inválida. Intenta de nuevo.")
                return elegir_metodo_pago()
    metodo=elegir_metodo_pago()
    #probar generar factura
    factura = Factura(id="F001", suscripcion=suscripcion, metodoPago=metodo, total=total)

    #probar pagar factura 
    factura.pagar()

# Ejecutar Prueba
if __name__ == "__main__":
    seguirProbando=True
    while seguirProbando:
        probar_clases()
        Activar = input("Probar de nuevo? (Y/N): ")
        seguirProbando = Activar.strip().upper()[0]=="Y"
