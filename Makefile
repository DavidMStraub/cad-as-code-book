MYST := myst
PDFA_STANDARD := a-2b

.PHONY: all build watch clean figures pdfa

all: build

figures:
	python3 figures/generate_all.py

build:
	$(MYST) build --typst

# myst build --typst compiles the PDF itself, with no option to pass
# --pdf-standard through to typst. It does leave its intermediate .typ
# export behind in _build/temp/<random>/main.typ (not cleaned up), so this
# target reruns the build, finds that run's own temp dir, and compiles the
# same source a second time, directly with typst, asking for PDF/A.
pdfa: build
	typst compile --pdf-standard $(PDFA_STANDARD) \
		"$$(ls -td _build/temp/myst*/ | head -1)main.typ" main-pdfa.pdf

watch:
	$(MYST) start

clean:
	rm -rf _build/
