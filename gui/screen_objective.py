import customtkinter as ctk
from gui.widgets import (COLORS, FONTS, accent_button,
                         illustrated_card, CardContent, CardSpec, CardTheme,
                         draw_maximize_illus, draw_minimize_illus)
from config.labels import PROBLEM_LABELS, ALGORITHM_SHORT


class ScreenObjective(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS['bg'])
        self._app = app
        self._summary_var = ctk.StringVar()
        self._build()

    def _build(self):
        wrapper = ctk.CTkFrame(self, fg_color='transparent')
        wrapper.place(relx=0.5, rely=0.46, anchor='center')

        ctk.CTkLabel(
            wrapper, text='Selecciona el Objetivo',
            font=FONTS['title'], text_color=COLORS['text'],
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            wrapper, textvariable=self._summary_var,
            font=FONTS['subheading'], text_color=COLORS['text_secondary'],
        ).pack(pady=(0, 32))

        cards_frame = ctk.CTkFrame(wrapper, fg_color='transparent')
        cards_frame.pack()

        # Maximize card
        max_content = CardContent('MAX', 'Maximizar',
                                  'Encontrar el valor maximo\nde la funcion objetivo')
        max_theme = CardTheme(COLORS['success'], COLORS['success_hover'])
        max_spec = CardSpec(max_content, lambda: self._select(True), max_theme)

        illustrated_card(cards_frame, max_spec, draw_maximize_illus,
                         width=280, height=230).grid(row=0, column=0, padx=14)

        # Minimize card
        min_content = CardContent('MIN', 'Minimizar',
                                  'Encontrar el valor minimo\nde la funcion objetivo')
        min_theme = CardTheme(COLORS['secondary'], COLORS['secondary_hover'])
        min_spec = CardSpec(min_content, lambda: self._select(False), min_theme)

        illustrated_card(cards_frame, min_spec, draw_minimize_illus,
                         width=280, height=230).grid(row=0, column=1, padx=14)

        accent_button(
            wrapper, '<  Regresar',
            lambda: self._app.show_screen('algorithm'), width=160, height=38,
        ).pack(pady=(28, 0))

    def on_show(self):
        p = PROBLEM_LABELS.get(self._app.state.get('problem', ''), '?')
        a = ALGORITHM_SHORT.get(self._app.state.get('algorithm', ''), '?')
        self._summary_var.set(f'{p}  /  {a}')

    def _select(self, maximize: bool):
        self._app.state['maximize'] = maximize
        self._app.show_screen('params')
