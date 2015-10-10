'''connectable/Connectable.py

   Connectable enables child object to create dynamic connections
   (via signals/slots) at run-time. Inspired by QT's signal / slot mechanism

   Copyright (C) 2015  Timothy Edmund Crosley

   This program is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License
   as published by the Free Software Foundation; either version 2
   of the License, or (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''


class Connectable(object):
    __slots__ = ("connections")
    signals = ()

    def emit(self, signal, value=None, gather=False):
        """Emits a signal, causing all slot methods connected with the signal to be called (optionally w/ related value)

           signal: the name of the signal to emit, must be defined in the classes 'signals' list.
           value: the value to pass to all connected slot methods.
           gather: if set, causes emit to return a list of all slot results
        """
        results = [] if gather else True
        if hasattr(self, 'connections') and signal in self.connections:
            for requires, values in self.connections[signal].items():
                if requires is None or requires == value or (callable(requires) and requires(value)):
                    for slot, transform in values.items():
                        if transform is not None:
                            if callable(transform):
                                used_value = transform(value)
                            elif isinstance(transform, str):
                                used_value = transform.format(value=value)
                            else:
                                used_value = transform
                        else:
                            used_value = value

                        if used_value is not None:
                            if(accept_arguments(slot, 1)):
                                result = slot(used_value)
                            elif(accept_arguments(slot, 0)):
                                result = slot()
                            else:
                                result = ''
                        else:
                            result = slot()

                        if gather:
                            results.append(result)

        return results

    def connect(self, signal, slot, transform=None, requires=None):
        """Defines a connection between this objects signal and another objects slot

           signal: the signal this class will emit, to cause the slot method to be called
           receiver: the object containing the slot method to be called
           slot: the slot method to call
           transform: an optional value override to pass into the slot method as the first variable
           requires: only call the slot if the value emitted matches the required value or calling required returns True
        """
        if not signal in self.signals:
            print("WARNING: {0} is trying to connect a slot to an undefined signal: {1}".format(self.__class__.__name__,
                                                                                       str(signal)))
            return

        if not hasattr(self, 'connections'):
            self.connections = {}
        connection = self.connections.setdefault(signal, {})
        connection = connection.setdefault(requires, {})
        connection[slot] = transform

    def disconnect(self, signal=None, slot=None, transform=None, requires=None):
        """Removes connection(s) between this objects signal and connected slot(s)

           signal: the signal this class will emit, to cause the slot method to be called
           receiver: the object containing the slot method to be called
           slot: the slot method or function to call
           transform: an optional value override to pass into the slot method as the first variable
           requires: only call the slot method if the value emitted matches this requires
        """
        if slot:
            self.connections[signal][requires].pop(slot, None)
        elif requires is not None:
            self.connections[signal].pop(requires, None)
        elif signal:
            self.connections.pop(signal, None)
        else:
            delattr(self, 'connections')


def accept_arguments(method, number_of_arguments=1):
    """Returns True if the given method will accept the given number of arguments

       method: the method to perform introspection on
       number_of_arguments: the number_of_arguments
    """
    if 'method' in method.__class__.__name__:
        number_of_arguments += 1
        func = getattr(method, 'im_func', getattr(method, '__func__'))
        func_defaults = getattr(func, 'func_defaults', getattr(func, '__defaults__'))
        number_of_defaults = func_defaults and len(func_defaults) or 0
    elif method.__class__.__name__ == 'function':
        func_defaults = getattr(method, 'func_defaults', getattr(method, '__defaults__'))
        number_of_defaults = func_defaults and len(func_defaults) or 0

    coArgCount = getattr(method, 'func_code', getattr(method, '__code__')).co_argcount
    if(coArgCount >= number_of_arguments and coArgCount - number_of_defaults <= number_of_arguments):
        return True

    return False
