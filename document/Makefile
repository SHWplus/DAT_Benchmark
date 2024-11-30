SOURCEDIR = source
BUILDDIR = build

LANGS = zh en

SPHINXBUILD = sphinx-build
SPHINXOPTS =
O =

all: html

html:
	@for lang in $(LANGS); do \
		$(SPHINXBUILD) -b html $(SOURCEDIR)/$$lang $(BUILDDIR)/$$lang; \
done
