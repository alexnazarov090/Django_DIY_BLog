import os
import environ
import socket
from diyblog.settings.base import *


# Initialise environment variables
# env = environ.Env()
# environ.Env.read_env(os.path.join(BASE_DIR, '.env.dev'))

# if env("PROJECT") == "prod":
if socket.gethostname() != "DESKTOP-98M2CO0":
   from .production import *
else:
   from .local import *
