from typing import Dict, List, Optional


class Hub:
    def __init__(
            self, name:str, x:int, y:int, zo_type:str = "normal", color:str = "white"
            ) -> None:
        
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zo_type: str = zo_type
        self.color: str = color


class Connection:
    def __init__(
            self, name:str, zone1:Hub, zone2:Hub, capacity:int = 1
            ) -> None:

        self.name: str = name
        self.zone1: Hub = zone1
        self.zone2: Hub = zone2
        self.capacity: int = capacity


class Drone_Map:
    def __init__(self) -> None:

        self.hubs:Dict[str, Hub] = {}
        self.connections:list[Connection] = []
    
    def add_hub(self, hub:Hub) -> None:

        if hub.name not in self.hubs:
            self.hubs[hub.name] = hub
        else:
            raise ValueError(f"Error: El Hub con nombre '{hub.name}' ya existe.")

    def add_connection(self, connection:Connection) -> None:

        if connection not in self.connections:
            self.connections.append(connection)
        else:
            raise ValueError(f"Error: La conexion '{connection.name}' ya existe")

