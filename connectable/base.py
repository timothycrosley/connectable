'''
    Connectable.py

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

    signals = []

    def __init__(self):
        self.connections = None

    def emit(self, signal, value=None):
        """Emits a signal, causing all slot methods connected with the signal to be called (optionally w/ related value)

           signal: the name of the signal to emit, must be defined in the classes 'signals' list.
           value: the value to pass to all connected slot methods.
        """
        results = []
        if self.connections and signal in self.connections:
            for obj, conditions in self.connections[signal].items():

                for condition, values in conditions.items():
                    if condition is None or condition == value:
                        for overrideValue, slots in values.items():
                            if overrideValue is not None:
                                usedValue = overrideValue
                                if isinstance(overrideValue, str):
                                    usedValue = usedValue.replace('${value}', str(value))
                            else:
                                usedValue = value

                            for slot in slots:
                                if not hasattr(obj, slot):
                                    print(obj.__class__.__name__ +
                                            " slot not defined: " + slot)
                                    return False

                                slotMethod = getattr(obj, slot)
                                if usedValue is not None:
                                    if(acceptsArguments(slotMethod, 1)):
                                        results.append(slotMethod(usedValue))
                                    elif(acceptsArguments(slotMethod, 0)):
                                        results.append(slotMethod())
                                    else:
                                        results.append('')

                                else:
                                    results.append(slotMethod())

        return results

    def connect(self, signal, condition, receiver, slot, value=None):
        """Defines a connection between this objects signal and another objects slot

           signal: the signal this class will emit, to cause the slot method to be called.
           condition: only call the slot method if the value emitted matches this condition.
           receiver: the object containing the slot method to be called.
           slot: the name of the slot method to call.
           value: an optional value override to pass into the slot method as the first variable.
        """
        if not signal in self.signals:
            print("%(name)s is trying to connect a slot to an undefined signal: %(signal)s" %
                      {'name':self.__class__.__name__, 'signal':str(signal)})
            return

        if self.connections is None:
            self.connections = {}
        connections = self.connections.setdefault(signal, {})
        connection = connections.setdefault(receiver, {})
        connection = connection.setdefault(condition, {})
        connection = connection.setdefault(value, [])
        if not slot in connection:
            connection.append(slot)

    def disconnect(self, signal=None, condition=None,
                   obj=None, slot=None, value=None):
        """Removes connection(s) between this objects signal and connected slot(s)

           signal: the signal this class will emit, to cause the slot method to be called.
           condition: only call the slot method if the value emitted matches this condition.
           receiver: the object containing the slot method to be called.
           slot: the name of the slot method to call.
           value: an optional value override to pass into the slot method as the first variable.
        """
        if slot:
            connection = self.connections[signal][obj][condition][value]
            connection.remove(slot)
        elif obj:
            self.connections[signal].pop(obj)
        elif signal:
            self.connections.pop(signal, None)
        else:
            self.connections = None


def acceptsArguments(method, number_of_arguments=1):
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
