import sys
from typing import Dict, List, Optional


class Valid_List:

    valid_hubs = {
        "hub:",
        "start_hub:",
        "end_hub:"
    }

    valid_zones = {
        "normal",
        "blocked",
        "restricted",
        "priority"
        }

    valid_colors = {
        "green": "\033[32m",
        "yellow": "\033[33m",
        "red": "\033[31m",
        "blue": "\033[34m",
        "cyan": "\033[36m",
        "magenta": "\033[35m",
        "white": "\033[37m",
        "purple": "\033[35;1m",
        "orange": "\033[38;5;208m",
        "brown": "\033[38;5;130m",
        "maroon": "\033[38;5;88m",
        "black": "\033[90m",
        "gold": "\033[33;1m",
        "violet": "\033[35;1m",
        "crimson": "\033[31;1m",
        "darkred": "\033[31m",
        "rainbow": "\033[36;1m",
        "lime": "\033[38;5;118m",
        "gray": "\033[38;5;244m",
        "marron": "\033[38;5;88m",
        "darked": "\033[38;5;52m"
    }


    @classmethod
    def check_zone(cls, zone: str) -> None:
        if zone not in cls.valid_zones:
            raise ValueError(f"Zona no válida: '{zone}'")
        

class Hub:
    def __init__(
            self, name: str, x: int, y: int, zo_type: str = "normal",
            color: str = "none", hub_type: str = "normal",
            max_drones: int = 1) -> None:

        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zo_type: str = zo_type
        self.color: str = color
        self.hub_type: str = hub_type
        self.max_drones: int = max_drones


class Connection:
    def __init__(
            self, name:str, zone1:Hub, zone2:Hub, capacity:int = 1
            ) -> None:

        self.name: str = name
        self.zone1: Hub = zone1
        self.zone2: Hub = zone2
        self.capacity: int = capacity

    def _key(self) -> frozenset:
        # a-b y b-a son la misma conexion
        return frozenset({self.zone1.name, self.zone2.name})
 
    def __eq__(self, other: object) -> bool:
        
        if not isinstance(other, Connection):
            return NotImplemented
        
        return self._key() == other._key()
 
    def __hash__(self) -> int:
        return hash(self._key())


class Drone_Map:
    def __init__(self) -> None:

        self.hubs:Dict[str, Hub] = {}
        self.connections:list[Connection] = []
        self.start_hub: Optional[Hub] = None
        self.end_hub: Optional[Hub] = None
        self.used_coords: set = set()
    
    # ahora controla start y end
    def add_hub(self, hub: Hub) -> None:

        if hub.name in self.hubs:
            raise ValueError(f"Error: El Hub con nombre '{hub.name}' ya existe.")

        if (hub.x, hub.y) in self.used_coords:
            raise ValueError(f"Error: ya existe un hub en la coordenada ({hub.x}, {hub.y}).")

        if hub.hub_type == "start" and self.start_hub is not None:
            raise ValueError("Error: ya existe un start_hub.")

        if hub.hub_type == "end" and self.end_hub is not None:
            raise ValueError("Error: ya existe un end_hub.")

        self.hubs[hub.name] = hub
        self.used_coords.add((hub.x, hub.y))

        if hub.hub_type == "start":
            self.start_hub = hub

        elif hub.hub_type == "end":
            self.end_hub = hub


    def add_connection(self, connection:Connection) -> None:

        if connection not in self.connections:
            self.connections.append(connection)
        else:
            raise ValueError(f"Error: La conexion '{connection.name}' ya existe")



class Drone:
    def __init__(self, id_drone: int, curr_loc: Hub) -> None:
        self.id: int = id_drone
        self.location: Hub | Connection = curr_loc
        self.in_transit: bool = False
        self.turn: int = 0
        self.has_arrived: bool = False

    def get_drone_info(self) -> None:

        print(f"Drone_id: {self.id}")
        print(f"Drone location: {self.id}")
        print(f"In transit: {self.id}")
        print(f"Turn number: {self.id}")
        print(f"Has arrived?: {self.id}")


class Solver:
    def __init__(self, drone_map: Drone_Map, drones_number: int) -> None:
        self.drone_map: Drone_Map = drone_map
        self.curr_turn: int = 0
        self.history: list = []

        self.drones: list[Drone] = [
            Drone(
                f"D{i}", self.drone_map.start_hub) for i in range(1, drones_number + 1)
        ]


    def get_drones_in_hub(self, hub: Hub) -> int:
        return sum(1 for d in self.drones if d.location == hub)
    
    def get_drones_in_con(self, conn: Connection) -> str:
        return sum(1 for d in self.drones if d.location == conn)
    
    def can_move_hub(self, hub: Hub) -> bool:
        return self.get_drones_in_hub(hub) < hub.max_drones
    
    def can_move_conn(self, conn: Connection) -> bool:
        return self.get_drones_in_con(conn) < conn.capacity