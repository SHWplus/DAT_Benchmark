@echo off
setlocal

rem Set variables
set SOURCEDIR=source
set BUILDDIR=build

set LANGS=zh en

rem Path to Sphinx build tool
set SPHINXBUILD=sphinx-build
set SPHINXOPTS=

rem Build HTML for each language
for %%L in (%LANGS%) do (
    %SPHINXBUILD% -b html %SOURCEDIR%\%%L %BUILDDIR%\%%L %SPHINXOPTS%
)

endlocal