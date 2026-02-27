import os
from dotenv import load_dotenv
from app import create_app
from app.utils.cli import create_cli_commands, create_shell_context
from config import basedir

load_dotenv(os.path.join(basedir, '.env'))

app = create_app(os.environ.get('ENV') or 'production')

create_cli_commands(app)
create_shell_context(app)
