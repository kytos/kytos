"""Utilities functions used in Kytos."""
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Thread

from kytos.core.apm import ElasticAPM
from kytos.core.config import KytosConfig

__all__ = ['listen_to', 'now', 'run_on_thread', 'get_time']

LOG = logging.getLogger(__name__)


def get_thread_pool_max_workers():
    """Get the number of thread pool max workers."""
    return KytosConfig().options["daemon"].thread_pool_max_workers


def get_apm_name():
    """Get apm backend name."""
    return KytosConfig().options["daemon"].apm


# pylint: disable=invalid-name
executors = {name: ThreadPoolExecutor(max_workers=max_workers,
                                      thread_name_prefix=f"thread_pool_{name}")
             for name, max_workers in get_thread_pool_max_workers().items()}


def listen_to(event, *events, pool=None):
    """Decorate Event Listener methods.

    This decorator was built to be used on NAPPs methods to define which
    type of event the method will handle. With this, we will be able to
    'schedule' the app/method to receive an event when a new event is
    registered on the controller buffers.
    By using the run_on_thread decorator, we also guarantee that the method
    (handler) will be called from inside a new thread, avoiding this method to
    block its caller.

    The decorator will add an attribute to the method called 'events', that
    will be a list of the events that the method will handle.

    The event that will be listened to is always a string, but it can represent
    a regular expression to match against multiple Event Types. All listened
    events are documented in :doc:`/developer/listened_events` section.

    The pool option gives you control on which ThreadPoolExecutor that will
    execute the decorated handler. This knob is meant for prioritization,
    allowing executions on different pools depending on the handler primary
    responsibility and importance to avoid potential scheduling starvation.

    Example of usage:

    .. code-block:: python3

        class MyAppClass(KytosApp):
            @listen_to('kytos/of_core.messages.in')
            def my_handler_of_message_in(self, event):
                # Do stuff here...

            @listen_to('kytos/of_core.messages.out')
            def my_handler_of_message_out(self, event):
                # Do stuff here...

            @listen_to('kytos/of_core.messages.in.ofpt_hello',
                       'kytos/of_core.messages.out.ofpt_hello')
            def my_handler_of_hello_messages(self, event):
                # Do stuff here...

            @listen_to('kytos/of_core.message.*.hello')
            def my_other_handler_of_hello_messages(self, event):
                # Do stuff here...

            @listen_to('kytos/of_core.message.*.hello')
            def my_handler_of_hello_messages(self, event):
                # Do stuff here...

            @listen_to('kytos/of_core.message.*')
            def my_stats_handler_of_any_message(self, event):
                # Do stuff here...

            @listen_to("some_db_oriented_event", pool="db")
            def db_update(self, event):
                # Do stuff here...
    """
    def thread_decorator(handler):
        """Decorate the handler method.

        Returns:
            A method with an `events` attribute (list of events to be listened)
            and also decorated to run on a new thread.

        """
        @run_on_thread
        def threaded_handler(*args):
            """Decorate the handler to run from a new thread."""
            handler(*args)

        threaded_handler.events = [event]
        threaded_handler.events.extend(events)
        return threaded_handler

    # pylint: disable=broad-except
    def thread_pool_decorator(handler):
        """Decorate the handler method.

        Returns:
            A method with an `events` attribute (list of events to be listened)
            and also decorated to run on in the thread pool

        """
        def done_callback(future):
            """Done callback."""
            if not future.exception():
                _ = future.result()
                return

        # pylint: disable=unused-argument
        def handler_context(*args, **kwargs):
            """Handler's context for ThreadPool."""
            cls, kytos_event = args[0], args[1]
            try:
                result = handler(*args)
            except Exception as exc:
                result = None
                exc_str = f"{type(exc)}: {str(exc)}"
                LOG.error(f"listen_to handler: {handler}, "
                          f"args: {args}, exception: {exc_str}")
                if hasattr(cls, "controller"):
                    cls.controller.dead_letter.add_event(kytos_event)
            return result

        def handler_context_apm(*args, apm_client=None):
            """Handler's context for ThreadPool APM instrumentation."""
            cls, kytos_event = args[0], args[1]
            trace_parent = kytos_event.trace_parent
            tx_type = "kytos_event"
            tx = apm_client.begin_transaction(transaction_type=tx_type,
                                              trace_parent=trace_parent)
            kytos_event.trace_parent = tx.trace_parent
            tx.name = f"{kytos_event.name}@{cls.napp_id}"
            try:
                result = handler(*args)
                tx.result = result
            except Exception as exc:
                result = None
                exc_str = f"{type(exc)}: {str(exc)}"
                LOG.error(f"listen_to handler: {handler}, "
                          f"args: {args}, exception: {exc_str}")
                if hasattr(cls, "controller"):
                    cls.controller.dead_letter.add_event(kytos_event)
                apm_client.capture_exception(
                    exc_info=(type(exc), exc, exc.__traceback__),
                    context={"args": args},
                    handled=False,
                )
            tx.end()
            apm_client.tracer.queue_func("transaction", tx.to_dict())
            return result

        handler_func, kwargs = handler_context, {}
        if get_apm_name() == "es":
            handler_func = handler_context_apm
            kwargs = dict(apm_client=ElasticAPM.get_client())

        def get_executor(pool, event, default_pool="app"):
            """Get executor."""
            if pool:
                return executors[pool]
            if not event:
                return executors[default_pool]

            if event.name.startswith("kytos/of_core") and "sb" in executors:
                return executors["sb"]
            core_of = "kytos/core.openflow"
            if event.name.startswith(core_of) and "sb" in executors:
                return executors["sb"]
            if event.name.startswith("kytos.storehouse") and "db" in executors:
                return executors["db"]
            return executors[default_pool]

        def inner(*args):
            """Decorate the handler to run in the thread pool."""
            event = args[1] if len(args) > 1 else None
            executor = get_executor(pool, event)
            future = executor.submit(handler_func, *args, **kwargs)
            future.add_done_callback(done_callback)

        inner.events = [event]
        inner.events.extend(events)
        return inner

    if executors:
        return thread_pool_decorator
    return thread_decorator


def alisten_to(event, *events):
    """Decorate async subscribing methods."""

    def decorator(handler):
        """Decorate the handler method.

        Returns:
            A method with an `events` attribute (list of events to be listened)
            and also decorated as an asyncio task.
        """
        # pylint: disable=unused-argument
        async def handler_context(*args, **kwargs):
            """Handler's context for ThreadPool."""
            cls, kytos_event = args[0], args[1]
            try:
                result = await handler(*args)
            except Exception as exc:
                result = None
                exc_str = f"{type(exc)}: {str(exc)}"
                LOG.error(f"alisten_to handler: {handler}, "
                          f"args: {args}, exception: {exc_str}")
                if hasattr(cls, "controller"):
                    cls.controller.dead_letter.add_event(kytos_event)
            return result

        async def handler_context_apm(*args, apm_client=None):
            """Handler's context for ThreadPool APM instrumentation."""
            cls, kytos_event = args[0], args[1]
            trace_parent = kytos_event.trace_parent
            tx_type = "kytos_event"
            tx = apm_client.begin_transaction(transaction_type=tx_type,
                                              trace_parent=trace_parent)
            kytos_event.trace_parent = tx.trace_parent
            tx.name = f"{kytos_event.name}@{cls.napp_id}"
            try:
                result = await handler(*args)
                tx.result = result
            except Exception as exc:
                result = None
                exc_str = f"{type(exc)}: {str(exc)}"
                LOG.error(f"alisten_to handler: {handler}, "
                          f"args: {args}, exception: {exc_str}")
                if hasattr(cls, "controller"):
                    cls.controller.dead_letter.add_event(kytos_event)
                apm_client.capture_exception(
                    exc_info=(type(exc), exc, exc.__traceback__),
                    context={"args": args},
                    handled=False,
                )
            tx.end()
            apm_client.tracer.queue_func("transaction", tx.to_dict())
            return result

        handler_func, kwargs = handler_context, {}
        if get_apm_name() == "es":
            handler_func = handler_context_apm
            kwargs = dict(apm_client=ElasticAPM.get_client())

        async def inner(*args):
            """Inner decorated with events attribute."""
            return await handler_func(*args, **kwargs)
        inner.events = [event]
        inner.events.extend(events)
        return inner

    return decorator


def now(tzone=timezone.utc):
    """Return the current datetime (default to UTC).

    Args:
        tzone (datetime.timezone): Specific time zone used in datetime.

    Returns:
        datetime.datetime.now: Date time with specific time zone.

    """
    return datetime.now(tzone)


def run_on_thread(method):
    """Decorate to run the decorated method inside a new thread.

    Args:
        method (function): function used to run as a new thread.

    Returns:
        Decorated method that will run inside a new thread.
        When the decorated method is called, it will not return the created
        thread to the caller.

    """
    def threaded_method(*args):
        """Ensure the handler method runs inside a new thread."""
        thread = Thread(target=method, args=args)

        # Set daemon mode so that we don't have to wait for these threads
        # to finish when exiting Kytos
        thread.daemon = True
        thread.start()
    return threaded_method


def get_time(data=None):
    """Receive a dictionary or a string and return a datatime instance.

    data = {"year": 2006,
            "month": 11,
            "day": 21,
            "hour": 16,
            "minute": 30 ,
            "second": 00}

    or

    data = "21/11/06 16:30:00"

    2018-04-17T17:13:50Z

    Args:
        data (str, dict): python dict or string to be converted to datetime

    Returns:
        datetime: datetime instance.

    """
    if isinstance(data, str):
        date = datetime.strptime(data, "%Y-%m-%dT%H:%M:%S")
    elif isinstance(data, dict):
        date = datetime(**data)
    else:
        return None
    return date.replace(tzinfo=timezone.utc)
