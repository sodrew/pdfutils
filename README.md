# pdfutils

## Is this your Use Case?
You don't want to use online tools (or adobe acrobate) to modify your PDF and you'd like to:
-encrypt
-merge
-rotate
-extract
-watermark
-redact

## Context for creation
PyMuPDF is a great library for manipulating PDFs.  This just calls many of the functions of PyMuPDF through the use of a config file

## How to use this:
1. Install python3, pip, and virtualenv (google this)
1. Update your config.json file to indicate what actions you want to take
   1. See example in the data directory
1. Run python pyutils.py <directory>

