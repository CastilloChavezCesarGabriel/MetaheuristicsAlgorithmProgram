import customtkinter as ctk
from gui.widgets import (COLORS, FONTS, illustrated_card,
                         CardContent, CardSpec, CardTheme,
                         PROBLEM_ILLUSTRATIONS)
from config.labels import PROBLEMS, PROBLEM_SHORT


class ScreenProblem(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS['bg'])
        self._app = app
        self._build()

    def _build(self):
        wrapper = ctk.CTkFrame(self, fg_color='transparent')
        wrapper.place(relx=0.5, rely=0.5, anchor='center')

        # ── Hero section ──
        ctk.CTkLabel(
            wrapper, text='Bienvenido a',
            font=FONTS['hero'], text_color=COLORS['text'],
        ).pack()

        ctk.CTkLabel(
            wrapper, text='Metaheuristic Lab',
            font=FONTS['hero_accent'], text_color=COLORS['primary'],
        ).pack(pady=(0, 6))

        ctk.CTkLabel(
            wrapper, text='Selecciona el tipo de problema que deseas resolver\n'
                          'y comienza tu optimizacion',
            font=FONTS['subheading'], text_color=COLORS['text_secondary'],
            justify='center',
        ).pack(pady=(0, 24))

        # ── Cards grid ──
        cards_frame = ctk.CTkFrame(wrapper, fg_color='transparent')
        cards_frame.pack()

        for i, (key, label, _short, desc) in enumerate(PROBLEMS):
            badge_text = PROBLEM_SHORT.get(key, '?')
            card_content = CardContent(badge_text, label, desc)
            theme = CardTheme(COLORS['primary'], COLORS['primary'])
            spec = CardSpec(card_content, lambda k=key: self._select(k), theme)
            draw_fn = PROBLEM_ILLUSTRATIONS.get(key, lambda c, w, h: None)

            card = illustrated_card(cards_frame, spec, draw_fn,
                                    width=300, height=235)
            card.grid(row=i // 2, column=i % 2, padx=10, pady=10)

    def _select(self, key: str):
        self._app.state['problem'] = key
        self._app.show_screen('algorithm')
