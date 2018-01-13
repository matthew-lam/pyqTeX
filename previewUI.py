from editorUI import *
from pathlib import Path
import glob
import time

class PreviewWindow(QWidget):

    def __init__(self, EditorWindow_class, screenDimX, screenDimY):
        time.sleep(1.25)
        self.init_pathVariables(EditorWindow_class)
        super(PreviewWindow, self).__init__()

        self.scene = QGraphicsScene()
        self.view = View(self.scene)
        self.scene.setBackgroundBrush(QColor('darkGray'))
        self.imagePos = 0
        pageBreakValue = 25
        
        for file in (sorted(os.listdir(self.folderDir))):
            print(file)
            #Probably should sleep first and wait for files to finish processing and THEN run this shit
            pixmap = QPixmap(os.path.join(self.folderDir, file))
            imageObj = self.scene.addPixmap(pixmap)
            imageObj.setOffset(0, self.imagePos)
            self.imagePos = self.imagePos + pixmap.height() + pageBreakValue

        self.view.fitInView(25, 0, screenDimY, screenDimX, Qt.KeepAspectRatio)
        self.view.setAlignment(Qt.AlignCenter)
        self.view.resize(screenDimX, screenDimY)
        WindowUtilityFunctions.setTopRight(self.view)
        self.view.setWindowTitle('LaTeX editor -- Preview Window')
        self.view.show()

    def init_pathVariables(self, EditorWindow_class):
        self.file = EditorWindow_class.currentFile
        filePath = os.path.splitext(self.file)
        self.p = Path(filePath[0])
        self.baseFolder = str(self.p.parent.parent) + '/' + os.path.basename(os.path.normpath(self.p) + '-pdf') 
        self.folderDir = self.baseFolder + '-compiled'


class View(QGraphicsView):

    def __init__(self, parent = None):
        QGraphicsView.__init__(self, parent)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Equal:
            self.scale(1.1, 1.1)
        elif event.key() == Qt.Key_Minus:
            self.scale(0.9, 0.9) 

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
        doc = fitz.open(self.pdfPath)
        try:
            os.makedirs(self.folderDir)
        except:
            #Folder already exists
            pass
        for pageCount in range(0, len(doc)):
            zoom = 250.0 / 72.0
            matr = fitz.Matrix(zoom, zoom)
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
        #Statements to be processed in thread placed in this method. Use .start() to run thread.         
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
                    "\n------\nPlease ignore console debugging options.")
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
                pngFileFolder = self.baseFolder + '-compiled'
                os.chdir(pngFileFolder)
                files2delete = glob.glob('*.png')
                for pngfiles in files2delete:
                    os.unlink(pngfiles)
                shutil.copy2(pdfFile, (os.path.join(self.baseFolder)))
                shutil.copy2(auxFile, (os.path.join(self.baseFolder)))
                shutil.copy2(logFile, (os.path.join(self.baseFolder)))
                os.remove(pdfFile)
                os.remove(auxFile)
                os.remove(logFile)
        except:
            pass

        try:
            self.PDFtoPNG()
        except:
            pass