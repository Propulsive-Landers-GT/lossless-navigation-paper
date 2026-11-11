# Internal draft: main.pdf.  Shareable version: main-share.pdf (no internal pointers, reader-facing tags).
.PHONY: all draft share student clean
all: draft share
draft:
	latexmk -pdf -interaction=nonstopmode main.tex
share:
	latexmk -pdf -interaction=nonstopmode -jobname=main-share -usepretex='\def\SHAREBUILD{}' main.tex
# AIAA student-conference version (11-page limit): aiaa-student/main.pdf
student:
	cd aiaa-student && latexmk -pdf -interaction=nonstopmode main.tex
clean:
	latexmk -C main.tex; latexmk -C -jobname=main-share main.tex
