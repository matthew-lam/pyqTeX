from PyQt5.QtWidgets import *

class WindowUtilityFunctions(QWidget):

    def __init__(self, argApp):
        super().__init__()
        self.screenObj = argApp.primaryScreen()

    def getScreenDims(self):
        screenSize = self.screenObj.size()
        screenDims = self.screenObj.availableGeometry()
        return screenDims

    def getScreenSizeX(self, screenDims):
        return screenDims.width()

    def getScreenSizeY(self, screenDims):
        return screenDims.height()

    def setCenter(self):    #Probably will need to be moved to a different class / may be removed
        windowProp = self.frameGeometry()
        centerPosition = QDesktopWidget().availableGeometry().center()
        windowProp.moveCenter(centerPosition)
        self.move(windowProp.topLeft())

    def setTopLeft(self):   #Probably will need to be moved to a different class
        #Ensures that window is always set to the top left no matter the screen res
        windowProp = self.frameGeometry()
        topLeftPosition = QDesktopWidget().availableGeometry().topLeft()
        windowProp.moveLeft(0)
        self.move(windowProp.topLeft())   

    def setTopRight(self):   #Probably will need to be moved to a different class
        #Ensures that window is always set to the top left no matter the screen res
        self.move(QApplication.desktop().screen().rect().topRight())

    def isMacOS():
            try:
            #Detects if OS is MacOS.
                if platform.system() == "Darwin":
                    print(platform.system() + " -- OS used is MacOS.")
                    return True
            except:
                return False
