from tkinter import ttk


class UI(ttk.Style):
    def __init__(self):
        super().__init__()
        self.theme_use('clam')

        # Couleurs
        self.primary = "#4a6cd4"
        self.secondary = "#f0f0f0"
        self.accent = "#2c3e50"
        self.success = "#27ae60"
        self.warning = "#f39c12"
        self.error = "#e74c3c"

        # Configuration des styles
        self.configure('TFrame', background=self.secondary)
        self.configure('TLabel', background=self.secondary, font=('Helvetica', 10))
        self.configure('TButton', background=self.primary, foreground='white',
                       font=('Helvetica', 10, 'bold'), borderwidth=0)
        self.map('TButton', background=[('active', self.accent), ('disabled', '#a0a0a0')])

        self.configure('Header.TLabel', font=('Helvetica', 16, 'bold'), foreground=self.accent)
        self.configure('Status.TLabel', font=('Helvetica', 9), foreground='#555555')

        # Style pour la barre de progression
        self.configure('TProgressbar', 
                      background=self.primary,
                      troughcolor=self.secondary,
                      borderwidth=0,
                      thickness=10)
        
        # Force le rafraîchissement du style
        self.layout('TProgressbar', [
            ('Horizontal.Progressbar.trough', {
                'children': [('Horizontal.Progressbar.pbar', {'side': 'left', 'sticky': 'ns'})],
                'sticky': 'nswe'
            })
        ])

        # Style pour le Treeview
        self.configure('Treeview', background='white', fieldbackground='white', font=('Helvetica', 9))
        self.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'), background=self.secondary)
        self.map('Treeview', background=[('selected', self.primary)], foreground=[('selected', 'white')])

        # Style pour le bouton d'annulation
        self.configure('Danger.TButton', background=self.error, foreground='white')
        self.map('Danger.TButton',
                 background=[('active', '#ff0000'), ('pressed', '#cc0000')],
                 foreground=[('active', 'white'), ('pressed', 'white')])

