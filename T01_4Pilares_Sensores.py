from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from statistics import mean
from typing import Protocol, List
from datetime import datetime

class Notificador(Protocol):
    def enviar(self, mensaje: str) -> None: ...
class NotificadorEmail:
    def __init__(self, destinatario: str) -> None:
        self._destinatario = destinatario # encapsulado
    def enviar(self, mensaje: str) -> None:
        print(f"[EMAIL a {self._destinatario}] {mensaje}")
class NotificadorWebhook:
    def __init__(self, url: str) -> None:
        self._url = url
    def enviar(self, mensaje: str) -> None:
        print(f"[WEBHOOK {self._url}] {mensaje}")
@dataclass
class Sensor(ABC):
    id: str
    ventana: int = 5
    _calibracion: float = field(default=0.0, repr=False) # encapsulado
    _buffer: list[float] = field(default_factory=list, repr=False)

    def leer(self, valor: float) -> None:
        """Agrega lectura aplicando calibración y mantiene ventana móvil."""
        v = valor + self._calibracion
        self._buffer.append(v)
        if len(self._buffer) > self.ventana:
            self._buffer.pop(0)
    @property
    def promedio(self) -> float:
        return mean(self._buffer) if self._buffer else 0.0
    @abstractmethod
    def en_alerta(self) -> bool: ...
@dataclass
class SensorTemperatura(Sensor):
    umbral: float = 80.0
    def en_alerta(self) -> bool:
    # Polimorfismo: cada sensor define su propia condición
        return self.promedio >= self.umbral
@dataclass
class SensorVibracion(Sensor):
    rms_umbral: float = 2.5
    def en_alerta(self) -> bool:
    # Ejemplo tonto de RMS ~ promedio absoluto
        return abs(self.promedio) >= self.rms_umbral
class GestorAlertas:
    def __init__(self, sensores: List[Sensor], notificadores: List[Notificador]) -> None:
        self._sensores = sensores
        self._notificadores = notificadores
    def evaluar_y_notificar(self) -> None:
        for s in self._sensores:
            if s.en_alerta():
                msg = f"ALERTA: Sensor {s.id} en umbral (avg={s.promedio:.2f})"
                for n in self._notificadores:
                    n.enviar(msg)

#  nuevos elementos orientados al monitoreo de desastres 

@dataclass
class SensorSismo(Sensor):
    magnitud_umbral: float = 5.0

    def en_alerta(self) -> bool:
        return self.promedio >= self.magnitud_umbral

@dataclass
class SensorVolcan(Sensor):
    temperatura_umbral: float = 900.0 
    gas_umbral: float = 50.0 

    def en_alerta(self) -> bool:
        # alerta si promedio supera cualquiera de los umbrales
        return self.promedio >= self.temperatura_umbral or self.promedio >= self.gas_umbral

# Panel de monitoreo para desastres
@dataclass
class PanelEmergencias:
    gestor: GestorAlertas 
    notificador: Notificador  
    indicadores: list[Sensor] = field(default_factory=list)

    def actualizar_panel(self) -> None:
        for s in self.indicadores:
            estado = "ALERTA" if s.en_alerta() else "NORMAL"
            print(f"[PANEL] Sensor {s.id}: {estado} (avg={s.promedio:.2f})")
            if s.en_alerta():
                self.notificador.enviar(f"ALERTA: {s.id} en estado {estado}")

class NotificadorSMS:
    def __init__(self, telefono: str) -> None:
        self._telefono = telefono

    def enviar(self, mensaje: str) -> None:
        print(f"[SMS a {self._telefono}] {mensaje}")


@dataclass
class RegistroEvento:
    sensor: Sensor  
    mensaje: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class HistorialEventos:
    registros: list[RegistroEvento] = field(default_factory=list) 

    def agregar_evento(self, sensor: Sensor, mensaje: str) -> None:
        self.registros.append(RegistroEvento(sensor=sensor, mensaje=mensaje))




def probar_sistema():
    print("Elige un tipo de sensor:")
    print("1 - Temperatura")
    print("2 - Vibración")
    print("3 - Sismo")
    print("4 - Volcán")
    opcion = input("Ingresa el número de tu opción: ").strip()
    
    sensor_id = input("ID del sensor: ")
    
    if opcion == "1":
        umbral = float(input("Umbral de temperatura: "))
        sensor = SensorTemperatura(id=sensor_id, umbral=umbral)
    elif opcion == "2":
        umbral = float(input("Umbral RMS: "))
        sensor = SensorVibracion(id=sensor_id, rms_umbral=umbral)
    elif opcion == "3":
        umbral = float(input("Umbral de magnitud sismo: "))
        sensor = SensorSismo(id=sensor_id, magnitud_umbral=umbral)
    elif opcion == "4":
        temp_umbral = float(input("Umbral de temperatura volcán: "))
        gas_umbral = float(input("Umbral de gas volcán: "))
        sensor = SensorVolcan(id=sensor_id, temperatura_umbral=temp_umbral, gas_umbral=gas_umbral)
    else:
        print("Opción inválida, usando SensorTemperatura por defecto.")
        sensor = SensorTemperatura(id=sensor_id)

    print("Elige tipo de notificador:")
    print("1 - Email")
    print("2 - Webhook")
    print("3 - SMS")
    opcion_notif = input("Ingresa número: ").strip()
    if opcion_notif == "1":
        destino = input("Correo destinatario: ")
        notificador = NotificadorEmail(destino)
    elif opcion_notif == "2":
        url = input("URL webhook: ")
        notificador = NotificadorWebhook(url)
    elif opcion_notif == "3":
        tel = input("Número de teléfono: ")
        notificador = NotificadorSMS(tel)
    else:
        print("Opción inválida, usando Email por defecto.")
        notificador = NotificadorEmail("default@email.com")
    
    gestor = GestorAlertas(sensores=[sensor], notificadores=[notificador])
    panel = PanelEmergencias(gestor=gestor, indicadores=[sensor], notificador=notificador)

    seguir = True
    while seguir:
        valor = float(input(f"Ingrese valor de lectura para sensor {sensor.id}: "))
        sensor.leer(valor)
        print(f"Promedio actual: {sensor.promedio:.2f}")
        
        gestor.evaluar_y_notificar()
        panel.actualizar_panel()
        
        continuar = input("Ingresar otra lectura? (Y/N): ").strip().upper()
        seguir = continuar == "Y"

# Ejecutar prueba
if __name__ == "__main__":
    seguir_prueba = True
    while seguir_prueba:
        probar_sistema()
        continuar = input("Probar otro sensor? (Y/N): ").strip().upper()
        seguir_prueba = continuar == "Y"
