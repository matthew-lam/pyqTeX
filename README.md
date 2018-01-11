# ${1: Simple LaTeX Editor}

#About
This application is a simple and lightweight text editor specifically for the LaTeX languages.
The main purpose of this program is to be used for writing scientific papers, writing technical documents or whatever you may use the LaTeX language for.

![Alt text](./assets/editor-screenshot-11_01_18.png?raw=true "Basic screenshot")

#Features
This project is a work-in-progress and as such, I will be looking to add a lot more features. The current features included as of 11/01/2018 are:

- Simple text editor functions (the usual hotkey functions, file management, etc.)

- Syntax highlighting based on LaTeX.

- Conversion of files from '.tex' file format to '.pdf' and '.png' format for viewing in the application and externally, using another PDF viewer.

- Ability to preview '.tex' files and display them as '.png' files in-app.

#Code
PyQt5 has been heavily utilised in the code as a means for developing the GUI and almost everything in the LaTeX editor.
PyMuPDF (fitz) was also used and functions the same as if I were to use poppler. i.e. for utilising PDF files.

Feel free to fork this project from my GitHub page if you'd like to mess around with my code.