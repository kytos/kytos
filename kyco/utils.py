"""Utilities"""

import logging

from inspect import getargspec
from abc import abstractmethod, ABCMeta

from types import InstanceType
from functools import wraps
import inspect

APP_MSG = "[App %s] %s | ID: %02d | R: %02d | P: %02d | F: %s"


def start_logger():
    general_formatter = logging.Formatter('%(asctime)s - %(levelname)s '
                                          '[%(name)s] %(message)s')
    app_formatter = logging.Formatter('%(asctime)s - %(levelname)s '
                                      '[%(name)s] %(message)s')

    controller_console_handler = logging.StreamHandler()
    controller_console_handler.setLevel(logging.DEBUG)
    controller_console_handler.setFormatter(general_formatter)

    app_console_handler = logging.StreamHandler()
    app_console_handler.setLevel(logging.DEBUG)
    app_console_handler.setFormatter(app_formatter)

    controller_log = logging.getLogger('Kyco')
    controller_log.setLevel(logging.DEBUG)
    controller_log.addHandler(controller_console_handler)

    app_log = logging.getLogger('KycoNApp')
    app_log.setLevel(logging.DEBUG)
    app_log.addHandler(app_console_handler)

    return controller_log


class KycoApp(metaclass=ABCMeta):
    _listeners = {'msg_in_event': None,
                  'msg_out_event': None,
                  'apps_event': None}
    def __init__(self):
        # Get all methods from the instance
        # check which one has a attribute named 'event_type'
        # register this method on the '_listeners' dict
        # of the instance
        pass

    @abstractmethod
    def setUp(self):
        pass






class ListenAppEvents(object):
    """Decorator for App Events Listener"""
    def __init__(self, listener):
        if not 'AppEvents' in instancia_do_app._listeners:
            instancia_do_app._listeners['AppEvent'] = []
        instancia_do_app._listeners.append(listener)
        self.listener = listener
        print(dir(listener))
        # print(listener.__self__)
        # print(dir(listener.__module__))
        # listener.__class__._listeners['apps_event'] = listener

    def __call__(self, *args, **kwargs):
        self.listener(*args, **kwargs)




class App(KycoApp):
    def __init__(self):
        self.nome = "APP"

    @ListenAppEvents
    def teste(self):
        print("Teste")



def dec(func):

    #get the sig of the function
    sig = []
    @wraps(func)
    def wrapper(*args, **kwargs):
        ret = None
        #if this is a method belonging to an object...
        if args and getattr(args[0], func.__name__, None):
            instance, args = args[0], args[1:]
            #if sig of object is not already set
            if not hasattr(instance, "_listeners"):
                instance._listeners = {}
            if 'dec' not in instance._listeners:
                instance._listeners['dec'] = []
            instance._listeners['dec'].append(getattr(args[0], func.__name__))
            ret = func(instance, *args, **kwargs)
        else:
            ret = func(*args, **kwargs)
            print "Sig of %s is %s" % (func.__name__, id(sig))
        return ret

   #modify the doc string
   try:
      docs = inspect.getsourcelines(func)
   except:
      docs = "<unable to fetch defintion>"
   else:
      docs = docs[0][1].rstrip('\n').rstrip(':').lstrip(' ').lstrip('def')
   wrapper.__doc__ = docs + "\n" + (func.__doc__ or '')
   return wrapper

class A(object):
   def __init__(self):
      super(A, self).__init__()

   @dec
   def f(self, x):
      """something"""
      print '%s.f(%s)' % (self, x)


@dec
def myfunc():
   print "myfunc"

@dec
def myfunc2():
   print "myfunc2"

@dec
def myfunc3():
   print "myfunc3"

if __name__ == "__main__":
   list = []
   for x in xrange(3):
      list.append(A())

   [a.f(123) for a in list]
   myfunc()
   myfunc()
   myfunc2()
   myfunc2()
   myfunc3()
   myfunc3()
