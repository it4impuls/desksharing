import calendar
import tkinter as tk, tkinter.ttk as ttk
import math, data, config
from tkinter import messagebox, font, filedialog
from datetime import date, timedelta
from PIL import ImageOps, ImageTk, Image
from tkcalendar import Calendar, DateEntry

rootDir = './'
imgDir = rootDir + 'img/'
iconDir = imgDir + 'icons/'

class View(tk.Tk):
    def __init__(self):
        super().__init__()
        super().focus_set()

        self.config = config.Config()

        self.title('DeskShare')

        self.showSeat = None #self.config.data
        self.showParticipant = None
        self.draggedParticipant = None
        self.draggedTo = None
        self.timeMode = False
        self.showDate = date.today()

        self.mainframe = MainFrame(self)
        self.bind('<Configure>', self.resize)
        self.bind('<<OpenAddParticipantDialog>>', self.openAddParticipantDialog)
        self.bind_all('<<AddParticipant>>', self.addParticipant)
        self.bind('<<OpenMoveParticipantDialog>>', self.openMoveParticipantDialog)
        self.bind('<<ClickedOnRoommap>>', self.onClickOnRoommap)
        self.bind('<<ReleasedOnRoomMap>>', self.onReleaseOnRoommap)
        self.bind_all('<<MoveParticipant>>', self.moveParticipant)
        self.bind('<<OpenSaveAsDialog>>', self.openSaveAsDialog)
        self.bind('<<OpenOpenDialog>>', self.openOpenDialog)
        self.bind('<<NewFile>>', self.newFile)
        self.bind('<<OpenEditParticipantDialog>>', self.openEditParticipantDialog)
        self.bind_all('<<EditParticipant>>', self.editParticipant)
        self.bind('<<RemoveParticipant>>', self.removeParticpant)

        self.oldWidth = self.winfo_width()
        self.oldHeight = self.winfo_height()
    def resize(self, event):
        if event.width != self.oldWidth or event.height != self.oldHeight:
            self.oldWidth = event.width
            self.oldHeight = event.height
            self.draw()
    def draw(self):
        self.mainframe.roommap.draw()
        self.mainframe.roommap.pack(fill='both', expand=True)
        self.mainframe.pack(fill='both', expand=True)
    def onClickOnRoommap(self, event):
        if event.data.num in [1, 3]:
            seat = self.config.data.getSeat(event.data.x, event.data.y)
            if seat != None:
                participant = seat.getParticipant(self.showDate)
                if participant != None:
                    self.draggedParticipant = participant
    def onReleaseOnRoommap(self, event):
        newSeat = self.config.data.getSeat(event.data.x, event.data.y)
        if self.draggedParticipant == None:
            self.showSeat = newSeat
        else:
            if newSeat == None:
                self.showSeat = None
                self.draggedParticipant = None
            else:
                self.draggedTo = newSeat
                if newSeat.getParticipant(self.showDate) == self.draggedParticipant:
                    if event.data.num == 1:
                        self.showSeat = newSeat
                        self.draggedParticipant = None
                    elif event.data.num == 3:
                        #Kontextmenü
                        pass
                else:
                    if event.data.num == 1:
                        tk.Event.data = [1, self.draggedParticipant.entryDate, self.draggedParticipant.exitDate, False]
                        self.event_generate('<<MoveParticipant>>')
                    elif event.data.num == 3:
                        self.draggedTo = newSeat
                        self.event_generate('<<OpenMoveParticipantDialog>>')
        self.draw()
    def openAddParticipantDialog(self, event):
        self.addParticipantDialog = AddParticipantDialog()
    def closeAddParticipantDialog(self):
        self.addParticipantDialog.destroy()
    def addParticipant(self, event):
        isAdded = self.config.data.addParticipant(event.data[0], event.data[1], event.data[2], event.data[3], note=event.data[4])
        if isinstance(isAdded, data.Error):
            messagebox.showerror("Error", isAdded.message)
        else:
            self.closeAddParticipantDialog()
            self.mainframe.sidebar.refresh()
    def openMoveParticipantDialog(self, event):
        newSeat = self.config.data.getSeat(event.data.x, event.data.y)
        if newSeat != None:
            self.moveParticipantDialog = MoveParticipantDialog(self.draggedParticipant)
    def closeMoveParticipantDialog(self):
        self.moveParticipantDialog.destroy()
    def moveParticipant(self, event):
        if event.data[0] == 1:
            self.config.data.moveParticipant(self.draggedParticipant, self.draggedTo, event.data[1], event.data[2])
        if event.data[3]:
            self.closeMoveParticipantDialog()
        self.draggedParticipant = None
        self.draggedTo = None
        self.draw()
    def newFile(self, event):
        self.config.data = data.ITLOFT()
        self.showSeat = None
        self.draw()
        self.mainframe.sidebar.refresh()
        self.mainframe.roommap.refresh()
    def openOpenDialog(self, event):
        loadfile = filedialog.askopenfilename(filetypes=(('save files','*.sav'),('all files','*.*')))
        self.config.loadData(loadfile)
        self.showSeat = None
        self.draw()
        self.mainframe.sidebar.refresh()
        self.mainframe.roommap.refresh()
    def openSaveAsDialog(self, event):
        savefile = filedialog.asksaveasfilename(filetypes=(('save files','*.sav'),('all files','*.*')), defaultextension='.sav')
        self.config.saveData(savefile)
    def openEditParticipantDialog(self, event):
        self.editParticipantDialog = EditParticipantDialog(event.data)
    def editParticipant(self, event):
        isEdited = self.config.data.editParticipant(event.data[0], event.data[1], event.data[2], event.data[3], event.data[4], note=event.data[5])
        if isinstance(isEdited, data.Error):
            messagebox.showerror("Error", isEdited.message)
        else:
            self.closeEditParticipantDialog()
            self.mainframe.sidebar.refresh()
    def closeEditParticipantDialog(self):
        self.editParticipantDialog.destroy()
    def removeParticpant(self, event):
        self.config.data.removeParticipant(int(self.mainframe.sidebar.table.selection()[0]))
        self.draw()
        self.mainframe.sidebar.refresh()


class MainFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        self.master = master
        self.roommap = Roommap(self)
        #self.menubar = MenuBar(self.master)
        self.toolbar = ToolBar(self.master)
        self.sidebar = SideBar(self.master)
class MenuBar(tk.Menu):
    def __init__(self, master):
        super().__init__(master)
        master.config(menu=self)

        fileMenu = tk.Menu(self, tearoff=0)
        fileMenu.add_command(label='New', underline=0, command=lambda: self.master.event_generate('<<NewFile>>'))
        fileMenu.add_command(label='Öffnen', underline=0, command=lambda: self.master.event_generate('<<OpenOpenDialog>>'))
        fileMenu.add_command(label='Speichern', underline=0)
        fileMenu.add_command(label='Speichern unter', underline=5, command=lambda: self.master.event_generate('<<OpenSaveAsDialog>>'))
        fileMenu.add_command(label='Beenden', underline=0, command=self.quit)
        self.add_cascade(label='Datei', underline=0, menu=fileMenu)

        editMenu = tk.Menu(self, tearoff=0)
        self.add_cascade(label='Bearbeiten', underline=0, menu=editMenu)

        viewMenu = tk.Menu(self, tearoff=0)
        self.add_cascade(label='Ansicht', underline=0, menu=viewMenu)

        helpMenu = tk.Menu(self, tearoff=0)
        self.add_cascade(label='?', underline=0, menu=helpMenu)
class ToolBar(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bd=1, relief=tk.RAISED)
        self.addButton('doc_new_icon&24.png', '<<NewFile>>')
        self.addButton('folder_open_icon&24.png', '<<OpenOpenDialog>>')
        self.addButton('save_icon&24.png', '<<OpenSaveAsDialog>>')
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill='y')
        self.addButton('doc_plus_icon&24.png', '<<OpenAddParticipantDialog>>')
        self.addButton('doc_minus_icon&24.png', '<<RemoveParticipant>>')
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill='y')

        self.dateText =  DateEntry(self, width=10, date_pattern = 'dd.mm.yyyy')
        self.dateText.pack(side=tk.LEFT, padx=2, pady=1)
        self.dateText.bind('<<DateEntrySelected>>', self.applyDate)
        self.dateText.bind('<Return>', self.applyDate)
        self.dateText.bind('<FocusOut>', self.applyDate)

        self.pack(side=tk.TOP, fill=tk.X)
        self.update()
        
    def addButton(self, iconFilename, eventName):
        icon = ImageTk.PhotoImage(Image.open(iconDir + iconFilename))
        button = tk.Button(self, image=icon, relief=tk.FLAT, command=lambda: self.event_generate(eventName))
        button.image = icon
        button.pack(side=tk.LEFT, padx=2, pady=1)
    def applyDate(self, event):
        self.master.showDate = self.master.config.data.stringToDate(self.dateText.get_date())
        self.focus_set()
        self.master.draw()
class SideBar(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bd=1, relief=tk.RAISED)
        self.bind('<<Button>>', self.onClick)

        self.table = ttk.Treeview(self, columns=('Name', 'StartDate', 'EndDate'), selectmode='browse')
        self.table.column('#0', width=0, minwidth=0, stretch=tk.NO)
        self.table.column('Name', width=150, minwidth=150, stretch=tk.NO)
        self.table.column('StartDate', width=100, minwidth=100, stretch=tk.NO)
        self.table.column('EndDate', width=100, minwidth=100, stretch=tk.NO)
        
        self.table.heading('Name', text='Name', anchor=tk.W)
        self.table.heading('StartDate', text='Eintrittsdatum', anchor=tk.W)
        self.table.heading('EndDate', text='Austrittsdatum', anchor=tk.W)

        self.table.bind('<Button>', self.onClick)
        self.table.bind('<ButtonRelease>', self.onRelease)
        self.table.bind('<Double-Button-1>', self.onDoubleClick)

        self.firstNameFields = []
        self.lastNameFields = []

        self.refresh()

        self.table.pack(side=tk.TOP, fill=tk.X)
        self.pack(side=tk.RIGHT, fill=tk.Y)


    def refresh(self):
        for row in self.table.get_children():
            self.table.delete(row)
        if self.master.showSeat == None:
            for i in range(len(self.master.config.data.participants)):
                self.table.insert('', 'end', i, values=((self.master.config.data.participants[i].lastName + ', ' + self.master.config.data.participants[i].firstName), self.master.config.data.participants[i].entryDate.strftime('%d.%m.%Y'), self.master.config.data.participants[i].exitDate.strftime('%d.%m.%Y')))
        else:
            for i in range(len(self.master.showSeat.assignments)):
                self.table.insert('', 'end', i, values=((self.master.showSeat.assignments[i].participant.lastName + ', ' + self.master.showSeat.assignments[i].participant.firstName), self.master.showSeat.assignments[i].begin.strftime('%d.%m.%Y'), self.master.showSeat.assignments[i].end.strftime('%d.%m.%Y')))
    def onClick(self, event):
        if self.table.identify_row(event.y) != '':
            clickedOn = int(self.table.identify_row(event.y))
            if self.master.showSeat == None:
                self.master.draggedParticipant = self.master.config.data.participants[clickedOn]
            else:
                self.master.draggedParticipant = self.master.showSeat.assignments[clickedOn].participant
        else:
            self.master.draggedParticipant = None
    def onRelease(self, event):
        event.x = (event.x_root-self.master.mainframe.roommap.winfo_rootx())/self.master.mainframe.roommap.rel
        event.y = (event.y_root-self.master.mainframe.roommap.winfo_rooty())/self.master.mainframe.roommap.rel
        tk.Event.data = event
        self.event_generate('<<ReleasedOnRoomMap>>')
    def onDoubleClick(self, event):
        if self.table.identify_row(event.y) != '':
            clickedOn = int(self.table.identify_row(event.y))
            if self.master.showSeat == None:
                tk.Event.data = self.master.config.data.participants[clickedOn]
            else:
                tk.Event.data = self.master.showSeat.assignments[clickedOn].participant
            self.event_generate('<<OpenEditParticipantDialog>>')
        else:
            self.master.draggedParticipant = None
        

class Roommap(tk.Canvas):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.refresh()
        
        self.bind('<Button>', self.onClick)
        self.bind('<ButtonRelease>', self.onRelease)
    def refresh(self):
        self.roomImg = Image.open('./room.png')
        for seat in self.master.master.config.data.seats:
            self.roomImg = seat.draw(self.roomImg)
    def draw(self):
        self.update()
        relH = self.winfo_height()/self.roomImg.height
        relW = self.winfo_width()/self.roomImg.width
        self.rel = min(relW, relH)
        self.roomImgResized = ImageTk.PhotoImage(ImageOps.scale(self.roomImg, self.rel))
        
        super().create_image(0, 0, anchor=tk.NW, image=self.roomImgResized)
        self.font = font.Font(family='Helvetica', size=int(-20*self.rel))
        for seat in iter(self.master.master.config.data.seats):
            # seat.draw(self, self.rel)
            for assignment in iter(seat.assignments):
                if assignment.begin <= self.master.master.showDate and assignment.end >= self.master.master.showDate:
                    self.drawParticipant(seat, assignment.participant)
    def drawParticipant(self, seat, participant):
        x = seat.x1*self.rel+(seat.x2*self.rel-seat.x1*self.rel)/2
        yName = seat.y1*self.rel-self.font.cget('size')*0.5
        yNote = seat.y1*self.rel-self.font.cget('size')*1.5
        yEntry = seat.y1*self.rel-self.font.cget('size')*2.5
        yExit = seat.y1*self.rel-self.font.cget('size')*3.5
        super().create_text(x, yName, text=participant.lastName, font=self.font, fill='#FFFFFF')
        super().create_text(x, yNote, text=participant.note, font=self.font, fill='#FFFFFF')
        super().create_text(x, yEntry, text=participant.entryDate.strftime('%d.%m.%Y'), font=self.font, fill='#00FF00')
        super().create_text(x, yExit, text=participant.exitDate.strftime('%d.%m.%Y'), font=self.font, fill='#FF0000')
        if self.master.master.showSeat != None:
            super().create_rectangle(self.master.master.showSeat.x1*self.rel, self.master.master.showSeat.y1*self.rel, self.master.master.showSeat.x2*self.rel, self.master.master.showSeat.y2*self.rel, width=2, outline='#FF0000')

    def onClick(self, event):
        event.x = event.x/self.rel
        event.y = event.y/self.rel
        tk.Event.data = event
        self.event_generate('<<ClickedOnRoommap>>')
    def onRelease(self, event):
        event.x = event.x/self.rel
        event.y = event.y/self.rel
        tk.Event.data = event
        self.event_generate('<<ReleasedOnRoomMap>>')


class AddParticipantDialog(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title('Neuer Teilnehmer')
        self.grab_set()
        self.resizable(height=0, width=0)
        _width = 30

        firstNameLabel = tk.Label(self, text='Vorname', justify=tk.LEFT)
        firstNameLabel.grid(row=0, column=0, sticky=tk.W, pady=1)

        firstNameField = tk.Entry(self, width=_width)
        firstNameField.grid(row=0, column=1, pady=1)

        lastNameLabel = tk.Label(self, text='Nachname', justify=tk.LEFT)
        lastNameLabel.grid(row=1, column=0, sticky=tk.W, pady=1)

        lastNameField = tk.Entry(self, width=_width, borderwidth=1, )
        lastNameField.grid(row=1, column=1, pady=1)
        
        entryDateLabel = tk.Label(self, text='Eintritt', justify=tk.LEFT)
        entryDateLabel.grid(row=2, column=0, sticky=tk.W, pady=1)

        entryDateField = DateEntry(self, width=_width-3, date_pattern = 'dd.mm.yyyy')
        entryDateField.grid(row=2, column=1, pady=1)

        exitDateLabel = tk.Label(self, text='Austritt', justify=tk.LEFT)
        exitDateLabel.grid(row=3, column=0, sticky=tk.W, pady=1)

        exitDateField = DateEntry(self, width=_width-3, date_pattern = 'dd.mm.yyyy')
        exitDateField.set_date(date(date.today().year+2, date.today().month, date.today().day+1))
        exitDateField.grid(row=3, column=1, pady=1)

        noteLabel = tk.Label(self, text='Notiz')
        noteLabel.grid(row=4, column=0, sticky=tk.W, pady=1)

        noteField = tk.Entry(self, width=_width)
        noteField.grid(row=4, column=1, pady=1)
        
        addButton = tk.Button(self, text='Hinzufügen', command=lambda: self.tryAddParticipant(firstNameField.get(), lastNameField.get(), entryDateField.get(), exitDateField.get(), noteField.get()))
        addButton.grid(row=5, column=0, pady=1)

        cancelButton = tk.Button(self, text='Abbrechen', command=self.destroy)
        cancelButton.grid(row=5, column=1, pady=1)
    def tryAddParticipant(self, firstName, lastName, entryDate, exitDate, note=''):
        tk.Event.data = [firstName, lastName, entryDate, exitDate, note]
        self.event_generate('<<AddParticipant>>')
    
class EditParticipantDialog(tk.Toplevel):
    def __init__(self, participant):
        super().__init__()
        self.title('Teilnehmer bearbeiten')
        self.grab_set()
        self.resizable(height=0, width=0)

        firstNameLabel = tk.Label(self, text='Vorname', justify=tk.LEFT)
        firstNameLabel.grid(row=0, column=0, sticky=tk.W)

        firstNameField = tk.Entry(self, width=30)
        firstNameField.grid(row=0, column=1)
        firstNameField.insert('end', participant.firstName)

        lastNameLabel = tk.Label(self, text='Nachname', justify=tk.LEFT)
        lastNameLabel.grid(row=1, column=0, sticky=tk.W)

        lastNameField = tk.Entry(self, width=30)
        lastNameField.grid(row=1, column=1)
        lastNameField.insert('end', participant.lastName)
        
        entryDateLabel = tk.Label(self, text='Eintritt', justify=tk.LEFT)
        entryDateLabel.grid(row=2, column=0, sticky=tk.W)

        entryDateField = tk.Entry(self, width=30)
        entryDateField.grid(row=2, column=1)
        entryDateField.insert('end', participant.entryDate.strftime('%d.%m.%Y'))

        exitDateLabel = tk.Label(self, text='Austritt', justify=tk.LEFT)
        exitDateLabel.grid(row=3, column=0, sticky=tk.W)

        exitDateField = tk.Entry(self, width=30)
        exitDateField.grid(row=3, column=1)
        exitDateField.insert('end', participant.exitDate.strftime('%d.%m.%Y'))

        noteLabel = tk.Label(self, text='Notiz')
        noteLabel.grid(row=4, column=0, sticky=tk.W)

        noteField = tk.Entry(self, width=30)
        noteField.grid(row=4, column=1)
        noteField.insert('end', participant.note)
        
        addButton = tk.Button(self, text='Ändern', command=lambda: self.tryEditParticipant(participant, firstNameField.get(), lastNameField.get(), entryDateField.get(), exitDateField.get(), noteField.get()))
        addButton.grid(row=5, column=0)

        cancelButton = tk.Button(self, text='Abbrechen', command=self.destroy)
        cancelButton.grid(row=5, column=1)   
    def tryEditParticipant(self, participant, firstName, lastName, entryDate, exitDate, note=''):
        tk.Event.data = [participant, firstName, lastName, entryDate, exitDate, note]
        self.event_generate('<<EditParticipant>>')     

class MoveParticipantDialog(tk.Toplevel):
    def __init__(self, participant):
        super().__init__()
        self.title('Teilnehmer umziehen')
        self.grab_set()
        self.resizable(height=0, width=0)
        self.checked = tk.IntVar()

        tk.Radiobutton(self, text='Umsetzen', padx=20, variable=self.checked, value=1, command=self.activateEntries).grid(row=0, column=0)
        tk.Radiobutton(self, text='Nichts tun', padx=20, variable=self.checked, value=0, command=self.deactivateEntries).grid(row=4, column=0)

        self.beginText = tk.Label(self, justify=tk.LEFT, padx=10, text='Zeitraum von', state=tk.DISABLED)
        self.beginText.grid(row=2, column=0)

        self.endText = tk.Label(self, justify=tk.LEFT, text='bis', state=tk.DISABLED)
        self.endText.grid(row=2, column=1)

        self.beginField = tk.Entry(self, width=10)
        self.beginField.grid(row=3, column=0)
        self.beginField.insert(0, participant.entryDate.strftime('%d.%m.%Y'))
        self.beginField['state'] = tk.DISABLED

        self.endField = tk.Entry(self, width=10)
        self.endField.grid(row=3, column=1)
        self.endField.insert(0, participant.exitDate.strftime('%d.%m.%Y'))
        self.endField['state'] = tk.DISABLED

        okButton = tk.Button(self, text='OK', command=self.tryMoveParticipant)
        okButton.grid(row=5, column=0)

        cancelButton = tk.Button(self, text='Cancel', command=self.destroy)
        cancelButton.grid(row=5, column=1)

    def activateEntries(self):
        self.beginText['state'] = tk.NORMAL
        self.endText['state'] = tk.NORMAL
        self.beginField['state'] = tk.NORMAL
        self.endField['state'] = tk.NORMAL
    def deactivateEntries(self):
        self.beginText['state'] = tk.DISABLED
        self.endText['state'] = tk.DISABLED
        self.beginField['state'] = tk.DISABLED
        self.endField['state'] = tk.DISABLED
    def tryMoveParticipant(self):
        tk.Event.data = [self.checked.get(), self.beginField.get(), self.endField.get(), True]
        self.event_generate('<<MoveParticipant>>')


if __name__ == '__main__':
    View().mainloop()