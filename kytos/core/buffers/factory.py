"""Utilities for composing KytosEventBuffers"""

from janus import PriorityQueue, Queue

from kytos.core.helpers import get_thread_pool_max_workers

from .buffers import KytosEventBuffer

queue_classes = {
    'queue': Queue,
    'priority': PriorityQueue,
}


def process_queue(config: dict) -> Queue:
    """
    Create a janus queue from a given config dict
    """
    queue_type = queue_classes[config.get('type', 'queue')]
    queue_size = config.get('maxsize', 0)
    if isinstance(queue_size, str):
        if queue_size.startswith('threadpool_'):
            threadpool = queue_size[len('threadpool_'):]
            queue_size = get_thread_pool_max_workers().get(threadpool, 0)
        else:
            raise TypeError(
                'Expected int or str formatted '
                'as "threadpool_{threadpool_name}"'
            )
    return queue_type(maxsize=queue_size)


extension_processors = {}


def buffer_from_config(name: str, config: dict) -> KytosEventBuffer:
    """
    Create a KytosEventBuffer from a given config dict
    """
    buffer_cls = KytosEventBuffer
    args = {}
    # Process Queue Config
    args['queue'] = process_queue(config.get('queue', {}))

    buffer = buffer_cls(name, **args)

    # Process Mixins
    extensions: dict = config.get('extensions', [])
    for extension in extensions:
        extension_type = extension['type']
        extension_args = extension.get('args', {})
        buffer = extension_processors[extension_type](buffer, extension_args)

    return buffer
