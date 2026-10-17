import os
import sys
import traceback
from datetime import datetime

# ========== 超级启动日志（在一切之前） ==========
def write_startup_error(error_text):
    """捕获启动阶段的错误，写入日志（无论任何异常）"""
    try:
        # 获取exe所在目录（如果是打包后）或脚本所在目录
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(base_dir, "startup_error.log")
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(error_text)
    except:
        pass  # 如果连写入日志都失败，那就没办法了

# 使用 try 包裹整个启动过程
try:
    # 正常的导入和启动
    import tkinter as tk
    from tkinter import filedialog, messagebox
    from tkinterdnd2 import DND_FILES, TkinterDnD

    # 导入 pypdf（注意文件名不要是 pdf.py）
    try:
        from pypdf import PdfMerger
    except ImportError:
        # 如果失败，尝试从 PyPDF2 导入（但推荐只用 pypdf）
        try:
            from PyPDF2 import PdfMerger
        except ImportError:
            raise ImportError("请安装 pypdf 库：pip install pypdf")

except Exception as e:
    # 任何导入或初始化错误都会被捕获并写入日志
    error_msg = traceback.format_exc()
    write_startup_error(error_msg)
    # 如果你还想弹窗提示（可能弹不出，因为tk还没初始化），但可以先尝试
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("启动失败", f"程序启动时发生错误，详情请查看 startup_error.log\n错误：{e}")
        root.destroy()
    except:
        pass
    sys.exit(1)

# ========== 如果导入成功，继续正常的类定义 ==========
class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 拼接器")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        self.file_list = []
        self.create_widgets()
        self.setup_drag_drop()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            frame,
            selectmode=tk.SINGLE,
            yscrollcommand=scrollbar.set,
            height=12
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="添加文件", command=self.add_files, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除选中", command=self.delete_selected, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="上移", command=self.move_up, width=6).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="下移", command=self.move_down, width=6).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="拼接", command=self.merge_pdfs, width=10, bg="lightblue").pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.root, text="将PDF文件拖入此处或点击添加", fg="gray")
        self.status_label.pack(pady=5)

    def setup_drag_drop(self):
        self.listbox.drop_target_register(DND_FILES)
        self.listbox.dnd_bind('<<Drop>>', self.on_drop)

    def on_drop(self, event):
        data = event.data
        paths = self.root.tk.splitlist(data)
        for path in paths:
            path = path.strip()
            if path.lower().endswith('.pdf'):
                self.add_file(path)
            else:
                messagebox.showwarning("警告", f"文件不是 PDF 格式：{path}")

    def add_files(self):
        files = filedialog.askopenfilenames(
            title="选择 PDF 文件",
            filetypes=[("PDF files", "*.pdf")]
        )
        for f in files:
            self.add_file(f)

    def add_file(self, path):
        if path not in self.file_list:
            self.file_list.append(path)
            self.listbox.insert(tk.END, os.path.basename(path))
            self.update_status()

    def delete_selected(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showinfo("提示", "请先选中一个文件")
            return
        idx = selected[0]
        self.listbox.delete(idx)
        del self.file_list[idx]
        self.update_status()

    def move_up(self):
        selected = self.listbox.curselection()
        if not selected or selected[0] == 0:
            return
        idx = selected[0]
        self.file_list[idx], self.file_list[idx-1] = self.file_list[idx-1], self.file_list[idx]
        self.refresh_listbox()

    def move_down(self):
        selected = self.listbox.curselection()
        if not selected or selected[0] == len(self.file_list) - 1:
            return
        idx = selected[0]
        self.file_list[idx], self.file_list[idx+1] = self.file_list[idx+1], self.file_list[idx]
        self.refresh_listbox()

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for f in self.file_list:
            self.listbox.insert(tk.END, os.path.basename(f))
        self.update_status()

    def update_status(self):
        count = len(self.file_list)
        self.status_label.config(text=f"已添加 {count} 个文件")

    def log_error(self, error_msg, exc_info=None):
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pdf_merger.log")
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(f"错误发生时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"错误信息：{error_msg}\n")
                if exc_info:
                    if isinstance(exc_info, Exception):
                        f.write("详细堆栈：\n")
                        f.write(traceback.format_exc())
                    else:
                        f.write(str(exc_info))
                f.write("\n")
        except Exception:
            pass

    def merge_pdfs(self):
        if len(self.file_list) < 2:
            messagebox.showinfo("提示", "至少需要两个 PDF 文件才能拼接")
            return

        output_file = filedialog.asksaveasfilename(
            title="保存拼接后的 PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not output_file:
            return

        merger = None
        try:
            merger = PdfMerger()
            for pdf_path in self.file_list:
                if not os.path.exists(pdf_path):
                    error_msg = f"文件不存在：{pdf_path}"
                    self.log_error(error_msg)
                    messagebox.showerror("错误", error_msg)
                    return
                merger.append(pdf_path)

            merger.write(output_file)
            merger.close()
            messagebox.showinfo("完成", f"拼接成功！\n文件保存为：{output_file}")

        except Exception as e:
            error_msg = f"拼接过程中发生错误：{str(e)}"
            self.log_error(error_msg, e)
            messagebox.showerror("错误", error_msg)

        finally:
            if merger:
                try:
                    merger.close()
                except:
                    pass


if __name__ == "__main__":
    # 这里已经被 try 包裹了，但为了防止意外的退出，再加一层
    try:
        root = TkinterDnD.Tk()
        app = PDFMergerApp(root)
        root.mainloop()
    except Exception as e:
        error_msg = traceback.format_exc()
        write_startup_error(error_msg)
        # 尝试显示错误（可能弹窗）
        try:
            root = tk.Tk()
            root.withdraw()
            tk.messagebox.showerror("运行时错误", f"程序运行中发生严重错误，请查看 startup_error.log")
            root.destroy()
        except:
            pass
        sys.exit(1)
        
