import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import fitz
import pandas as pd
import re

# Dummy user credentials (for demonstration)
USER_CREDENTIALS = {'admin': 'bobo'}

def authenticate():
    username = login_user.get()
    password = login_pass.get()

    if USER_CREDENTIALS.get(username) == password:
        login_win.destroy()
        main_app()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def forgot_password():
    messagebox.showinfo("Forgot Password", "Please contact admin to reset your password.")

def main_app():
    def process_pdf(pdf_path, prefix, exclude_column):
        doc = fitz.open(pdf_path)
        extracted_rows = []

        for page in doc:
            text = page.get_text()
            mobile_match = re.search(r"Mobile[#:\s]+(03\d{9})", text)
            name_line_match = re.search(r"Name[:\s]+(.+)", text, re.IGNORECASE)
            name = None
            if name_line_match:
                name_line = name_line_match.group(1).strip()
                name_parts = re.split(r"\s{2,}", name_line)
                name = name_parts[0].strip()
            if name and mobile_match:
                mobile = mobile_match.group(1).strip()
                extracted_rows.append({'Name': name, 'Mobile': mobile})

        if not extracted_rows:
            return None

        df = pd.DataFrame(extracted_rows)
        for col in df.columns:
            if col != exclude_column:
                df[col] = prefix + df[col].astype(str)
        return df

    def browse_file():
        file_path.set(filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")]))
        entry_file_path.xview_moveto(1)

    def generate_csv():
        pdf = file_path.get()
        pref = prefix.get()
        exc = exclude.get()
        filename = custom_name.get() or pref

        if not pdf:
            messagebox.showerror("Error", "Please select a PDF file.")
            return

        df = process_pdf(pdf, pref, exc)
        if df is None:
            messagebox.showwarning("Warning", "No valid name and mobile pairs found.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"{filename}.csv",
                                                 filetypes=[("CSV Files", "*.csv")])
        if save_path:
            df.to_csv(save_path, index=False)
            messagebox.showinfo("Success", f"CSV saved as:\n{save_path}")

    root = tk.Tk()
    root.title("📄 PDF Data Extractor for Production")
    root.geometry("900x600")

    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TButton", font=("Segoe UI", 12), padding=10)
    style.configure("TLabel", font=("Segoe UI", 12))
    style.configure("TEntry", font=("Segoe UI", 12))
    style.configure("TCombobox", font=("Segoe UI", 12))

    main_frame = ttk.Frame(root, padding=30)
    main_frame.pack(fill="both", expand=True)

    file_path = tk.StringVar()
    prefix = tk.StringVar(value="EX-")
    exclude = tk.StringVar(value="Mobile")
    custom_name = tk.StringVar()

    ttk.Label(main_frame, text="PDF to CSV Converter", font=("Segoe UI", 18, "bold")).grid(column=0, row=0, columnspan=3, pady=20)

    ttk.Label(main_frame, text="📁 Select PDF File:").grid(column=0, row=1, sticky="w", padx=10)
    entry_file_path = ttk.Entry(main_frame, textvariable=file_path, width=60)
    entry_file_path.grid(column=1, row=1, sticky="w")
    ttk.Button(main_frame, text="Browse", command=browse_file).grid(column=2, row=1, padx=10)

    ttk.Label(main_frame, text="🔢 Prefix to Add:").grid(column=0, row=2, sticky="w", padx=10, pady=(30, 0))
    ttk.Entry(main_frame, textvariable=prefix, width=40).grid(column=1, row=2, sticky="w", pady=(30, 0))

    ttk.Label(main_frame, text="🚫 Column to Exclude from Prefix:").grid(column=0, row=3, sticky="w", padx=10, pady=10)
    exclude_box = ttk.Combobox(main_frame, textvariable=exclude, values=["Name", "Mobile"], width=38, state="readonly")
    exclude_box.grid(column=1, row=3, sticky="w")

    ttk.Label(main_frame, text="📝 Custom Filename (Optional):").grid(column=0, row=4, sticky="w", padx=10, pady=(30, 0))
    ttk.Entry(main_frame, textvariable=custom_name, width=40).grid(column=1, row=4, sticky="w", pady=(30, 0))

    ttk.Button(main_frame, text="🚀 Generate CSV File", command=generate_csv).grid(column=1, row=5, pady=50, sticky="ew", columnspan=2)

    root.mainloop()

# Login Window
login_win = tk.Tk()
login_win.title("Login")
login_win.geometry("400x250")

login_user = tk.StringVar()
login_pass = tk.StringVar()

ttk.Label(login_win, text="Login to Access PDF Converter", font=("Segoe UI", 14, "bold")).pack(pady=20)
ttk.Entry(login_win, textvariable=login_user, width=30).pack(pady=5)
ttk.Entry(login_win, textvariable=login_pass, width=30, show="*").pack(pady=5)

ttk.Button(login_win, text="Login", command=authenticate).pack(pady=15)
ttk.Button(login_win, text="Forgot Password?", command=forgot_password).pack()

login_win.mainloop()
