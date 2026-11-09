"""Central Launcher 1.1 — dark glass / coral interface."""
import json
import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

APP_NAME = "Central Launcher"
BG = "#101722"
SIDE = "#263344"
SURFACE = "#192431"
PANEL = "#202C3C"
TILE = "#243142"
STROKE = "#3B4A5B"
WHITE = "#F3F6FA"
MUTED = "#A9B8C8"
PALETTE = [
    ("Azul", "#248BFF"), ("Verde", "#12BE83"),
    ("Amarelo", "#F2C626"), ("Laranja", "#F97922"),
    ("Vermelho", "#ED3C4B"), ("Rosa", "#C43DCA"),
    ("Violeta", "#8953F7"), ("Ciano", "#11CBE9"),
    ("Coral", "#F67E76"),
]


def resource(name):
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / name


def app_dir():
    base = Path(os.environ.get("APPDATA", Path.home())) / "CentralLauncher"
    base.mkdir(parents=True, exist_ok=True)
    return base


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def dump_json(path, value):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(value, fh, ensure_ascii=False, indent=2)


def load_projects():
    target = app_dir() / "projects.json"
    if not target.exists():
        shutil.copyfile(resource("projects.json"), target)
    return load_json(target, {"version": 1, "projects": []})


def set_palette(light=False):
    global BG, SIDE, SURFACE, PANEL, TILE, STROKE, WHITE, MUTED
    if light:
        BG, SIDE, SURFACE, PANEL = "#E8EDF3", "#D5DFEB", "#F9FBFE", "#E4EBF4"
        TILE, STROKE, WHITE, MUTED = "#FFFFFF", "#B6C5D7", "#243247", "#52647A"
    else:
        BG, SIDE, SURFACE, PANEL = "#101722", "#263344", "#192431", "#202C3C"
        TILE, STROKE, WHITE, MUTED = "#A9B8C8", "#3B4A5B", "#F3F6FA", "#A9B8C8"
        TILE = "#243142"


def windows_light_mode():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
            return bool(winreg.QueryValueEx(key,"AppsUseLightTheme")[0])
    except (OSError, ImportError):
        return False


def color_mix(a, b, ratio):
    def rgb(h):
        return tuple(int(h[i:i+2], 16) for i in (1,3,5))
    ca, cb = rgb(a), rgb(b)
    return "#" + "".join(f"{round(x*(1-ratio)+y*ratio):02x}" for x,y in zip(ca,cb))


class Launcher(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.data = load_projects()
        self.theme_file = app_dir() / "theme.json"
        self.prefs = load_json(self.theme_file, {"appearance": "Dark", "accent": "#F67E76", "density": 3,
                                                 "radius": 15, "animations": True, "bold_focus": False})
        self.accent = self.prefs.get("accent", "#F67E76")
        self.apply_palette()
        self.active_section = "Biblioteca"
        self.query = ctk.StringVar()
        self.category = "Todos"
        self.title(APP_NAME)
        self.geometry("1280x810")
        self.minsize(1020, 650)
        self.configure(fg_color=BG)
        self.make_shell()
        self.show_section("Biblioteca")
        self.query.trace_add("write", lambda *_: self.render_projects())

    def apply_palette(self):
        mode = self.prefs.get("appearance", "Dark")
        light = (mode == "Light") or (mode == "Auto" and windows_light_mode())
        set_palette(light)

    def rebuild_shell(self, section=None):
        section = section or self.active_section
        self.apply_palette()
        self.configure(fg_color=BG)
        for child in self.winfo_children():
            child.destroy()
        self.make_shell()
        self.show_section(section)

    def fg(self):
        return "#142031" if self.prefs["appearance"] == "Dark" else "#E8EDF4"

    def accent_pale(self):
        return color_mix(self.accent, WHITE, .16)

    def label(self, parent, text, size=12, weight="normal", color=MUTED, **kw):
        return ctk.CTkLabel(parent, text=text, font=("Segoe UI", size, weight), text_color=color, **kw)

    def make_shell(self):
        self.sidebar = ctk.CTkFrame(self, width=236, fg_color=SIDE, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=19, pady=(27, 24))
        orb = ctk.CTkFrame(brand, width=40, height=40, corner_radius=13, fg_color=self.accent)
        orb.pack(side="left")
        orb.pack_propagate(False)
        self.label(orb, "✦", 23, "bold", "#18202A").pack(expand=True)
        text = ctk.CTkFrame(brand, fg_color="transparent")
        text.pack(side="left", padx=(11,0))
        self.label(text, "CENTRAL", 18, "bold", WHITE).pack(anchor="w")
        self.label(text, "O teu universo criativo", 10, color=MUTED).pack(anchor="w")
        self.label(self.sidebar, "WORKSPACE", 10, "bold", "#95A8BF").pack(anchor="w", padx=26, pady=(14,9))
        self.nav = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav.pack(fill="x", padx=12)
        self.nav_buttons = {}
        entries = [("Biblioteca","▦"), ("Jogos","◈"), ("Música","♫"), ("Escrita","▤"),
                   ("Podcasts","◉"), ("Redes sociais","◎"), ("Desenvolvimento","⌘"),
                   ("Temas","◐"), ("Definições","⚙")]
        for section, symbol in entries:
            button = ctk.CTkButton(self.nav, text=f"  {symbol}     {section}", anchor="w", width=210,
                                   height=43, corner_radius=10, fg_color="transparent",
                                   hover_color="#3A495B", font=("Segoe UI", 12),
                                   text_color="#C3D0DE",
                                   command=lambda sec=section:self.show_section(sec))
            button.pack(fill="x", pady=3)
            self.nav_buttons[section] = button
        ctk.CTkFrame(self.sidebar, fg_color="#526273", height=1).pack(fill="x", padx=23, pady=(20,14))
        self.label(self.sidebar, "LIGAÇÕES RÁPIDAS", 10, "bold", "#95A8BF").pack(anchor="w",padx=25,pady=(0,8))
        for name, url in [("↗  Central no GitHub", "https://github.com/Xtvback/central"),
                          ("↗  Solvero no Suno","https://suno.com/@solvero")]:
            ctk.CTkButton(self.sidebar, text=name, anchor="w", fg_color="transparent",
                          hover_color="#3A495B", text_color=MUTED, height=33,
                          command=lambda link=url:webbrowser.open(link)).pack(fill="x", padx=14)
        self.label(self.sidebar, "CENTRAL LAUNCHER  •  v1.1", 10, color="#8295AA").pack(side="bottom", pady=24)
        self.main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.main.pack(side="left", fill="both", expand=True)
        self.header = ctk.CTkFrame(self.main, fg_color="transparent")
        self.header.pack(fill="x", padx=32, pady=(28,10))
        self.body = ctk.CTkFrame(self.main, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=30, pady=(3,12))
        self.footer = ctk.CTkFrame(self.main, height=45, fg_color=SURFACE, corner_radius=0)
        self.footer.pack(fill="x", side="bottom")
        self.status_var = ctk.StringVar(value="Pronto. Os projetos locais podem ser configurados neste computador.")
        self.label(self.footer, "", 10).pack(side="left", padx=8)
        ctk.CTkLabel(self.footer, textvariable=self.status_var, font=("Segoe UI", 10),
                     text_color=MUTED).pack(side="left", padx=17)
        self.label(self.footer, "●  LOCAL", 10, "bold", "#2BCC95").pack(side="right",padx=26)

    def clear(self, widget):
        for child in widget.winfo_children():child.destroy()

    def show_section(self, name):
        self.active_section = name
        for key, button in self.nav_buttons.items():
            if key == name:
                button.configure(fg_color=color_mix(self.accent,SIDE,.80), text_color=WHITE,
                                 border_width=1, border_color=color_mix(self.accent,WHITE,.37),
                                 hover_color=color_mix(self.accent,SIDE,.67))
            else:
                button.configure(fg_color="transparent", border_width=0, text_color="#C3D0DE",
                                 hover_color="#3A495B")
        self.clear(self.header)
        self.clear(self.body)
        if name == "Temas":
            self.render_theme()
        elif name == "Definições":
            self.render_settings()
        else:
            self.render_library_shell(name)

    def make_heading(self, name, subtitle):
        self.label(self.header, name, 31, "bold", WHITE).pack(anchor="w")
        self.label(self.header, subtitle, 12, color=MUTED).pack(anchor="w", pady=(2,0))

    def render_library_shell(self, name):
        self.make_heading("A tua Biblioteca" if name=="Biblioteca" else name,
                          "Todos os teus projetos criativos, num único lugar." if name=="Biblioteca"
                          else f"Explora os projetos na categoria {name}.")
        toolbar = ctk.CTkFrame(self.body, fg_color="transparent")
        toolbar.pack(fill="x", pady=(5,14))
        ctk.CTkEntry(toolbar, textvariable=self.query, placeholder_text="⌕   Pesquisar projetos, jogos, música...",
                     font=("Segoe UI", 12), height=43, corner_radius=12, fg_color=PANEL,
                     border_color=STROKE, text_color=WHITE, placeholder_text_color=MUTED).pack(side="left",fill="x",expand=True)
        ctk.CTkButton(toolbar, text="+  Novo projeto", width=144,height=43,fg_color=self.accent,
                      hover_color=self.accent_pale(),text_color="#19202B",font=("Segoe UI",11,"bold"),
                      corner_radius=12,command=self.add_project).pack(side="left",padx=(12,0))
        self.info_row = ctk.CTkFrame(self.body, fg_color="transparent")
        self.info_row.pack(fill="x",pady=(0,12))
        self.label(self.info_row, "PROJETOS", 10,"bold",color=MUTED).pack(side="left")
        self.count_label = self.label(self.info_row,"",10,color=self.accent)
        self.count_label.pack(side="left",padx=12)
        self.tiles_container = ctk.CTkScrollableFrame(self.body, fg_color="transparent",
                                                      corner_radius=0,scrollbar_button_color=STROKE,
                                                      scrollbar_button_hover_color=self.accent)
        self.tiles_container.pack(fill="both",expand=True)
        self.render_projects()

    def filtered(self):
        term = self.query.get().casefold().strip()
        aliases = {"Jogos":["Jogos"],"Música":["Música"],"Escrita":["Escrita"],"Podcasts":["Podcasts"],
                   "Redes sociais":["Redes sociais"],"Desenvolvimento":["Desenvolvimento"]}
        cats = aliases.get(self.active_section)
        return [p for p in self.data.get("projects",[])
                if (not cats or p.get("category") in cats)
                and (not term or term in " ".join(str(p.get(x,"")) for x in ("name","description","category")).casefold())]

    def render_projects(self):
        if not hasattr(self,"tiles_container") or self.active_section in ("Temas","Definições"):return
        self.clear(self.tiles_container)
        items = self.filtered()
        self.count_label.configure(text=f"●  {len(items)} disponíveis")
        if not items:
            self.label(self.tiles_container,"Nenhum projeto encontrado",14,color=MUTED).pack(pady=65)
            return
        columns = 3 if self.winfo_width()>=1190 else 2
        for col in range(columns):
            self.tiles_container.grid_columnconfigure(col, weight=1,uniform="cards")
        radius = int(self.prefs.get("radius",15))
        density = int(self.prefs.get("density",3))
        pad = 11 if density<=1 else 14 if density==2 else 18
        for i, p in enumerate(items):
            row,col=divmod(i,columns)
            card=ctk.CTkFrame(self.tiles_container,fg_color=TILE,corner_radius=radius,
                              border_width=1,border_color=STROKE)
            card.grid(row=row,column=col,sticky="nsew",padx=7,pady=8)
            inner=ctk.CTkFrame(card,fg_color="transparent")
            inner.pack(fill="both",expand=True,padx=pad,pady=pad)
            top=ctk.CTkFrame(inner,fg_color="transparent")
            top.pack(fill="x")
            project_color=p.get("accent",self.accent)
            badge=ctk.CTkFrame(top,fg_color=color_mix(project_color,TILE,.79),width=49,height=49,corner_radius=14,
                               border_width=1,border_color=color_mix(project_color,TILE,.52))
            badge.pack(side="left")
            badge.pack_propagate(False)
            self.label(badge,p.get("icon","✦"),22,"bold",project_color).pack(expand=True)
            self.label(top,p.get("category","PROJETO").upper(),9,"bold",MUTED).pack(side="right")
            self.label(inner,p.get("name","Projeto"),15,"bold",WHITE,wraplength=244,justify="left",
                       anchor="w").pack(fill="x",pady=(18,5))
            self.label(inner,p.get("description",""),11,color=MUTED,wraplength=244,justify="left",
                       anchor="w").pack(fill="x",pady=(0,13))
            actions=ctk.CTkFrame(inner,fg_color="transparent")
            actions.pack(fill="x",side="bottom",pady=(10,0))
            ctk.CTkButton(actions,text="Abrir  ↗",width=90,height=36,fg_color=self.accent,
                          hover_color=self.accent_pale(),text_color="#19202B",font=("Segoe UI",11,"bold"),
                          corner_radius=10,command=lambda item=p:self.open_project(item)).pack(side="left")
            ctk.CTkButton(actions,text="⚙",width=39,height=36,fg_color=PANEL,hover_color="#3C5166",
                          text_color=MUTED,corner_radius=10,
                          command=lambda item=p:self.edit_project(item)).pack(side="right")

    def render_theme(self):
        self.make_heading("Temas","Personaliza o estilo visual da tua Central.")
        scroll=ctk.CTkScrollableFrame(self.body,fg_color="transparent")
        scroll.pack(fill="both",expand=True)
        wrapper=ctk.CTkFrame(scroll,fg_color=SURFACE,corner_radius=20,border_width=1,border_color=STROKE)
        wrapper.pack(fill="x",padx=5,pady=(13,12))
        left=ctk.CTkFrame(wrapper,fg_color="transparent")
        left.pack(side="left",fill="both",expand=True,padx=27,pady=24)
        self.label(left,"APARÊNCIA",10,"bold",MUTED).pack(anchor="w",pady=(0,9))
        self.appearance_control=ctk.CTkSegmentedButton(left,values=["Auto","Light","Dark"],height=42,
                        font=("Segoe UI",12),corner_radius=15,
                        selected_color=self.accent,selected_hover_color=self.accent_pale(),
                        unselected_color=PANEL,unselected_hover_color="#445269",
                        text_color=WHITE,command=self.change_appearance)
        self.appearance_control.pack(anchor="w",pady=(0,25))
        self.appearance_control.set(self.prefs.get("appearance","Dark"))
        self.label(left,"COR DE DESTAQUE",10,"bold",MUTED).pack(anchor="w",pady=(0,10))
        palette=ctk.CTkFrame(left,fg_color="transparent")
        palette.pack(anchor="w")
        for title,color in PALETTE:
            fg=color
            surround=ctk.CTkFrame(palette,width=43,height=43,corner_radius=22,
                                   fg_color=color_mix(color,SURFACE,.65),
                                   border_width=2 if color==self.accent else 0,
                                   border_color=color_mix(color,WHITE,.42))
            surround.pack(side="left",padx=(0,7))
            surround.pack_propagate(False)
            ctk.CTkButton(surround,text="",width=31,height=31,corner_radius=17,fg_color=fg,
                          hover_color=color_mix(color,WHITE,.18),
                          command=lambda shade=color:self.set_accent(shade)).pack(expand=True)
        selected = next((k for k,c in PALETTE if c==self.accent),"Personalizada")
        self.color_name=self.label(left,selected,11,color=self.accent)
        self.color_name.pack(anchor="w",pady=(8,24))
        self.label(left,"DENSIDADE",10,"bold",MUTED).pack(anchor="w",pady=(0,13))
        self.density_slider=ctk.CTkSlider(left,from_=1,to=3,number_of_steps=2,width=290,
                         progress_color=self.accent,button_color=self.accent,
                         button_hover_color=self.accent_pale(),command=self.set_density)
        self.density_slider.pack(anchor="w")
        self.density_slider.set(self.prefs.get("density",3))
        densityrow=ctk.CTkFrame(left,fg_color="transparent")
        densityrow.pack(anchor="w",pady=(7,25))
        for t in ["Relaxado","Padrão","Compacto"]:
            self.label(densityrow,t,10,color=MUTED,width=100).pack(side="left")
        self.label(left,"CANTOS ARREDONDADOS",10,"bold",MUTED).pack(anchor="w",pady=(0,12))
        self.radius_slider=ctk.CTkSlider(left,from_=4,to=22,number_of_steps=18,width=290,
                         progress_color=self.accent,button_color=self.accent,
                         button_hover_color=self.accent_pale(),command=self.set_radius)
        self.radius_slider.pack(anchor="w")
        self.radius_slider.set(self.prefs.get("radius",15))
        self.radius_value=self.label(left,f"{self.prefs.get('radius',15)} px",10,color=MUTED)
        self.radius_value.pack(anchor="w",pady=(6,22))
        self.smooth=ctk.CTkSwitch(left,text="Animações suaves",progress_color=self.accent,
                         button_color=WHITE,command=self.change_switches,
                         font=("Segoe UI",12),text_color=WHITE)
        self.smooth.pack(anchor="w",pady=(0,5))
        if self.prefs.get("animations",True):self.smooth.select()
        self.label(left,"Transições suaves para elementos da interface.",10,color=MUTED).pack(anchor="w",padx=(52,0),pady=(0,19))
        self.focus=ctk.CTkSwitch(left,text="Realce de seleção",progress_color=self.accent,
                         button_color=WHITE,command=self.change_switches,font=("Segoe UI",12),text_color=WHITE)
        self.focus.pack(anchor="w")
        if self.prefs.get("bold_focus",False):self.focus.select()
        self.label(left,"Aumenta a visibilidade da navegação.",10,color=MUTED).pack(anchor="w",padx=(52,0),pady=(4,8))
        preview=ctk.CTkFrame(wrapper,fg_color="#111924",width=280,corner_radius=18,
                             border_width=1,border_color=STROKE)
        preview.pack(side="right",fill="y",padx=(8,24),pady=22)
        preview.pack_propagate(False)
        self.label(preview,"PRÉ-VISUALIZAÇÃO",10,"bold",MUTED).pack(anchor="w",padx=20,pady=(21,15))
        self.label(preview,"A tua Central",22,"bold",WHITE).pack(anchor="w",padx=19)
        self.label(preview,"Um espaço só teu.",11,color=MUTED).pack(anchor="w",padx=20,pady=(4,21))
        self.preview_card=ctk.CTkFrame(preview,fg_color=TILE,border_width=1,border_color=STROKE,corner_radius=15)
        self.preview_card.pack(fill="x",padx=18,pady=(0,20))
        self.label(self.preview_card,"◈    USLORDS",14,"bold",WHITE).pack(anchor="w",padx=15,pady=(18,6))
        self.label(self.preview_card,"O Despertar dos Colares",11,color=MUTED).pack(anchor="w",padx=15,pady=(0,18))
        self.preview_button=ctk.CTkButton(self.preview_card,text="Abrir projeto  ↗",height=37,
                            fg_color=self.accent,hover_color=self.accent_pale(),text_color="#19202B",
                            corner_radius=10,font=("Segoe UI",11,"bold"))
        self.preview_button.pack(fill="x",padx=15,pady=(0,17))
        self.label(preview,"Alterações guardadas automaticamente.",10,color=MUTED,wraplength=220).pack(anchor="w",padx=20,pady=(0,20))

    def persist(self):
        dump_json(self.theme_file,self.prefs)

    def change_appearance(self, value):
        self.prefs["appearance"] = value
        self.persist()
        self.rebuild_shell("Temas")
        self.status_var.set("Aparência aplicada: "+value+".")
    def set_accent(self, value):
        self.prefs["accent"]=value
        self.accent=value
        self.persist()
        self.rebuild_shell("Temas")

    def set_density(self, value):
        self.prefs["density"]=int(round(value));self.persist()
    def set_radius(self, value):
        self.prefs["radius"]=int(round(value));self.persist()
        if hasattr(self,"radius_value"):self.radius_value.configure(text=f"{self.prefs['radius']} px")
        if hasattr(self,"preview_card"):self.preview_card.configure(corner_radius=self.prefs["radius"])
    def change_switches(self):
        self.prefs["animations"]=bool(self.smooth.get())
        self.prefs["bold_focus"]=bool(self.focus.get())
        self.persist()

    def render_settings(self):
        self.make_heading("Definições","Organiza os caminhos dos teus projetos neste computador.")
        block=ctk.CTkFrame(self.body,fg_color=SURFACE,corner_radius=18,border_width=1,border_color=STROKE)
        block.pack(fill="x",pady=(14,0))
        self.label(block,"Biblioteca local",20,"bold",WHITE).pack(anchor="w",padx=25,pady=(24,8))
        self.label(block,"As configurações são independentes em cada computador. Não alteramos os teus ficheiros originais.",
                   12,color=MUTED,wraplength=600,justify="left").pack(anchor="w",padx=25,pady=(0,20))
        ctk.CTkButton(block,text="Abrir pasta de configurações  ↗",fg_color=self.accent,
                      hover_color=self.accent_pale(),text_color="#19202B",width=290,height=42,
                      command=lambda:os.startfile(str(app_dir()))).pack(anchor="w",padx=25,pady=(0,23))
        self.label(self.body,"Os links online abrem no navegador. Os projetos locais necessitam de estar presentes neste PC.",
                   11,color=MUTED,wraplength=650,justify="left").pack(anchor="w",pady=20)

    def resolve(self, value):
        return Path(os.path.expandvars(value)).expanduser()
    def open_project(self, item):
        target=item.get("target","")
        if item.get("kind")=="url":
            webbrowser.open(target)
            self.status_var.set("Aberto no navegador: "+item["name"])
            return
        file=self.resolve(target)
        if not file.exists():
            self.status_var.set("Ficheiro ou pasta não encontrado neste computador.")
            if messagebox.askyesno("Projeto não encontrado","Este projeto não está nesta localização.\n\nQueres configurar o caminho?"):
                self.edit_project(item)
            return
        try:
            if item.get("kind")=="godot":
                exe=self.find_godot()
                if exe:
                    subprocess.Popen([str(exe),"--path",str(file.parent),"-e"],cwd=str(file.parent))
                else:
                    os.startfile(str(file.parent))
                    messagebox.showinfo("Godot","O Godot não foi encontrado; abri a pasta do projeto.")
            else:os.startfile(str(file))
            self.status_var.set("A abrir: "+item["name"])
        except Exception as exc:
            messagebox.showerror("Não foi possível abrir",str(exc))
    def find_godot(self):
        found=shutil.which("godot") or shutil.which("godot.exe")
        if found:return found
        root=Path(os.environ.get("LOCALAPPDATA",""))/"Microsoft"/"WinGet"/"Packages"
        if root.is_dir():
            paths=[p for p in root.glob("GodotEngine.GodotEngine*/*.exe") if p.name.lower().startswith("godot") and "console" not in p.name.lower()]
            if paths:return str(paths[0])
        return None

    def add_project(self):
        obj={"name":"Novo projeto","category":"Outros","description":"","kind":"url","target":"https://","icon":"✦","accent":self.accent}
        self.edit_project(obj,new=True)

    def edit_project(self, item, new=False):
        dialog=ctk.CTkToplevel(self)
        dialog.title("Configurar projeto")
        dialog.geometry("680x570")
        dialog.resizable(False,False)
        dialog.configure(fg_color=BG)
        dialog.transient(self)
        dialog.after(100, dialog.grab_set)
        self.label(dialog,"Novo projeto" if new else "Editar projeto",25,"bold",WHITE).pack(anchor="w",padx=29,pady=(23,13))
        fields={}
        for title,key in [("Nome","name"),("Categoria","category"),("Descrição","description"),
                          ("Destino (URL, programa ou pasta)","target"),("Pasta local (opcional)","folder")]:
            row=ctk.CTkFrame(dialog,fg_color="transparent")
            row.pack(fill="x",padx=26,pady=6)
            self.label(row,title,11,color=MUTED,width=194,anchor="w").pack(side="left")
            value=ctk.StringVar(value=item.get(key,""))
            entry=ctk.CTkEntry(row,textvariable=value,width=375,height=36,fg_color=PANEL,
                               border_color=STROKE,text_color=WHITE)
            entry.pack(side="left",fill="x",expand=True)
            fields[key]=value
            if key in ("target","folder"):
                ctk.CTkButton(row,text="…",width=32,height=35,fg_color=PANEL,hover_color=STROKE,
                              command=lambda v=value:self.choose_path(v,dialog)).pack(side="left",padx=(6,0))
        row=ctk.CTkFrame(dialog,fg_color="transparent")
        row.pack(fill="x",padx=26,pady=(9,5))
        self.label(row,"Tipo",11,color=MUTED,width=194,anchor="w").pack(side="left")
        kind=ctk.StringVar(value=item.get("kind","url"))
        ctk.CTkOptionMenu(row,variable=kind,values=["url","local","godot"],
                          fg_color=PANEL,button_color=STROKE,width=360,height=36).pack(side="left")
        self.label(dialog,"URL: navegador  ·  local: ficheiro/pasta  ·  godot: editor Godot",10,color=MUTED).pack(anchor="w",padx=30,pady=10)
        buttons=ctk.CTkFrame(dialog,fg_color="transparent")
        buttons.pack(fill="x",padx=26,pady=14)
        def save():
            if not fields["name"].get().strip() or not fields["target"].get().strip():
                messagebox.showwarning("Dados em falta","Nome e destino são obrigatórios.",parent=dialog);return
            for key,value in fields.items():item[key]=value.get().strip()
            item["kind"]=kind.get()
            if new:self.data["projects"].append(item)
            dump_json(app_dir()/"projects.json",self.data)
            dialog.destroy()
            self.show_section(self.active_section)
            self.status_var.set("Projeto guardado neste computador.")
        def remove():
            if messagebox.askyesno("Remover cartão","Remover o atalho da Central?\nOs ficheiros do projeto serão preservados.",parent=dialog):
                if not new and item in self.data["projects"]:self.data["projects"].remove(item)
                dump_json(app_dir()/"projects.json",self.data)
                dialog.destroy();self.show_section(self.active_section)
        ctk.CTkButton(buttons,text="Guardar alterações",height=40,fg_color=self.accent,
                      hover_color=self.accent_pale(),text_color="#19202B",command=save).pack(side="left")
        if not new:
            ctk.CTkButton(buttons,text="Remover cartão",height=40,fg_color="#442F36",
                          hover_color="#603C48",command=remove).pack(side="left",padx=(11,0))
        ctk.CTkButton(buttons,text="Cancelar",height=40,fg_color=PANEL,
                      hover_color=STROKE,command=dialog.destroy).pack(side="right")

    def choose_path(self, var, dialog):
        p=filedialog.askopenfilename(parent=dialog,title="Escolher ficheiro")
        if not p:p=filedialog.askdirectory(parent=dialog,title="Escolher pasta")
        if p:var.set(p)


if __name__=="__main__":
    app=Launcher()
    app.mainloop()
