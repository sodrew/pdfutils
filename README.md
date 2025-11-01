# pdfutils

## 📘 Overview

This script provides a **config-driven PDF utility** built on [PyMuPDF](https://github.com/pymupdf/PyMuPDF).
It lets you manipulate PDFs **without Adobe Acrobat or online tools** by defining your operations in a simple `config.json` file.

Supported actions include:
- ✅ Merge multiple PDFs into one
- ✂️ Extract specific pages
- 🔄 Rotate pages
- 🩸 Redact text (hide sensitive info)
- 💧 Add image or PDF watermarks
- 🔒 Encrypt the final PDF with a password
- 🖼️ Convert image files (e.g. `.jpg`, `.png`) into PDFs automatically

---

## ⚙️ Installation

1. Install Python 3 and pip.
2. Install PyMuPDF:
   ```bash
   pip install PyMuPDF
   ```
3. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

---

## 🧩 Configuration (config.json)

All operations are controlled through a `config.json` file placed in the same directory as your input PDFs.

Example configuration:
```json
{
  "output": "merged_output.pdf",
  "encrypt": "MySecretPassword123",
  "redact": ["CONFIDENTIAL", "SSN", "SECRET"],
  "pdfs": [
    {
      "file": "document1.pdf",
      "extract": [1],
      "rotate": 0,
      "redact": ["PRIVATE", "INTERNAL USE ONLY"],
      "watermark": ["watermark.pdf", [1], 0.5, [50, 50]]
    },
    {
      "file": "report.pdf",
      "extract": [1],
      "rotate": 90,
      "redact": ["DRAFT"],
      "watermark": ["logo.png", [1], 0.3, [100, 100]]
    },
    {
      "file": "scan.jpg",
      "rotate": 0,
      "watermark": ["watermark.pdf", [1], 0.7, [0, 0]]
    }
  ]
}
```

---

## 🚀 Usage

Run the script by specifying a directory or config file path:

```bash
python pdfutils.py data/
```

---

## 🧾 Example Workflow

1. Place your PDFs and images in a folder named `data/`.
2. Add a valid `config.json`.
3. Run:
   ```bash
   python pdfutils.py data
   ```
4. The result will appear as `merged_output.pdf` in the same folder.

---

## 📄 Minimal Example

```json
{
  "output": "combined.pdf",
  "pdfs": [
    { "file": "file1.pdf" },
    { "file": "file2.pdf" }
  ]
}
```

Run:
```bash
python pdfutils.py ./data
```

---

## 🧰 Dependencies

- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/)
- Python ≥ 3.8

---

## 🪶 License

MIT License
