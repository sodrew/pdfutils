# pdfutils

## 📘 Overview

I don't know about you but I hesitate sending sensitive pdfs online and definitely don't want to use free online tools to modify them.
This provides a **config-driven PDF utility** built on [PyMuPDF](https://github.com/pymupdf/PyMuPDF).
It lets you manipulate PDFs **without Adobe Acrobat or online tools** by defining your operations in a simple `config.json` file.

Supported actions include:
- ✅ Merge multiple PDFs into one
- ✂️ Extract specific pages
- 🔄 Rotate pages
- 🩸 Redact text (hide sensitive info)
- 💧 Add image or PDF watermarks (and resize)
- 🔒 Encrypt the final PDF with a password
- 🖼️ Convert image files (e.g. `.jpg`, `.png`) into PDFs automatically

---

## ⚙️ Installation

1. Install Python 3 and pip.
2. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install PyMuPDF:
   ```bash
   pip install PyMuPDF
   ```
   or Install from requirements.txt
   ```bash
   pip install -r requirements.txt
   ```

---

## 🧩 Configuration (config.json)

All operations are controlled through a `config.json` file placed in the same directory as your input PDFs.

Example configuration:
```json
{
  "output": "merged_output.pdf",
  "encrypt": "P4ssw0rd&",
  "pdfs": [
    {
      "file": "document.pdf",
      "rotate": 90
    },  {
      "file": "document.pdf",
      "extract": [1]
    },  {
      "file": "document.pdf",
      "watermark": ["watermark.pdf", [2]]
    },  {
      "file": "document.pdf",
      "watermark": ["watermark.pdf", [2], 0.25, [100, 200]]
    },  {
      "file": "document.pdf",
      "redact": ["PHI", "SSN", "Confidential"]
    }
  ]
}
```

---

## 🚀 Usage

Run the script by specifying a directory or config file path:

```bash
python pdfutils.py data/config.json

```
or

```bash
python pdfutils.py data
```

---

## 🧰 Dependencies

- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/) ≥ 1.22
- Python ≥ 3.8

---

## 🪶 License

GNU GPL v3
