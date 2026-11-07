# Internal draft: main.pdf.  Shareable version: main-share.pdf (no internal pointers, reader-facing tags).
.PHONY: all draft share clean
all: draft share
draft:
	latexmk -pdf -interaction=nonstopmode main.tex
share:
	latexmk -pdf -interaction=nonstopmode -jobname=main-share -usepretex='\def\SHAREBUILD{}' main.tex
clean:
	latexmk -C main.tex; latexmk -C -jobname=main-share main.tex
