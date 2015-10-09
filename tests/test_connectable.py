'''
    test_Connectable.py

    Tests the functionality of connectable

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
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
'''
from connectable import Connectable

function_called = False


class Value(Connectable):
    signals = ['valueChanged']

    def __init__(self, value):
        super(Value, self).__init__()
        self.value = value

    def set_value(self, value):
        self.value = value
        self.emit('valueChanged', value)

    def clearValue(self):
        self.value = ""

    def too_many_params_to_be_slot(self, param1, param2):
        pass


def set_value_function(value):
    globals()['function_called'] = True


def test_incorrectSignalSlotConnections():
    value1, value2 = (Value(1), Value(2))

    #emit fake signal
    assert value1.emit("fake signal") == []

    #connect using fake signal
    assert value1.connect("fake signal", None, value1, 'set_value') is None

    #connect to fake slot
    value1.connect("valueChanged", None, value1, 'fake slot')
    assert value1.emit('valueChanged') is False


def test_connectWithoutCondition():
    value1, value2 = (Value(1), Value(2))

    #test without value overide
    value1.connect('valueChanged', None, value2, 'set_value')
    value1.set_value("This is a test")
    assert value2.value == "This is a test"
    value1.disconnect()

    #test with value overide
    value1.connect('valueChanged', None, value2, 'set_value', 'I changed the value')
    value1.connect('valueChanged', None, value2, 'call_function', 'I changed the value')
    value2.call_function = set_value_function
    value1.set_value("This is a test")
    assert value2.value == "I changed the value"
    assert function_called == True


def test_connectWithCondition():
    value1, value2 = (Value(1), Value(2))

    #test without value overide
    value1.connect('valueChanged', 'Hello', value2, 'set_value')
    value1.set_value('Goodbye')
    assert value2.value == 2
    value1.set_value('Hello')
    assert value2.value == 'Hello'
    value1.disconnect()

    #test with value overide
    value1.connect('valueChanged', 'Hello',
                        value2, 'set_value', 'Goodbye')
    value1.set_value('Goodbye')
    assert value2.value == 'Hello'
    value1.set_value('Hello')
    assert value2.value == 'Goodbye'

    #Test on slot that takes no arguments
    value1.connect('valueChanged', 'Die!!', value2, 'clearValue')
    assert value1.emit('valueChanged', 'Die!!') == [None]
    value1.connect('valueChanged', None, value2, 'clearValue')
    assert value1.emit('valueChanged') == [None]
    value1.disconnect()

    #Test method with too many params to be a slot
    value1.connect('valueChanged', 'False', value2, 'too_many_params_to_be_slot')
    assert value1.emit('valueChanged', 'False') == ['']


def test_disconnect():
    value1, value2 = (Value(1), Value(2))

    value1.connect('valueChanged', None, value2, 'set_value')
    value1.set_value('It changes the value')
    assert value2.value == 'It changes the value'

    value1.disconnect('valueChanged', None, value2, 'set_value')
    value1.set_value('But not anymore')
    assert value2.value == 'It changes the value'

    value1.connect('valueChanged', None, value2, 'set_value')
    value1.disconnect('valueChanged', None, value2)
    value1.set_value('Still Wont')
    assert value2.value == 'It changes the value'

    value1.connect('valueChanged', None, value2, 'set_value')
    value1.disconnect('valueChanged')
    value1.set_value('Still Wont')
    assert value2.value == 'It changes the value'
