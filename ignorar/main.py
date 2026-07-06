import sys
import re
from models import Drone_Map, Hub, Connection, VALID_ZONE_TYPES


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

        self.validate()

    def validate(self) -> None:
        if self.nb_drones <= 0:
            print(
                "Error: nb_drones debe ser un entero positivo.", file=sys.stderr
                )
            sys.exit(1)

        if self.map.start_hub is None:
            print("Error: no se definió ningún start_hub.", file=sys.stderr)
            sys.exit(1)

        if self.map.end_hub is None:
            print("Error: no se definió ningún end_hub.", file=sys.stderr)
            sys.exit(1)

    def parse_metadata(self, content: str) -> dict[str, str]:
        """Extrae el contenido de [tag=valor ...] como un dict tag -> valor."""
        match_brackets = re.search(r"\[(.*?)\]", content)
        if not match_brackets:
            return {}

        raw_tags = match_brackets.group(1)
        metadata: dict[str, str] = {}
        # cada tag es tag=valor, separadas por espacios
        for tag_match in re.finditer(r"(\w+)=(\S+)", raw_tags):
            key, value = tag_match.group(1), tag_match.group(2)
            metadata[key] = value

        return metadata

    def parse_hub_content(
            self, content: str, line_num: int
            ) -> tuple[str, int, int, str, str, int]:
        metadata = self.parse_metadata(content)

        color = metadata.get("color", "white")

        zone_type = metadata.get("zone", "normal")
        if zone_type not in VALID_ZONE_TYPES:
            raise ValueError(
                f"Tipo de zona inválido '{zone_type}' en línea {line_num}. "
                f"Debe ser uno de: {', '.join(sorted(VALID_ZONE_TYPES))}."
                )

        max_drones_str = metadata.get("max_drones", "1")
        if not max_drones_str.isdigit() or int(max_drones_str) <= 0:
            raise ValueError(
                f"max_drones inválido '{max_drones_str}' en línea {line_num}. "
                "Debe ser un entero positivo."
                )
        max_drones = int(max_drones_str)

        main_part = re.sub(r"\[.*?\]", "", content).strip()
        parts = main_part.split()

        if len(parts) != 3:
            raise ValueError(f"Formato de hub inválido: '{content}'")

        name, x_str, y_str = parts

        if "-" in name or " " in name:
            raise ValueError(
                f"Nombre de zona inválido '{name}': no puede contener "
                "guiones ni espacios."
                )

        return name, int(x_str), int(y_str), zone_type, color, max_drones

    def parse_line(self, line: str, line_num: int) -> None:
        if line.startswith("nb_drones:"):
            value = line.split(":", 1)[1].strip()
            if not value.isdigit() or int(value) <= 0:
                print(
                    f"Error en línea {line_num}: nb_drones debe ser un "
                    f"entero positivo (recibido: '{value}').", file=sys.stderr
                    )
                sys.exit(1)
            self.nb_drones = int(value)

        elif any(line.startswith(p) for p in ["hub:", "start_hub:", "end_hub:"]):
            prefix, content = line.split(":", 1)
            content = content.strip()

            try:
                name, x, y, zone_type, color, max_drones = self.parse_hub_content(
                    content, line_num
                    )

                match prefix:
                    case "start_hub":
                        if self.map.start_hub is not None:
                            print(
                                f"Error en línea {line_num}: ya existe un "
                                "start_hub definido.", file=sys.stderr
                                )
                            sys.exit(1)
                        nuevo_hub = Hub(name, x, y, "start", color, max_drones)
                        self.map.start_hub = nuevo_hub

                    case "end_hub":
                        if self.map.end_hub is not None:
                            print(
                                f"Error en línea {line_num}: ya existe un "
                                "end_hub definido.", file=sys.stderr
                                )
                            sys.exit(1)
                        nuevo_hub = Hub(name, x, y, "end", color, max_drones)
                        self.map.end_hub = nuevo_hub

                    case "hub":
                        nuevo_hub = Hub(name, x, y, zone_type, color, max_drones)
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

            metadata = self.parse_metadata(content)
            capacity_str = metadata.get("max_link_capacity", "1")
            if not capacity_str.isdigit() or int(capacity_str) <= 0:
                print(
                    f"Error en línea {line_num}: max_link_capacity inválido "
                    f"'{capacity_str}'. Debe ser un entero positivo.",
                    file=sys.stderr
                    )
                sys.exit(1)
            capacity = int(capacity_str)

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
            try:
                self.map.add_connection(new_connection)
            except ValueError as e:
                print(f"Error en línea {line_num}: {e}", file=sys.stderr)
                sys.exit(1)

        else:
            print(
                f"Error de sintaxis en línea {line_num}: "
                "Comando desconocido.", file=sys.stderr
                )
            sys.exit(1)


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python3 -m tu_modulo mapa.txt", file=sys.stderr)
        sys.exit(1)

    drone_map = Drone_Map()
    parser = Parser(drone_map)
    parser.parse_file(sys.argv[1])
    print(f"Mapa cargado exitosamente. Drones totales: {parser.nb_drones}")


if __name__ == "__main__":
    main()