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
    '''A basic example connectable object, that can be used for testing'''
    signals = ['valueChanged']

    def __init__(self, value):
        super(Value, self).__init__()
        self.value = value

    def set_value(self, value):
        self.value = value
        self.emit('valueChanged', value)

    def clear_value(self):
        self.value = ""

    def too_many_params_to_be_slot(self, param1, param2):
        pass


def set_value_function(value):
    '''Sets a global variable to enable ensuring functions can be called as slots'''
    globals()['function_called'] = True


def test_incorrect_signal_slot_connections():
    '''Test to ensure that connectable elegantly handles mis-formed connections'''
    value1, value2 = (Value(1), Value(2))

    #emit fake signal
    assert value1.emit("fake signal") == True

    #connect using fake signal
    assert value1.connect("fake signal", value1.set_value) is None


def test_connect_without_condition():
    '''Test that basic connections (without conditions) work as expected'''
    value1, value2 = (Value(1), Value(2))

    #test without value overide
    value1.connect('valueChanged', value2.set_value)
    value1.set_value("This is a test")
    assert value2.value == "This is a test"
    value1.disconnect()

    #test with value override
    value1.connect('valueChanged', value2.set_value, 'I changed the value')
    value1.connect('valueChanged', set_value_function)
    value1.set_value("This is a test")
    assert value2.value == "I changed the value"
    assert function_called == True

    #test with int value override
    value1.connect('valueChanged', value2.set_value, 2)
    value1.set_value("This is a test")
    assert value2.value == 2

    #test with function value override
    value1.connect('valueChanged', value2.set_value, lambda value: value + ' for humanity!')
    value1.set_value("This is a test")
    assert value2.value == 'This is a test for humanity!'


def test_connect_with_condition():
    '''Test to ensure its possible to quickly, conditionally make connections'''
    value1, value2 = (Value(1), Value(2))

    #test without value overide
    value1.connect('valueChanged', value2.set_value, requires='Hello')
    value1.set_value('Goodbye')
    assert value2.value == 2
    value1.set_value('Hello')
    assert value2.value == 'Hello'
    value1.disconnect()

    #test with value overide
    value1.connect('valueChanged', value2.set_value, requires='Hello', transform='Goodbye')
    value1.set_value('Goodbye')
    assert value2.value == 'Hello'
    value1.set_value('Hello')
    assert value2.value == 'Goodbye'

    #test on slot that takes no arguments
    value1.connect('valueChanged', value2.clear_value, requires='Die!!')
    assert value1.emit('valueChanged', 'Die!!', gather=True) == [None]
    value1.disconnect('valueChanged', requires='Die!!')
    assert value1.emit('valueChanged', 'Die!!', gather=True) == []
    value1.connect('valueChanged', value2.clear_value)
    assert value1.emit('valueChanged', gather=True) == [None]
    value1.disconnect()

    #test method with too many params to be a slot
    value1.connect('valueChanged', value2.too_many_params_to_be_slot, requires='False')
    assert value1.emit('valueChanged', 'False', gather=True) == ['']


def test_disconnect():
    '''Test to ensure that it is possible to disconnect previously made connections'''
    value1, value2 = (Value(1), Value(2))

    value1.connect('valueChanged', value2.set_value)
    value1.set_value('It changes the value')
    assert value2.value == 'It changes the value'

    value1.disconnect('valueChanged', value2.set_value)
    value1.set_value('But not anymore')
    assert value2.value == 'It changes the value'

    value1.connect('valueChanged', value2.set_value)
    value1.disconnect('valueChanged', value2.set_value)
    value1.set_value('Still Wont')
    assert value2.value == 'It changes the value'

    value1.connect('valueChanged', value2.set_value)
    value1.disconnect('valueChanged')
    value1.set_value('Still Wont')
    assert value2.value == 'It changes the value'
