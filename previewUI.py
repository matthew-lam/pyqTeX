from editorUI import *
from pathlib import Path

#previewWindow class contains code associated with previewTex (txt -> LaTeX) button
#To create PDFs we can simply call from Python commands to TeX compiler that must have been installed by user.
class PreviewWindow(QScrollArea, QWidget):

    def __init__(self, EditorWindow_class):
        self.init_pathVariables(EditorWindow_class)
        super(PreviewWindow, self).__init__()
        
        windowWidget = QWidget()
        vlayout = QVBoxLayout(windowWidget)
        self.setWidget(windowWidget)
        self.setWidgetResizable(True)
        self.setWindowTitle("LaTeX editor - Document viewer")
        for file in (sorted(os.listdir(self.folderDir))):
            print(str(file))
            label = QLabel(self)
            pixmap = QPixmap(os.path.join(self.folderDir, file))
            label.setPixmap(pixmap)
            vlayout.addWidget(label)
        self.show()

    def init_pathVariables(self, EditorWindow_class):
        self.file = EditorWindow_class.currentFile
        filePath = os.path.splitext(self.file)
        self.p = Path(filePath[0])
        self.baseFolder = str(self.p.parent.parent) + '/' + os.path.basename(os.path.normpath(self.p) + '-pdf') 
        self.folderDir = self.baseFolder + '-compiled'

        # vBox = QVBoxLayout(self)
        # self.setLayout(vBox)
        # self.setWindowTitle("LaTeX editor -- PDF Preview")
        # 
        # vBox.addWidget(scrollArea)
        # self.show()

#Insert worker thread class into another module to maintain readability of code, perhaps previewUI.py?
class preview_thread(QThread):

    thread_message = pyqtSignal(str)
    returnCode = pyqtSignal(int)

    #Instantiate a thread object and then run thread by using .start() method instead of .run()
    def __init__(self, EditorWindow_class):
        QThread.__init__(self)
        self.exiting = False
        self.copiedFile_name = EditorWindow_class.currentFile
        filePath = os.path.splitext(self.copiedFile_name)
        self.p = Path(filePath[0])
        self.baseFolder = str(self.p.parent.parent) + '/' + os.path.basename(os.path.normpath(self.p) + '-pdf') 
        self.folderDir = self.baseFolder + '-compiled'

    def __del__(self):
        #Ensures that processing of thread is finished before thread object is destroyed.
        self.exiting = True
        self.wait()

    def write(self, message):
        thread_message.emit(message)

    def send_ReturnCode(self, intCode):
        returnCode.emit(intCode)

    def PDFtoPNG(self):
        #Converts each page in a PDF file into a PNG file and move to another folder so that they can be viewed in a qt image viewer.
        self.pdfPath = self.baseFolder + '/' + os.path.basename(os.path.normpath(self.p)) + '.pdf' #need to add filename.pdf at the end to get document
        print(self.pdfPath)
        doc = fitz.open(self.pdfPath)
        try:
            os.makedirs(self.folderDir)
        except:
            #Folder already exists
            pass
        for pageCount in range(0, len(doc)):
            px = doc.getPagePixmap(pageCount)
            px_name = "%s-%s.png" % (os.path.basename(os.path.normpath(self.p)), str(pageCount))
            fileDir = str(self.p.parent.parent) + '/' + px_name
            if os.path.isfile(os.path.join(self.baseFolder + '-compiled/' + px_name)):
                px.writePNG(px_name)
                shutil.copy2(fileDir, self.folderDir)
                os.remove(fileDir)
            else:
                px.writePNG(px_name)
                try:
                    shutil.move(fileDir, self.folderDir)
                except:
                    pass
            px = None
        doc.close()
        return        

    def run(self):
        #Statements to be processed in thread placed in this method. Use .start() to run thread.         
        #Creates a new subprocess to compile current document
        proc = subprocess.Popen(['pdflatex', '%s' % self.copiedFile_name],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
        try:
            stdoutdata, stderrdata = proc.communicate(timeout=5)
            #try looking at return code.
            if proc.returncode == 1: 
            #Subprocess (pdflatex) error -- pdflatex crashes (fatal error) and notifies user of error.
                self.thread_message.emit("An error has occured --- error message from log file:\
                    \n\n" + stdoutdata.decode('ascii') + 
                    "\n\nPlease ignore console debugging options.")
                print(stdoutdata.decode('ascii'))
                self.returnCode.emit(1)
            elif proc.returncode == 0: 
            #Subprocess successfully completes as expected.
                self.thread_message.emit("File successfully compiled into .tex format and converted to PDF for viewing out of LaTeX editor and .png format for viewing in LaTeX editor.")
                self.returnCode.emit(0)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdoutdata, stderrdata = proc.communicate()
            print("\n\nErrors have occured during compilation.")
            self.thread_message.emit(stdoutdata.decode('ascii'))

        pdfFile = str(self.p.parent.parent) + '/' + os.path.basename(os.path.normpath(self.p) + '.pdf')
        auxFile = str(self.p.parent.parent) + '/' + os.path.basename(os.path.normpath(self.p) + '.aux')
        logFile = str(self.p.parent.parent) + '/' + os.path.basename(os.path.normpath(self.p) + '.log')
        try:
            if os.path.exists(os.path.join(self.baseFolder)) == False:
                os.makedirs((os.path.join(self.baseFolder)))
                shutil.move(pdfFile, (os.path.join(self.baseFolder)))
                shutil.move(auxFile, (os.path.join(self.baseFolder)))
                shutil.move(logFile, (os.path.join(self.baseFolder)))
            else:
                shutil.copy2(pdfFile, (os.path.join(self.baseFolder)))
                shutil.copy2(auxFile, (os.path.join(self.baseFolder)))
                shutil.copy2(logFile, (os.path.join(self.baseFolder)))
                os.remove(pdfFile)
                os.remove(auxFile)
                os.remove(logFile)
        except:
            pass

        self.PDFtoPNG()

        #When the thread has finished running, a signal is sent to notify the main appwindow to raise a message box
        #to notify the user that the file has successfully been compiled and is ready to view...to

        #After the notification, an instance of PreviewWindow is created to render and view the PDF file.
