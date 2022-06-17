import data
from datetime import date, timedelta
import os

class Config():
    def __init__(self):
        self.data = data.Data()
        self.lastSavefile = None
        self.dateFormat = '%d.%m.%Y'
        self.loadConfig()
        if os.path.isfile(self.lastSavefile):
            pass
        self.loadData(self.lastSavefile)
    def loadConfig(self):
        with open('./config.ini', 'r') as file:
            for line in file.readlines():
                parts = line.split()
                if parts[1] == '=':
                    if parts[0] == 'lastSavefile':
                        self.lastSavefile = parts[2].replace('\'', '')
                    elif parts[0] == 'dateFormat':
                        self.dateFormat = parts[2].replace('\'', '')
        file.closed
    def saveConfig(self):
        with open('./config.ini', 'w') as file:
            file.writelines([
                'lastSavefile = \'' + self.lastSavefile + '\'\n',
                'dateFormat = \'' + self.dateFormat + '\''
            ])
        file.closed
    def saveData(self, path):
        with open(path, 'wb') as file:
            file.write(str('DeSh').encode('utf-8'))
            file.write(int(len(self.data.seats)).to_bytes(2, 'big'))
            file.write(int(len(self.data.participants)).to_bytes(2, 'big'))
            file.write(int(len(self.data.assignments)).to_bytes(2, 'big'))
            for seat in iter(self.data.seats):
                file.write(int(seat.x1).to_bytes(2, 'big'))
                file.write(int(seat.y1).to_bytes(2, 'big'))
                file.write(int(seat.x2).to_bytes(2, 'big'))
                file.write(int(seat.y2).to_bytes(2, 'big'))
                file.write(int(seat.rot).to_bytes(2, 'big'))
            for participant in iter(self.data.participants):
                file.write(int(len(participant.firstName)).to_bytes(1, 'big'))
                file.write(str(participant.firstName).encode('utf-16')[2:])
                file.write(int(len(participant.lastName)).to_bytes(1, 'big'))
                file.write(str(participant.lastName).encode('utf-16')[2:])
                file.write(int(participant.entryDate.day).to_bytes(1, 'big'))
                file.write(int(participant.entryDate.month).to_bytes(1, 'big'))
                file.write(int(participant.entryDate.year).to_bytes(2, 'big'))
                file.write(int(participant.exitDate.day).to_bytes(1, 'big'))
                file.write(int(participant.exitDate.month).to_bytes(1, 'big'))
                file.write(int(participant.exitDate.year).to_bytes(2, 'big'))
                file.write(int(len(participant.note)).to_bytes(1, 'big'))
                file.write(str(participant.note).encode('utf-16')[2:])
            for assignment in iter(self.data.assignments):
                file.write(int(self.data.seats.index(assignment.seat)).to_bytes(1, 'big'))
                file.write(int(self.data.participants.index(assignment.participant)).to_bytes(1, 'big'))
                file.write(int(assignment.begin.day).to_bytes(1, 'big'))
                file.write(int(assignment.begin.month).to_bytes(1, 'big'))
                file.write(int(assignment.begin.year).to_bytes(2, 'big'))
                file.write(int(assignment.end.day).to_bytes(1, 'big'))
                file.write(int(assignment.end.month).to_bytes(1, 'big'))
                file.write(int(assignment.end.year).to_bytes(2, 'big'))
        file.closed
    def loadData(self, path):
        new_data = data.Data()
        try:
            with open(path, 'rb') as file:
                if(file.read(4).decode('utf-8') == 'DeSh'):
                    lenSeats = int.from_bytes(file.read(2), 'big')
                    lenParticipants = int.from_bytes(file.read(2), 'big')
                    lenAssignments = int.from_bytes(file.read(2), 'big')
                    for i in range(lenSeats):
                        x1 = int.from_bytes(file.read(2), 'big')
                        y1 = int.from_bytes(file.read(2), 'big')
                        x2 = int.from_bytes(file.read(2), 'big')
                        y2 = int.from_bytes(file.read(2), 'big')
                        rot = int.from_bytes(file.read(2), 'big')
                        new_data.seats.append(data.Seat(x1, y1, x2, y2, rot))
                    for i in range(lenParticipants):
                        lenFirstName = int.from_bytes(file.read(1), 'big')
                        firstName = file.read(2*lenFirstName).decode('utf-16')
                        lenLastName = int.from_bytes(file.read(1), 'big')
                        lastName = file.read(2*lenLastName).decode('utf-16')
                        entryDay = int.from_bytes(file.read(1), 'big')
                        entryMonth = int.from_bytes(file.read(1), 'big')
                        entryYear = int.from_bytes(file.read(2), 'big')
                        exitDay = int.from_bytes(file.read(1), 'big')
                        exitMonth = int.from_bytes(file.read(1), 'big')
                        exitYear = int.from_bytes(file.read(2), 'big')
                        lenNote = int.from_bytes(file.read(1), 'big')
                        note = file.read(2*lenNote).decode('utf-16')
                        new_data.participants.append(data.Participant(firstName, lastName, date(entryYear, entryMonth, entryDay), date(exitYear, exitMonth, exitDay), note))
                    for i in range(lenAssignments):
                        seat = new_data.seats[int.from_bytes(file.read(1), 'big')]
                        participant = new_data.participants[int.from_bytes(file.read(1), 'big')]
                        beginDay = int.from_bytes(file.read(1), 'big')
                        beginMonth = int.from_bytes(file.read(1), 'big')
                        beginYear = int.from_bytes(file.read(2), 'big')
                        endDay = int.from_bytes(file.read(1), 'big')
                        endMonth = int.from_bytes(file.read(1), 'big')
                        endYear = int.from_bytes(file.read(2), 'big')
                        new_data.assignments.append(data.Assignment(participant, seat, date(beginYear, beginMonth, beginDay), date(endYear, endMonth, endDay)))
            self.data = new_data
        except Exception as e:
            print("Can't load File")
            self.data = data.ITLOFT()
        
        self.lastSavefile = path
        self.saveConfig()
        # file.closed


if __name__ == '__main__':
    c = Config()
    c.loadConfig()