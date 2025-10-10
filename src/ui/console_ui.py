"""Console UI for interacting with team data."""
from typing import Optional, List
from pathlib import Path
from ..team import TeamManager
from ..github.repository_client import GitHubRepositoryClient
from ..reports.team_report_generator import TeamReportGenerator


class ConsoleUI:
    """Console-based user interface for team management."""

    def __init__(self, team_manager: TeamManager, github_client: Optional[GitHubRepositoryClient] = None) -> None:
        """
        Initialize console UI.

        Args:
            team_manager: TeamManager instance
            github_client: Optional GitHubRepositoryClient instance for repository operations
        """
        self.team_manager = team_manager
        self.github_client = github_client
        self.report_generator: Optional[TeamReportGenerator] = None

        if self.github_client:
            self.report_generator = TeamReportGenerator(self.team_manager, self.github_client)

    def show_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "=" * 50)
        print("GitHubTracker - Team Management System")
        print("=" * 50)
        print("1. Comenzar la lectura (Load CSV file)")
        print("2. Listar los datos de los equipos (List all teams)")
        print("3. Buscar equipo por número (Search team by number)")
        print("4. Ver comentarios de commits por equipo (View team commit comments)")
        print("5. Terminar (Exit)")
        print("=" * 50)

    def get_user_choice(self) -> str:
        """
        Get user menu choice.

        Returns:
            User's choice as string
        """
        choice = input("\nIngrese su opción: ").strip()
        return choice

    def get_csv_files(self) -> List[Path]:
        """Get list of CSV files in data directory."""
        data_dir = Path("data")
        if not data_dir.exists():
            return []

        csv_files = list(data_dir.glob("*.csv"))
        return sorted(csv_files)

    def load_csv(self) -> None:
        """Handle CSV file loading."""
        print("\n--- Cargar archivo CSV ---")

        # Get available CSV files
        csv_files = self.get_csv_files()

        if not csv_files:
            print("\nNo se encontraron archivos CSV en la carpeta 'data'.")
            print("Por favor, coloque archivos CSV en la carpeta 'data' e intente nuevamente.")
            return

        # Display available files
        print("\nArchivos CSV disponibles:")
        for i, file in enumerate(csv_files, 1):
            print(f"{i}. {file.name}")

        # Get user choice
        choice = input(f"\nSeleccione un archivo (1-{len(csv_files)}): ").strip()

        try:
            file_index = int(choice) - 1
            if file_index < 0 or file_index >= len(csv_files):
                print("\nOpción inválida.")
                return

            selected_file = csv_files[file_index]
            csv_path = str(selected_file)
        except ValueError:
            print("\nOpción inválida. Debe ingresar un número.")
            return

        # Ask for delimiter
        print("\n¿Qué separador utiliza el archivo CSV?")
        print("1. Coma (,)")
        print("2. Punto y coma (;)")
        delimiter_choice = input("Ingrese su opción (1 o 2): ").strip()

        if delimiter_choice == "1":
            delimiter = ","
        elif delimiter_choice == "2":
            delimiter = ";"
        else:
            print("\nOpción inválida. Usando coma (,) por defecto.")
            delimiter = ","

        try:
            self.team_manager.load_from_csv(csv_path, delimiter=delimiter)
            print(f"\n¡Éxito! Los datos se cargaron correctamente desde {selected_file.name}")
        except FileNotFoundError:
            print(f"\nError: No se encontró el archivo '{csv_path}'")
        except ValueError as e:
            print(f"\nError: Formato inválido en el CSV - {e}")
        except Exception as e:
            print(f"\nError inesperado: {e}")

    def list_all_teams(self) -> None:
        """Display all teams."""
        print("\n--- Lista de Equipos ---")

        if not self.team_manager.has_data():
            print("No hay datos cargados. Por favor, primero cargue un archivo CSV.")
            return

        try:
            count = 0
            for team in self.team_manager.iter_teams():
                print(f"\n{team}")
                count += 1

            print(f"\n--- Total de equipos: {count} ---")
        except Exception as e:
            print(f"\nError al listar equipos: {e}")

    def search_team(self) -> None:
        """Handle team search by number."""
        print("\n--- Buscar Equipo ---")

        if not self.team_manager.has_data():
            print("No hay datos cargados. Por favor, primero cargue un archivo CSV.")
            return

        team_number = input("Ingrese el número de equipo a buscar: ").strip()

        try:
            team = self.team_manager.find_team(team_number)

            if team:
                print(f"\n¡Equipo encontrado!")
                print(f"\n{team}")
                print(f"\nIntegrantes:")
                for i, member in enumerate(team.get_members(), 1):
                    print(f"  {i}. {member}")
            else:
                print(f"\nNo se encontró el equipo con número '{team_number}'")
        except Exception as e:
            print(f"\nError al buscar equipo: {e}")

    def display_team_reports(self) -> None:
        """Display commit comments for each team's repository."""
        print("\n--- Comentarios de Commits por Equipo ---")

        if not self.team_manager.has_data():
            print("No hay datos cargados. Por favor, primero cargue un archivo CSV.")
            return

        if not self.report_generator:
            print("\nError: No se configuró el cliente de GitHub.")
            print("Esta funcionalidad requiere configuración de GitHub.")
            return

        try:
            print("\nGenerando reportes para todos los equipos...")
            print("Esto puede tomar algunos momentos...\n")

            reports = self.report_generator.generate_reports()

            for report in reports:
                print("=" * 70)
                print(f"EQUIPO: {report.team.team_number}")
                print(f"Integrantes: {', '.join([m.name for m in report.team.get_members()])}")
                print(f"IDs: {', '.join([m.student_id for m in report.team.get_members()])}")
                print("-" * 70)

                if report.found and report.repository_name:
                    print(f"Repositorio encontrado: {report.repository_name}")
                    print(f"\nCantidad de commits: {len(report.commit_messages)}")
                    print("\nMensajes de commits:")
                    print("-" * 70)

                    if report.commits_with_authors:
                        for i, (message, author_name, author_username) in enumerate(report.commits_with_authors, 1):
                            # Display commit message with author
                            author_display = f"{author_name}"
                            if author_username:
                                author_display += f" (@{author_username})"
                            print(f"\n{i}. [{author_display}] {message}")
                    elif report.commit_messages:
                        for i, message in enumerate(report.commit_messages, 1):
                            # Fallback: display without author info
                            print(f"\n{i}. {message}")
                    else:
                        print("No se encontraron commits en este repositorio.")
                else:
                    print("No se encontró un repositorio para este equipo.")
                    print("Verifique que el repositorio contenga los IDs de todos los miembros.")

                print("\n" + "=" * 70)

                # Wait for user to press Enter before showing next team
                input("\nPresione Enter para continuar con el siguiente equipo...")

            print(f"\n¡Proceso completado! Se procesaron {len(reports)} equipos.")

        except Exception as e:
            print(f"\nError al generar reportes: {e}")

    def run(self) -> None:
        """Run the main console UI loop."""
        print("\n¡Bienvenido a GitHubTracker!")

        while True:
            self.show_menu()
            choice = self.get_user_choice()

            if choice == "1":
                self.load_csv()
            elif choice == "2":
                self.list_all_teams()
            elif choice == "3":
                self.search_team()
            elif choice == "4":
                self.display_team_reports()
            elif choice == "5":
                print("\n¡Gracias por usar GitHubTracker! ¡Hasta pronto!")
                break
            else:
                print("\nOpción inválida. Por favor, elija una opción del 1 al 5.")
