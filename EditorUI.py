import sysimport osimport platformimport subprocessimport threadingimport shutilimport previewUIimport highlighter#Packages used: PyQt5, PyMuPDF(fitz)...from PyQt5.QtWidgets import *from PyQt5.QtCore import QDate, QFile, Qt, QTextStream, pyqtSlot, QThread, pyqtSignal, QRect, QSize, QStringListModel, QRegExp, QCoreApplication, QSettingsfrom PyQt5.QtGui import QIcon, QTextDocument, QTextCursor, QPixmap, QPalette, QColor, QKeyEvent, QFontMetrics, QPainter, QTextFormat, QRegExpValidatorfrom PyQt5 import QtPrintSupportimport fitz#mainWindow class is used to create an instance of the text editor window.class EditorWindow(QMainWindow):    #Initializes an instance of mainWindow and QMainWindow class    def __init__(self, parent = None):        super(EditorWindow, self).__init__(parent)        self.setCurrentFile('')        self.initUI()    def initUI(self):        #Setting properties for the newly initialized window        self.setWindowTitle('LaTeX editor')        self.toolbar = self.addToolBar('Toolbar')        WindowUtilityFunctions.setTopLeft(self)        self.resize(screenX/2, screenY/1.25)        self.init_menuBar()        self.footerBar_init()        self.leftDock_sideBar()        self.mainActivity_init()        self.init_highlighter()        self.toolBar_init()        self.show()    def mainActivity_init(self):        #Initializes an editable text box and sets it as the central widget to cover the whole window.        self.text = textEditor() #Replace with textEditor        try:            file = QFile('example_texdocs/intro.tex')            file.open(QFile.ReadOnly | QFile.Text)            instr = QTextStream(file)            QApplication.setOverrideCursor(Qt.WaitCursor)            self.text.document().setPlainText(instr.readAll())            QApplication.restoreOverrideCursor()            file.close()            self.text.document().setModified(False)        except:            pass        self.setCentralWidget(self.text)    def closeEvent(self, event):        close_dialogBox = QMessageBox()        if self.text.document().isModified():            close_dialogBox.setText("Current loaded document has not been saved.\nDo you want to save the document and then quit?")            close_dialogBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)            response = close_dialogBox.exec_()            if response == QMessageBox.Yes:                self.saveFile_action()                if self.text.document().isModified() == True:                    event.ignore()                else:                    event.accept()            elif response == QMessageBox.No:                event.accept()            else:                event.ignore()                    else:            close_dialogBox.setText("Are you sure you want to quit?")            close_dialogBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)            if close_dialogBox.exec_() == QMessageBox.Yes:                event.accept()            else:                event.ignore()                def closeEvent_quitButton(self):        #Modified closeEvent method to ensure that quit button works from menu bar as quit button passes a bool (and not an event).        close_dialogBox = QMessageBox()        if self.text.document().isModified():            close_dialogBox.setText("Current loaded document has not been saved.\nDo you want to save the document and then quit?")            close_dialogBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)            response = close_dialogBox.exec_()                        if response == QMessageBox.Yes:                self.saveFile_action()                qApp.quit()            elif response == QMessageBox.No:                qApp.quit()            else:                pass        else:            close_dialogBox.setText("Are you sure you want to quit?")            close_dialogBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)            if close_dialogBox.exec_() == QMessageBox.Yes:                qApp.quit()            else:                pass    def init_menuBar(self):        menuBar = self.menuBar()        fileMenu = menuBar.addMenu('&File')        quitAction = fileMenu.addAction('Quit')        quitAction.triggered.connect(self.closeEvent_quitButton)        newFile_fileMenu = fileMenu.addAction('&New File')        newFile_fileMenu.setShortcut('CTRL+N')        newFile_fileMenu.triggered.connect(self.newFile_action)        openFile_fileMenu = fileMenu.addAction('&Open document...')        openFile_fileMenu.setShortcut('CTRL+O')        openFile_fileMenu.triggered.connect(self.openFile_action)        save_fileMenu = fileMenu.addAction('&Save')        save_fileMenu.setShortcut('CTRL+S')        save_fileMenu.triggered.connect(self.saveFile_action)        saveAs_fileMenu = fileMenu.addAction('&Save as...')        saveAs_fileMenu.setShortcut('CTRL+SHIFT+S')        saveAs_fileMenu.triggered.connect(self.saveAs)        editMenu = menuBar.addMenu('&Edit')        undo_editMenu = editMenu.addAction('Undo')        undo_editMenu.setShortcut('CTRL+Z')        #Lambda expressions used to ensure that methods function properly when called on event trigger.        undo_editMenu.triggered.connect(lambda: \                    (self.text.undo(), self.footerBar_setMessage("Menu -> Edit: Undo", 500)))                redo_editMenu = editMenu.addAction('Redo')        redo_editMenu.setShortcut('CTRL+Y')        redo_editMenu.triggered.connect(self.redoAction)        findText_editMenu = editMenu.addAction('Find text...')        findText_editMenu.setShortcut('CTRL+F')        findText_editMenu.triggered.connect(lambda: self.testing_QLineEdit.setFocus())        editMenu.addSeparator()        cut_editMenu = editMenu.addAction('Cut')        cut_editMenu.setShortcut('CTRL+X')        cut_editMenu.triggered.connect(lambda: \                    (self.text.cut(), self.footerBar_setMessage("Menu -> Edit: Cut", 500)))        copy_editMenu = editMenu.addAction('Copy')        copy_editMenu.setShortcut('CTRL+C')        copy_editMenu.triggered.connect(lambda: \                    (self.text.copy(), self.footerBar_setMessage("Menu -> Edit: Copy", 500)))        paste_editMenu = editMenu.addAction('Paste')        paste_editMenu.setShortcut('CTRL+V')        paste_editMenu.triggered.connect(lambda: \                    (self.text.paste(), self.footerBar_setMessage("Menu -> Edit: Paste", 500)))        viewMenu = menuBar.addMenu('&View')        view_Test = viewMenu.addAction('Filler')        windowMenu = menuBar.addMenu('&Window')        window_Test = windowMenu.addAction('Filler')        window_Preferences = windowMenu.addAction('Preferences')        #Need to add preferences menu as a new window to adjust visual settings on editor.        helpMenu = menuBar.addMenu('&Help')        if WindowUtilityFunctions.isMacOS() == True:            print("-- Help menu items appears in the 'applicationName' dropdown menu on MacOS.")        helpMenu_about = helpMenu.addAction('About')        helpMenu_about.triggered.connect(self.about)        self.show()     def toolBar_init(self):        self.toolbar.setMovable(False)        self.toolbar.setMinimumSize(0,30)        self.openFile = QAction(QIcon('Assets/Icons/of_Icon.png'), '&Open file', self)        self.openFile.setShortcut('CTRL+O')        self.openFile.triggered.connect(self.openFile_action)        self.toolbar.addAction(self.openFile)        self.saveFile = QAction(QIcon('Assets/Icons/sf_Icon.png'), '&Save file', self)        self.saveFile.setShortcut('CTRL+S')        self.saveFile.triggered.connect(self.saveFile_action)        self.toolbar.addAction(self.saveFile)        self.newFile = QAction(QIcon('Assets/Icons/nf_Icon.png'), '&New file', self)        self.newFile.setShortcut('CTRL+N')        self.newFile.triggered.connect(self.newFile_action)        self.toolbar.addAction(self.newFile)        self.previewTexFile = QAction(QIcon('Assets/Icons/pftex_Icon.png'), '&Preview in LaTeX format', self)        self.previewTexFile.triggered.connect(self.previewTex)        self.toolbar.addAction(self.previewTexFile)        self.toolbar_spacer()        self.findText_toolbar()        self.show()    def init_highlighter(self):        self.higlight = highlighter.SyntaxHighlighter(self.text.document())    def toolbar_spacer(self):        tb_Spacer = QWidget()        tb_Spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)        self.toolbar.addWidget(tb_Spacer)    def footerBar_init(self):        #May need to create an instance of statusBar in this function to add more widgets if needed.        self.statusBar().showMessage('LaTeX editor booted up!', 2000)        self.show()    def footerBar_setMessage(self, message, mSecs):        self.statusBar().showMessage(message, mSecs)        self.show()    def newFile_action(self):        childWindow = EditorWindow()        childWindow.show()        childWindow.statusBar().showMessage("New window", 2000)        #Need to be able to detect if file is opened in another window to prevent user from editing same document twice in 2 different windows.    def openFile_action(self):        close_dialogBox = QMessageBox()        if self.text.document().isModified():            close_dialogBox.setText("Current loaded document has not been saved.\nDo you want to save the document before opening a file?")            close_dialogBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)            response = close_dialogBox.exec_()                        if response == QMessageBox.Yes:                self.saveFile_action()            else:                pass        fileName, _ = QFileDialog.getOpenFileName(self)        if fileName:            self.loadFile(fileName)            self.text.document().setModified(False)    def saveFile_action(self):        if self.currentFile:            self.save(self.currentFile)            self.text.document().setModified(False)        else:            self.saveAs()    def saveAs(self):        fileName, _ = QFileDialog.getSaveFileName(self)        if fileName:            self.save(fileName)            self.text.document().setModified(False)    def save(self, fileName):        file = QFile(fileName)        if not file.open( QFile.WriteOnly | QFile.Text):            QMessageBox.warning(self, "Recent Files",                    "Cannot write file %s:\n%s." % (fileName, file.errorString()))            return        outstr = QTextStream(file)        QApplication.setOverrideCursor(Qt.WaitCursor)        outstr << self.text.toPlainText()        QApplication.restoreOverrideCursor()        self.setCurrentFile(fileName)        self.statusBar().showMessage("File saved", 1000)    def setCurrentFile(self, fileName):        self.currentFile = fileName        if self.currentFile:            self.setWindowTitle("LaTeX editor --- " + fileName)        else:            self.setWindowTitle("LaTeX editor")    def loadFile(self, fileName):        file = QFile(fileName)        if not file.open( QFile.ReadOnly | QFile.Text):            QMessageBox.warning(self, "Error",                    "Cannot read file %s:\n%s." % (fileName, file.errorString()))            return        instr = QTextStream(file)        QApplication.setOverrideCursor(Qt.WaitCursor)        self.text.setPlainText(instr.readAll())        QApplication.restoreOverrideCursor()        self.setCurrentFile(fileName)        self.statusBar().showMessage("File loaded", 2000)    def about(self):        QMessageBox.about(self, "About LaTeX text editor...",                         "LaTeX text editor created by Matthew Lam. \                          \nGithub page: https://www.github.com/matthew-lam")    def redoAction(self):            self.text.redo()            redo_actionsLeft = self.text.document().availableRedoSteps()            self.footerBar_setMessage("Redo actions remaining on stack: " \                                        + str(redo_actionsLeft), 2000)    def findText_toolbar(self):        self.toolbar.addSeparator()        self.testing_QLineEdit = QLineEdit()        self.testing_QLineEdit.setPlaceholderText(" 🔍   Find text...")        self.testing_QLineEdit.setMaximumWidth(200)        self.toolbar.addWidget(self.testing_QLineEdit)        self.testing_QLineEdit.returnPressed.connect(lambda: self.findText())            def findText(self):        text_toFind = self.testing_QLineEdit.text()        textCursor = self.text.textCursor()        if text_toFind:            if self.text.find(text_toFind) == False and not textCursor.atStart():                textCursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor, 1)                                self.text.setTextCursor(textCursor)            else:                self.text.document().find(text_toFind)        else:            self.footerBar_setMessage("Search bar is empty. Please enter a word to find.", 2000)    def previewTex(self):        #Compiles contents of current document into LaTeX format and then displays it on a preview window.        #Thread used to run function so GUI remains responsive due to non-blocking processing from multi-threading.        pathNameExt = os.path.splitext(self.currentFile)        copiedFile_name = pathNameExt[0] + '.tex'        if pathNameExt[0] == '':            invalidFile_message = QMessageBox()            invalidFile_message.setText("No file / invalid file referenced. \                \n\nPlease choose a valid .tex file to convert and preview as a PDF. \                \n\nIf trying to preview an unsaved file, save the file and try again.")            invalidFile_message.exec_()        elif pathNameExt[1] != '.tex':            self.saveFile_action()            warning_message = QMessageBox()            warning_message.setText("File being previewed did not have a .tex extension.\                File was copied and file was changed to have a .tex extension.")            warning_message.exec_()            self.save(copiedFile_name)            print("File copied:" + self.currentFile + " -- and saved as: " + copiedFile_name)            self.workThread = previewUI.preview_thread(self)            self.workThread.start()            self.workThread.thread_message.connect(self.thread_finish_message)            self.workThread.returnCode.connect(self.get_returnCode)        else:            self.footerBar_setMessage("File being converted to viewable PDF .tex file.", 5000)            self.workThread = previewUI.preview_thread(self)            self.workThread.start()            self.workThread.thread_message.connect(self.thread_finish_message)            self.workThread.returnCode.connect(self.get_returnCode)    def thread_finish_message(self, message):        #executed when preview_thread.thread_message emits signal            thread_message = QMessageBox()            thread_message.setText("Processing of .tex file has finished.\                    \n\nPress the 'show details' button to read log.")            thread_message.setDetailedText(message)            thread_message.exec_()    def get_returnCode(self, returnCode):        if returnCode == 0:            self.spawnPreviewWindow = previewUI.PreviewWindow(self, screenX/2, screenY/1.25)            self.footerBar_setMessage("PREVIEW WINDOW HOTKEYS : Press '=' to zoom in. Press '-' to zoom out.", 8000)        else:            pass    def leftDock_sideBar(self):        upperDockWidget = self.addLeftDockWidget("LaTeX actions and commands")        upperCase_GSymbols = self.addLeftDockWidget("Greek letters - Upper ")        lowerCase_GSymbols = self.addLeftDockWidget(" Lower ")        mathSymbols = self.addLeftDockWidget("Math symbols")        mathSymbols.setMaximumHeight(150)        dockTreeWidget = self.dock_treeWidget()        grid_lowerCase = self.dockSymbols(0)        grid_upperCase = self.dockSymbols(1)        dockGridWidget_ms = self.dockSymbols(2)        #Creates a scroll area as a container for grid of buttons -- greek alphabet        scrollArea = self.addLD_ScrollWidget(grid_lowerCase)        scrollArea2 = self.addLD_ScrollWidget(grid_upperCase)        #Math symbols        scrollArea3 = self.addLD_ScrollWidget(dockGridWidget_ms)        upperDockWidget.setWidget(dockTreeWidget)        lowerCase_GSymbols.setWidget(scrollArea)        upperCase_GSymbols.setWidget(scrollArea2)        mathSymbols.setWidget(scrollArea3)        self.addDockWidget(Qt.LeftDockWidgetArea, upperDockWidget)        self.splitDockWidget(upperDockWidget, upperCase_GSymbols, Qt.Vertical)        self.splitDockWidget(upperDockWidget, mathSymbols, Qt.Vertical)        self.tabifyDockWidget(upperCase_GSymbols, lowerCase_GSymbols)    def addLD_ScrollWidget(self, widget):        scrollArea = QScrollArea()        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)        scrollArea.setWidget(widget)        scrollArea.setAlignment(Qt.AlignHCenter)        return scrollArea        def dockSymbols(self, alphabetCase):        #When pressing button to insert text, insert text into currently focused textbox        #So when user is formulating a mathematical equation, they can use math symbols        gridContainer = QWidget()        symbolGrid = QGridLayout()        if alphabetCase == 0:            buttons = {'α':'\\alpha', 'β':'\\beta', 'γ':'\\gamma', 'δ':'\delta',            'ε':'\epsilon', 'ζ':'\zeta', 'η':'\eta', 'θ':'\\theta', 'ι':'\iota', 'κ':'\kappa',            'λ':'\lambda', 'μ':'\mu', 'ν':'\\nu', 'ο':'\omnicron', 'π':'\pi', 'ρ':'\\rho',             'φ':'\phi', 'χ':'\chi','ψ':'\psi', 'ω':'\omega', 'ξ':'\\xi', 'τ':'\\tau', 'σ':'\\sigma', 'υ':'\\upsilon'}        elif alphabetCase == 1:            buttons = {'Α':'\\Alpha', 'Β':'\\Beta', 'Γ':'\\Gamma', 'Δ':'\Delta',            'Ε':'\Epsilon', 'Ζ':'\Zeta', 'Η':'\Eta', 'Θ':'\\Theta', 'Ι':'\Iota', 'Κ':'\Kappa',            'Λ':'\Lambda', 'Μ':'\Mu', 'Ν':'\\Nu', 'Ο':'\Omnicron', 'Π':'\Pi', 'Ρ':'\\Rho',             'Φ':'\Phi', 'Χ':'\Chi','Ψ':'\Psi', 'Ω':'\Omega', 'Ξ':'\\Xi', 'Τ':'\\Tau', 'Σ':'\\Sigma', 'Υ':'\\Upsilon'}        else:            buttons = {'∨':'\or', '∧':'\\and', '×':'\\times', '+':'+', '-':'-', '÷':'\div', '∑':'\sum', '≤':'\le', '≥':'\ge',            '⇒':'\Rightarrow', '⊆':'\subseteq', '⊂':'\subset', '⊇':'\supseteq', '⊃':'\supset', '→':'\\to', '↦':'\mapsto', '⊢':'\\vdash',            '∫':'\int', '…':'\ldots', '⋮':'\cdots', '⋱':'\ddots', '∴':'\\therefore', '¬':'\\neg', '∞':'\infty' ,            '≠':'\\ne', '≈':'\\approx', '≡':'\equiv', '∀':'\\forall', '∃':'\exists', '∈':'\in', '⇔':'\Leftrightarrow',            '∌':'\\ni', '∅':'\\empty', 'ℙ':'\mathbb{P}', 'ℝ':'\mathbb{R}', 'ℤ':'\mathbb{Z}', '⊥':'\\bot',             '∪':'\cup', '∩':'\cap', '⊗':'\otimes'}        #xi, tau, sigma, upsilon                i = 0        j = 0        buttonsInRow = 4        for key in buttons:            button = QPushButton('%s' % key)            button.clicked.connect(lambda state, x=buttons.get(key): self.editor_insertText(x))            symbolGrid.addWidget(button, i, j)            if(j == buttonsInRow): #Change const val to however many buttons should be in a row                j = 0                i = i + 1            else:                j = j + 1        QLayout.setAlignment(symbolGrid, Qt.AlignHCenter)        symbolGrid.setContentsMargins(0, 0, 0, 0)        symbolGrid.setSpacing(0)        gridContainer.setContentsMargins(0, 0, 0, 0)        gridContainer.setLayout(symbolGrid)        gridContainer.show()        return gridContainer    def editor_insertText(self, text):        txtCursor = self.text.textCursor()        txtCursor.insertText(text)    def addLeftDockWidget(self, title):        dock = QDockWidget(title, self)        dock.setAllowedAreas(Qt.LeftDockWidgetArea)        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)        dock.setMaximumWidth(225)        dock.setMinimumWidth(225)        return dock    def dock_treeWidget(self):         self.initializeQSettings()        self.treeWidget = QTreeWidget()        self.treeWidget.setFocusPolicy(Qt.NoFocus)        self.treeWidget.header().close()        treeItem1 = QTreeWidgetItem(self.treeWidget)        treeItem1.setText(0, "Macros")        self.treeItem1_addMacro = QTreeWidgetItem(treeItem1)        self.treeItem1_addMacro.setText(0, "Add macro")                self.treeItem1_defined = QTreeWidgetItem(treeItem1)        self.treeItem1_defined.setText(0, "User-defined macros/env...")        #Quick access (sidebar) macros        self.macroSlot1 = QTreeWidgetItem(self.treeItem1_defined)        self.macroSlot1.setText(0, "Slot 1")        self.macroSlot2 = QTreeWidgetItem(self.treeItem1_defined)        self.macroSlot2.setText(0, "Slot 2")        self.macroSlot3 = QTreeWidgetItem(self.treeItem1_defined)        self.macroSlot3.setText(0, "Slot 3")        self.macroSlot4 = QTreeWidgetItem(self.treeItem1_defined)        self.macroSlot4.setText(0, "Slot 4")        self.macroSlot5 = QTreeWidgetItem(self.treeItem1_defined)        self.macroSlot5.setText(0, "Slot 5")        self.macroSlot6 = QTreeWidgetItem(self.treeItem1_defined)        self.macroSlot6.setText(0, "Slot 6")        treeItem3 = QTreeWidgetItem(self.treeWidget)        treeItem3.setText(0, "Math functions")        #highlight math in-line / begin math equation -> simple adding text to doc if clicked        #if enough time : add graph previewer -> can then be repurposed into preview image        treeItem4 = QTreeWidgetItem(self.treeWidget)        treeItem4.setText(0, "Document formatting / other")        #add image and other stuff        treeItem5 = QTreeWidgetItem(self.treeWidget)        treeItem5.setText(0, "Blank templates")        treeItem6 = QTreeWidgetItem(self.treeWidget)        treeItem6.setText(0, "Help & more...")        self.treeWidget.itemDoubleClicked.connect(self.TI_selectedHandler)        return self.treeWidget    def TI_selectedHandler(self, item, column): #Where args (item & column) are parameters of the 'itemDoubleClicked(...)' signal        #TODO: Add handler functions for each item clicked.        #Handlers should have QMessageBox popups for users to input information about user-defined commands        if item == self.treeItem1_addMacro and item.isSelected():            self.addMacro_msgBox()        elif item == self.treeItem1_defined and item.isSelected():            print("User-defined macros/env... has been double clicked.")        elif item == self.macroSlot1 or self.macroSlot2 or self.macroSlot3 or self.macroSlot4 or self.macroSlot5 or self.macroSlot6: #condition for doubleclicked and inserting macro into text            macroSlot = item.data(0, 2)            #Bug fix: all DIRECT children (second level) of QTreeWidget kept triggering this whole elif condition and would                #   insert their corresponding text into the editor. Sloppy fix for now, but it works.            if(macroSlot == "Macros"):                pass            elif(macroSlot == "Math functions"):                pass            elif(macroSlot == "Document formatting / other"):                pass            elif(macroSlot == "Blank templates"):                pass            elif(macroSlot == "Help & more..."):                pass            else:                self.editor_insertText(macroSlot)        else:            pass    def addMacro_msgBox(self): #Make into a re-usable method for either newenvironment or newcommand via method parameters and conditonal statements        self.dialogBox = QDialog()        self.dialogBox.setWindowTitle("Add macro")        wikiBooksLink = "<a href=\"https://en.wikibooks.org/wiki/LaTeX/Macros\">Wikibooks.</a>"        descriptionText = QLabel("Macros are user defined commands that invoke a set of commands, as set by the user in the macro.\            \n\nFor more information please refer to online resources such as : %s\            \n\nAdd a macro to LaTeX editor to be used throughout the document." % wikiBooksLink)        descriptionText.setTextFormat(Qt.RichText)        descriptionText.setWordWrap(True)        descriptionText.setTextInteractionFlags(Qt.TextBrowserInteraction)        descriptionText.setOpenExternalLinks(True)                nameFieldText = QLabel("Macro name: ")        inputFieldText = QLabel("Macro command(s): ")        macroNameField = QLineEdit("{\\name}")        macroInputField = QLineEdit("[num]{definition/commands}")        verticalLayout = QVBoxLayout()        inLineLayout_container1 = QWidget()        inLineLayout_container2 = QWidget()        inLineLayout1 = QHBoxLayout()        inLineLayout1.addWidget(nameFieldText)        inLineLayout1.addWidget(macroNameField)        inLineLayout2 = QHBoxLayout()        inLineLayout2.addWidget(inputFieldText)        inLineLayout2.addWidget(macroInputField)        inLineLayout_container1.setLayout(inLineLayout1)        inLineLayout_container2.setLayout(inLineLayout2)        buttonBox = QDialogButtonBox()        buttonBox.addButton('Add macro', QDialogButtonBox.AcceptRole)        buttonBox.addButton('Cancel', QDialogButtonBox.RejectRole)        validatorRegex = QRegExp("[a-zA-Z\{\}\\\\]+")        macroNameValidator = QRegExpValidator(validatorRegex, macroNameField)        macroNameField.setValidator(macroNameValidator)        rbText = QLabel("\nMacro definition type: ")        self.radioButton_isCommand = QRadioButton("New command")        self.radioButton_isEnvironment = QRadioButton("New environment")        #If radio buttons are not checked, display a warning box and reject defined macro from being saved.        buttonBox.accepted.connect(lambda: self.boxAcceptRole(macroNameField.text(), macroInputField.text(), self.radioButton_isCommand.isChecked(), self.radioButton_isEnvironment.isChecked()))        buttonBox.rejected.connect(lambda: self.dialogBox.close())        dropDownListText = QLabel("\nSave to slot: ")        self.dropDownList = QComboBox()        self.dropDownList.addItem("Slot 1")        self.dropDownList.addItem("Slot 2")        self.dropDownList.addItem("Slot 3")        self.dropDownList.addItem("Slot 4")        self.dropDownList.addItem("Slot 5")        self.dropDownList.addItem("Slot 6")        self.dropDownList_itemIndex = 0        self.dropDownList.activated.connect(self.setCurrentListIndex)        #Class variable -- dropDownList activated index found in function testFunc: used to tell which item in the list has been selected by user.        verticalLayout.addWidget(descriptionText)        verticalLayout.addWidget(inLineLayout_container1)        verticalLayout.addWidget(inLineLayout_container2)        verticalLayout.addWidget(dropDownListText)        verticalLayout.addWidget(self.dropDownList)        verticalLayout.addWidget(rbText)        verticalLayout.addWidget(self.radioButton_isCommand)        verticalLayout.addWidget(self.radioButton_isEnvironment)        verticalLayout.addWidget(buttonBox)        self.dialogBox.setFixedSize(600, 400)        self.dialogBox.setLayout(verticalLayout)        self.dialogBox.show()    def setCurrentListIndex(self, index):        #Setter for dropDownList_itemIndex        self.dropDownList_itemIndex = index        #The variable is then used in the boxAcceptRole method to determine which slot the user picked to store their macro in to.    def boxAcceptRole(self, macroName, macroCommands, isCommandChecked, isEnvironmentChecked):        #Need to put QSettings stuff here so we can save and use macros        #Qt radio buttons to be checked to determine whether new environment or new command macro is defined        if(isCommandChecked or isEnvironmentChecked):            macroList = [macroName, macroCommands]            self.saveMacro(macroList, isCommandChecked, isEnvironmentChecked)            self.dialogBox.close()        else:            errorMessageBox = QMessageBox()            errorMessageBox.setText("Macro type not specified. Use radio buttons to specify macro type to be defined.")            errorMessageBox.exec_()    def saveMacro(self, macroList, isCommandChecked, isEnvironmentChecked):        #Uses QSettings to allow program to remember user defined macros between sessions (application opening/closing)        strippedMacroName = macroList[0].strip("{}")        print("Stripped macro name: %s" % strippedMacroName)        settings = QSettings()        settings.setValue(strippedMacroName, macroList[1])        #At this point, we have the thing macro name and the command stored in QSettings. We need to now harness it to be shown to user.        saveMacroSettingsValue = settings.value(strippedMacroName)        #Get item by index of selected macro slot and then set QTreeWidgetItem's text        self.treeItem1_defined.child(self.dropDownList_itemIndex).setText(0, strippedMacroName)        #Need to put macro definition somewhere in the document right here...        if(isCommandChecked):            #Define new command            newMacroString = "\n\\newcommand" + macroList[0] + macroList[1] + "\n"            self.editor_insertText(newMacroString)        elif(isEnvironmentChecked):            newMacroString = "\n\\newenvironment" + macroList[0] + macroList[1] + "\n"            self.editor_insertText(newMacroString)        self.treeItem1_defined.child(self.dropDownList_itemIndex).setData(0, 2, strippedMacroName)    def initializeQSettings(self):        QCoreApplication.setOrganizationName("ML")        QCoreApplication.setOrganizationDomain("matthew-lam.github.com")        QCoreApplication.setApplicationName("LaTeX editor")        settings = QSettings()class LineNumberArea(QWidget):    def __init__(self, editor):        super().__init__(editor)        self.editor = editor        def sizeHint(self):        return QSize(self.editor.lineNumberAreaWidth(), 0)        def paintEvent(self, event):        self.editor.lineNumberAreaPaintEvent(event)class autoCompleter(QCompleter):    completerSignal = pyqtSignal(str)    def __init__(self, keywords = None, parent = None): #Super call to fill out params declared in this class        keywords = []        kwDocSettings = ['\documentclass[options]{style}', '\setlength{options}{length}',         r'\usepackage{pkgName}', r'\newcommand']                kwDocFormatting = [r'\newpage', '\pagebreak[number]', r'\nopagebreak[number]',         r'\newenvironment{name}[optional_num][optional_default]{before}{after}', '\pageref{key}',        r'\ref{key}', '\label{key}', '\hspace{length}', '\hspace[*]{length}',        '\rspace{length}', r'\vspace[*]{length}', '\par']        kwBody = ['\section{text}', '\subsection{text}', '\subsubsection{text}',        r"\title{text}", r"\author{name}", "\maketitle{title}", 'begin{document}',         'end{document}', r'\begin{args}', "\end{args}"]        keywords.extend(kwDocSettings)        keywords.extend(kwDocFormatting)        keywords.extend(kwBody)        super().__init__(keywords, parent)        self.setCompletionMode(QCompleter.PopupCompletion)        self.highlighted.connect(self.setHighlighted)    def setHighlighted(self, text):        self.lastSelected = text    def getSelected(self):        return self.lastSelectedclass textEditor(QPlainTextEdit):        #An extension of the QPlainTextEdit widget.    #Added functionality of having line numbers and an auto-completer.    def __init__(self):        super().__init__()        self.lineNumberArea = LineNumberArea(self)        self.LineWrapMode(QTextEdit.FixedPixelWidth)        self.setLineWrapMode(0)        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)        self.updateRequest.connect(self.updateLineNumberArea)        self.cursorPositionChanged.connect(self.highlightCurrentLine)        self.updateLineNumberAreaWidth(0)        self.autoComplete = autoCompleter()        self.autoComplete.setWidget(self)        self.autoComplete.setFilterMode(Qt.MatchContains)        self.autoComplete.completerSignal.connect(self.insertCompleterText)    def insertCompleterText(self, completeText):        cursor = self.textCursor()        cursor.select(QTextCursor.WordUnderCursor)        tailText = (len(completeText) - len(self.autoComplete.completionPrefix()))        cursor.movePosition(QTextCursor.Left)        cursor.movePosition(QTextCursor.EndOfWord)        for i in range(len(cursor.selectedText())):            cursor.deletePreviousChar()        cursor.insertText(completeText[-tailText:])        self.setTextCursor(cursor)        self.autoComplete.popup().hide()    def focusInEvent(self, event):        if self.autoComplete:            self.autoComplete.setWidget(self)        QPlainTextEdit.focusInEvent(self, event)    def keyPressEvent(self, event):        cursor = self.textCursor()        if event.key() == Qt.Key_Return and self.autoComplete.popup().isVisible():            self.autoComplete.completerSignal.emit(self.autoComplete.getSelected())            self.autoComplete.setCompletionMode(QCompleter.PopupCompletion)            return        QPlainTextEdit.keyPressEvent(self, event)        cursorRect = self.cursorRect()        if(event.key() == Qt.Key_Backslash or (event.key() == Qt.Key_Control and self.autoComplete.popup().isVisible() == False)):            self.autoComplete.setCompletionPrefix(cursor.selectedText())            listPopup = self.autoComplete.popup()            listPopup.setCurrentIndex(self.autoComplete.completionModel().index(0,0))            cursorRect.setWidth(self.autoComplete.popup().sizeHintForColumn(0) + self.autoComplete.popup().verticalScrollBar().sizeHint().width())            self.autoComplete.complete(cursorRect)        else:            self.autoComplete.popup().hide()    def lineNumberAreaWidth(self):        blockCountLines = max(1, self.blockCount())        digits = 1        while(blockCountLines >= 10):            blockCountLines /= 10            digits += 1        space = 5 + self.fontMetrics().width('9') * digits        return space    def updateLineNumberAreaWidth(self, _): #Where '_' is an arbitrary variable.        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)    def updateLineNumberArea(self, rect, dy):        if dy:            self.lineNumberArea.scroll(0, dy)        else:            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())        if rect.contains(self.viewport().rect()):            self.updateLineNumberAreaWidth(0)    def resizeEvent(self, event):        super().resizeEvent(event)        rectContents = self.contentsRect()        self.lineNumberArea.setGeometry(QRect(rectContents.left(), rectContents.top(), self.lineNumberAreaWidth(), rectContents.height()))    def lineNumberAreaPaintEvent(self, event):        painter = QPainter(self.lineNumberArea)        painter.fillRect(event.rect(), Qt.lightGray)        block = self.firstVisibleBlock()        blockNumber = block.blockNumber()        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()        bottom = top + self.blockBoundingRect(block).height()        height = self.fontMetrics().height()        while block.isValid() and (top <= event.rect().bottom()):            if block.isVisible() and (bottom >= event.rect().top()):                number = str(blockNumber + 1)                painter.setPen(Qt.black)                painter.drawText(0, top, self.lineNumberArea.width(), height, Qt.AlignHCenter, number)            block = block.next()            top = bottom            bottom = top + self.blockBoundingRect(block).height()            blockNumber += 1    def highlightCurrentLine(self):        extraSelections = []        if not self.isReadOnly():            selection = QTextEdit.ExtraSelection()            lineColor = QColor(Qt.lightGray).lighter(115)            selection.format.setBackground(lineColor)            selection.format.setProperty(QTextFormat.FullWidthSelection, True)            selection.cursor = self.textCursor()            selection.cursor.clearSelection()            extraSelections.append(selection)        self.setExtraSelections(extraSelections)class WindowUtilityFunctions(QWidget):    def getScreenDims():        screenObj = app.primaryScreen()        screenSize = screenObj.size()        screenDims = screenObj.availableGeometry()        return screenDims    def getScreenSizeX(screenDims):        return screenDims.width()    def getScreenSizeY(screenDims):        return screenDims.height()    def setCenter(self):    #Probably will need to be moved to a different class / may be removed        windowProp = self.frameGeometry()        centerPosition = QDesktopWidget().availableGeometry().center()        windowProp.moveCenter(centerPosition)        self.move(windowProp.topLeft())    def setTopLeft(self):   #Probably will need to be moved to a different class        #Ensures that window is always set to the top left no matter the screen res        windowProp = self.frameGeometry()        topLeftPosition = QDesktopWidget().availableGeometry().topLeft()        windowProp.moveLeft(0)        self.move(windowProp.topLeft())       def setTopRight(self):   #Probably will need to be moved to a different class        #Ensures that window is always set to the top left no matter the screen res        self.move(QApplication.desktop().screen().rect().topRight())    def isMacOS():            try:            #Detects if OS is MacOS.                if platform.system() == "Darwin":                    print(platform.system() + " -- OS used is MacOS.")                    return True            except:                return False#Put this block of code into desired main file. mainWindow() is used as a constructor for creating windows.if __name__ == '__main__':    #Application main loop for event handling and continuous running of application.    print(fitz.__doc__)    app = QApplication(sys.argv)    screenDims = WindowUtilityFunctions.getScreenDims()       #Can use this variable to re-size preview tex window.    screenX = WindowUtilityFunctions.getScreenSizeX(screenDims)    screenY = WindowUtilityFunctions.getScreenSizeY(screenDims)    newWindow = EditorWindow()    sys.exit(app.exec_())