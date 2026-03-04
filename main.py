import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
import easyocr
from docx import Document
from pdf2docx import Converter
from docx2pdf import convert as docx2pdf_convert
import threading
import numpy as np
import cv2

# Initialize EasyOCR reader once (heavy model load)
reader = easyocr.Reader(['en'])


class FileConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF / DOCX Converter with OCR")
        self.root.geometry("520x320")
        self.root.resizable(False, False)

        title = tk.Label(root, text="File Converter", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        subtitle = tk.Label(
            root,
            text="PDF ⇄ DOCX  +  Scanned PDF → DOCX (OCR)",
            font=("Arial", 10)
        )
        subtitle.pack(pady=5)

        self.btn_pdf_to_docx = tk.Button(
            root, text="PDF → DOCX", width=30, command=self.pdf_to_docx
        )
        self.btn_pdf_to_docx.pack(pady=6)

        self.btn_docx_to_pdf = tk.Button(
            root, text="DOCX → PDF", width=30, command=self.docx_to_pdf
        )
        self.btn_docx_to_pdf.pack(pady=6)

        self.btn_scan_pdf = tk.Button(
            root,
            text="Scanned PDF → DOCX (OCR)",
            width=30,
            command=self.start_ocr_thread
        )
        self.btn_scan_pdf.pack(pady=6)

        self.status = tk.Label(root, text="Ready", fg="green")
        self.status.pack(pady=12)

    # ---------------- UI Helpers ---------------- #

    def set_status(self, text, color="black"):
        self.root.after(0, lambda: self.status.config(text=text, fg=color))

    def set_buttons_state(self, state):
        self.root.after(0, lambda: self.btn_pdf_to_docx.config(state=state))
        self.root.after(0, lambda: self.btn_docx_to_pdf.config(state=state))
        self.root.after(0, lambda: self.btn_scan_pdf.config(state=state))

    # ---------------- Normal Conversions ---------------- #

    def pdf_to_docx(self):
        pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not pdf_path:
            return

        docx_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx")]
        )
        if not docx_path:
            return

        try:
            self.set_status("Converting PDF → DOCX...", "blue")
            self.set_buttons_state("disabled")

            cv = Converter(pdf_path)
            cv.convert(docx_path)
            cv.close()

            self.set_status("PDF → DOCX completed", "green")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error", "red")
        finally:
            self.set_buttons_state("normal")

    def docx_to_pdf(self):
        docx_path = filedialog.askopenfilename(filetypes=[("Word Document", "*.docx")])
        if not docx_path:
            return

        pdf_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )
        if not pdf_path:
            return

        try:
            self.set_status("Converting DOCX → PDF...", "blue")
            self.set_buttons_state("disabled")

            docx2pdf_convert(docx_path, pdf_path)

            self.set_status("DOCX → PDF completed", "green")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.set_status("Error", "red")
        finally:
            self.set_buttons_state("normal")

    # ---------------- OCR Conversion ---------------- #

    def start_ocr_thread(self):
        thread = threading.Thread(target=self.scanned_pdf_to_docx)
        thread.daemon = True
        thread.start()

    def scanned_pdf_to_docx(self):
        pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not pdf_path:
            return

        docx_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx")]
        )
        if not docx_path:
            return

        try:
            self.set_buttons_state("disabled")
            self.set_status("Starting OCR...", "blue")

            pdf = fitz.open(pdf_path)
            document = Document()
            total_pages = len(pdf)

            for page_num in range(total_pages):
                self.set_status(
                    f"OCR page {page_num + 1} of {total_pages}...",
                    "blue"
                )

                page = pdf.load_page(page_num)

                # Lower DPI for better performance
                pix = page.get_pixmap(dpi=200)
                img_bytes = pix.tobytes("png")

                # Convert bytes to OpenCV image
                img_array = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                text_result = reader.readtext(img)
                text = " ".join([res[1] for res in text_result])

                document.add_paragraph(text)

            document.save(docx_path)
            pdf.close()

            self.set_status("Scanned PDF → DOCX completed", "green")

        except Exception as e:
            messagebox.showerror("OCR Error", str(e))
            self.set_status("OCR Error", "red")

        finally:
            self.set_buttons_state("normal")


# ---------------- Main ---------------- #

def main():
    root = tk.Tk()
    app = FileConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

