from editorUI import *

#previewWindow class contains code associated with previewTex (txt -> LaTeX) button
#To create PDFs we can simply call from Python commands to TeX compiler that must have been installed by user.
class PreviewWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        pass
        
#Insert worker thread class into another module to maintain readability of code, perhaps previewUI.py?
class preview_thread(QThread):

    thread_message = pyqtSignal(str)

    #Instantiate a thread object and then run thread by using .start() method instead of .run()
    def __init__(self, EditorWindow_class):
        QThread.__init__(self)
        self.exiting = False
        self.copiedFile_name = EditorWindow_class.currentFile

    def __del__(self):
        #Ensures that processing of thread is finished before thread object is destroyed.
        self.exiting = True
        self.wait()

    def write(self, message):
        thread_message.emit(message)

    def run(self):
        #Statements to be processed in thread placed in this method. Again, use .start() to run thread.         
        #Creates a new subprocess to compile current document
        proc = subprocess.Popen(['pdflatex', '%s' % self.copiedFile_name],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
        try:
            stdoutdata, stderrdata = proc.communicate(timeout=3)
            #try looking at return code.
            if proc.returncode == 1:
                self.thread_message.emit("An error has occured --- error message from log file: \n\n" + stdoutdata.decode('ascii'))
            elif proc.returncode == 0:
                self.thread_message.emit("File successfully compiled into .tex format and converted to PDF for viewing.")
            #print("\n\nNo errors occured during compilation.")
            #print("NO ERROR PRODUCED -- stdoutdata: \n\n" + stdoutdata.decode('ascii'))
            #print("\ERROR PRODUCED -- stderrdata: \n\n" + stderrdata.decode('ascii'))
            
        except subprocess.TimeoutExpired:
            proc.kill()
            stdoutdata, stderrdata = proc.communicate()
            print("\n\nErrors HAVE occured during compilation.")
            self.thread_message.emit(stdoutdata.decode('ascii'))



        #When the thread has finished running, a signal is sent to notify the main appwindow to raise a message box
        #to notify the user that the file has successfully been compiled and is ready to view...to

        #After the notification, an instance of PreviewWindow is created to render and view the PDF file.
