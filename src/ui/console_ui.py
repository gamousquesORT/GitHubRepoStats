"""Console UI for interacting with team data."""
from typing import Optional
from ..team import TeamManager


class ConsoleUI:
    """Console-based user interface for team management."""

    def __init__(self, team_manager: TeamManager) -> None:
        """
        Initialize console UI.

        Args:
            team_manager: TeamManager instance
        """
        self.team_manager = team_manager

    def show_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "=" * 50)
        print("GitHubTracker - Team Management System")
        print("=" * 50)
        print("1. Comenzar la lectura (Load CSV file)")
        print("2. Listar los datos de los equipos (List all teams)")
        print("3. Buscar equipo por número (Search team by number)")
        print("4. Terminar (Exit)")
        print("=" * 50)

    def get_user_choice(self) -> str:
        """
        Get user menu choice.

        Returns:
            User's choice as string
        """
        choice = input("\nIngrese su opción: ").strip()
        return choice

    def load_csv(self) -> None:
        """Handle CSV file loading."""
        print("\n--- Cargar archivo CSV ---")
        csv_path = input("Ingrese la ruta del archivo CSV: ").strip()

        try:
            self.team_manager.load_from_csv(csv_path)
            print(f"\n¡Éxito! Los datos se cargaron correctamente desde {csv_path}")
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
                print("\n¡Gracias por usar GitHubTracker! ¡Hasta pronto!")
                break
            else:
                print("\nOpción inválida. Por favor, elija una opción del 1 al 4.")
