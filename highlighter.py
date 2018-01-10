from editorUI import *
from PyQt5.QtGui import QSyntaxHighlighter, QColor, QTextCharFormat, QFont
from PyQt5.QtCore import *

class SyntaxHighlighter(QSyntaxHighlighter):
    #documentclass, {}, begin{document}/end{document}, subsection, begin/end, section, usepackage
    
    def __init__(self, parent=None):
        super(SyntaxHighlighter, self).__init__(parent)

        self.highlightRules = []

        docSettingFormat = QTextCharFormat()
        docSettingFormat.setForeground(Qt.darkGreen)
        docSettingDict = ["\\bdocumentclass\\b", "\\busepackage\\b"]

        self.highlightRules += [(QRegExp(item), docSettingFormat) for item in docSettingDict]

        enclosedWords_regex = QTextCharFormat()
        enclosedWords_regex.setForeground(Qt.blue)
        enclosedWords_dict = ["\{[A-Za-z0-9=\s]*\}", "\\\\"]
        self.highlightRules += [(QRegExp(item), enclosedWords_regex) for item in enclosedWords_dict]

        texNewLine = QTextCharFormat()
        texNewLine.setForeground(Qt.darkMagenta)
        texNewLineContent = ["\\\\", "\\\\\\b[A-Za-z]+\\b"]
        self.highlightRules += [(QRegExp(item), texNewLine) for item in texNewLineContent]

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkBlue)
        keywordFormat.setFontWeight(QFont.Bold)

        keywordPatterns = ["begin\{document\}", "end\{document\}", "\\\\begin", "\\\\end"]

        self.highlightRules += [(QRegExp(item), keywordFormat)
                for item in keywordPatterns]

    def highlightBlock(self, text):
        for pattern, format in self.highlightRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)