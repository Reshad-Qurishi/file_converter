import os
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

# Libraries required:
# pip install pdf2docx pdf2image pytesseract python-docx
# macOS: brew install tesseract poppler
# Windows: install Tesseract OCR + Poppler and add to PATH

from pdf2docx import Converter
from pdf2image import convert_from_path
import pytesseract
from docx import Document

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF ↔ DOCX Converter")
        self.root.geometry("520x300")
        self.root.resizable(False, False)

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Input File:").pack(pady=(20, 5))
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill="x", padx=20)
        tk.Entry(input_frame, textvariable=self.input_path).pack(side="left", fill="x", expand=True)
        tk.Button(input_frame, text="Browse", command=self.browse_input).pack(side="left", padx=5)

        tk.Label(self.root, text="Output File:").pack(pady=(10, 5))
        output_frame = tk.Frame(self.root)
        output_frame.pack(fill="x", padx=20)
        tk.Entry(output_frame, textvariable=self.output_path).pack(side="left", fill="x", expand=True)
        tk.Button(output_frame, text="Browse", command=self.browse_output).pack(side="left", padx=5)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="PDF → DOCX", width=16, command=self.pdf_to_docx).pack(side="left", padx=6)
        tk.Button(btn_frame, text="DOCX → PDF", width=16, command=self.docx_to_pdf).pack(side="left", padx=6)

        tk.Button(self.root, text="Scanned PDF → DOCX (OCR)", width=25, command=self.scanned_pdf_to_docx).pack(pady=10)

    def browse_input(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf"), ("Word files", "*.docx")]
        )
        if file_path:
            self.input_path.set(file_path)

    def browse_output(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word files", "*.docx"), ("PDF files", "*.pdf")]
        )
        if file_path:
            self.output_path.set(file_path)

    def pdf_to_docx(self):
        input_file = self.input_path.get()
        output_file = self.output_path.get()

        if not input_file.lower().endswith(".pdf"):
            messagebox.showerror("Error", "Input must be a PDF file.")
            return
        if not output_file.lower().endswith(".docx"):
            messagebox.showerror("Error", "Output must be a DOCX file.")
            return

        try:
            cv = Converter(input_file)
            cv.convert(output_file, start=0, end=None)
            cv.close()
            messagebox.showinfo("Success", "PDF converted to DOCX successfully.")
        except Exception as e:
            messagebox.showerror("Conversion Error", str(e))

    def docx_to_pdf(self):
        input_file = self.input_path.get()
        output_file = self.output_path.get()

        if not input_file.lower().endswith(".docx"):
            messagebox.showerror("Error", "Input must be a DOCX file.")
            return
        if not output_file.lower().endswith(".pdf"):
            messagebox.showerror("Error", "Output must be a PDF file.")
            return

        try:
            subprocess.run([
                "/Applications/LibreOffice.app/Contents/MacOS/soffice",
                "--headless",
                "--convert-to", "pdf",
                "--outdir", os.path.dirname(output_file),
                input_file
            ], check=True)

            generated_pdf = os.path.join(
                os.path.dirname(output_file),
                os.path.splitext(os.path.basename(input_file))[0] + ".pdf"
            )
            if os.path.exists(generated_pdf) and generated_pdf != output_file:
                os.replace(generated_pdf, output_file)

            messagebox.showinfo("Success", "DOCX converted to PDF successfully.")
        except Exception as e:
            messagebox.showerror("Conversion Error", str(e))

    def scanned_pdf_to_docx(self):
        input_file = self.input_path.get()
        output_file = self.output_path.get()

        if not input_file.lower().endswith(".pdf"):
            messagebox.showerror("Error", "Input must be a PDF file.")
            return
        if not output_file.lower().endswith(".docx"):
            messagebox.showerror("Error", "Output must be a DOCX file.")
            return

        try:
            images = convert_from_path(input_file, dpi=300)
            doc = Document()

            for img in images:
                text = pytesseract.image_to_string(img, lang="eng")
                doc.add_paragraph(text)

            doc.save(output_file)
            messagebox.showinfo("Success", "Scanned PDF converted to DOCX with OCR.")
        except Exception as e:
            messagebox.showerror("OCR Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()
