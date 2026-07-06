MYST := myst

.PHONY: all build watch clean figures

all: build

figures:
	python3 figures/generate_all.py

build:
	$(MYST) build --typst

watch:
	$(MYST) start

clean:
	rm -rf _build/
