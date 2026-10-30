PDF=main.pdf

.PHONY: pdf clean

pdf:
	pdflatex -interaction=nonstopmode -halt-on-error main.tex
	pdflatex -interaction=nonstopmode -halt-on-error main.tex

clean:
	rm -f main.aux main.log main.nav main.out main.snm main.toc $(PDF)
