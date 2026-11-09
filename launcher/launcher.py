import json, os, sys, subprocess, shutil, webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_TITLE = "Central Launcher"
BG = "#090F1D"
PANEL = "#111C2D"
CARD = "#17243A"
FG = "#F2F6FE"
MUTED = "#A1B1CB"
ACCENT = "#91B7FF"

def resource(name):
    base = getattr(sys, "_MEIPASS", str(Path(__file__).resolve().parent))
    return Path(base) / name

def config_path():
    home = Path(os.environ.get("APPDATA", str(Path.home()))) / "CentralLauncher"
    home.mkdir(parents=True, exist_ok=True)
    return home / "projects.json"

def load_projects():
    path = config_path()
    if not path.exists():
        shutil.copyfile(resource("projects.json"), path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_projects(data):
    with open(config_path(), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1160x740")
        self.minsize(820, 570)
        self.configure(bg=BG)
        self.data = load_projects()
        self.query = tk.StringVar()
        self.category = tk.StringVar(value="Todos")
        self.status = tk.StringVar(value="Os atalhos locais podem ser configurados para cada computador.")
        self.make_ui()
        self.query.trace_add("write", lambda *_: self.draw_cards())
        self.draw_filters()
        self.draw_cards()

    def make_ui(self):
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=30, pady=(27, 13))
        tk.Label(head, text="A MINHA CENTRAL  /  DESKTOP", font=("Segoe UI", 10, "bold"), fg=ACCENT, bg=BG).pack(anchor="w")
        tk.Label(head, text="Central Launcher", font=("Segoe UI", 31, "bold"), fg=FG, bg=BG).pack(anchor="w")
        tk.Label(head, text="Todos os teus mundos, jogos e projetos num só lugar.", font=("Segoe UI", 11), fg=MUTED, bg=BG).pack(anchor="w", pady=(2, 12))

        controls = tk.Frame(self, bg=BG)
        controls.pack(fill="x", padx=30, pady=(5, 12))
        search = tk.Entry(controls, textvariable=self.query, bg=PANEL, fg=FG, insertbackground=FG,
                          relief="flat", font=("Segoe UI", 12), highlightthickness=1,
                          highlightbackground="#354A67", highlightcolor=ACCENT)
        search.pack(side="left", fill="x", expand=True, ipady=9, ipadx=9)
        tk.Button(controls, text="+ Projeto", command=self.add_project, fg=FG, bg="#294D7D", activebackground="#4169A2",
                  activeforeground=FG, relief="flat", font=("Segoe UI", 10, "bold"), padx=17, pady=11).pack(side="left", padx=(12, 0))
        tk.Button(controls, text="Pasta de configuração", command=lambda: os.startfile(str(config_path().parent)),
                  fg=FG, bg=PANEL, relief="flat", font=("Segoe UI", 10), padx=14, pady=11).pack(side="left", padx=(10, 0))
        self.filter_bar = tk.Frame(self, bg=BG)
        self.filter_bar.pack(fill="x", padx=30, pady=(0, 12))

        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=28)
        canvas = tk.Canvas(outer, bg=BG, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(canvas, bg=BG)
        self.window = canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: (canvas.itemconfig(self.window, width=e.width), self.draw_cards()))
        self.canvas = canvas
        def wheel(e):
            canvas.yview_scroll(-int(e.delta/120), "units")
        canvas.bind_all("<MouseWheel>", wheel)

        foot = tk.Frame(self, bg=PANEL)
        foot.pack(fill="x", side="bottom")
        tk.Label(foot, textvariable=self.status, bg=PANEL, fg=MUTED, font=("Segoe UI", 9), anchor="w").pack(fill="x", padx=30, pady=11)

    def draw_filters(self):
        for w in self.filter_bar.winfo_children(): w.destroy()
        categories = ["Todos"] + sorted({p.get("category", "Outros") for p in self.data["projects"]})
        for name in categories:
            tk.Button(self.filter_bar, text=name, command=lambda x=name: self.choose_category(x),
                      bg="#2D4771" if name==self.category.get() else PANEL, fg=FG,
                      activebackground="#46658F", activeforeground=FG, relief="flat", padx=11, pady=7,
                      font=("Segoe UI", 9)).pack(side="left", padx=(0, 7))

    def choose_category(self, category):
        self.category.set(category)
        self.draw_filters()
        self.draw_cards()

    def entries(self):
        q = self.query.get().casefold().strip()
        category = self.category.get()
        return [p for p in self.data["projects"] if (category=="Todos" or p.get("category")==category)
                and (not q or q in (p.get("name", "")+" "+p.get("description", "")+" "+p.get("category", "")).casefold())]

    def draw_cards(self):
        for w in self.inner.winfo_children(): w.destroy()
        width = max(self.canvas.winfo_width(), 850)
        cols = 3 if width >= 920 else 2
        entries = self.entries()
        if not entries:
            tk.Label(self.inner, text="Nenhum projeto encontrado.", bg=BG, fg=MUTED, font=("Segoe UI", 12)).pack(pady=50)
            return
        for idx, p in enumerate(entries):
            r, c = divmod(idx, cols)
            frame = tk.Frame(self.inner, bg=CARD, highlightthickness=1, highlightbackground="#2E405D")
            frame.grid(row=r, column=c, sticky="nsew", padx=7, pady=7, ipady=9)
            self.inner.grid_columnconfigure(c, weight=1, uniform="tiles")
            top = tk.Frame(frame, bg=CARD)
            top.pack(fill="x", padx=18, pady=(10, 12))
            tk.Label(top, text=p.get("icon", "●"), bg=CARD, fg=p.get("accent", ACCENT), font=("Segoe UI Symbol", 21)).pack(side="left")
            tk.Label(top, text=p.get("category","Projeto").upper(), bg=CARD, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(side="right")
            tk.Label(frame, text=p["name"], bg=CARD, fg=FG, font=("Segoe UI", 12, "bold"),
                     anchor="w", justify="left", wraplength=max(220, width//cols-90)).pack(fill="x", padx=18)
            tk.Label(frame, text=p.get("description",""), bg=CARD, fg=MUTED, font=("Segoe UI", 9),
                     anchor="w", justify="left", wraplength=max(220, width//cols-90)).pack(fill="x", padx=18, pady=(5, 13))
            buttons = tk.Frame(frame, bg=CARD)
            buttons.pack(fill="x", padx=18, pady=(0, 8))
            tk.Button(buttons, text="ABRIR", command=lambda x=p: self.open_project(x), bg="#315D92",
                      activebackground="#4775B0", activeforeground="white", fg="white", relief="flat",
                      font=("Segoe UI", 9, "bold"), padx=12, pady=7).pack(side="left")
            if p.get("kind") != "url":
                tk.Button(buttons, text="Configurar", command=lambda x=p: self.edit_project(x), bg=CARD,
                          fg=ACCENT, activeforeground="white", relief="flat", font=("Segoe UI", 9)).pack(side="left", padx=(8,0))
            elif p.get("folder"):
                tk.Button(buttons, text="Pasta", command=lambda x=p:self.open_folder(x), bg=CARD,
                          fg=ACCENT, relief="flat", font=("Segoe UI", 9)).pack(side="left", padx=(8,0))
            tk.Button(buttons, text="⋯", command=lambda x=p:self.edit_project(x), bg=CARD, fg=MUTED,
                      relief="flat", font=("Segoe UI", 12), padx=6).pack(side="right")

    def resolve(self, p):
        return Path(os.path.expandvars(p)).expanduser()

    def open_folder(self, item):
        target = item.get("folder") or item.get("target")
        folder = self.resolve(target)
        if folder.is_file(): folder = folder.parent
        if not folder.exists():
            self.status.set("Pasta não encontrada neste computador: "+str(folder))
            messagebox.showwarning("Pasta não encontrada", "Configura o caminho correto para este computador.\n\n"+str(folder))
            return
        os.startfile(str(folder))

    def open_project(self, item):
        value = item.get("target", "")
        if item.get("kind") == "url":
            webbrowser.open(value)
            self.status.set("Abri no navegador: "+item["name"])
            return
        path = self.resolve(value)
        if not path.exists():
            self.status.set("Projeto local por configurar: "+item["name"])
            if messagebox.askyesno("Localização não encontrada", "O projeto não foi encontrado neste computador.\n\nQueres configurar a localização?"):
                self.edit_project(item)
            return
        try:
            if item.get("kind") == "godot":
                exe = self.find_godot()
                if exe:
                    subprocess.Popen([str(exe), "--path", str(path.parent), "-e"], cwd=str(path.parent))
                else:
                    os.startfile(str(path.parent))
                    messagebox.showinfo("Godot", "Não encontrei o executável Godot automaticamente; abri a pasta do projeto.")
            else:
                os.startfile(str(path))
            self.status.set("A abrir: "+item["name"])
        except Exception as e:
            self.status.set("Não foi possível abrir "+item["name"])
            messagebox.showerror("Erro", str(e))

    def find_godot(self):
        which = shutil.which("godot") or shutil.which("godot.exe")
        if which: return which
        winget = Path(os.environ.get("LOCALAPPDATA",""))/"Microsoft"/"WinGet"/"Packages"
        if winget.is_dir():
            matches = list(winget.glob("GodotEngine.GodotEngine*/*.exe"))
            matches = [x for x in matches if "console" not in x.name.lower() and x.name.lower().startswith("godot")]
            if matches: return matches[0]
        return None

    def add_project(self):
        item = {"name":"Novo projeto","category":"Outros","description":"","kind":"url","target":"https://","icon":"★","accent":ACCENT}
        self.data["projects"].append(item)
        self.edit_project(item, new=True)

    def edit_project(self, item, new=False):
        editor = tk.Toplevel(self)
        editor.title("Configurar projeto")
        editor.geometry("630x490")
        editor.configure(bg=BG)
        editor.transient(self)
        editor.grab_set()
        fields={}
        labels=[("Nome","name"),("Categoria","category"),("Descrição","description"),("Destino (URL ou caminho)","target"),("Pasta local (opcional)","folder")]
        for label, key in labels:
            row=tk.Frame(editor,bg=BG);row.pack(fill="x",padx=22,pady=6)
            tk.Label(row,text=label,bg=BG,fg=MUTED,width=24,anchor="w",font=("Segoe UI",9)).pack(side="left")
            val=tk.StringVar(value=item.get(key,""))
            field=tk.Entry(row,textvariable=val,bg=PANEL,fg=FG,insertbackground=FG,relief="flat",
                           highlightthickness=1,highlightbackground="#354A67",font=("Segoe UI",10))
            field.pack(side="left",fill="x",expand=True,ipady=6)
            fields[key]=val
            if key in ("target","folder"):
                tk.Button(row,text="…",command=lambda v=val:self.pick_path(v),bg="#2D4771",fg=FG,relief="flat").pack(side="left",padx=(5,0))
        row=tk.Frame(editor,bg=BG);row.pack(fill="x",padx=22,pady=9)
        tk.Label(row,text="Tipo",bg=BG,fg=MUTED,width=24,anchor="w").pack(side="left")
        kind=tk.StringVar(value=item.get("kind","url"))
        ttk.Combobox(row,textvariable=kind,values=["url","local","godot"],state="readonly").pack(side="left",fill="x",expand=True)
        hint="URL = abre o navegador · Local = abre ficheiro/pasta · Godot = abre projeto no editor"
        tk.Label(editor,text=hint,bg=BG,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=22,pady=(5,10))
        row=tk.Frame(editor,bg=BG);row.pack(fill="x",padx=22,pady=12)
        def commit():
            if not fields["name"].get().strip() or not fields["target"].get().strip():
                messagebox.showwarning("Dados em falta","Nome e destino são obrigatórios.",parent=editor);return
            for k,v in fields.items():item[k]=v.get().strip()
            item["kind"]=kind.get()
            save_projects(self.data)
            self.draw_filters();self.draw_cards()
            editor.destroy()
            self.status.set("Projeto guardado apenas neste computador.")
        def delete():
            if messagebox.askyesno("Remover atalho","Remover este cartão? Não apaga os ficheiros do projeto.",parent=editor):
                self.data["projects"].remove(item);save_projects(self.data)
                self.draw_filters();self.draw_cards();editor.destroy()
        tk.Button(row,text="Guardar",command=commit,bg="#315D92",fg=FG,relief="flat",padx=18,pady=9).pack(side="left")
        tk.Button(row,text="Remover cartão",command=delete,bg=PANEL,fg="#FFB0AA",relief="flat",padx=15,pady=9).pack(side="left",padx=12)
        tk.Button(row,text="Cancelar",command=editor.destroy,bg=PANEL,fg=MUTED,relief="flat",padx=14,pady=9).pack(side="right")
        if new:
            def cancel_new():
                if item in self.data["projects"]:self.data["projects"].remove(item)
                editor.destroy()
            editor.protocol("WM_DELETE_WINDOW",cancel_new)

    def pick_path(self,var):
        path=filedialog.askopenfilename(parent=self)
        if path:var.set(path)

if __name__ == "__main__":
    Launcher().mainloop()
