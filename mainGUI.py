import sys
import os

from PyQt4 import QtGui, QtCore 
from grammar import DSLflow
from borderlayout import BorderLayout
from highlighter import DslHighlighter

class MainGUI(QtGui.QWidget):
    
    def __init__(self):
        super(MainGUI, self).__init__()
        
        self.createActions()
        self.createMenuBar()        
        self.createStatusBar()
        self.createEditor()
        self.createViewer()
        self.createUI()
        
        self.workflow = DSLflow()
        self.deleteImage()
        
    def createUI(self):
                
        self.setWindowTitle('DSLflow')
        self.setGeometry(0, 0, 850, 550)
        self.center()        
        
        spliter = QtGui.QSplitter()
        spliter.addWidget(self.textEditor)
        spliter.addWidget(self.scrollAreaViewer)
        spliter.setSizes([150, 300])
        
        layout = BorderLayout()
        layout.addWidget(self.menubar, BorderLayout.North)
        layout.addWidget(spliter, BorderLayout.Center)
        layout.addWidget(self.statusbar, BorderLayout.South)
        
        self.setLayout(layout)
        
        self.show()
        
    def createViewer(self):
        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored,
                QtGui.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
                
        self.scrollAreaViewer = QtGui.QScrollArea(self)
        self.scrollAreaViewer.setBackgroundRole(QtGui.QPalette.Light)
        self.scrollAreaViewer.setAlignment(QtCore.Qt.AlignCenter)
        self.scrollAreaViewer.setWidget(self.imageLabel) 
        
    def createEditor(self):
        self.textEditor = QtGui.QTextEdit()
        self.textEditor.textChanged.connect(self.textChanged)
        
        _dslgl = DslHighlighter(self.textEditor)        
        
        font = QtGui.QFont('Courier', 10)
        self.textEditor.setFont(font) 
        
        metrics = QtGui.QFontMetrics(font)
        self.textEditor.setTabStopWidth(4 * metrics.width(' '))
        
    def createMenuBar(self):
        self.menubar = QtGui.QMenuBar()
                
        self.fileMenu = QtGui.QMenu('File')
        self.fileMenu.addAction('New')
        self.fileMenu.addAction('Open...')
        self.fileMenu.addSeparator()
        self.fileMenu.addAction('Save')
        self.fileMenu.addAction('Save as...')
        self.fileMenu.addSeparator()
        self.fileMenu.addAction('Exit')   
        
        self.searchtMenu = QtGui.QMenu('Search')
        self.searchtMenu.addAction('Find')
        self.searchtMenu.addAction('Replace')
        
        self.viewMenu = QtGui.QMenu('View')
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addAction(self.fitToWindowAct)
        
        self.helpMenu = QtGui.QMenu('Help')
        self.helpMenu.addAction('Help content')
        self.helpMenu.addAction('About')
        
        self.menubar.addMenu(self.fileMenu)
        self.menubar.addMenu(self.searchtMenu)
        self.menubar.addMenu(self.viewMenu)
        self.menubar.addMenu(self.helpMenu)
        
    def createActions(self):
        
        self.zoomInAct = QtGui.QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QtGui.QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QtGui.QAction("&Normal Size", self,
                shortcut="Ctrl+S", enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)
        
    def createStatusBar(self):
        self.statusbar = QtGui.QStatusBar()
        self.statusbar.showMessage('Ready')
    
    def center(self):        
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())        

    def closeEvent(self, event):        
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.deleteImage()
            event.accept()
        else:
            event.ignore() 
    
    def textChanged(self):
        
        wfProgram = "%s" % self.textEditor.toPlainText()     
        self.workflow.run(wfProgram)
        
        pic_path = os.getcwd() + "\\workflow.png"
        if os.path.isfile(pic_path):
            image = QtGui.QImage(pic_path)
            self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))
            self.scaleFactor = 1.0
            self.imageLabel.adjustSize()
            
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.imageLabel.adjustSize()
    
    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollAreaViewer.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollAreaViewer.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 4.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.2) 
        
    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())
    
    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollAreaViewer.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()
        
    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))
               
    def wheelEvent(self,event):
            if event.delta() > 0:
                self.zoomIn()
            else:
                self.zoomOut()        
            
    def handleButton(self):
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            self.wheelEvent()
            
    def deleteImage(self):
        pic_path = os.getcwd() + "\\workflow.png"
        if os.path.isfile(pic_path):
            os.remove(pic_path)
            
def main():    
    app = QtGui.QApplication(sys.argv)
    _mainGUI = MainGUI()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()   
