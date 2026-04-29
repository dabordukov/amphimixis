# Minimal makefile for Sphinx documentation with uv.

SPHINXBUILD ?= uv run sphinx-build
SOURCEDIR = .
BUILDDIR = build

.PHONY: html clean

html:
	$(SPHINXBUILD) -M html $(SOURCEDIR) $(BUILDDIR)

clean:
	rm -rf $(BUILDDIR)
