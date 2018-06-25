from editorUI import *
from pathlib import Path
import glob
import time

class PreviewWindow(QMainWindow):
    #This class iterates through all the files that exist in the directory where PDF files
    #are located and then shows them in a newly spawned window.
    def __init__(self, EditorWindow_class, screenDimX, screenDimY):
        time.sleep(1.25)
        self.init_pathVariables(EditorWindow_class)
        super(PreviewWindow, self).__init__()

        self.scene = QGraphicsScene()
        self.view = View(self.scene)
        self.scene.setBackgroundBrush(QColor('darkGray'))
        self.imagePos = 0
        pageBreakValue = 25
        
        try:
            for file in (sorted(os.listdir(self.folderDir))):
                print(file)
                #Probably should sleep first and wait for files to finish processing and THEN run this shit
                pixmap = QPixmap(os.path.join(self.folderDir, file))
                imageObj = self.scene.addPixmap(pixmap)
                imageObj.setOffset(0, self.imagePos)
                self.imagePos = self.imagePos + pixmap.height() + pageBreakValue
        except:
            pass

        self.view.fitInView(25, 0, screenDimY, screenDimX, Qt.KeepAspectRatio)
        self.view.setAlignment(Qt.AlignCenter)
        self.setWindowTitle('LaTeX editor -- Preview Window')
        self.setCentralWidget(self.view)
        self.resize(screenDimX, screenDimY)
        windowUtility.WindowUtilityFunctions.setTopRight(self)
        self.toolbar = self.addToolBar('Toolbar')
        self.PW_toolBar_init()
        self.view.scaleDown()
        self.view.scaleDown()
        self.view.scaleDown()
        self.view.scaleDown()
        self.show()

    def init_pathVariables(self, EditorWindow_class):
        self.file = EditorWindow_class.currentFile
        filePath = os.path.splitext(self.file)
        self.p = Path(filePath[0])
        self.baseFolder = str(self.p.parent.parent) + '/' + os.path.basename(os.path.normpath(self.p) + '-pdf') 
        self.folderDir = self.baseFolder + '-compiled'

    def PW_toolBar_init(self):
        self.toolbar.setMovable(False)
        self.toolbar.setMinimumSize(0,45)

        self.printFile = QAction(QIcon('Assets/Icons/print_Icon.png'), '&Print file', self)
        self.printFile.triggered.connect(self.printHandler)
        self.toolbar.addAction(self.printFile)

        self.zoomInFile = QAction(QIcon('Assets/Icons/zoomIn_Icon.png'), '&Zoom in', self)
        self.zoomInFile.triggered.connect(self.view.scaleUp)
        self.toolbar.addAction(self.zoomInFile)

        self.zoomOutFile = QAction(QIcon('Assets/Icons/zoomOut_Icon.png'), '&Zoom out', self)
        self.zoomOutFile.triggered.connect(self.view.scaleDown)
        self.toolbar.addAction(self.zoomOutFile)
        
        self.show()

    def printHandler(self):
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        printDialog = QtPrintSupport.QPrintDialog(printer, self)
        if printDialog.exec_() == QtPrintSupport.QPrintDialog.Accepted:
            painter = QPainter(printer)
            painter.setRenderHint(QPainter.Antialiasing)
            self.view.render(painter)
            painter.end()
        else:
            pass

class View(QGraphicsView):

    def __init__(self, parent = None):
        QGraphicsView.__init__(self, parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Equal:
            self.scaleUp()
        elif event.key() == Qt.Key_Minus:
            self.scaleDown()

    def scaleDown(self):
        self.scale(0.9, 0.9)

    def scaleUp(self):
        self.scale(1.1, 1.1)

class preview_thread(QThread):
    #This class processes .tex -> PDF -> PNG file conversions in a worker thread, seperate from GUI thread
    #then outputs all compiled files into seperate folders.

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
        doc = fitz.open(self.pdfPath)
        try:
            os.makedirs(self.folderDir)
        except:
            #Folder already exists
            pass
        for pageCount in range(0, len(doc)):
            initialZoom = 175.0 / 50.0
            matr = fitz.Matrix(initialZoom, initialZoom)
            px = doc.getPagePixmap(pageCount, matrix = matr, clip = None, alpha = False)
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
        #Statements to be processed in thread is placed in this method. Use .start() to run thread.         
        #Creates a new subprocess to compile current document
        proc = subprocess.Popen(['pdflatex', '%s' % self.copiedFile_name],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
        try:
            stdoutdata, stderrdata = proc.communicate(timeout=1000)
            #try looking at return code.
            if proc.returncode == 1: 
            #Subprocess (pdflatex) error -- pdflatex crashes (fatal error) and notifies user of error.
                self.thread_message.emit("An error has occured --- error message from log file:\n------\
                    \n\n" + stdoutdata.decode('ascii') + 
                    "\n------\nWhere 'l.xxx represents error occuring at line number xxx.\n------\nPlease ignore console debugging options.")
                print(stdoutdata.decode('ascii'))
                self.returnCode.emit(1)
            elif proc.returncode == 0: 
            #Subprocess successfully completes as expected.
                self.thread_message.emit("File successfully compiled into .tex format and converted to PDF for viewing out of LaTeX editor and .png format for viewing in LaTeX editor.")
                self.returnCode.emit(0)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdoutdata, stderrdata = proc.communicate()
            self.thread_message.emit(stdoutdata.decode('ascii'))

        try:
            pdfFile = str(self.p.parent.parent) + '/' + os.path.basename(os.path.normpath(self.p) + '.pdf')
            auxFile = str(self.p.parent.parent) + '/' + os.path.basename(os.path.normpath(self.p) + '.aux')
            logFile = str(self.p.parent.parent) + '/' + os.path.basename(os.path.normpath(self.p) + '.log')

            #Checking if directory already exists befoer moving files
            if os.path.exists(os.path.join(self.baseFolder)) == False:
                os.makedirs((os.path.join(self.baseFolder)))
                shutil.move(pdfFile, (os.path.join(self.baseFolder)))
                shutil.move(auxFile, (os.path.join(self.baseFolder)))
                shutil.move(logFile, (os.path.join(self.baseFolder)))
            elif os.path.exists(os.path.join(self.baseFolder)):
                print((os.path.join(self.baseFolder)))
                shutil.rmtree((os.path.join(self.baseFolder)))
                shutil.rmtree(self.baseFolder + '-compiled')
                os.makedirs((os.path.join(self.baseFolder)))
                shutil.move(pdfFile, (os.path.join(self.baseFolder)))
                shutil.move(auxFile, (os.path.join(self.baseFolder)))
                shutil.move(logFile, (os.path.join(self.baseFolder)))
        except:
            pass

        try:
            self.PDFtoPNG()
        except:
            pass
