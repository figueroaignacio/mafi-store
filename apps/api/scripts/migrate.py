import subprocess
import sys

def main():
    args = sys.argv[1:]

    if not args:
        print("Uso: uv run scripts/migrate.py <comando>")
        print("Comandos: up, down, create <mensaje>")
        return

    command = args[0]

    if command == "up":
        subprocess.run(["alembic", "upgrade", "head"])
    elif command == "down":
        subprocess.run(["alembic", "downgrade", "-1"])
    elif command == "create":
        if len(args) < 2:
            print("Uso: uv run scripts/migrate.py create <mensaje>")
            return
        message = args[1]
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", message])
    else:
        print(f"Comando desconocido: {command}")

if __name__ == "__main__":
    main()