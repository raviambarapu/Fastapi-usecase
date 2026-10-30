from slowapi import Limiter  # type: ignore[reportMissingImports]
from slowapi.util import get_remote_address  # type: ignore[reportMissingImports]

# Limiter object
limiter = Limiter(key_func=get_remote_address)