from datetime import date, timedelta
from PIL import ImageOps, ImageTk, Image
import tkinter as tk
from os import path
rootDir = path.dirname(path.abspath(__file__))

class Data():
    def __init__(self):
        self.participants = []
        self.seats = []
        self.assignments = []
        self.roomFile = ''
        self.scale = 1
    def stringToDate(self, string):
        string = str(string)
        if string.count('.') == 2:
            stringParts = string.split('.')
            dayString = stringParts[0]
            monthString = stringParts[1]
            yearString = stringParts[2]
        elif string.count('/') == 2:
            stringParts = string.split('/')
            dayString = stringParts[1]
            monthString = stringParts[0]
            yearString = stringParts[2]
        elif string.count('-') == 2:
            stringParts = string.split('-')
            dayString = stringParts[2]
            monthString = stringParts[1]
            yearString = stringParts[0]
        else:
            return Error('Kein gültiges Datumsformat')
        if dayString.isdecimal():
            day = int(dayString)
            if day >= 1 and day <= 31:
                if monthString.isdecimal():
                    month = int(monthString)
                    if month >= 1 and month <= 12:
                        if yearString.isdecimal():
                            year = int(yearString)
                            if year <= 9999:
                                return date(year, month, day)
        return Error('Kein gültiges Datum')
                
    def addParticipant(self, firstName, lastName, entryDate, exitDate, seat=None, note=''):
        entryDate = self.stringToDate(entryDate)
        if isinstance(entryDate, Error):
            return Error('Eintrittsdatum: ') + entryDate
        exitDate = self.stringToDate(exitDate)
        if isinstance(exitDate, Error):
            return Error('Austrittsdatum: ') + exitDate
        self.participants.append(Participant(firstName, lastName, entryDate, exitDate, seat, note))
        return None  
    def editParticipant(self, participant, firstName, lastName, entryDate, exitDate, note=''):
        entryDate = self.stringToDate(entryDate)
        if isinstance(entryDate, Error):
            return Error('Eintrittsdatum: ') + entryDate
        exitDate = self.stringToDate(exitDate)
        if isinstance(exitDate, Error):
            return Error('Austrittsdatum: ') + exitDate
        participant.doAssignmentsByTime(entryDate, exitDate, self.removeAssignment, True)
        participant.firstName = firstName
        participant.lastName = lastName
        participant.entryDate = entryDate
        participant.exitDate = exitDate
        participant.note = note
    def moveParticipant(self, participant, newSeat, beginDate, endDate):
        beginDate = self.stringToDate(beginDate)
        if isinstance(beginDate, Error):
            return Error('Anfangsdatum: ') + beginDate
        elif beginDate < participant.entryDate:
            beginDate = participant.entryDate
            print("Zeitraum vor Eintrittsdatum nicht gültig, setze Zeitraumsanfang zu Eintrittsdatum des Teilnehmers")
            # return Error('Zeitraum kann nicht vor Eintrittsdatum des Teilnehmers sein.')
        endDate = self.stringToDate(endDate)
        if isinstance(endDate, Error):
            return Error('Enddatum: ') + endDate
        elif endDate > participant.exitDate:
            endDate = participant.exitDate
            print("Zeitraum nach Eintrittsdatum nicht gültig, setze Zeitraumsende zu Austrittsdatum des Teilnehmers")
            # return Error('Zeitraum kann nicht nach Austrittsdatum des Teilnehmers sein.')
        if len(newSeat.getAssignmentsByTime(beginDate, endDate)) > 0:
            return Error('Es können nicht mehrere Teilnehmer im selben Zeitraum an einem Platz sitzen.')

        participant.doAssignmentsByTime(beginDate, endDate, self.removeAssignment)
        participant.seat = newSeat
        self.assignments.append(Assignment(participant, newSeat, beginDate, endDate))
    def getSeat(self, x, y):
        for seat in iter(self.seats):
            if seat.x1 < x and seat.x2 > x and seat.y1 < y and seat.y2 > y:
                return seat
        return None
    def removeAssignment(self, assignment, beginDate, endDate, exclude=False):
        if exclude:
            if assignment.end <= beginDate or assignment.begin >= endDate:
                assignment.seat.assignments.remove(assignment)
                assignment.participant.assignments.remove(assignment)
                self.assignments.remove(assignment)
            elif assignment.begin < beginDate:
                assignment.begin = beginDate
            elif assignment.end > endDate:
                assignment.end = endDate
        else:
            collisionBegin = assignment.begin >= beginDate and assignment.begin <= endDate
            collisionEnd = assignment.end >= beginDate and assignment.end <= endDate
            if collisionBegin and collisionEnd:
                assignment.seat.assignments.remove(assignment)
                assignment.participant.assignments.remove(assignment)
                self.assignments.remove(assignment)
            elif collisionBegin and not collisionEnd:
                assignment.begin = endDate + timedelta(days=1)
            elif not collisionBegin and collisionEnd:
                assignment.end = beginDate - timedelta(days=1)
    def removeParticipant(self, number=None, participant = None):
        if number!=None:
            for assignment in self.participants[number].assignments:
                assignment.seat.assignments.remove(assignment)
                self.assignments.remove(assignment)
        self.participants.remove(self.participants[number])
        
    def removeParticipantFromSeat(self, participant, newSeat, beginDate, endDate):
        beginDate = self.stringToDate(beginDate)
        if isinstance(beginDate, Error):
            return Error('Anfangsdatum: ') + beginDate
        elif beginDate < participant.entryDate:
            return Error('Zeitraum kann nicht vor Eintrittsdatum des Teilnehmers sein.')
        endDate = self.stringToDate(endDate)
        if isinstance(endDate, Error):
            return Error('Enddatum: ') + endDate
        elif endDate > participant.exitDate:
            return Error('Zeitraum kann nicht nach Austrittsdatum des Teilnehmers sein.')
        if len(newSeat.getAssignmentsByTime(beginDate, endDate)) > 0:
            return Error('Es können nicht mehrere Teilnehmer im selben Zeitraum an einem Platz sitzen.')

        participant.doAssignmentsByTime(beginDate, endDate, self.removeAssignment)
        self.assignments.append(Assignment(participant, newSeat, beginDate, endDate))

class Participant():
    def __init__(self, firstName, lastName, entryDate, exitDate, seat=None, note=''):
        self.firstName = firstName
        self.lastName = lastName
        self.entryDate = entryDate
        self.exitDate = exitDate
        self.seat = seat
        self.note = note
        self.assignments = []
        self.textIDs = []
    def doAssignmentsByTime(self, beginDate, endDate, func, exclude=False):
        for assignment in iter(self.assignments):
            func(assignment, beginDate, endDate, exclude)
    def draw(self, rel, font, canvas:tk.Canvas, x1,x2,y1,y2):
        x = x1*rel+(x2*rel-x1*rel)/2
        height =  ((y2-y1)/2)*rel# - (font.cget('size')*3)*rel
        yName = y1*rel+font.cget('size')*0.5 + height
        yNote = y1*rel+font.cget('size')*1.5 + height
        yEntry = y1*rel+font.cget('size')*2.5 + height
        yExit = y1*rel+font.cget('size')*3.5 + height

        self.textIDs = []
        self.textIDs.append(canvas.create_text(x, yName, text=self.lastName, font=font, fill='#EEEEEE'))
        self.textIDs.append(canvas.create_text(x, yNote, text=self.note, font=font, fill='#EEEEEE'))
        self.textIDs.append(canvas.create_text(x, yEntry, text=self.entryDate.strftime('%d.%m.%Y'), font=font, fill='#00FF00'))
        self.textIDs.append(canvas.create_text(x, yExit, text=self.exitDate.strftime('%d.%m.%Y'), font=font, fill='#FF0000'))
        
        

class Seat():
    def __init__(self, x1, y1, x2, y2, rot=0):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.assignments = []
        self.rot = rot
        self.img = Image.open(path.join(rootDir, 'img', 'Desk.png')).convert()
        self.img_id = None

    def getParticipant(self, date):
        for assignment in iter(self.assignments):
            if assignment.begin < date and assignment.end > date:
                return assignment.participant
        return None
    def getAssignmentsByTime(self, beginDate, endDate):
        assignments = []
        for assignment in iter(self.assignments):
            if (assignment.begin > beginDate and assignment.begin < endDate) or (assignment.end > beginDate and assignment.end < endDate):
                assignments.append(assignment)
        return assignments
    def doAssignmentsByTime(self, beginDate, endDate, func):
        for assignment in iter(self.assignments):
            func(assignment, beginDate, endDate)
    def draw(self, canvas:tk.Canvas, scale = 1):
        img = self.img.rotate(self.rot*90,resample=Image.NEAREST)
        self.image_resized=ImageTk.PhotoImage(ImageOps.scale(img, canvas.rel * scale))
        self.img_id = canvas.create_image((self.x1)*canvas.rel,(self.y1)*canvas.rel, image=self.image_resized, anchor=tk.NW)
        
    # def move(self, x:int, y:int):
    #     pass

class Assignment():
    def __init__(self, participant, seat, begin, end):
        self.participant = participant
        self.seat = seat
        self.begin = begin
        self.end = end
        participant.assignments.append(self)
        seat.assignments.append(self)

class Error():
    def __init__(self, message):
        self.message = message
    def __add__(self, error2):
        return Error(self.message + error2.message)

class ITLOFT(Data):
    def __init__(self):
        super().__init__()
        self.roomFile = 'ITloft.png'
        self.seats.append(Seat(161, 362, 255, 497, 3))
        self.seats.append(Seat(258, 362, 352, 497, 1))
        self.seats.append(Seat(161, 596, 255, 731, 3))
        self.seats.append(Seat(258, 596, 352, 731, 1))
        self.seats.append(Seat(161, 884, 255, 1019, 3))
        self.seats.append(Seat(258, 884, 352, 1019, 1))
        self.seats.append(Seat(630, 569, 765, 663, 2))
        self.seats.append(Seat(630, 666, 765, 760, 0))
        self.seats.append(Seat(768, 597, 862, 732, 1))
        self.seats.append(Seat(1113, 742, 1248, 836, 0))
        self.seats.append(Seat(1113, 645, 1248, 739, 2))
        self.seats.append(Seat(1394, 742, 1529, 836, 0))
        self.seats.append(Seat(1394, 645, 1529, 739, 2))
        self.seats.append(Seat(1396, 264, 1531, 358, 2))
        self.seats.append(Seat(1113, 264, 1248, 358, 2))
        self.seats.append(Seat(976, 232, 1069, 367, 3))
        self.seats.append(Seat(975, 37, 1068, 172, 3))
        self.seats.append(Seat(627, 232, 721, 367, 1))
        self.seats.append(Seat(627, 37, 721, 172, 1))