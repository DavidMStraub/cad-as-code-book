MYST := myst

.PHONY: all build watch clean

all: build

build:
	$(MYST) build --typst

watch:
	$(MYST) start

clean:
	rm -rf _build/
