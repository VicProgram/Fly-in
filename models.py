from typing import Dict, List, Optional


class Hub:
    def __init__(
            self, name:str, x:int, y:int, zo_type:str = "normal"
            ) -> None:
        
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zo_type: str = zo_type


class Connection:
    def __init__(
            self, name:str, zone1:Hub, zone2:Hub, capacity:int = 1
            ) -> None:

        self.name: str = name
        self.zone1: Hub = Hub
        self.zone2: Hub = Hub
        self.capacity: int = capacity


class Drone_Map:
    def __init__(self) -> None:

        self.hubs:Dict[str, Hub] = {}
        self.connections:list[Connection] = []
    
    def add_hub(self, hub:Hub) -> None:
        new_hub = Hub()

        if new_hub.name not in self.hubs:
            self.hubs[new_hub.name] = hub
        else:
            raise ValueError(f"Error: El Hub con nombre '{hub.name}' ya existe.")

    def add_conection(self, connection:Connection) -> None:
        new_conex = Connection()

        if new_conex not in self.conections:
            connection.add(new_conex)
        else:
            raise ValueError(f"Error: La conexion '{connection}' ya existe")

