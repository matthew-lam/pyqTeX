from editorUI import window_utility_functions

#previewWindow class contains code associated with previewTex (txt -> LaTeX) button
#Needs usage of poppler-qt package to render PDFs
#To create PDFs we can simply call from Python commands to TeX compiler that must have been installed by user.
class previewWindow(QMainWindow):

		def __init__(self):
			super().__init__()
			pass

		