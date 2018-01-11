from editorUI import *
from PyQt5.QtGui import QSyntaxHighlighter, QColor, QTextCharFormat, QFont
from PyQt5.QtCore import *

class SyntaxHighlighter(QSyntaxHighlighter):
    
    def __init__(self, parent=None):
        super(SyntaxHighlighter, self).__init__(parent)

        self.highlightRules = []
        #Rules that are appended first have weaker precedence/priority for highlighting
        #Color coding:
        #Green = Document settings
        #Blue = Parameters / strings enclosed in square/curly brackets
        #Purple = General TeX commands
        #Bolded dark blue = begin/end keywords
        #Dark Yellow = sections
        #Need to add : text formatting, comments, maths stuff(?)

        texNewLine = QTextCharFormat()
        texNewLine.setForeground(Qt.darkMagenta)
        texNewLineContent = ["\\\\", "\\\\\\b[A-Za-z0-9]+\\b"]
        self.highlightRules += [(QRegExp(item), texNewLine) for item in texNewLineContent]

        bracesEnclosed = QTextCharFormat()
        bracesEnclosed.setForeground(Qt.blue)
        bracesEnclosedDict = ["\{[A-Za-z0-9\s-_'~;:().\\\\,\{\}]*\}"]
        self.highlightRules += [(QRegExp(item), bracesEnclosed) for item in bracesEnclosedDict]

        squareBracketsEnclosed = QTextCharFormat()
        squareBracketsEnclosed.setForeground(Qt.darkBlue)
        squareBracketsDict = ["\[[A-Za-z0-9\s-_'~;:!\?().\\\\,\{\}]*\]"]
        self.highlightRules += [(QRegExp(item), squareBracketsEnclosed) for item in squareBracketsDict]

        texSections = QTextCharFormat()
        texSections.setForeground(Qt.darkYellow)
        texSectionDict = ["\\\\section", "\\\\subsection", "\\\\subsubsection"]
        self.highlightRules += [(QRegExp(item), texSections) for item in texSectionDict]

        docSettingFormat = QTextCharFormat()
        docSettingFormat.setForeground(Qt.darkGreen)
        docSettingDict = ["\\\\\\bdocumentclass\\b", "\\\\\\busepackage\\b"]
        self.highlightRules += [(QRegExp(item), docSettingFormat) for item in docSettingDict]

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkBlue)
        keywordFormat.setFontWeight(QFont.Bold)

        keywordPatterns = ["begin\{document\}", "end\{document\}", "\\\\begin", "\\\\end"]

        self.highlightRules += [(QRegExp(item), keywordFormat)
                for item in keywordPatterns]

#This block of code is based on the PyQt5 example for QSyntaxHighlighter. (baoboa github)
    def highlightBlock(self, text):
        for pattern, format in self.highlightRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)