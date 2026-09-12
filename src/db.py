import os
import pyexasol
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return pyexasol.connect(
        dsn=f"{os.environ['EXASOL_HOST']}:{os.environ['EXASOL_PORT']}",
        user=os.environ["EXASOL_USER"],
        password=os.environ["EXASOL_PASSWORD"],
        compression=True,
        encryption=True,
        websocket_sslopt={"cert_reqs": 0},  # accept the self-signed cert from Exasol Personal
    )
