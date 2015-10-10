from connectable import Connectable


class Person(Connectable):
    signals = ('says_hello', )

    def __init__(self, name):
        self.name = name

    def say_hello(self, to=None):
        if to:
            print("Hi {to}, this is {name}".format(to=to, name=self.name))
        else:
            print("Hi! This is {name}".format(name=self.name))
        self.emit('says_hello', self.name)


speaker = Person('Tim')
room = (Person('Amanda'), Person('Bob'), Person('Ted'), Person('Sue'))
heckler = Person('The *Real* Timothy')

for person in room:
    speaker.connect('says_hello', person.say_hello)
speaker.connect('says_hello', heckler.say_hello, transform='you horrible imposter')

speaker.say_hello()

