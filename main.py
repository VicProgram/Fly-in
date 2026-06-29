import sys
from .models import Drone_Map, Hub, Connection



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
            print(f"Error: El archivo '{file_path}' no existe.", file=sys.stderr)
            sys.exit(1)

    def parse_line(self, line:str, line_num:int) -> None:

        if line.startswith("nb__drones:"):
            self.nb_drones = int(line.split(":")[1].strip())

        elif(
            line.startswith("hub:") or line.startswith("start_hub:") \
            or line.startswith("end_hub:")
            ):

            # TODO: Extraer coordenadas, nombre y metadatos de los corchetes
            # nuevo_hub = Hub(name, x, y, zo_type)
            # self.map.add_hub(nuevo_hub)
            pass

        elif line.startswith("connection:"):
            # Separar las dos zonas (ej: hub1-hub2) y buscar los objetos Hub en self.map.hubs
            # nueva_conex = Connection(zone1, zone2, capacity)
            # self.map.add_connection(nueva_conex)
            pass

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