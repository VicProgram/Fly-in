import parser


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
