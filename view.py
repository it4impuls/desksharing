# import calendar
import tkinter as tk, tkinter.ttk as ttk
import data, config
from tkinter import messagebox, font, filedialog
from datetime import date, timedelta
from PIL import ImageOps, ImageTk, Image
from tkcalendar import Calendar, DateEntry
from os import path

rootDir = path.dirname(path.abspath(__file__))
imgDir = path.join(rootDir, 'img')
iconDir =path.join(imgDir, 'icons')

class View(tk.Tk):
    def __init__(self):
        super().__init__()
        super().focus_set()

        self.config = config.Config()

        self.title('DeskShare')

        self.showSeat = None
        self.showParticipant = None
        self.draggedParticipant = None
        self.draggedSeat = None
        self.draggedTo = None
        self.timeMode = False
        self.showDate = date.today()
        self.edit_room = False
        self.originalPosition  = (0,0,0,0)

        self.mainframe = MainFrame(self)
        
        # self.draw()
        self.bind('<Configure>', self.resize)
        self.bind('<<OpenAddParticipantDialog>>', self.openAddParticipantDialog)
        self.bind_all('<<AddParticipant>>', self.addParticipant)
        self.bind('<<OpenMoveParticipantDialog>>', self.openMoveParticipantDialog)
        self.bind('<<ClickedOnRoommap>>', self.onClickOnRoommap)
        self.bind('<<ReleasedFromRoomMap>>', self.onReleasedFromRoomMap)
        self.bind_all('<<MoveParticipant>>', self.moveParticipant)
        self.bind('<<OpenSaveAsDialog>>', self.openSaveAsDialog)
        self.bind('<<OpenOpenDialog>>', self.openOpenDialog)
        self.bind('<<NewFile>>', self.newFile)
        self.bind('<<OpenEditParticipantDialog>>', self.openEditParticipantDialog)
        self.bind_all('<<EditParticipant>>', self.editParticipant)
        self.bind('<<RemoveParticipant>>', self.removeParticpantFromList)
        self.bind('<<ReleasedFromSidebar>>', self.onReleasedFromSidebar)
        self.bind('<<EditRoom>>', self.editRoom)
        self.bind('<<AddSeat>>', self.addSeat)
        self.bind_all('<Escape>', self.onEsc)
        self.bind_all('<r>', self.onR)
        self.bind_all('<+>', self.onPlus)
        self.bind_all('<KP_Add>', self.onPlus)
        self.bind_all('<minus>', self.onMinus)
        self.bind_all('<KP_Subtract>', self.onMinus)

        self.oldWidth = self.winfo_width()
        self.oldHeight = self.winfo_height()
        self.after(0, self.onUpdate)        # run code alongside mainloop()

    def onUpdate(self):
        self.mainframe.roommap.update_dragged(self.draggedParticipant,self.draggedSeat, self.config.data.seats)
        self.after(1, self.onUpdate)
    def resize(self, event):
        if event.width != self.oldWidth or event.height != self.oldHeight:
            self.oldWidth = event.width
            self.oldHeight = event.height
            self.draw()
    def draw(self):
        self.mainframe.roommap.draw()
        self.mainframe.roommap.pack(fill='both', expand=True)
        self.mainframe.pack(fill='both', expand=True)
        self.mainframe.toolbar.update()
    def onClickOnRoommap(self, event):
        if event.data.num in [1, 3]:    #leftclick or rightclick
            seat = self.config.data.getSeat(event.data.x, event.data.y)
            
            if isinstance(seat, data.Seat):
                if self.edit_room:
                    self.draggedSeat = seat
                    self.originalPosition = (self.draggedSeat.x1, self.draggedSeat.y1, self.draggedSeat.x2, self.draggedSeat.y2)

                else:
                    participant = seat.getParticipant(self.showDate)
                    if participant != None:
                        self.draggedParticipant = participant
    def onReleasedFromRoomMap(self, event):
        newSeat = self.config.data.getSeat(event.data.x, event.data.y)
        x,y = self.winfo_pointerxy()
        if isinstance(self.draggedSeat, data.Seat):
            if self.mainframe.winfo_containing(x,y) == self.mainframe.roommap:
                if self.draggedSeat not in self.config.data.seats:
                    self.config.data.seats.append(self.draggedSeat)
                    self.originalPosition  = (0,0,0,0)
                self.draggedSeat = None
            else:
                self.draggedSeat.x1, self.draggedSeat.y1, self.draggedSeat.x2, self.draggedSeat.y2 = self.originalPosition
                self.draggedSeat = None
                self.originalPosition  = (0,0,0,0)
        elif isinstance(self.draggedParticipant, data.Participant):
            if newSeat == None:   
                # remove participent from desk if dragged over sidebar.
                
                if self.mainframe.winfo_containing(x,y) == self.mainframe.sidebar.table:
                    self.removeParticpantFromSeat(self.draggedParticipant)
                self.showSeat = None
                self.draggedParticipant = None
            else:
                self.draggedTo = newSeat
                # assign to new seat
                if newSeat.getParticipant(self.showDate) == self.draggedParticipant:
                    if event.data.num == 1:     #leftclick
                        self.showSeat = newSeat
                        self.draggedParticipant = None
                    elif event.data.num == 3:   #rightclick
                        self.showSeat = newSeat
                        self.draggedParticipant = None
                        #Kontextmenü
                        pass
                else:
                    if event.data.num == 1:     #leftclick
                        tk.Event.data = [1, self.draggedParticipant.entryDate, self.draggedParticipant.exitDate, False]
                        self.event_generate('<<MoveParticipant>>')
                    elif event.data.num == 3:   #rightclick
                        self.draggedTo = newSeat
                        self.event_generate('<<OpenMoveParticipantDialog>>')
        else:
            self.showSeat = newSeat
        self.draw()
    def onReleasedFromSidebar(self,event):
        if isinstance(self.draggedParticipant, data.Participant):
            newSeat = self.config.data.getSeat(event.data.x, event.data.y)
            if isinstance(newSeat, data.Seat):
                self.draggedTo = newSeat
                tk.Event.data = [1, self.draggedParticipant.entryDate, self.draggedParticipant.exitDate, False]
                self.event_generate('<<MoveParticipant>>')
            # self.showSeat = None
            self.draggedParticipant = None
            self.mainframe.roommap.update()
    def onEsc(self, event):
        if isinstance(self.draggedParticipant, data.Participant):
            self.draggedParticipant = None
            self.mainframe.roommap.draw()
    def onR(self, event):
        if isinstance(self.draggedSeat, data.Seat):
            self.mainframe.roommap.delete(self.draggedSeat.img_id)
            self.draggedSeat.rot+=1
            if self.draggedSeat.rot>3:
                self.draggedSeat.rot = 0
            self.draggedSeat.draw(self.mainframe.roommap)
    def onPlus(self, event):
        if self.edit_room:
            self.config.data.scale *= 1.1
            self.mainframe.roommap.draw()
    def onMinus(self, event):
        if self.edit_room:
            self.config.data.scale /= 1.1
            self.mainframe.roommap.draw()

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
        NewFile = filedialog.askopenfilename(   filetypes=(('save files','*.png'),('all files','*.*')),
                                                initialdir = path.join(rootDir, 'img', 'rooms'))
        self.config.data = data.Data()
        self.config.data.roomFile = NewFile
        self.mainframe.roommap.roomImg = Image.open(path.join(imgDir, 'rooms', NewFile)).convert()
        self.showSeat = None
        self.draw()
        self.mainframe.sidebar.refresh()
        self.mainframe.roommap.refresh()
    def openOpenDialog(self, event):
        loadfile = filedialog.askopenfilename(  filetypes=(('save files','*.sav'),('all files','*.*')), 
                                                initialdir = path.join(rootDir, 'saves'))
        self.config.loadData(loadfile)
        self.mainframe.roommap.roomImg = Image.open(path.join(imgDir, 'rooms', self.config.data.roomFile)).convert()
        self.showSeat = None
        self.draw()
        self.mainframe.sidebar.refresh()
        self.mainframe.roommap.refresh()
    def openSaveAsDialog(self, event):
        savefile = filedialog.asksaveasfilename(filetypes=(('save files','*.sav'),('all files','*.*')), 
                                                defaultextension='.sav', 
                                                initialdir = path.join(rootDir, 'saves'))
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
    def removeParticpantFromList(self, event):
        if isinstance(self.showSeat, data.Seat):
            self.removeParticpantFromSeat(self.showSeat.getParticipant(self.showDate))
        elif True:
            self.config.data.removeParticipant(int(self.mainframe.sidebar.table.selection()[0]))
        self.draw()
        self.mainframe.sidebar.refresh()
    def editRoom(self, event):
        bttn = event.widget.editBttn
        assert isinstance(bttn, tk.Button)
        if bttn.cget("relief") == tk.FLAT:
            bttn.config(relief=tk.SUNKEN)
            self.mainframe.toolbar.addSeatBttn.pack(side=tk.LEFT, padx=2, pady=1)
            self.edit_room = True
        elif bttn.cget("relief") == tk.SUNKEN:
            bttn.config(relief=tk.FLAT)
            self.mainframe.toolbar.addSeatBttn.pack_forget()
            self.edit_room = False
    def addSeat(self, event):
        cursorPos = ((self.winfo_pointerx()-self.winfo_rootx()), 
                      (self.winfo_pointery()-self.winfo_rooty()))
        self.draggedSeat = data.Seat(cursorPos[0], cursorPos[1], cursorPos[0]+132, cursorPos[1] + 136)
        self.draggedSeat.draw(self.mainframe.roommap)
    def removeParticpantFromSeat(self, participent):
        if isinstance(participent, data.Participant):
            participent.doAssignmentsByTime(participent.entryDate,participent.entryDate,self.config.data.removeAssignment, True)
            for iid in participent.textIDs:
                self.mainframe.roommap.delete(iid)
            participent.textIDs = []
    def asignParticipentToSeat(self, participent):
        pass

class MainFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        
        self.master = master
        self.roommap = Roommap(self)
        # self.menubar = MenuBar(self)
        self.toolbar = ToolBar(self.master)
        self.toolbar.addSeatBttn.pack_forget()
        self.sidebar = SideBar(self.master)
class MenuBar(tk.Menu): #disabled
    def __init__(self, master):
        super().__init__(master)
        self.master.config(menu=self)

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
        self.editBttn = self.addButton('wrench_icon&24.png', '<<EditRoom>>')
        
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill='y')
        self.addButton('doc_plus_icon&24.png', '<<OpenAddParticipantDialog>>')
        self.addButton('doc_minus_icon&24.png', '<<RemoveParticipant>>')
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill='y')

        self.dateText =  DateEntry(self, width=10, date_pattern = 'dd.mm.yyyy')
        self.dateText.pack(side=tk.LEFT, padx=2, pady=1)
        self.addSeatBttn = self.addButton('user_icon&24.png', '<<AddSeat>>')
        
        self.dateText.bind('<<DateEntrySelected>>', self.applyDate)
        self.dateText.bind('<Return>', self.applyDate)
        self.dateText.bind('<FocusOut>', self.applyDate)
        self.bind('<ButtonRelease>', self.onRelease)

        self.pack(side=tk.TOP, fill=tk.X)
        self.update()
        
    def addButton(self, iconFilename, eventName):
        icon = ImageTk.PhotoImage(Image.open(path.join(iconDir, iconFilename)))
        button = tk.Button(self, image=icon, relief=tk.FLAT, command=lambda: self.event_generate(eventName))
        button.image = icon
        button.pack(side=tk.LEFT, padx=2, pady=1)
        return button
    def applyDate(self, event):
        self.master.showDate = self.master.config.data.stringToDate(self.dateText.get_date())
        self.focus_set()
        self.master.draw()

    def onRelease(self, event):
        if isinstance(self.master.draggedSeat, data.Seat):
            self.master.draggedSeat = None
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
        # Triggers everywhere if pressed on sidebar, doesnt trigger if pressed anywhere else for some reason
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
        
        for i in range(len(self.master.config.data.participants)):
            self.table.insert('', 'end', i, values=((self.master.config.data.participants[i].lastName + ', ' + self.master.config.data.participants[i].firstName), self.master.config.data.participants[i].entryDate.strftime('%d.%m.%Y'), self.master.config.data.participants[i].exitDate.strftime('%d.%m.%Y')))
        if self.master.showSeat != None:
            for i in range(len(self.master.showSeat.assignments)):
                self.table.insert('', 'end', i, values=((self.master.showSeat.assignments[i].participant.lastName + ', ' + self.master.showSeat.assignments[i].participant.firstName), self.master.showSeat.assignments[i].begin.strftime('%d.%m.%Y'), self.master.showSeat.assignments[i].end.strftime('%d.%m.%Y')))
    def onClick(self, event):
        if self.table.identify_row(event.y) != '':
            clickedOn = int(self.table.identify_row(event.y))
            self.master.draggedParticipant = self.master.config.data.participants[clickedOn]
        else:
            self.master.draggedParticipant = None
    def onRelease(self, event):
        event.x = (event.x_root-self.master.mainframe.roommap.winfo_rootx())/self.master.mainframe.roommap.rel
        event.y = (event.y_root-self.master.mainframe.roommap.winfo_rooty())/self.master.mainframe.roommap.rel
        tk.Event.data = event
        self.event_generate('<<ReleasedFromSidebar>>')
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
        if self.master.master.config.data.roomFile == '':
            self.roomImg = Image.open(path.join(imgDir, 'rooms', 'ITloft.png')).convert()
        else:
            self.roomImg = Image.open(path.join(imgDir, 'rooms', self.master.master.config.data.roomFile)).convert()
        self.rel = 1
        # self.scale = 1
        
        self.bind('<Button>', self.onClick)
        self.bind('<ButtonRelease>', self.onRelease)    # Triggers everywhere as if in master

    def draw(self):
        self.update()
        self.delete("all")
        
        relH = self.winfo_height()/self.roomImg.height
        relW = self.winfo_width()/self.roomImg.width
        self.rel = max(min(relW, relH), 0.1)
        self.roomImgResized = ImageTk.PhotoImage(ImageOps.scale(self.roomImg, self.rel))
        self.create_image(0, 0, anchor=tk.NW, image=self.roomImgResized)
        
        self.font = font.Font(family='Helvetica', size=int(max(20*self.rel, 0)))
        for seat in self.master.master.config.data.seats:
            seat.draw(self, scale = self.master.master.config.data.scale)           # seperate, so that all seats are drawn before the nametags, so nametags are layered above.
        for seat in self.master.master.config.data.seats:
            for assignment in seat.assignments:
                if assignment.begin <= self.master.master.showDate and assignment.end >= self.master.master.showDate:
                    self.drawParticipant(seat, assignment.participant)
        # items = self.find_all()
        # pass

    def refresh(self):
        self.draw()

    def update_dragged(self, dragged_participent, dragged_seat, seats_temp):
        snapSize = 10*self.rel
        cursorPos = (   round((self.winfo_pointerx()-self.winfo_rootx())/snapSize)*snapSize, 
                        round((self.winfo_pointery()-self.winfo_rooty())/snapSize)*snapSize)
        if isinstance(dragged_participent, data.Participant):
            if len(dragged_participent.textIDs) > 0:
                root = self.coords(dragged_participent.textIDs[0])
                if len(root)==0:
                    root=cursorPos
                root[1] += self.font.cget("size")
                reMove = (cursorPos[0]-root[0], cursorPos[1]-root[1])
                for txtID in dragged_participent.textIDs:
                    self.move(txtID, reMove[0], reMove[1])
            else:
                x_len = seats_temp[0].x2-seats_temp[0].x1
                y_len = seats_temp[0].y2-seats_temp[0].y1
                x1 = (cursorPos[0]-(x_len/2))/self.rel
                x2 = (cursorPos[0]+(x_len/2))/self.rel
                y1 = (cursorPos[1]-(y_len/2))/self.rel
                y2 = (cursorPos[1]+(y_len/2))/self.rel
                dragged_participent.draw(self.rel, self.font, self, x1,x2,y1,y2)
            
        elif isinstance(dragged_seat, data.Seat):
            root = self.coords(dragged_seat.img_id)
            width=dragged_seat.x2-dragged_seat.x1
            height=dragged_seat.y2-dragged_seat.y1
            root[0] = (root[0] + width*self.rel/2)
            root[1] = (root[1] + height*self.rel/2)

            reMove = (cursorPos[0]-root[0], cursorPos[1]-root[1])
            if any(i > snapSize or snapSize < -i for i in reMove):
                if (reMove[0] > snapSize or snapSize < -reMove[0]):
                    self.move(dragged_seat.img_id, reMove[0], 0)
                if (reMove[1] > snapSize or snapSize < -reMove[1]):
                    self.move(dragged_seat.img_id, 0, reMove[1])
                
                root = self.coords(dragged_seat.img_id)
                bb = self.bbox(dragged_seat.img_id)
                dragged_seat.x1 = (bb[0]/self.rel)
                dragged_seat.y1 = (bb[1]/self.rel)
                dragged_seat.x2 = (bb[2]/self.rel)
                dragged_seat.y2 = (bb[3]/self.rel)
                
                self.create_rectangle(bb)

    def drawParticipant(self, seat, participant):
        participant.draw(self.rel, self.font, self, seat.x1, seat.x2, seat.y1, seat.y2)
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
        self.event_generate('<<ReleasedFromRoomMap>>')

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
        
        addCmd = lambda: self.tryAddParticipant(firstNameField.get(), lastNameField.get(), entryDateField.get(), exitDateField.get(), noteField.get())
        addButton = tk.Button(self, text='Hinzufügen', command=addCmd)
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
        _width = 30

        firstNameLabel = tk.Label(self, text='Vorname', justify=tk.LEFT)
        firstNameLabel.grid(row=0, column=0, sticky=tk.W)

        firstNameField = tk.Entry(self, width=_width)
        firstNameField.grid(row=0, column=1)
        firstNameField.insert('end', participant.firstName)

        lastNameLabel = tk.Label(self, text='Nachname', justify=tk.LEFT)
        lastNameLabel.grid(row=1, column=0, sticky=tk.W)

        lastNameField = tk.Entry(self, width=_width)
        lastNameField.grid(row=1, column=1)
        lastNameField.insert('end', participant.lastName)
        
        entryDateLabel = tk.Label(self, text='Eintritt', justify=tk.LEFT)
        entryDateLabel.grid(row=2, column=0, sticky=tk.W)

        entryDateField = DateEntry(self, width=_width-3, date_pattern = 'dd.mm.yyyy')
        entryDateField.set_date(participant.entryDate)
        entryDateField.grid(row=2, column=1)

        exitDateLabel = tk.Label(self, text='Austritt', justify=tk.LEFT)
        exitDateLabel.grid(row=3, column=0, sticky=tk.W)

        exitDateField = DateEntry(self, width=_width-3, date_pattern = 'dd.mm.yyyy')
        exitDateField.set_date(participant.exitDate)
        exitDateField.grid(row=3, column=1)

        noteLabel = tk.Label(self, text='Notiz')
        noteLabel.grid(row=4, column=0, sticky=tk.W)

        noteField = tk.Entry(self, width=_width)
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

        self.beginField = DateEntry(self, width=10, date_pattern = 'dd.mm.yyyy')
        self.beginField.set_date(participant.entryDate)
        self.beginField.grid(row=3, column=0)
        self.beginField['state'] = tk.DISABLED

        self.endField = DateEntry(self, width=10, date_pattern = 'dd.mm.yyyy')
        self.endField.set_date(participant.exitDate)
        self.endField.grid(row=3, column=1)
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