import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import fitz
import easyocr
from docx import Document
from pdf2docx import Converter
from docx2pdf import convert as docx2pdf_convert
import threading
import numpy as np
import cv2

# OCR languages:
'''
English	en
Arabic	ar
Persian (Farsi)	fa
Swedish	sv
Spanish	es
French	fr
German	de
Italian	it
Portuguese	pt
Dutch	nl
Danish	da
Finnish	fi
Norwegian	no
Turkish	tr
Russian	ru
Chinese	zh
Japanese	ja
Korean	ko
Hindi	hi
Urdu	ur
'''
#Posibility of selecting the language for the pdf to convert

reader = easyocr.Reader(['ar','en','fa'])


class FileConverterApp:

    def __init__(self, root):

        self.root = root
        self.root.title("PDF / DOCX Converter with OCR")
        self.root.geometry("550x380")

        title = tk.Label(root, text="File Converter", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        subtitle = tk.Label(
            root,
            text="PDF ⇄ DOCX  +  Scanned PDF → DOCX (OCR)",
            font=("Arial", 10)
        )
        subtitle.pack()

        self.btn_pdf_to_docx = tk.Button(root, text="PDF → DOCX", width=30, command=self.pdf_to_docx)
        self.btn_pdf_to_docx.pack(pady=6)

        self.btn_docx_to_pdf = tk.Button(root, text="DOCX → PDF", width=30, command=self.docx_to_pdf)
        self.btn_docx_to_pdf.pack(pady=6)

        self.btn_scan_pdf = tk.Button(root, text="Scanned PDF → DOCX (OCR)", width=30, command=self.start_ocr_thread)
        self.btn_scan_pdf.pack(pady=6)

        # Drag & drop area
        self.drop_label = tk.Label(root, text="Drag & Drop PDF Here", bg="#eeeeee", width=40, height=4)
        self.drop_label.pack(pady=15)

        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.drop_file)

        # Progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        self.status = tk.Label(root, text="Ready", fg="green")
        self.status.pack()

    def set_status(self, text, color="black"):
        self.root.after(0, lambda: self.status.config(text=text, fg=color))

    def set_progress(self, value):
        self.root.after(0, lambda: self.progress.config(value=value))

    def pdf_to_docx(self):

        pdf_path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not pdf_path:
            return

        docx_path = filedialog.asksaveasfilename(defaultextension=".docx")

        try:

            self.set_status("Converting PDF → DOCX...", "blue")

            cv = Converter(pdf_path)
            cv.convert(docx_path)
            cv.close()

            self.set_status("Done!", "green")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def docx_to_pdf(self):

        docx_path = filedialog.askopenfilename(filetypes=[("DOCX", "*.docx")])
        if not docx_path:
            return

        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf")

        try:

            self.set_status("Converting DOCX → PDF...", "blue")

            docx2pdf_convert(docx_path, pdf_path)

            self.set_status("Done!", "green")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def drop_file(self, event):

        file_path = event.data.strip("{}")

        if file_path.lower().endswith(".pdf"):
            threading.Thread(target=self.scanned_pdf_to_docx, args=(file_path,), daemon=True).start()
        else:
            messagebox.showerror("Error", "Only PDF files allowed")

    def start_ocr_thread(self):

        pdf_path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])

        if pdf_path:
            threading.Thread(target=self.scanned_pdf_to_docx, args=(pdf_path,), daemon=True).start()

    def scanned_pdf_to_docx(self, pdf_path):

        docx_path = filedialog.asksaveasfilename(defaultextension=".docx")

        if not docx_path:
            return

        try:

            pdf = fitz.open(pdf_path)
            total_pages = len(pdf)

            document = Document()

            self.set_progress(0)

            for i, page in enumerate(pdf):

                percent = int((i + 1) / total_pages * 100)
                self.set_progress(percent)

                self.set_status(f"OCR page {i+1}/{total_pages}", "blue")

                pix = page.get_pixmap(dpi=300)

                img_bytes = pix.tobytes("png")

                img_array = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                results = reader.readtext(gray)

                text = " ".join([r[1] for r in results])

                document.add_paragraph(text)

            document.save(docx_path)

            pdf.close()

            self.set_status("OCR completed!", "green")
            self.set_progress(100)

        except Exception as e:

            messagebox.showerror("OCR Error", str(e))
            self.set_status("Error", "red")


def main():

    root = TkinterDnD.Tk()

    app = FileConverterApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()
