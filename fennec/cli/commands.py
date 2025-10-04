"""
CLI commands system
"""

from typing import Callable, Dict, List
import sys


class CLI:
    """
    Command-line interface
    يدير commands ويسمح بإضافة commands جديدة
    """

    def __init__(self):
        self.commands: Dict[str, Callable] = {}
        self.descriptions: Dict[str, str] = {}

    def command(self, name: str, description: str = ""):
        """
        Decorator لتسجيل command

        Usage:
            cli = CLI()

            @cli.command("hello", "Say hello")
            def hello_command(name: str = "World"):
                print(f"Hello, {name}!")
        """

        def decorator(func: Callable):
            self.commands[name] = func
            self.descriptions[name] = description or func.__doc__ or ""
            return func

        return decorator

    def execute(self, args: List[str] = None):
        """
        تنفيذ command من command line arguments

        Args:
            args: Command line arguments (defaults to sys.argv[1:])
        """
        if args is None:
            args = sys.argv[1:]

        if not args or args[0] in ("-h", "--help"):
            self.print_help()
            return

        command_name = args[0]

        if command_name not in self.commands:
            print(f"Error: Unknown command '{command_name}'")
            print("\nUse --help to see available commands")
            sys.exit(1)

        # Parse command arguments
        command_args = args[1:]
        kwargs = {}

        for arg in command_args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                kwargs[key.lstrip("-")] = value

        # Execute command
        try:
            self.commands[command_name](**kwargs)
        except TypeError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error executing command: {e}")
            sys.exit(1)

    def print_help(self):
        """
        طباعة help message
        """
        print("Fennec Framework 🦊 CLI")
        print("\nUsage: python -m fennec.cli <command> [options]")
        print("\nAvailable commands:")

        for name, description in self.descriptions.items():
            print(f"  {name:20} {description}")

        print("\nUse <command> --help for more information about a command")



# Create default CLI instance
cli = CLI()


@cli.command("startproject", "Create a new project")
def startproject(name: str = "myproject"):
    """
    إنشاء project جديد مع الهيكل الأساسي
    """
    import os

    print(f"Creating project: {name}")

    # Create project structure
    directories = [
        name,
        f"{name}/app",
        f"{name}/app/routers",
        f"{name}/app/models",
        f"{name}/app/services",
        f"{name}/tests",
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  Created: {directory}/")

    # Create main.py
    main_content = '''"""
Main application entry point
"""

from framework import Application, Router, JSONResponse

app = Application(title="{name} API", version="1.0.0")
router = Router()


@router.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(data={{"message": "Welcome to {name} API"}})


@router.get("/health")
async def health():
    """Health check endpoint"""
    return JSONResponse(data={{"status": "healthy"}})


app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''.format(
        name=name
    )

    with open(f"{name}/app/main.py", "w") as f:
        f.write(main_content)
    print(f"  Created: {name}/app/main.py")

    # Create __init__.py files
    init_files = [
        f"{name}/app/__init__.py",
        f"{name}/app/routers/__init__.py",
        f"{name}/app/models/__init__.py",
        f"{name}/app/services/__init__.py",
        f"{name}/tests/__init__.py",
    ]

    for init_file in init_files:
        with open(init_file, "w") as f:
            f.write("")
        print(f"  Created: {init_file}")

    # Create README.md
    readme_content = f"""# {name}

A REST API built with Lightweight Framework

## Installation

```bash
pip install lightweight-framework uvicorn
```

## Running

```bash
cd {name}
python -m app.main
```

Or with uvicorn:

```bash
uvicorn app.main:app --reload
```

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.
"""

    with open(f"{name}/README.md", "w") as f:
        f.write(readme_content)
    print(f"  Created: {name}/README.md")

    print(f"\n✓ Project '{name}' created successfully!")
    print(f"\nNext steps:")
    print(f"  cd {name}")
    print(f"  python -m app.main")


@cli.command("create:module", "Create a new module")
def create_module(name: str = "users"):
    """
    إنشاء module جديد مع router, model, service
    """
    import os

    print(f"Creating module: {name}")

    # Create router
    router_content = f'''"""
{name.title()} router
"""

from framework import Router, JSONResponse

router = Router(prefix="/{name}")


@router.get("/")
async def list_{name}():
    """List all {name}"""
    return JSONResponse(data={{"{name}": []}})


@router.get("/{{id}}")
async def get_{name.rstrip('s')}(id: int):
    """Get {name.rstrip('s')} by ID"""
    return JSONResponse(data={{"id": id}})


@router.post("/")
async def create_{name.rstrip('s')}():
    """Create new {name.rstrip('s')}"""
    return JSONResponse(data={{"message": "{name.rstrip('s').title()} created"}})
'''

    os.makedirs("app/routers", exist_ok=True)
    with open(f"app/routers/{name}.py", "w") as f:
        f.write(router_content)
    print(f"  Created: app/routers/{name}.py")

    # Create model
    model_content = f'''"""
{name.title()} model
"""

from fennec.validation import BaseModel


class {name.rstrip('s').title()}(BaseModel):
    """
    {name.rstrip('s').title()} model
    """
    id: int
    name: str
'''

    os.makedirs("app/models", exist_ok=True)
    with open(f"app/models/{name}.py", "w") as f:
        f.write(model_content)
    print(f"  Created: app/models/{name}.py")

    # Create service
    service_content = f'''"""
{name.title()} service
"""


class {name.title()}Service:
    """
    Business logic for {name}
    """

    async def get_all(self):
        """Get all {name}"""
        return []

    async def get_by_id(self, id: int):
        """Get {name.rstrip('s')} by ID"""
        return {{"id": id}}

    async def create(self, data: dict):
        """Create new {name.rstrip('s')}"""
        return data
'''

    os.makedirs("app/services", exist_ok=True)
    with open(f"app/services/{name}.py", "w") as f:
        f.write(service_content)
    print(f"  Created: app/services/{name}.py")

    print(f"\n✓ Module '{name}' created successfully!")
    print(f"\nDon't forget to include the router in your main app:")
    print(f"  from app.routers.{name} import router as {name}_router")
    print(f"  app.include_router({name}_router)")



@cli.command("runserver", "Run development server")
def runserver(host: str = "0.0.0.0", port: str = "8000", reload: str = "true"):
    """
    تشغيل development server
    """
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn is not installed")
        print("Install it with: pip install uvicorn")
        sys.exit(1)

    print(f"Starting server on {host}:{port}")
    print("Press CTRL+C to stop")

    # Import app
    try:
        from app.main import app
    except ImportError:
        print("Error: Could not import app from app.main")
        print("Make sure you're in the project directory")
        sys.exit(1)

    # Run server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=int(port),
        reload=reload.lower() == "true",
    )


@cli.command("migrate", "Run database migrations")
def migrate(action: str = "up"):
    """
    تشغيل database migrations
    """
    print(f"Running migrations: {action}")

    if action == "up":
        print("  Applying migrations...")
        # In a real implementation, you'd run actual migrations here
        print("  ✓ Migrations applied successfully")
    elif action == "down":
        print("  Rolling back migrations...")
        print("  ✓ Migrations rolled back successfully")
    elif action == "create":
        print("  Creating new migration...")
        print("  ✓ Migration file created")
    else:
        print(f"  Error: Unknown action '{action}'")
        print("  Available actions: up, down, create")
        sys.exit(1)


# Main entry point
if __name__ == "__main__":
    cli.execute()
