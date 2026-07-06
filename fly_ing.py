import sys
import re
from models import Drone_Map, Hub, Connection, Valid_List


class Parser:
    def __init__(self, drone_map: Drone_Map) -> None:
        self.map: Drone_Map = drone_map
        self.nb_drones: int = 0
        self.hub_counter = 0
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
        Valid_List.check_color(color)

        match_zone = re.search(r"zone=(\w+)", content)
        zo_type = match_zone.group(1).lower().strip() if match_zone else "normal"
        Valid_List.check_zone(zo_type)

        match_max_drone_nb = re.search(r"max_drones=(\d+)", content)
        max_drones = int(match_max_drone_nb.group(1)) if match_max_drone_nb else 1
        if max_drones <= 0:
            raise ValueError(f"max_drones debe ser positivo: '{max_drones}'")


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
                        self.hub_counter += 1
                    case "end_hub":
                        nuevo_hub = Hub(name, x, y, zo_type, color, "end", max_drones)
                        self.hub_counter += 1
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
            try:
                _, content = line.split(":", 1)

                match_capacity = re.search(r"max_link_capacity=(\d+)", content)
                capacity = int(match_capacity.group(1)) if match_capacity else 1

                if capacity <= 0:
                    raise ValueError(f"max_link_capacity debe ser positivo: '{capacity}'")

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

                if first_hub is second_hub:
                    raise ValueError(
                        f"Una conexión no puede unir un hub consigo mismo: '{zone_1}'"
                    )

                self.connection_counter += 1
                new_connection = Connection(
                    f"Conn{self.connection_counter}", first_hub, second_hub, capacity
                )
                self.map.add_connection(new_connection)

            except ValueError as e:
                print(f"Error en línea {line_num}: {e}", file=sys.stderr)
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
   TODO (Pendientes de implementar)

    Validaciones requeridas al terminar el archivo (Post-parsing)
    ----------------------------------------------------------
    - Verificar la existencia obligatoria de la ruta: El enunciado exige que el mapa tenga 
      exactamente un 'start_hub' y un 'end_hub'. Al finalizar la lectura de todas las líneas, 
      se debe comprobar que 'self.map.start_hub' y 'self.map.end_hub' no sean None.

    Restricciones de caracteres y formato en nombres
    ------------------------------------------------
    - Validar caracteres prohibidos en nombres de Hubs: Los nombres de zona no pueden contener 
      espacios ni guiones ("-"), ya que el guión está explícitamente reservado como separador 
      para las líneas de "connection:". Añadir validación 'if "-" in name:'.

    Robustez y control de formato estricto
    --------------------------------------
    - Validar que 'nb_drones:' sea siempre la primera instrucción válida/leída del archivo.
    - Control de excepciones genéricas: Asegurar que ante cualquier línea malformada inesperada 
      el programa no haga un crash directo (traceback), sino que se capture elegantemente 
      mostrando el error por 'sys.stderr' y finalizando con 'sys.exit(1)'.

    '''