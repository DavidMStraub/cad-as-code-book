TYPST   := typst
MAIN    := main.typ
OUT     := main.pdf
SOURCES := $(MAIN) template.typ $(wildcard chapters/*.typ)

.PHONY: all watch clean

all: $(OUT)

$(OUT): $(SOURCES)
	$(TYPST) compile $(MAIN) $(OUT)

watch:
	$(TYPST) watch $(MAIN) $(OUT)

clean:
	rm -f $(OUT)
