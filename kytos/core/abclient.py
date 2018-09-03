"""
Autobahn client to publish Kytos events as WAMP messages.

Connects to a crossbar.io router and publishes all messages from the new UI
event buffer.

Event flow:

  app event -> ui event -> ui buffer
                             |
                             |
                             V
                      autobahn client
                             |
                             |
                             V
                      crossbar router
                       (kytos realm)
                             |
                             |
                             V
                       any wamp client


Instructions on how to run:

1. Checkout kytos' "autobahn" branch

2. Run kytosd:

  $ kytosd -f

3. Start crossbar router from docker

  $ docker run --user 1000 -v ${PWD}:/node -p 8080:8080 --name crossbar --rm -it crossbario/crossbar --colour true

4. That starts a local autobahn web client where events are published:

  http://localhost:8080

"""


from autobahn.asyncio.component import Component, run
from autobahn.wamp.types import SubscribeOptions, PublishOptions

import asyncio
import txaio

LOG = txaio.make_logger()

# txaio logger has a bug when the string contains dict representations {}
# so we're using print() instead in some places
#LOG.info(msg)

component = Component(
    transports=u"ws://localhost:8080/ws",
    realm=u"kytos",
)

def on_event(name, content, source):
    msg = f"'{name}' event, content: {content}, source: {source}"
    print(msg)

def on_ping(counter, content, source):
    msg = f"ui.ping event #{counter}, content: {content}, source: {source}"
    LOG.info(msg)

@component.on_join
async def joined(session, details):
    LOG.info("session ready")

    # composing session inside component so that we can use its .publish method
    if not getattr(component, 'session', None):
        component.session = session

    match_prefix = SubscribeOptions(match='prefix')

    # Keep-alive test
    await session.subscribe(on_ping, 'kytos/ui.ping')

    # Watch for all Kytos Events:
    #await session.subscribe(on_event, 'kytos/', match_prefix)

    # Kytos Core Events:
    await session.subscribe(on_event, 'kytos/core.', match_prefix)

    # Specific NApps' Events:
    await session.subscribe(on_event, 'kytos/of_core.', match_prefix)
    await session.subscribe(on_event, 'kytos/topology.', match_prefix)

    # Specific events:
    #await session.subscribe(on_event, 'kytos/core.switch.new')

    #await session.subscribe(on_event, 'kytos/core.start')
    #await session.subscribe(on_event, 'kytos/core.shutdown')

    # on join, start async task to listen to events
    loop = asyncio.get_event_loop()
    loop.create_task(ui_event_handler())

    #session.publish(topic=event.name, content=event.content)


async def ui_event_handler():
    """
    Watches the `ui_buffer` event queue to forward its events to WAMP channels.

    """
    LOG.info('Starting UI event handler')
    while True:
        event = await component.ui_buffer.aget()
        serialized_content = serialize_dict(event.content)
        #serialized_content = event.content
        #LOG.info(f'Forwarding new UI event received from Kytos: {event}, content: {serialized_content}')
        print(f'Forwarding new UI event received from Kytos: {event}, content: {serialized_content}')
        component.session.publish(topic=event.name,
                                  name=event.name,
                                  content=serialized_content,
                                  source='kytos.core.abclient',
                                  options=PublishOptions(exclude_me=False))
        if event.name == "kytos/core.shutdown":
            LOG.debug("App Event handler stopped")
            break


# TODO: move helper function to appropriate module
def serialize_dict(data: dict):
    """Force conversion of value objects to JSON.

    If we don't make this conversion manually, autobahn.wamp.serializer
    will cause this exception:

    umsgpack.UnsupportedTypeException:
      unsupported type: <class 'kytos.core.switch.Switch'>
    """

    result = {}
    for key, obj in data.items():
        if not isinstance(obj, str):
            if getattr(obj, 'as_json', None):
                obj = obj.as_json()
            elif callable(obj):
                # do not forward functions/methods as event content
                continue
            elif isinstance(obj, dict):
                obj = serialize_dict(obj)
            else:
                print("XXX key '%s' doesn't have .as_json(), value: %s, class %s" % (key, obj, type(obj)))
                obj = str(obj)
        result[key] = obj
    return result


if __name__ == "__main__":
    run([component])

