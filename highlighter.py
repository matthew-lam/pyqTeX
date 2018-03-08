from editorUI import *
from PyQt5.QtGui import QSyntaxHighlighter, QColor, QTextCharFormat, QFont
from PyQt5.QtCore import *
import re

class SyntaxHighlighter(QSyntaxHighlighter):
    
    def __init__(self, parent=None):
        super(SyntaxHighlighter, self).__init__(parent)

        #Rules that are appended first have weaker precedence/priority for highlighting
        #Color coding:
        #Green = Document settings
        #Blue = Parameters / strings enclosed in square/curly brackets
        #Purple = General TeX commands
        #Bolded dark blue = begin/end keywords
        #Dark Yellow = sections
        #Dark red = text formatting
        #Gray = comments
        #Need to add : maths stuff(?)
        #To add math stuff within brackets, make sure '$' is allowed in enclosed braces rule and math rule is appended last

        self.highlightRules = []

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

        textFormatting = QTextCharFormat()
        textFormatting.setForeground(Qt.darkRed)
        textFormattingDict = ["\\\\par", "\\\\vspace", "\\\\hspace", "\\\\label", "\\\\ref", "\\\\pageref"]
        self.highlightRules += [(QRegExp(item), textFormatting) for item in textFormattingDict]

        texSections = QTextCharFormat()
        texSections.setForeground(Qt.darkYellow)
        texSectionDict = ["\\\\section", "\\\\subsection", "\\\\subsubsection", "\\\\title", "\\\\author", "\\\\maketitle", "\\\\bibliography", "\\\\references", "\\\\tableofcontents", "\\\\toc"]
        self.highlightRules += [(QRegExp(item), texSections) for item in texSectionDict]

        docSettingFormat = QTextCharFormat()
        docSettingFormat.setForeground(Qt.darkGreen)
        docSettingDict = ["\\\\\\bdocumentclass\\b", "\\\\\\busepackage\\b", "\\\\setlength", "\\\\newcommand"]
        self.highlightRules += [(QRegExp(item), docSettingFormat) for item in docSettingDict]

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(Qt.darkBlue)
        keywordFormat.setFontWeight(QFont.Bold)
        keywordPatterns = ["begin\{document\}", "end\{document\}", "\\\\begin", "\\\\end"]
        self.highlightRules += [(QRegExp(item), keywordFormat) for item in keywordPatterns]

        self.commentFormat = QTextCharFormat()
        self.commentFormat.setForeground(Qt.darkGray)

        self.commentStartChar = QRegExp("\\%")
        self.commentEndChar = QRegExp("$")

        mathRules = QTextCharFormat()
        mathRules.setForeground(Qt.darkCyan)
        mathRulesDict = ["\$.*\$", "\\\\begin\{displaymath\}", "\\\\end\{displaymath\}", "\\\\begin\{equation\}", "\\\\end\{equation\}"]
        self.highlightRules += [(QRegExp(item), mathRules) for item in mathRulesDict]

#This block of code is based on the PyQt5 example for QSyntaxHighlighter. (baoboa github)
    def highlightBlock(self, text):
        #Highlight a block of text using the formatting settings defined by the programmer and the syntax rules set above.
        for item, format in self.highlightRules:
            expression = QRegExp(item)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
        self.setCurrentBlockState(0)

        #Handling multi-lined comments
        startIndex = 0
        if self.previousBlockState() != 1:  
            #Checking to see if currently in a block of commented text
            startIndex = self.commentStartChar.indexIn(text)

        while startIndex >= 0:  
            #Deducing how long the commented piece of text is
            endIndex = self.commentEndChar.indexIn(text, startIndex)

            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndChar.matchedLength()

            #Formatting comment block based on rules & formatting settings defined by programmer.
            self.setFormat(startIndex, commentLength, self.commentFormat)
            startIndex = self.commentStartChar.indexIn(text,
                    startIndex + commentLength);