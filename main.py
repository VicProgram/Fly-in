import sys
from models import Drone_Map


class  Parser:
    def __init__(self, drone_map:Drone_Map) -> None:
        self.map:Drone_Map = drone_map
        self.nb_drones: int = 0

    def parse_file(self, map_path:str) -> None:
        try:
            with open(map_path, "r") as file:
                for line_num, line, in enumerate(file, 1):
                    clean_line = line.strip()

                    if not clean_line or clean_line.startswith("#"):
                        continue
                    self.parse_line(clean_line, line_num)
        
        except FileNotFoundError:
            print(f"Error: El archivo '{map_path}' no existe.", file=sys.stderr)
            sys.exit(1)

    def parse_line(self, line:str, line_num:int) -> None:

        if line.startswith("nb_drones:"):
            self.nb_drones = int(line.split(":")[1].strip())

        elif any(line.startswith(p) for p in ["hub:", "start_hub:", "end_hub:"]):
            
            prefix, content = line.split(":", 1)
            hub_nb = 1

            match prefix:
                case "start_hub":
                    nuevo_hub = self.map.Hub("Start_Hub", 0, 0, "start")
                    self.map.add_hub(nuevo_hub)

                case "end_hub":
                    nuevo_hub = self.map.Hub("End_Hub", 0, 0, "end")
                    self.map.add_hub(nuevo_hub)

                case "hub":
                    nuevo_hub = self.map.Hub(f"Hub{i}", 0, 0, "end")
                    self.map.add_hub(nuevo_hub)
                    i+=1

        # Separar las dos zonas (ej: hub1-hub2) y buscar los objetos Hub en self.map.hubs
        elif line.startswith("connection:"):
            
            _, content = line.split("-", 1)
            content = content.strip()

            zone_1, zone_2 = line.split("-", 1)
            zone_1 = zone_1.strip()
            zone_2 = zone_2.strip()


            first_hub = next((h for h in self.map.hubs if h.name == zone_1), None)
            second_hub = next((h for h in self.map.hubs if h.name == zone_2), None)

            if first_hub and second_hub:
                new_connection = self.map.connections(first_hub, second_hub)
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
