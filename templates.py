# -*- coding: utf-8 -*-

template_sampleArticle = r"""%Sample article document.
%Press CTRL to use auto-complete or type in any characters leading to a command to pop-up.
\documentclass{article}
\usepackage{graphicx}

\begin{document}

\title{Introduction to \LaTeX{}}
\author{Author's Name}
\maketitle

\begin{abstract}
The abstract text goes here.\\
\end{abstract}

\section{Introduction}
Here is the text of your introduction.

\begin{equation}
	\label{simple_equation}
	\alpha = \sqrt{ \beta }
\end{equation}

\subsection{Example subsection}
Write your subsection text here. \\ The quick brown fox jumped over the lazy dog.
\\ Another line break! \\ $\alpha\beta$
\newpage

\section{Conclusion}
Page break!
Write your conclusion here.
\end{document}"""

template_sampleReport = r"""\documentclass{report}
\begin{document}
 
\title{First document}
\author{Person's name}

\begin{titlepage}
\maketitle
\end{titlepage}

\begin{abstract}
This is a simple paragraph at the beginning of the document. A brief introduction to the main subject.
\end{abstract}
 
In this document some extra packages and parameters
were added. There is an encoding package
pagesize and fontsize parameters.
 
This line will start a second paragraph. And I can
 brake\\ the lines \\ and continue in a new line.
 
\end{document}"""

template_report = r"""\documentclass{report}

\begin{document}

\section{Introduction}
This is a report

\end{document}
"""

template_article = r"""\documentclass{article}

\begin{document}

\section{Introduction}
This is an article

\end{document}"""