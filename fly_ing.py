import sys
import re
from models import Drone_Map, Hub, Connection, CosasValidas


class Parser:
    def __init__(self, drone_map: Drone_Map) -> None:
        self.map: Drone_Map = drone_map
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


    def parse_hub_content(self, content: str) -> tuple[str, int, int, str, str, int]:

        match_color = re.search(r"color=(\w+)", content)
        color = match_color.group(1) if match_color else "white"
        CosasValidas.check_color(color)

        match_zone = re.search(r"zone=(\w+)", content)
        zo_type = match_zone.group(1).lower().strip() if match_zone else "normal"
        CosasValidas.check_zone(zo_type)

        match_max_drone_nb = re.search(r"max_drones=(\d+)", content)
        max_drones = int(match_max_drone_nb.group(1)) if match_max_drone_nb else 1


        main_part = re.sub(r"\[.*?\]", "", content).strip()
        parts = main_part.split()
        

        if len(parts) != 3:
            raise ValueError(f"Formato de hub inválido: '{content}'")

        name, x_str, y_str = parts
        return name, int(x_str), int(y_str), zo_type, color, int(max_drones)


    def parse_line(self, line: str, line_num: int) -> None:

        if line.startswith("nb_drones:"):
            try:
                self.nb_drones = int(line.split(":")[1].strip())
                if self.nb_drones <= 0 or self.nb_drones >= 500:
                    raise ValueError("Número de drones inválido")

            except ValueError as e:
                print(f"Error en línea {line_num}: {e}", file=sys.stderr)
                sys.exit(1)

            except IndexError:
                print(f"Error en línea {line_num}: falta ':' en 'nb_drones'.", file=sys.stderr)
                sys.exit(1)

        elif any(line.startswith(p) for p in ["hub:", "start_hub:", "end_hub:"]):
            prefix, content = line.split(":", 1)
            content = content.strip()

            try:
                name, x, y, zo_type, color, max_drones = self.parse_hub_content(content)
                
                match prefix:
                    case "start_hub":
                        nuevo_hub = Hub(name, x, y, zo_type, color, "start", max_drones)

                    case "end_hub":
                        nuevo_hub = Hub(name, x, y, zo_type, color, "end", max_drones)

                    case "hub":
                        nuevo_hub = Hub(name, x, y, zo_type, color, "normal", max_drones)
                        self.hub_counter += 1

                    case _:
                        print(
                            f"Error de sintaxis en línea {line_num}: "
                            "prefijo de hub desconocido.", file=sys.stderr
                            )
                        sys.exit(1)

                self.map.add_hub(nuevo_hub)

            except ValueError as e:
                print(f"Error en línea {line_num}: {e}", file=sys.stderr)
                sys.exit(1)

        elif line.startswith("connection:"):
            _, content = line.split(":", 1)

            match_capacity = re.search(r"max_link_capacity=(\d+)", content)
            capacity = int(match_capacity.group(1)) if match_capacity else 1

            content_clean = re.sub(r"\[.*?\]", "", content).strip()

            if "-" not in content_clean:
                print(f"Error de sintaxis en línea {line_num}: Conexión malformada.", file=sys.stderr)
                sys.exit(1)

            zone_1, zone_2 = content_clean.split("-", 1)
            zone_1 = zone_1.strip()
            zone_2 = zone_2.strip()


            first_hub = self.map.hubs.get(zone_1)
            second_hub = self.map.hubs.get(zone_2)

            if not first_hub or not second_hub:
                print(
                    f"Error en línea {line_num}: zona no encontrada "
                    f"en la conexión ('{zone_1}' o '{zone_2}').", file=sys.stderr
                    )
                sys.exit(1)

            self.connection_counter += 1
            new_connection = Connection(
                f"Conn{self.connection_counter}", first_hub, second_hub, capacity
                )
            self.map.add_connection(new_connection)

        else:
            print(
                f"Error de sintaxis en línea {line_num}: "
                "Comando desconocido.", file=sys.stderr
                )
            sys.exit(1)

    # PRUEBAS
    def print_avances(self) -> None:

        print(f"Mapa cargado exitosamente. Drones totales: {self.nb_drones}")
        print(f"Mapa cargado exitosamente. Hubs totales: {self.hub_counter}")
        print(f"Mapa cargado exitosamente. Conexiones totales: {self.connection_counter}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python3 -m tu_modulo mapa.txt", file=sys.stderr)
        sys.exit(1)

    drone_map = Drone_Map()
    parser = Parser(drone_map)
    parser.parse_file(sys.argv[1])

    # PRUEBAS
    parser.print_avances()


if __name__ == "__main__":
    main()


''' 
   TODO

    zone=<tipo> nunca se extrae. Sólo se saca color con regex; el resto del contenido se descarta con re.sub(r"\[.*?\]", "", content).
    Como consecuencia, normal/blocked/restricted/priority no se guardan en ningún lado, y eso es central para el coste de movimiento y las zonas bloqueadas.
    Bug: en el caso "hub:" llamas Hub(name, x, y, color) — pero el 4º parámetro posicional de Hub.__init__ es zo_type, no color.
    Estás metiendo el color en el slot de tipo de zona, y el color real nunca se asigna (siempre queda "white" por defecto).
    max_drones=<n> (capacidad de zona) no se parsea ni se guarda en Hub.
    max_link_capacity=<n> (capacidad de conexión) no se parsea; Connection.capacity queda siempre en 1.

    Validaciones del parser que exige el enunciado y no están

    No se valida que nb_drones sea un entero positivo (ni que exista/sea la primera línea); si el valor no es numérico, int() lanza una excepción no controlada → crash.
    No se verifica que haya exactamente un start_hub y un end_hub (el subject lo exige explícitamente).
    No se valida que los nombres de zona no contengan espacios ni guiones ("-" está reservado para conexiones).
    No se valida el tipo de zona (zone= debe ser uno de normal|blocked|restricted|priority; cualquier otro valor debe lanzar error de parseo). Como ni se parsea, tampoco se valida.
    No se valida que los valores de capacidad (max_drones, max_link_capacity) sean enteros positivos.
    Duplicados de conexión no se detectan de verdad: Drone_Map.add_connection hace if connection not in self.connections,
    pero Connection no define __eq__, así que la comparación siempre es por identidad de objeto → nunca detecta que a-b y b-a (o a-b repetido) sean duplicados, aunque el subject lo exige explícitamente.

    Manejo de errores general

    Sólo se capturan FileNotFoundError y ValueError; cualquier otra excepción (p. ej. int() fallando en nb_drones, o un IndexError si la línea no tiene :)
    no se controla y el programa crashea sin mensaje claro — el enunciado pide manejo elegante de excepciones (III.1) siempre.

    -OK-No puede haber dos coordenadas duplicadas
    No puede haber mas de un start_hub
    No puede haber mas de un end_hub
    No puede haber nombres repetidos

    No puede haber conexiones repetidas, que no significa
    que sea la misma en direccion opuesta
    MIRAR BIEN EL __eq__ y el __hash__ a lo mejor no se necesita
    LAS CONEXIONES SON BIDIRECCIONALES!!

    Puede no estar la info de colores por ejemplo

    longitud de metadatos de hubs tiene que ser 3 
    longitud de metadatos de conexiones tiene que ser 1

    SI ESO COMPROBAR EL NOMBRE DE LOS COLORES, QUE ESTÉ BIEN:
    Greeeen NO DEBERIA FUNCIONAR
    LANZAR ERROR


    Comprobar si estamos cogiendo bien el numero de drones
    y que todo siempre en minuscula

    '''