from PyQt4.QtGui import QSyntaxHighlighter, QTextCharFormat, QBrush, QFont
from PyQt4.Qt import Qt
from PyQt4.QtCore import QStringList, QRegExp


class DslHighlighter(QSyntaxHighlighter):
    
    def __init__(self, parent):
        QSyntaxHighlighter.__init__(self, parent)
        self.parent = parent
                
        self.highlightingRules = []
        
        self.brush = QBrush(Qt.red, Qt.SolidPattern)              
        self.keywords = QStringList([ 'task' , 'workflow'])        
        self.themeWords()
        
        self.brush = QBrush(Qt.blue, Qt.SolidPattern)              
        self.keywords = QStringList([ 'next', 'deadline', 'exitCondition', 'type', 'description', 'role' ])
        self.themeWords()
        
        self.brush = QBrush(Qt.black, Qt.SolidPattern)              
        self.keywords = QStringList([ 'automatic', 'manual'])
        self.themeWords(True)

        self.brush = QBrush(Qt.black, Qt.SolidPattern)              
        self.keywords = QStringList(['quote'])
        self.themeWords(True)

    def themeWords(self, italic = False):
             
        keyword = QTextCharFormat()     
        keyword.setForeground(self.brush)
        
        if(italic):            
            keyword.setFontItalic(italic)
        else:
            keyword.setFontWeight(QFont.Bold)
        
        for word in self.keywords:
            if (word == "quote"):
                pattern = QRegExp("\"[\w\s]+\"")
            else:
                pattern = QRegExp("\\b" + word + "\\b")
                
            rule = HighlightingRule(pattern, keyword)
            self.highlightingRules.append(rule)
            
    def highlightBlock(self, text):
        for rule in self.highlightingRules:
            expression = QRegExp(rule.pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, rule.format)
                index = text.indexOf(expression, index + length)
        self.setCurrentBlockState(0)

class HighlightingRule():
    def __init__(self, pattern, frmt):
        self.pattern = pattern
        self.format = frmt
    
