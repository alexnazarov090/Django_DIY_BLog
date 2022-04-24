import os
import environ

from diyblog.settings.base import *


# Initialise environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env.dev'))

if env("PROJECT") == "prod":
   from .production import *
else:
   from .local import *
