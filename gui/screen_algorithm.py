import customtkinter as ctk
from gui.widgets import (COLORS, FONTS, accent_button,
                         illustrated_card, CardContent, CardSpec, CardTheme,
                         ALGORITHM_ILLUSTRATIONS)
from config.labels import ALGORITHMS, PROBLEM_LABELS


class ScreenAlgorithm(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS['bg'])
        self._app = app
        self._subtitle_var = ctk.StringVar()
        self._build()

    def _build(self):
        wrapper = ctk.CTkFrame(self, fg_color='transparent')
        wrapper.place(relx=0.5, rely=0.5, anchor='center')

        # ── Title area ──
        ctk.CTkLabel(
            wrapper, text='Selecciona el Algoritmo',
            font=FONTS['title'], text_color=COLORS['text'],
        ).pack()

        ctk.CTkLabel(
            wrapper, textvariable=self._subtitle_var,
            font=FONTS['subheading'], text_color=COLORS['text_secondary'],
        ).pack(pady=(4, 20))

        # ── Cards grid (3 + 2) ──
        cards_frame = ctk.CTkFrame(wrapper, fg_color='transparent')
        cards_frame.pack()

        for i, (key, label, short, desc) in enumerate(ALGORITHMS):
            card_content = CardContent(short, label, desc)
            theme = CardTheme(COLORS['secondary'], COLORS['secondary'])
            spec = CardSpec(card_content, lambda k=key: self._select(k), theme)
            draw_fn = ALGORITHM_ILLUSTRATIONS.get(key, lambda c, w, h: None)

            card = illustrated_card(cards_frame, spec, draw_fn,
                                    width=240, height=210)
            card.grid(row=i // 3, column=i % 3, padx=8, pady=8)

        # ── Back button ──
        accent_button(
            wrapper, '<  Regresar',
            lambda: self._app.show_screen('problem'), width=160, height=38,
        ).pack(pady=(20, 0))

    def on_show(self):
        prob = self._app.state.get('problem', '')
        self._subtitle_var.set(f'Problema: {PROBLEM_LABELS.get(prob, prob)}')

    def _select(self, key: str):
        self._app.state['algorithm'] = key
        self._app.show_screen('objective')
