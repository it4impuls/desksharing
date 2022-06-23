# import calendar
import tkinter as tk, tkinter.ttk as ttk
import data, config
from tkinter import messagebox, font, filedialog
from datetime import date
from PIL import ImageOps, ImageTk, Image
from tkcalendar import DateEntry
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
        self.deskDimensions = (132, 136)
        self.shiftPressed = False

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
        self.bind('<<Export>>', self.onExport)

        self.bind_all('<KeyPress>', self.onKeyPress)
        self.bind_all('<KeyRelease>', self.onKeyRelease)
        self.bind_all('<Control-s>', self.openSaveAsDialog)
        self.bind_all('<Control-n>', self.newFile)

        self.oldWidth = self.winfo_width()
        self.oldHeight = self.winfo_height()
        self.after(0, self.onUpdate)        # run code alongside mainloop()

    def onUpdate(self):
        """Executes every cycle
        """
        self.mainframe.roommap.update_dragged(self.draggedParticipant,self.draggedSeat, self.config.data.seats)
        self.after(1, self.onUpdate)
    def resize(self, event:tk.Event):
        """ saves old dimentions on resize

        Args:
            event (tk.Event): Automatically get send with tk bindings
        """
        if event.width != self.oldWidth or event.height != self.oldHeight:
            self.oldWidth = event.width
            self.oldHeight = event.height
            self.draw()
    def draw(self):
        """ Redraw every Widget
        """
        self.mainframe.roommap.draw()
        self.mainframe.roommap.pack(fill='both', expand=True)
        self.mainframe.pack(fill='both', expand=True)
        self.mainframe.toolbar.update()
    def onClickOnRoommap(self, event:tk.Event):
        """ What happens when you click on the RoomMap.
            If its a seat or participent, drag it.
        Args:
            event (tk.Event): Automatically get send with tk bindings
        """
        if event.data.num in [1, 3]:    # type: ignore #leftclick or rightclick
            seat = self.config.data.getSeat(event.data.x, event.data.y)  # type: ignore
            if isinstance(seat, data.Seat):
                if self.edit_room:
                    self.draggedSeat = seat
                    self.originalPosition = (self.draggedSeat.x1, self.draggedSeat.y1, self.draggedSeat.x2, self.draggedSeat.y2)

                else:
                    participant = seat.getParticipant(self.showDate)
                    if participant != None:
                        self.draggedParticipant = participant
    def onReleasedFromRoomMap(self, event:tk.Event):
        """ what happens if you release the mouse after clicking on the Roommap
            If a Participent is dragged and the mouse is over a Seat: move him there
            If a Participent is dragged and the mouse is over a Seat and the right mousebutton is released: open dialog
            If a Participent is dragged and the mouse is NOT over a Seat: reset him to his last seat
            If a Participent is dragged and the mouse is over the Sidebar: Remove him from the seat
            If a Seat is dragged and the mouse is over the Roommap: Set it as its new Position
        Args:
            event (tk.Event): Automatically get send with tk bindings
        """
        newSeat = self.config.data.getSeat(event.data.x, event.data.y)  # type: ignore
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
                    if event.data.num == 1:     # type: ignore #leftclick
                        self.showSeat = newSeat
                        self.draggedParticipant = None
                    elif event.data.num == 3:   # type: ignore #rightclick
                        self.showSeat = newSeat
                        self.draggedParticipant = None
                        #Kontextmenü
                        pass
                else:
                    if event.data.num == 1:     # type: ignore #leftclick
                        tk.Event.data = [1, self.draggedParticipant.entryDate, self.draggedParticipant.exitDate, False]  # type: ignore
                        self.event_generate('<<MoveParticipant>>')
                    elif event.data.num == 3:   # type: ignore #rightclick
                        self.draggedTo = newSeat
                        self.event_generate('<<OpenMoveParticipantDialog>>')
        else:
            self.showSeat = newSeat
        self.draw()
    def onReleasedFromSidebar(self,event:tk.Event):
        """ what happens if you release the mouse after clicking on the sidebar
            If a Participent is dragged and the mouse is over a Seat: move him there
        Args:
            event (tk.Event): Automatically get send with tk bindings
        """
        if isinstance(self.draggedParticipant, data.Participant):
            try:
                newSeat = self.config.data.getSeat(event.data.x, event.data.y)  # type: ignore
                if isinstance(newSeat, data.Seat):
                    self.draggedTo = newSeat
                    tk.Event.data = [1, self.draggedParticipant.entryDate, self.draggedParticipant.exitDate, False]  # type: ignore
                    self.event_generate('<<MoveParticipant>>')
                # self.showSeat = None
                self.draggedParticipant = None
            except:
                pass
    def onKeyPress(self, event:tk.Event):
        if event.keysym == "Shift_L":
            self.shiftPressed = True
        elif event.keysym == "Escape":
            if isinstance(self.draggedParticipant, data.Participant):
                self.draggedParticipant = None
                self.mainframe.roommap.draw()
            if isinstance(self.draggedSeat, data.Seat):
                self.draggedSeat = None
                self.mainframe.roommap.draw()
        elif event.keysym == "r":
            if isinstance(self.draggedSeat, data.Seat) and isinstance(self.draggedSeat.img_id, int):
                self.mainframe.roommap.delete(self.draggedSeat.img_id)
                self.draggedSeat.rot+=1
                if self.draggedSeat.rot>3:
                    self.draggedSeat.rot = 0
                self.draggedSeat.draw(self.mainframe.roommap, self.config.data.scale)
        elif event.keysym == "+" or event.keysym == "KP_Add":
            if self.edit_room:
                self.config.data.scale *= 1.1
                self.mainframe.roommap.draw()
        elif event.keysym == "minus" or event.keysym == "KP_Subtract":
            if self.edit_room:
                self.config.data.scale /= 1.1
                self.mainframe.roommap.draw()
        elif event.keysym == "Delete":
            if isinstance(self.draggedSeat, data.Seat):     # remove seat
                if self.draggedSeat in self.config.data.seats:
                    for assignment in self.draggedSeat.assignments:
                        assert isinstance(assignment, data.Assignment)
                        assert isinstance(assignment.participant, data.Participant)
                        assignment.participant.assignments.remove(assignment)
                        self.config.data.assignments.remove(assignment)
                        self.draggedSeat.assignments.remove(assignment)
                    self.config.data.seats.remove(self.draggedSeat)
                    self.draggedSeat = None
    def onKeyRelease(self, event:tk.Event):
        if event.keysym == "Shift_L":
            self.shiftPressed = False
    def onExport(self, event:tk.Event):
        """ Export current room to png.

        Args:
            event (tk.Event): Automatically get send with tk bindings
        """
        saveAs = filedialog.asksaveasfilename(  filetypes=(('save files','*.png'),('all files','*.*')),
                                            defaultextension='.png', 
                                            initialdir = rootDir)
        data.Exporter(self.config.data, self.mainframe.roommap.font, self.showDate, saveAs)
    def openAddParticipantDialog(self, event:tk.Event):
        self.addParticipantDialog = AddParticipantDialog()
    def closeAddParticipantDialog(self):
        self.addParticipantDialog.destroy()
    def addParticipant(self, event:tk.Event):
        isAdded = self.config.data.addParticipant(event.data[0], event.data[1], event.data[2], event.data[3], note=event.data[4])  # type: ignore
        if isinstance(isAdded, data.Error):
            messagebox.showerror("Error", isAdded.message)
        else:
            self.closeAddParticipantDialog()
            self.mainframe.sidebar.refresh()
    def openMoveParticipantDialog(self, event:tk.Event):
        newSeat = self.config.data.getSeat(event.data.x, event.data.y)  # type: ignore
        if isinstance(newSeat, data.data.Seat):  # type: ignore
            self.moveParticipantDialog = MoveParticipantDialog(self.draggedParticipant)
    def closeMoveParticipantDialog(self):
        self.moveParticipantDialog.destroy()
    def moveParticipant(self, event:tk.Event):
        """ move Participent to new seat.
        Args:
            event (tk.Event): Automatically get send with tk bindings
        """
        if event.data[0] == 1:  # type: ignore # leftclick
            # event.data[0] = startDate independent of participent join date, event.data[1] = endDate independent of participent leave date, 
            self.config.data.moveParticipant(self.draggedParticipant, self.draggedTo, event.data[1], event.data[2])  # type: ignore
        if event.data[3]:  # type: ignore
            self.closeMoveParticipantDialog()
        self.draggedParticipant = None
        self.draggedTo = None
        self.draw()
    def newFile(self, event:tk.Event):
        """ Create a new room.
            Takes an image for the new background and resets everything.

        Args:
            event (tk.Event): Automatically get send with tk bindings
        """
        newFile = filedialog.askopenfilename(   filetypes=(('save files','*.png'),('all files','*.*')),
                                                initialdir = path.join(rootDir, 'img', 'rooms'))
        if newFile == "":
            return
        self.config.data = data.Data()
        self.config.data.roomFile = newFile
        self.config.data.roomImage = Image.open(path.join(imgDir, 'rooms', newFile)).convert()
        self.showSeat = None
        self.draw()
        self.mainframe.sidebar.refresh()
        self.mainframe.roommap.refresh()
    def openOpenDialog(self, event:tk.Event):
        loadfile = filedialog.askopenfilename(  filetypes=(('save files','*.sav'),('all files','*.*')), 
                                                initialdir = path.join(rootDir, 'saves'))
        self.config.loadData(loadfile)
        self.showSeat = None
        self.draw()
        self.mainframe.sidebar.refresh()
        self.mainframe.roommap.refresh()
    def openSaveAsDialog(self, event:tk.Event):
        if isinstance(self.config.lastSavefile, str):
            savefile = filedialog.asksaveasfilename(filetypes=(('save files','*.sav'),('all files','*.*')), 
                                                    defaultextension='.sav',
                                                    initialfile=path.split(self.config.lastSavefile)[1],
                                                    initialdir = path.join(rootDir, 'saves'))
        else:
            savefile = filedialog.asksaveasfilename(filetypes=(('save files','*.sav'),('all files','*.*')), 
                                                defaultextension='.sav',
                                                initialdir = path.join(rootDir, 'saves'))
        if savefile != "":
            self.config.saveData(savefile)
    def openEditParticipantDialog(self, event:tk.Event):
        self.editParticipantDialog = EditParticipantDialog(event.data)  # type: ignore
    def editParticipant(self, event:tk.Event):
        isEdited = self.config.data.editParticipant(event.data[0], event.data[1], event.data[2], event.data[3], event.data[4], note=event.data[5])  # type: ignore
        if isinstance(isEdited, data.Error):
            messagebox.showerror("Error", isEdited.message)
        else:
            self.closeEditParticipantDialog()
            self.mainframe.sidebar.refresh()
    def closeEditParticipantDialog(self):
        self.editParticipantDialog.destroy()
    def removeParticpantFromList(self, event:tk.Event):
        if isinstance(self.showSeat, data.Seat) and isinstance(self.showSeat.getParticipant(self.showDate), data.Participant):
            self.removeParticpantFromSeat(self.showSeat.getParticipant(self.showDate))
        elif len(self.mainframe.sidebar.table.selection())>0:
            for i in self.mainframe.sidebar.table.selection():
                self.config.data.removeParticipant(int(i))
        else:
            return
        self.draw()
        self.mainframe.sidebar.refresh()
    def editRoom(self, event:tk.Event):
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
    def addSeat(self, event:tk.Event):
        cursorPos = ((self.winfo_pointerx()-self.winfo_rootx()), 
                      (self.winfo_pointery()-self.winfo_rooty()))
        self.draggedSeat = data.Seat(cursorPos[0], cursorPos[1], cursorPos[0]+self.deskDimensions[0], cursorPos[1]+self.deskDimensions[1])
        self.draggedSeat.draw(self.mainframe.roommap, self.config.data.scale)
    def removeParticpantFromSeat(self, participent):
        if isinstance(participent, data.Participant):
            participent.doAssignmentsByTime(participent.entryDate,participent.entryDate,self.config.data.removeAssignment, True)
            for iid in participent.textIDs:
                self.mainframe.roommap.delete(iid)
            participent.textIDs = []

class MainFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        assert isinstance(self.master, View)
        self.roommap = Roommap(self)
        self.toolbar = ToolBar(self.master)
        self.toolbar.addSeatBttn.pack_forget()
        self.toolbar.addSeatTTP = CreateToolTip(self.toolbar.addSeatBttn, "Neuen Sitzplatz hinzufügen")
        self.sidebar = SideBar(self.master)
class ToolBar(tk.Frame):
    def __init__(self, master:View):
        super().__init__(master, bd=1, relief=tk.RAISED)
        self.newFileBttn = self.addButton('doc_new_icon&24.png', '<<NewFile>>')
        self.newFileTTP = CreateToolTip(self.newFileBttn, "Neuer Raum. Erschaffe einen neuern Raum mit einem Bild als Vorlage")
        self.openFileBttn = self.addButton('folder_open_icon&24.png', '<<OpenOpenDialog>>')
        self.openFileTTP = CreateToolTip(self.openFileBttn, "Raum laden. lade einen bestehenden Raum")
        self.saveRoomBttn = self.addButton('save_icon&24.png', '<<OpenSaveAsDialog>>')
        self.saveRoomTTP = CreateToolTip(self.saveRoomBttn, "Raum speichern. Speicher diesen Raum.")
        self.editBttn = self.addButton('wrench_icon&24.png', '<<EditRoom>>')
        self.editTTP = CreateToolTip(self.editBttn, "Raum bearbeiten. Ermöglicht das Bewegen und Erschaffen neuer Sitze")
        self.addSeatTTP:CreateToolTip
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill='y')
        self.addPartiBttn = self.addButton('doc_plus_icon&24.png', '<<OpenAddParticipantDialog>>')
        self.addPartiTTP = CreateToolTip(self.addPartiBttn, "Neuen Teilnehmer hinzufügen")
        self.remPartiBttn = self.addButton('doc_minus_icon&24.png', '<<RemoveParticipant>>')
        self.remPartiTTP = CreateToolTip(self.remPartiBttn, "Teilnehmer löschen. Wenn ein Sitz ausgewählt ist, wird der momentane Teilnehmer von Sitz gelöscht,\
                             ansonsten wird der ausgewählte Teilnehmer aus der Liste gelöscht")
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill='y')

        self.datetxt = self.dateText =  DateEntry(self, width=10, date_pattern = 'dd.mm.yyyy')
        self.dateTTP = CreateToolTip(self.datetxt, "Datum auswählen. Wähle, für welches Datum die Raum-zuteilung angezeigt werden soll")
        self.dateText.pack(side=tk.LEFT, padx=2, pady=1)
        self.addSeatBttn = self.addButton('user_icon&24.png', '<<AddSeat>>')

        self.exportbttn = self.addButton('clipboard_past_icon&24.png', '<<Export>>')
        
        
        self.dateText.bind('<<DateEntrySelected>>', self.applyDate)
        self.dateText.bind('<Return>', self.applyDate)
        self.dateText.bind('<FocusOut>', self.applyDate)
        self.bind('<ButtonRelease>', self.onRelease)

        self.pack(side=tk.TOP, fill=tk.X)
        self.update()
        
    def addButton(self, iconFilename, eventName) -> tk.Button:
        icon = ImageTk.PhotoImage(Image.open(path.join(iconDir, iconFilename)))
        button = tk.Button(self, image=icon, relief=tk.FLAT, command=lambda: self.event_generate(eventName))
        setattr(button, "image", icon)
        button.pack(side=tk.LEFT, padx=2, pady=1)
        return button
    def applyDate(self, event:tk.Event):
        assert isinstance(self.master, View)
        self.master.showDate = self.master.config.data.stringToDate(self.dateText.get_date())
        self.focus_set()
        self.master.draw()
    def onRelease(self, event:tk.Event):
        if isinstance(self.master, View) and isinstance(self.master.draggedSeat, data.Seat):
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
        """ Recreate the table
        """
        for row in self.table.get_children():
            self.table.delete(row)
        assert isinstance(self.master, View)
        for i in range(len(self.master.config.data.participants)):
            self.table.insert('', 'end', str(i), values=((self.master.config.data.participants[i].lastName + ', ' + self.master.config.data.participants[i].firstName), self.master.config.data.participants[i].entryDate.strftime('%d.%m.%Y'), self.master.config.data.participants[i].exitDate.strftime('%d.%m.%Y')))
        if self.master.showSeat != None:
            for i in range(len(self.master.showSeat.assignments)):
                self.table.insert('', 'end', str(i), values=((self.master.showSeat.assignments[i].participant.lastName + ', ' + self.master.showSeat.assignments[i].participant.firstName), self.master.showSeat.assignments[i].begin.strftime('%d.%m.%Y'), self.master.showSeat.assignments[i].end.strftime('%d.%m.%Y')))
    def onClick(self, event:tk.Event):
        assert isinstance(self.master, View)
        if self.table.identify_row(event.y) != '':
            clickedOn = int(self.table.identify_row(event.y))
            self.master.draggedParticipant = self.master.config.data.participants[clickedOn]
        else:
            self.master.draggedParticipant = None
    def onRelease(self, event:tk.Event):
        assert isinstance(self.master, View)
        event.x = (event.x_root-self.master.mainframe.roommap.winfo_rootx())/self.master.mainframe.roommap.rel  # type: ignore
        event.y = (event.y_root-self.master.mainframe.roommap.winfo_rooty())/self.master.mainframe.roommap.rel  # type: ignore
        tk.Event.data = event  # type: ignore
        self.event_generate('<<ReleasedFromSidebar>>')
    def onDoubleClick(self, event:tk.Event):
        assert isinstance(self.master, View)
        if self.table.identify_row(event.y) != '':
            clickedOn = int(self.table.identify_row(event.y))
            if self.master.showSeat == None:
                tk.Event.data = self.master.config.data.participants[clickedOn]  # type: ignore
            else:
                tk.Event.data = self.master.showSeat.assignments[clickedOn].participant  # type: ignore
            self.event_generate('<<OpenEditParticipantDialog>>')
        else:
            self.master.draggedParticipant = None
class Roommap(tk.Canvas):
    def __init__(self, master):
        super().__init__(master)
        
        self.master = master
        assert isinstance(self.master.master, View)
        if self.master.master.config.data.roomImage == None:
            self.master.master.config.data.roomImage = Image.open(path.join(imgDir, 'rooms', 'ITloft.png')).convert()
        self.rel = 1
        self.bind('<Button>', self.onClick)
        self.bind('<ButtonRelease>', self.onRelease)    # Triggers everywhere as if in master

    def draw(self):
        self.update()
        self.delete("all")
        master = self.master.master
        assert isinstance(master, View)
        mdata = master.config.data
        
        relH = self.winfo_height()/mdata.roomImage.height
        relW = self.winfo_width()/mdata.roomImage.width
        self.rel = max(min(relW, relH), 0.1)
        self.roomImgResized = ImageTk.PhotoImage(ImageOps.scale(mdata.roomImage, self.rel))
        self.create_image(0, 0, anchor=tk.NW, image=self.roomImgResized)
        self.font = font.Font(family='Helvetica', size=int(max(20*self.rel, 0)))

        for seat in mdata.seats:
            seat.draw(self, scale = mdata.scale)           # seperate, so that all seats are drawn before the nametags, so nametags are layered above.
        # print(master.draggedParticipant)
        if isinstance(master.draggedParticipant, data.Participant):
            cursorPos = (   round(self.winfo_pointerx()-self.winfo_rootx()), 
                        round(self.winfo_pointery()-self.winfo_rooty()))
            master.draggedParticipant.draw(self.rel, self.font, self, cursorPos[0], cursorPos[0]+master.deskDimensions[0], cursorPos[1], cursorPos[1]+master.deskDimensions[1])
        if isinstance(master.draggedSeat, data.Seat):
            master.draggedSeat.draw(self, mdata.scale)
        for seat in mdata.seats:
            for assignment in seat.assignments:
                if assignment.begin <= master.showDate and assignment.end >= master.showDate:
                    self.drawParticipant(seat, assignment.participant)
    def refresh(self):
        self.draw()
    def update_dragged(self, dragged_participent, dragged_seat, seats_temp):
        
        assert isinstance(self.master.master, View)
        if self.master.master.shiftPressed:
            snapSize = 1
        else:
            snapSize = 10*self.rel
        cursorPos = [  round(self.winfo_pointerx()-self.winfo_rootx()), 
                        round(self.winfo_pointery()-self.winfo_rooty())]
        if isinstance(dragged_participent, data.Participant):
            if len(dragged_participent.textIDs) > 0:
                root = self.coords(dragged_participent.textIDs[0])
                if len(root)==0:
                    root=cursorPos
                root[1] += self.font.cget("size")  # type: ignore
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
            
        elif isinstance(dragged_seat, data.Seat) and isinstance(dragged_seat.img_id, int):
            root = self.coords(dragged_seat.img_id)
            if len(root) == 0:
                root=cursorPos
            if not self.master.master.shiftPressed:
                root[0] = round(root[0]/snapSize)*snapSize  # type: ignore
                root[1] = round(root[1]/snapSize)*snapSize  # type: ignore
            width=dragged_seat.x2-dragged_seat.x1
            height=dragged_seat.y2-dragged_seat.y1
            root[0] = (root[0] + width*self.rel/2)  # type: ignore
            root[1] = (root[1] + height*self.rel/2)  # type: ignore


            reMove = (cursorPos[0]-root[0], cursorPos[1]-root[1])

            if not (-snapSize < reMove[0] < snapSize):
                self.move(dragged_seat.img_id, reMove[0], 0)
            if not (-snapSize < reMove[1] < snapSize):
                self.move(dragged_seat.img_id, 0, reMove[1])
                
                root = self.coords(dragged_seat.img_id)
                bb = self.bbox(dragged_seat.img_id)
                dragged_seat.x1 = round(bb[0]/self.rel)
                dragged_seat.y1 = round(bb[1]/self.rel)
                dragged_seat.x2 = round(bb[2]/self.rel)
                dragged_seat.y2 = round(bb[3]/self.rel)
                
                self.create_rectangle(bb)
    def drawParticipant(self, seat, participant):
        assert isinstance(self.master.master, View)
        participant.draw(self.rel, self.font, self, seat.x1, seat.x2, seat.y1, seat.y2)
        if self.master.master.showSeat != None:
            super().create_rectangle(self.master.master.showSeat.x1*self.rel, self.master.master.showSeat.y1*self.rel, self.master.master.showSeat.x2*self.rel, self.master.master.showSeat.y2*self.rel, width=2, outline='#FF0000')
    def onClick(self, event:tk.Event):
        event.x = event.x/self.rel  # type: ignore
        event.y = event.y/self.rel  # type: ignore
        tk.Event.data = event  # type: ignore
        self.event_generate('<<ClickedOnRoommap>>')
    def onRelease(self, event:tk.Event):
        event.x = event.x/self.rel  # type: ignore
        event.y = event.y/self.rel  # type: ignore
        tk.Event.data = event  # type: ignore
        self.event_generate('<<ReleasedFromRoomMap>>')

class AddParticipantDialog(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title('Neuer Teilnehmer')
        self.grab_set()
        self.resizable(height=False, width=False)
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
        tk.Event.data = [firstName, lastName, entryDate, exitDate, note]  # type: ignore
        self.event_generate('<<AddParticipant>>')
class EditParticipantDialog(tk.Toplevel):
    def __init__(self, participant):
        super().__init__()
        self.title('Teilnehmer bearbeiten')
        self.grab_set()
        self.resizable(height=False, width=False)
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
        tk.Event.data = [participant, firstName, lastName, entryDate, exitDate, note]  # type: ignore
        self.event_generate('<<EditParticipant>>')     
class MoveParticipantDialog(tk.Toplevel):
    def __init__(self, participant):
        super().__init__()
        self.title('Teilnehmer umziehen')
        self.grab_set()
        self.resizable(height=False, width=False)
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
        tk.Event.data = [self.checked.get(), self.beginField.get(), self.endField.get(), True]  # type: ignore
        self.event_generate('<<MoveParticipant>>')

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

if __name__ == '__main__':
    View().mainloop()