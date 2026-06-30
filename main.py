import sys
import re
from models import Drone_Map, Hub, Connection


class   Parser:
    def __init__(self, drone_map: Drone_Map) -> None:
        self.map:Drone_Map = drone_map
        self.nb_drones: int = 0
        self.hub_counter = 1
        self.connection_counter: int = 0

    def parse_file(self, map_path: str) -> None:
        try:
            with open(map_path, "r") as file:
                for line_num, line, in enumerate(file, 1):
                    clean_line = line.strip()

                    if not clean_line or clean_line.startswith("#"):
                        continue

                    self.parse_line(clean_line, line_num)

        except FileNotFoundError:
            print(
                f"Error: El archivo '{map_path}' no existe.", file=sys.stderr
                )
            sys.exit(1)


def parse_hub_content(self, content: str) -> tuple[str, int, int, str]:
    
        match_color = re.search(r"\[color=(\w+)\]", content)
        color = match_color.group(1) if match_color else "white"

        # quita el bloque [color=...] para quedarte solo con "nombre x y"
        main_part = re.sub(r"\[.*?\]", "", content).strip()
        parts = main_part.split()

        if len(parts) != 3:
            raise ValueError(f"Formato de hub inválido: '{content}'")

        name, x_str, y_str = parts
        return name, int(x_str), int(y_str), color


def parse_line(self, line: str, line_num: int) -> None:
    if line.startswith("nb_drones:"):
        self.nb_drones = int(line.split(":")[1].strip())

    elif any(line.startswith(p) for p in ["hub:", "start_hub:", "end_hub:"]):
        
        prefix, content = line.split(":", 1)
        content = content.strip()

        match prefix:
            case "start_hub":
                nuevo_hub = Hub("Start_Hub", 0, 0, "start")

            case "end_hub":
                nuevo_hub = Hub("End_Hub", 0, 0, "end")

            case "hub":
                nuevo_hub = Hub(f"Hub{self.hub_counter}", 0, 0, "end")
                self.hub_counter += 1

            case _:
                print(f"Error de sintaxis en línea {line_num}: prefijo de hub desconocido.", file=sys.stderr)
                sys.exit(1)
        
        try:
            self.map.add_hub(nuevo_hub)

        except ValueError as e:
            print(f"Error en línea {line_num}: {e}", file=sys.stderr)
            sys.exit(1)

    elif line.startswith("connection:"):
        
        _, content = line.split(":", 1)
        zone_1, zone_2 = content.split("-", 1)
        zone_1 = zone_1.strip()
        zone_2 = zone_2.strip()

        first_hub = self.map.hubs.get(zone_1)
        second_hub = self.map.hubs.get(zone_2)

        if not first_hub or not second_hub:
            print(f"Error en línea {line_num}: zona no encontrada en la conexión.", file=sys.stderr)
            sys.exit(1)

        self.connection_counter += 1
        new_connection = Connection(f"Conn{self.connection_counter}", first_hub, second_hub)
        self.map.add_connection(new_connection)
        

    else:
        print(f"Error de sintaxis en línea {line_num}: Comando desconocido.", file=sys.stderr)
        sys.exit(1)


def main() -> None:


    if len(sys.argv) < 2:
        print("Uso: python3 -m tu_modulo mapa.txt", file=sys.stderr)
        sys.exit(1)

    drone_map = Drone_Map()
    parser = Parser(drone_map)
    parser.parse_file(sys.argv[1])
    print(f"Mapa cargado exitosamente. Drones totales: {parser.nb_drones}")


if  __name__ == "__main__":
    main()
