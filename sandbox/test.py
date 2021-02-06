# girls = ['Sakura', 'Xino', 'Monica', 'Astolfo']
# guys = ['Serega', 'Vladimir', 'Soslan', 'Naruto']

def findMatches(person):
    for i in person.likeInbox:
        if i in person.likeOutbox:
            print('MATCH!', person.first_name, 'and', i.first_name, 'are dancing from now!')

class Person:
    def __init__(self, first_name, last_name, gender, tgid):
        self.tgid = tgid
        
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender

        self.likeInbox = [] # Лайки челу
        self.likeOutbox = [] # Те, кого чел лайкнул

    def likeBy(self, from_person):
        self.likeInbox.append(from_person.tgid)
        from_person.likeOutbox.append(self.tgid)
        if from_person.tgid in self.likeOutbox:
            print('MATCH!', from_person.first_name, 'and', people[str(self.tgid)].first_name, 'are dancing from now!')

    def toDict(self):
        d = {}
        d['tgid'] = self.tgid

        d['first_name'] = self.first_name
        d['last_name'] = self.last_name
        d['gender'] = self.gender

        d['inbox'] = self.likeInbox
        d['outbox'] = self.likeOutbox

        return d

Naruto = Person('Naruto', 'Uzumaki', True, 1) # Пусть Наруто хочет танцевать с Сакурой и Астольфо

Sakura = Person('Sakura', 'Uzumaki', False, 2) # Сакура не хочет танцевать с Наруто, а Астольфо хочет
Astolfo = Person('Astolfo', 'Nigima', False, 3) 

people = {
    '1' : Naruto,
    '2' : Sakura, 
    '3' : Astolfo
    }

people['1'].likeBy(people['3'])

print("N's turn")

for name in people:
    if people[name].gender == False:
        print(name)
        people[name].likeBy(people['1'])

print(Naruto.toDict())