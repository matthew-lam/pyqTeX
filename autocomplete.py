from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal

class autoCompleter(QCompleter):
    completerSignal = pyqtSignal(str)

    def __init__(self, keywords = None, parent = None): #Super call to fill out params declared in this class

        keywords = []
        kwDocSettings = ['\documentclass[options]{style}', '\setlength{options}{length}', 
        r'\usepackage{pkgName}', r'\newcommand']
        
        kwDocFormatting = [r'\newpage', '\pagebreak[number]', r'\nopagebreak[number]', 
        r'\newenvironment{name}[optional_num][optional_default]{before}{after}', '\pageref{key}',
        r'\ref{key}', '\label{key}', '\hspace{length}', '\hspace[*]{length}',
        '\rspace{length}', r'\vspace[*]{length}', '\par']

        kwBody = ['\section{text}', '\subsection{text}', '\subsubsection{text}',
        r"\title{text}", r"\author{name}", "\maketitle{title}", 'begin{document}', 
        'end{document}', r'\begin{args}', "\end{args}"]

        keywords.extend(kwDocSettings)
        keywords.extend(kwDocFormatting)
        keywords.extend(kwBody)
        super().__init__(keywords, parent)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.highlighted.connect(self.setHighlighted)

    def setHighlighted(self, text):
        self.lastSelected = text

    def getSelected(self):
        return self.lastSelected