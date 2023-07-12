# pdfutils

## Is this your Use Case?
You don't want to use online tools (or adobe acrobate) to modify your PDF and you'd like to:
- merge (combine pdfs)
- extract (extract certain pages from a pdf)
- rotate (rotate pages)
- watermark (add a watermark to pages)
- encrypt (encrypt the pdf)
- redact (redact text in a pd)f

## Context for creation
[PyMuPDF](https://github.com/pymupdf/PyMuPDF) is a great library for manipulating PDFs.  This just calls many of the functions of PyMuPDF through the use of a config file

## How to use this:
1. Install python3, pip, and virtualenv (google this)
1. Update your config.json file to indicate what actions you want to take
   1. See [example](data/config.json) in the data directory
1. Run python pyutils.py <directory> (e.g., python pyutils.py data)
   1. the script will automatically look for a config.json in that directory

