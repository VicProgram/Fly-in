import sys
import re
from models import Drone_Map, Hub, Connection

class Parser:
    def __init__(self, drone_map: Drone_Map) -> None:
        self.map: Drone_Map = drone_map
        self.nb_drones: int = 0
        self.hub_counter: int = 1
        self.connection_counter: int = 0

    def parse_file(self, map_path: str) -> None:
        try:
            with open(map_path, "r") as file:
                for line_num, line in enumerate(file, 1):
                    clean_line = line.strip()
                    if clean_line and not clean_line.startswith("#"):
                        self.parse_line(clean_line, line_num)
        except FileNotFoundError:
            print(f"Error: El archivo '{map_path}' no existe.", file=sys.stderr)
            sys.exit(1)

    def parse_hub_content(self, content: str) -> tuple[str, int, int, str]:
        color_match = re.search(r"color=(\w+)", content)
        color = color_match.group(1) if color_match else "white"
        
        # Limpia corchetes y extrae las 3 partes principales
        parts = re.sub(r"\[.*?\]", "", content).split()
        if len(parts) != 3:
            raise ValueError(f"Formato de hub inválido: '{content}'")
            
        return parts[0], int(parts[1]), int(parts[2]), color

    def parse_line(self, line: str, line_num: int) -> None:
        try:
            prefix, content = (line.split(":", 1) if ":" in line else ("", ""))
            prefix, content = prefix.strip(), content.strip()

            if prefix == "nb_drones":
                self.nb_drones = int(content)
                if not (0 < self.nb_drones < 500):
                    raise ValueError("Número de drones inválido (debe ser entre 1 y 499)")

            elif prefix in ["hub", "start_hub", "end_hub"]:
                name, x, y, color = self.parse_hub_content(content)
                # Mapeo de prefijo a tipo de hub
                hub_types = {"start_hub": "start", "end_hub": "end", "hub": "normal"}
                
                if prefix == "hub":
                    self.hub_counter += 1
                    
                self.map.add_hub(Hub(name, x, y, color, hub_types[prefix]))

            elif prefix == "connection":
                content_clean = re.sub(r"\[.*?\]", "", content)
                if "-" not in content_clean:
                    raise ValueError("Conexión malformada (falta '-')")

                h1, h2 = [z.strip() for z in content_clean.split("-", 1)]
                hub_1, hub_2 = self.map.hubs.get(h1), self.map.hubs.get(h2)
                
                if not hub_1 or not hub_2:
                    raise ValueError(f"Zonas no encontradas: '{h1}' o '{h2}'")

                self.connection_counter += 1
                self.map.add_connection(Connection(f"Conn{self.connection_counter}", hub_1, hub_2))

            else:
                raise ValueError(f"Comando o sintaxis desconocida")

        except ValueError as e:
            print(f"Error en línea {line_num}: {e}", file=sys.stderr)
            sys.exit(1)

    def print_avances(self) -> None:
        print(f"Mapa cargado. Drones: {self.nb_drones} | Hubs: {self.hub_counter} | Conexiones: {self.connection_counter}")