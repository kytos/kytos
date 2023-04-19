"""APM module."""
import os
from functools import wraps

from elasticapm import Client
from elasticapm.contrib.starlette import ElasticAPM as StarletteAPM
from elasticapm.traces import execution_context

from kytos.core.exceptions import KytosAPMInitException


def init_apm(apm_backend="es", **kwargs):
    """Init APM backend."""
    backends = {"es": ElasticAPM}
    try:
        return backends[apm_backend].init_client(**kwargs)
    except KeyError:
        client_names = ",".join(list(backends.keys()))
        raise KytosAPMInitException(
            f"APM backend '{apm_backend}' isn't supported."
            f" Current supported APMs: {client_names}"
        )


def begin_span(func, span_type="custom"):
    """APM transaction begin_span decorator."""

    @wraps(func)
    def wrapper(*args, **kwds):
        transaction = execution_context.get_transaction()
        if transaction:
            transaction.begin_span(f'{func.__module__}.{func.__name__}',
                                   span_type)
        result = func(*args, **kwds)
        if transaction:
            transaction.end_span()
        return result

    return wrapper


class ElasticAPM:
    """ElasticAPM Client instance."""

    _client: Client = None

    @classmethod
    def get_client(cls, **kwargs) -> Client:
        """Get client."""
        if not cls._client:
            return cls.init_client(**kwargs)
        return cls._client

    @classmethod
    def init_client(
        cls,
        service_name=os.environ.get("ELASTIC_APM_SERVICE_NAME", "kytos"),
        server_url=os.environ.get("ELASTIC_APM_URL", "http://localhost:8200"),
        secret_token=os.environ.get("ELASTIC_APM_SECRET_TOKEN",
                                    "elasticapm_token"),
        **kwargs,
    ) -> Client:
        """Init APM Client."""
        app = kwargs.pop("app", None)
        if not cls._client:
            cls._client = Client(
                service_name=service_name,
                server_url=server_url,
                secret_token=secret_token,
                **kwargs,
            )
            app.add_middleware(StarletteAPM, client=cls._client)
        return cls._client
