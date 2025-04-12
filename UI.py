from tkinter import ttk


class UI(ttk.Style):
    def __init__(self):
        super().__init__()
        self.theme_use('clam')

        self.primary = "#3a7bd5"        # Bleu plus profond
        self.secondary = "#f5f7fa"      # Gris très clair
        self.accent = "#2c3e50"         # Bleu foncé
        self.success = "#2ecc71"        # Vert plus vif
        self.warning = "#f39c12"        # Orange
        self.error = "#e74c3c"          # Rouge
        self.text_dark = "#2d3436"      # Presque noir
        self.text_light = "#ecf0f1"     # Blanc cassé

        self.configure('TFrame', background=self.secondary)
        self.configure('TLabel', background=self.secondary, foreground=self.text_dark, font=('Helvetica', 10))

        self.configure('TButton',
                      background=self.primary,
                      foreground=self.text_light,
                      font=('Helvetica', 10, 'bold'),
                      borderwidth=0,
                      padding=6)
        self.map('TButton',
                background=[('active', self.accent), ('disabled', '#a0a0a0')],
                foreground=[('disabled', '#d0d0d0')])

        self.configure('Header.TLabel',
                      font=('Helvetica', 18, 'bold'),
                      foreground=self.accent,
                      background=self.secondary)

        self.configure('Status.TLabel',
                      font=('Helvetica', 9),
                      foreground='#7f8c8d',
                      background=self.secondary)

        self.configure('TProgressbar',
                      background=self.success,
                      troughcolor=self.secondary,
                      borderwidth=0,
                      thickness=8)

        self.configure('Treeview',
                      background='white',
                      fieldbackground='white',
                      font=('Helvetica', 9),
                      rowheight=25)

        self.configure('Treeview.Heading',
                      font=('Helvetica', 10, 'bold'),
                      background=self.secondary,
                      foreground=self.text_dark)

        self.map('Treeview',
                background=[('selected', self.primary)],
                foreground=[('selected', self.text_light)])
