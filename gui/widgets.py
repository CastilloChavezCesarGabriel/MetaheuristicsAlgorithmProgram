import math
import platform
import random as _rng
import tkinter as tk
import customtkinter as ctk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------------------------------------------------------
# Color Palette — Indigo-Cyan analogous scheme
# ---------------------------------------------------------------------------
COLORS = {
    'bg':             '#0c0c14',
    'bg_secondary':   '#10101c',
    'surface':        '#161625',
    'surface_hover':  '#1c1c30',
    'surface2':       '#1e1e32',
    'card':           '#141422',
    'card_hover':     '#1a1a30',
    'card_border':    '#252542',
    'card_illus':     '#111120',

    'primary':        '#6366f1',
    'primary_hover':  '#818cf8',
    'primary_dim':    '#4f46e5',
    'primary_glow':   '#6366f140',

    'secondary':      '#06b6d4',
    'secondary_hover':'#22d3ee',
    'secondary_dim':  '#0891b2',

    'accent_warm':    '#f59e0b',
    'accent_purple':  '#a855f7',

    'text':           '#f1f5f9',
    'text_secondary': '#94a3b8',
    'text_muted':     '#64748b',
    'text_dim':       '#475569',

    'success':        '#10b981',
    'success_hover':  '#34d399',
    'error':          '#ef4444',
    'error_hover':    '#f87171',
    'warning':        '#f59e0b',

    'border':         '#1e293b',
    'border_light':   '#334155',
    'divider':        '#1e293b',

    'chart_line1':    '#818cf8',
    'chart_line2':    '#06b6d4',
    'chart_fill1':    '#6366f1',
    'chart_fill2':    '#22d3ee',
    'chart_grid':     '#1e293b',
}

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
_SYS = platform.system()
_FAMILY = 'SF Pro Display' if _SYS == 'Darwin' else 'Segoe UI'
_FAMILY_MONO = 'SF Mono' if _SYS == 'Darwin' else 'Cascadia Code'

FONTS = {
    'hero':       (_FAMILY, 32, 'bold'),
    'hero_accent':(_FAMILY, 32, 'bold'),
    'title':      (_FAMILY, 22, 'bold'),
    'heading':    (_FAMILY, 16, 'bold'),
    'subheading': (_FAMILY, 13),
    'body':       (_FAMILY, 12),
    'body_bold':  (_FAMILY, 12, 'bold'),
    'card_title': (_FAMILY, 13, 'bold'),
    'small':      (_FAMILY, 10),
    'small_bold': (_FAMILY, 10, 'bold'),
    'tiny':       (_FAMILY, 9),
    'mono':       (_FAMILY_MONO, 11),
    'button':     (_FAMILY, 12, 'bold'),
    'button_sm':  (_FAMILY, 11, 'bold'),
    'step':       (_FAMILY, 10, 'bold'),
    'stat_big':   (_FAMILY, 24, 'bold'),
}

# ---------------------------------------------------------------------------
# CTk appearance
# ---------------------------------------------------------------------------
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

# ---------------------------------------------------------------------------
# Step definitions for the wizard
# ---------------------------------------------------------------------------
STEPS = [
    ('Problema',    'problem'),
    ('Algoritmo',   'algorithm'),
    ('Objetivo',    'objective'),
    ('Parametros',  'params'),
    ('Resultados',  'results'),
]


# ---------------------------------------------------------------------------
# Widget factories
# ---------------------------------------------------------------------------

def primary_button(parent, text, command, width=200, height=42):
    return ctk.CTkButton(
        parent, text=text, command=command,
        width=width, height=height,
        fg_color=COLORS['primary'],
        hover_color=COLORS['primary_hover'],
        text_color=COLORS['text'],
        font=FONTS['button'],
        corner_radius=10,
    )


def secondary_button(parent, text, command, width=160, height=38):
    return ctk.CTkButton(
        parent, text=text, command=command,
        width=width, height=height,
        fg_color=COLORS['surface2'],
        hover_color=COLORS['surface_hover'],
        text_color=COLORS['text_secondary'],
        font=FONTS['button_sm'],
        corner_radius=8,
        border_width=1,
        border_color=COLORS['border'],
    )


def accent_button(parent, text, command, width=200, height=42):
    return ctk.CTkButton(
        parent, text=text, command=command,
        width=width, height=height,
        fg_color=COLORS['secondary'],
        hover_color=COLORS['secondary_hover'],
        text_color=COLORS['bg'],
        font=FONTS['button'],
        corner_radius=10,
    )


def danger_button(parent, text, command, width=140, height=38):
    return ctk.CTkButton(
        parent, text=text, command=command,
        width=width, height=height,
        fg_color=COLORS['error'],
        hover_color=COLORS['error_hover'],
        text_color=COLORS['text'],
        font=FONTS['button_sm'],
        corner_radius=8,
    )


def ghost_button(parent, text, command, width=160, height=38):
    return ctk.CTkButton(
        parent, text=text, command=command,
        width=width, height=height,
        fg_color='transparent',
        hover_color=COLORS['surface_hover'],
        text_color=COLORS['text_muted'],
        font=FONTS['button_sm'],
        corner_radius=8,
    )


def entry_field(parent, textvariable=None, width=220, placeholder=''):
    return ctk.CTkEntry(
        parent, textvariable=textvariable,
        width=width, height=36,
        fg_color=COLORS['surface2'],
        text_color=COLORS['text'],
        placeholder_text_color=COLORS['text_dim'],
        border_color=COLORS['border'],
        font=FONTS['body'],
        corner_radius=8,
        placeholder_text=placeholder,
    )


def make_progress_bar(parent, width=400, height=8):
    return ctk.CTkProgressBar(
        parent, width=width, height=height,
        fg_color=COLORS['surface2'],
        progress_color=COLORS['primary'],
        corner_radius=4,
    )


# ---------------------------------------------------------------------------
# Selectable card (small) — used by ScreenAlgorithm, ScreenObjective
# ---------------------------------------------------------------------------

class CardTheme:
    def __init__(self, badge_color, hover_border):
        self.badge_color  = badge_color
        self.hover_border = hover_border


class CardContent:
    def __init__(self, badge_text, title, description):
        self.badge_text  = badge_text
        self.title       = title
        self.description = description


class CardSpec:
    def __init__(self, content, on_select, theme=None):
        self.content   = content
        self.on_select = on_select
        self.theme     = theme or CardTheme(COLORS['primary'], COLORS['primary'])


def selectable_card(parent, spec, width=230, height=140):
    card = ctk.CTkFrame(
        parent, fg_color=COLORS['card'],
        corner_radius=14, width=width, height=height,
        border_width=1, border_color=COLORS['card_border'],
    )
    card.pack_propagate(False)

    inner = ctk.CTkFrame(card, fg_color='transparent')
    inner.pack(expand=True, fill='both', padx=18, pady=14)

    badge = ctk.CTkLabel(
        inner, text=spec.content.badge_text,
        font=FONTS['small_bold'], text_color=spec.theme.badge_color,
        fg_color=COLORS['surface2'],
        width=44, height=24, corner_radius=6,
    )
    badge.pack(anchor='w', pady=(0, 8))

    ctk.CTkLabel(
        inner, text=spec.content.title,
        font=FONTS['body_bold'], text_color=COLORS['text'],
        anchor='w',
    ).pack(anchor='w', pady=(0, 4))

    ctk.CTkLabel(
        inner, text=spec.content.description,
        font=FONTS['tiny'], text_color=COLORS['text_muted'],
        anchor='w', justify='left',
    ).pack(anchor='w')

    _bind_card_hover(card, inner, badge, spec)
    return card


def _bind_card_hover(card, inner, badge, spec):
    def on_enter(_e):
        card.configure(fg_color=COLORS['card_hover'],
                       border_color=spec.theme.hover_border)

    def on_leave(_e):
        card.configure(fg_color=COLORS['card'],
                       border_color=COLORS['card_border'])

    def on_click(_e):
        spec.on_select()

    for widget in [card, inner, badge] + list(inner.winfo_children()):
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
        widget.bind('<Button-1>', on_click)
        try:
            widget.configure(cursor='arrow')
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Illustrated card (large) — used by ScreenProblem
# Has a canvas illustration area taking ~55% of the card height,
# a title, description, and an arrow indicator.
# ---------------------------------------------------------------------------

def illustrated_card(parent, spec, draw_fn, width=300, height=240):
    card = ctk.CTkFrame(
        parent, fg_color=COLORS['card'],
        corner_radius=16, width=width, height=height,
        border_width=1, border_color=COLORS['card_border'],
    )
    card.pack_propagate(False)
    card.grid_propagate(False)

    # Badge (top-left overlay)
    badge = ctk.CTkLabel(
        card, text=spec.content.badge_text,
        font=FONTS['small_bold'], text_color=spec.theme.badge_color,
        fg_color=COLORS['surface2'],
        width=44, height=24, corner_radius=6,
    )
    badge.place(x=14, y=12)

    # Canvas illustration area
    canvas_h = int(height * 0.52)
    canvas = tk.Canvas(
        card, width=width - 2, height=canvas_h,
        bg=COLORS['card_illus'], highlightthickness=0,
    )
    canvas.pack(fill='x', padx=1, pady=(1, 0))

    # Draw the illustration
    draw_fn(canvas, width - 2, canvas_h)

    # Text area below
    text_frame = ctk.CTkFrame(card, fg_color='transparent')
    text_frame.pack(fill='both', expand=True, padx=16, pady=(8, 12))

    ctk.CTkLabel(
        text_frame, text=spec.content.title,
        font=FONTS['card_title'], text_color=COLORS['text'],
        anchor='w',
    ).pack(anchor='w', pady=(0, 2))

    bottom_row = ctk.CTkFrame(text_frame, fg_color='transparent')
    bottom_row.pack(fill='x', expand=True, anchor='s')

    ctk.CTkLabel(
        bottom_row, text=spec.content.description,
        font=FONTS['tiny'], text_color=COLORS['text_muted'],
        anchor='w', justify='left',
    ).pack(side='left', anchor='sw')

    arrow_lbl = ctk.CTkLabel(
        bottom_row, text='\u2192',
        font=(_FAMILY, 16), text_color=COLORS['text_dim'],
        fg_color=COLORS['surface2'],
        width=30, height=30, corner_radius=15,
    )
    arrow_lbl.pack(side='right', anchor='se')

    # Hover and click
    def on_enter(_e):
        card.configure(fg_color=COLORS['card_hover'],
                       border_color=spec.theme.hover_border)
        arrow_lbl.configure(text_color=COLORS['text'],
                            fg_color=spec.theme.badge_color)

    def on_leave(_e):
        card.configure(fg_color=COLORS['card'],
                       border_color=COLORS['card_border'])
        arrow_lbl.configure(text_color=COLORS['text_dim'],
                            fg_color=COLORS['surface2'])

    def on_click(_e):
        spec.on_select()

    all_widgets = [card, canvas, badge, text_frame, arrow_lbl, bottom_row]
    all_widgets += list(text_frame.winfo_children())
    all_widgets += list(bottom_row.winfo_children())
    for widget in all_widgets:
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
        widget.bind('<Button-1>', on_click)
        try:
            widget.configure(cursor='arrow')
        except Exception:
            pass

    return card


# ---------------------------------------------------------------------------
# Canvas illustration drawing functions
# ---------------------------------------------------------------------------

def draw_continuous_illus(canvas, w, h):
    """Sine-like wave with glow effect."""
    _rng.seed(42)
    points = []
    for i in range(60):
        x = (i / 59) * w
        y = h / 2 + math.sin(i * 0.15) * (h * 0.28) + math.sin(i * 0.08) * (h * 0.12)
        points.append((x, y))

    # Glow layer (thicker, dim)
    if len(points) >= 2:
        flat = [c for p in points for c in p]
        canvas.create_line(*flat, fill='#4338ca', width=6, smooth=True)
        canvas.create_line(*flat, fill='#6366f1', width=3, smooth=True)
        canvas.create_line(*flat, fill='#818cf8', width=1.5, smooth=True)

    # Subtle grid
    for i in range(1, 4):
        y_line = h * i / 4
        canvas.create_line(0, y_line, w, y_line, fill='#1e293b', dash=(2, 6))


def draw_knapsack_illus(canvas, w, h):
    """Stacked item blocks with varying sizes."""
    _rng.seed(7)
    colors = ['#6366f1', '#818cf8', '#a5b4fc', '#4f46e5', '#6366f1']
    cx, cy = w / 2, h / 2
    for i in range(5):
        bw = 30 + _rng.randint(10, 50)
        bh = 16 + _rng.randint(4, 14)
        x0 = cx - bw / 2 + _rng.randint(-20, 20)
        y0 = cy - 40 + i * 20
        canvas.create_rectangle(
            x0, y0, x0 + bw, y0 + bh,
            fill=colors[i % len(colors)], outline=COLORS['card_border'], width=1,
        )

    # Capacity bar at bottom
    bar_y = h - 20
    canvas.create_rectangle(30, bar_y, w - 30, bar_y + 6,
                            fill=COLORS['surface2'], outline='')
    canvas.create_rectangle(30, bar_y, 30 + (w - 60) * 0.65, bar_y + 6,
                            fill='#22d3ee', outline='')


def draw_categorical_illus(canvas, w, h):
    """Scattered dots in color groups with faint grid."""
    _rng.seed(13)
    cat_colors = ['#818cf8', '#22d3ee', '#34d399']
    for i in range(1, 4):
        canvas.create_line(0, h * i / 4, w, h * i / 4, fill='#1e293b', dash=(2, 6))
    for i in range(1, 4):
        canvas.create_line(w * i / 4, 0, w * i / 4, h, fill='#1e293b', dash=(2, 6))

    for cat_i, color in enumerate(cat_colors):
        cx_base = w * (0.25 + cat_i * 0.25)
        cy_base = h * 0.5
        for _ in range(8):
            ox = _rng.gauss(0, w * 0.06)
            oy = _rng.gauss(0, h * 0.1)
            r = 3
            canvas.create_oval(
                cx_base + ox - r, cy_base + oy - r,
                cx_base + ox + r, cy_base + oy + r,
                fill=color, outline='',
            )


def draw_tsp_illus(canvas, w, h):
    """Cities connected by dashed route lines."""
    _rng.seed(21)
    cities = [(w * 0.2, h * 0.3), (w * 0.45, h * 0.15), (w * 0.75, h * 0.25),
              (w * 0.8, h * 0.6), (w * 0.55, h * 0.75), (w * 0.25, h * 0.65)]

    # Route lines (dashed, glow)
    for i in range(len(cities)):
        x1, y1 = cities[i]
        x2, y2 = cities[(i + 1) % len(cities)]
        canvas.create_line(x1, y1, x2, y2, fill='#4338ca', width=2, dash=(4, 4))
        canvas.create_line(x1, y1, x2, y2, fill='#818cf8', width=1, dash=(4, 4))

    # City dots
    for i, (cx, cy) in enumerate(cities):
        r = 5
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                           fill='#22d3ee', outline=COLORS['card_illus'], width=2)

    # Label A and B
    canvas.create_text(cities[0][0] - 12, cities[0][1] - 12,
                       text='A', fill='#f87171', font=(_FAMILY, 9, 'bold'))
    canvas.create_text(cities[2][0] + 12, cities[2][1] - 12,
                       text='B', fill='#34d399', font=(_FAMILY, 9, 'bold'))


def draw_ga_illus(canvas, w, h):
    """Chromosome bars with crossover visualization."""
    colors_a = ['#6366f1', '#818cf8', '#6366f1', '#4f46e5', '#818cf8',
                '#6366f1', '#818cf8', '#4f46e5']
    colors_b = ['#06b6d4', '#22d3ee', '#06b6d4', '#0891b2', '#22d3ee',
                '#06b6d4', '#22d3ee', '#0891b2']
    seg_w = (w - 60) / 8
    # Parent A
    for i, c in enumerate(colors_a):
        x0 = 30 + i * seg_w
        canvas.create_rectangle(x0, h * 0.2, x0 + seg_w - 2, h * 0.2 + 14,
                                fill=c, outline='')
    # Parent B
    for i, c in enumerate(colors_b):
        x0 = 30 + i * seg_w
        canvas.create_rectangle(x0, h * 0.42, x0 + seg_w - 2, h * 0.42 + 14,
                                fill=c, outline='')
    # Crossover arrows
    cx = w / 2
    canvas.create_line(cx, h * 0.36, cx, h * 0.58, fill='#f59e0b', width=1.5,
                       arrow='last', arrowshape=(6, 8, 4))
    canvas.create_line(cx - 20, h * 0.38, cx + 20, h * 0.56,
                       fill='#f59e0b', width=1, dash=(3, 3))
    # Child
    child_colors = colors_a[:4] + colors_b[4:]
    for i, c in enumerate(child_colors):
        x0 = 30 + i * seg_w
        canvas.create_rectangle(x0, h * 0.65, x0 + seg_w - 2, h * 0.65 + 14,
                                fill=c, outline='')


def draw_pso_illus(canvas, w, h):
    """Particles with velocity arrows converging toward a point."""
    _rng.seed(17)
    target = (w * 0.6, h * 0.4)
    # Target glow
    for r in [18, 12, 6]:
        alpha_color = '#4f46e5' if r > 12 else '#6366f1' if r > 6 else '#818cf8'
        canvas.create_oval(target[0] - r, target[1] - r,
                           target[0] + r, target[1] + r,
                           fill=alpha_color, outline='')
    # Particles
    for _ in range(12):
        px = _rng.uniform(20, w - 20)
        py = _rng.uniform(15, h - 15)
        dx = (target[0] - px) * 0.15
        dy = (target[1] - py) * 0.15
        canvas.create_oval(px - 3, py - 3, px + 3, py + 3,
                           fill='#22d3ee', outline='')
        canvas.create_line(px, py, px + dx, py + dy,
                           fill='#22d3ee', width=1, arrow='last',
                           arrowshape=(4, 5, 3))


def draw_aco_illus(canvas, w, h):
    """Pheromone trails between nodes."""
    _rng.seed(31)
    nodes = [(w * 0.15, h * 0.5), (w * 0.35, h * 0.2), (w * 0.55, h * 0.7),
             (w * 0.75, h * 0.3), (w * 0.85, h * 0.6)]
    # Trails with varying thickness (pheromone intensity)
    trails = [(0, 1, 3), (1, 3, 4), (3, 4, 2), (0, 2, 2.5), (2, 4, 1.5), (1, 2, 1)]
    for a, b, thickness in trails:
        x1, y1 = nodes[a]
        x2, y2 = nodes[b]
        canvas.create_line(x1, y1, x2, y2, fill='#4f46e5',
                           width=thickness + 1)
        canvas.create_line(x1, y1, x2, y2, fill='#818cf8',
                           width=max(1, thickness - 0.5))
    for cx, cy in nodes:
        canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                           fill='#22d3ee', outline=COLORS['card_illus'], width=2)


def draw_ais_illus(canvas, w, h):
    """Antibody/cell shapes with clone and mutation."""
    _rng.seed(41)
    # Central cell
    cx, cy = w * 0.35, h * 0.45
    for r in [22, 16, 10]:
        c = '#4f46e5' if r > 16 else '#6366f1' if r > 10 else '#818cf8'
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=c, outline='')
    # Clone arrows
    clones = [(w * 0.6, h * 0.25), (w * 0.65, h * 0.55), (w * 0.55, h * 0.75)]
    for tx, ty in clones:
        canvas.create_line(cx + 16, cy, tx - 8, ty,
                           fill='#f59e0b', width=1, dash=(3, 3),
                           arrow='last', arrowshape=(4, 5, 3))
        canvas.create_oval(tx - 7, ty - 7, tx + 7, ty + 7,
                           fill='#34d399', outline='')
    # Mutation marker
    mx, my = clones[1]
    canvas.create_text(mx + 14, my - 8, text='~', fill='#f87171',
                       font=(_FAMILY, 11, 'bold'))


def draw_de_illus(canvas, w, h):
    """Differential vectors and trial point."""
    _rng.seed(55)
    pts = {'x1': (w * 0.2, h * 0.6), 'x2': (w * 0.5, h * 0.2),
           'x3': (w * 0.75, h * 0.55)}
    # Points
    for name, (px, py) in pts.items():
        canvas.create_oval(px - 4, py - 4, px + 4, py + 4,
                           fill='#818cf8', outline='')
        canvas.create_text(px, py - 12, text=name, fill=COLORS['text_muted'],
                           font=(_FAMILY, 8))
    # Difference vector x2-x3
    x2, y2 = pts['x2']
    x3, y3 = pts['x3']
    dx, dy = x2 - x3, y2 - y3
    canvas.create_line(x3, y3, x2, y2, fill='#22d3ee', width=1.5,
                       arrow='last', arrowshape=(5, 7, 3))
    # Trial vector from x1
    x1, y1 = pts['x1']
    tx, ty = x1 + dx * 0.6, y1 + dy * 0.6
    canvas.create_line(x1, y1, tx, ty, fill='#f59e0b', width=1.5,
                       arrow='last', arrowshape=(5, 7, 3), dash=(4, 3))
    # Trial point
    canvas.create_oval(tx - 5, ty - 5, tx + 5, ty + 5,
                       fill='#34d399', outline='')
    canvas.create_text(tx, ty - 12, text='trial', fill='#34d399',
                       font=(_FAMILY, 8))


def draw_maximize_illus(canvas, w, h):
    """Ascending bar chart with upward arrow."""
    bars = [0.2, 0.35, 0.3, 0.5, 0.65, 0.6, 0.8, 0.95]
    bar_w = (w - 60) / len(bars)
    base_y = h * 0.85
    for i, frac in enumerate(bars):
        x0 = 30 + i * bar_w
        bh = frac * h * 0.65
        color = '#10b981' if i >= 6 else '#1e4d3a'
        canvas.create_rectangle(x0, base_y - bh, x0 + bar_w - 3, base_y,
                                fill=color, outline='')
    # Upward arrow
    ax = w * 0.8
    canvas.create_line(ax, h * 0.5, ax, h * 0.15, fill='#34d399', width=2,
                       arrow='last', arrowshape=(8, 10, 5))


def draw_minimize_illus(canvas, w, h):
    """Descending curve converging to minimum."""
    points = []
    for i in range(50):
        t = i / 49
        x = 30 + t * (w - 60)
        y = h * 0.2 + (h * 0.55) * (1 - math.exp(-3 * t))
        points.append((x, y))

    if len(points) >= 2:
        flat = [c for p in points for c in p]
        canvas.create_line(*flat, fill='#0891b2', width=4, smooth=True)
        canvas.create_line(*flat, fill='#22d3ee', width=2, smooth=True)

    # Minimum marker
    mx, my = points[-1]
    canvas.create_oval(mx - 6, my - 6, mx + 6, my + 6,
                       fill='#22d3ee', outline=COLORS['card_illus'], width=2)
    canvas.create_text(mx, my + 14, text='min', fill='#22d3ee',
                       font=(_FAMILY, 8))


# Map illustration functions by key
PROBLEM_ILLUSTRATIONS = {
    'continuous':  draw_continuous_illus,
    'knapsack':    draw_knapsack_illus,
    'categorical': draw_categorical_illus,
    'tsp':         draw_tsp_illus,
}

ALGORITHM_ILLUSTRATIONS = {
    'ga':  draw_ga_illus,
    'pso': draw_pso_illus,
    'aco': draw_aco_illus,
    'ais': draw_ais_illus,
    'de':  draw_de_illus,
}


# ---------------------------------------------------------------------------
# Styled combobox
# ---------------------------------------------------------------------------

def styled_combobox(parent, variable, values, width=280):
    return ctk.CTkComboBox(
        parent, variable=variable, values=values,
        width=width, height=34,
        fg_color=COLORS['surface2'],
        border_color=COLORS['border'],
        button_color=COLORS['primary'],
        button_hover_color=COLORS['primary_hover'],
        dropdown_fg_color=COLORS['surface2'],
        dropdown_hover_color=COLORS['surface_hover'],
        dropdown_text_color=COLORS['text'],
        text_color=COLORS['text'],
        font=FONTS['small'],
        state='readonly',
        corner_radius=8,
    )


# ---------------------------------------------------------------------------
# Stat card — for results screen metric display
# ---------------------------------------------------------------------------

def stat_card(parent, title, value_var, accent_color=None, width=180):
    accent = accent_color or COLORS['primary']
    card = ctk.CTkFrame(
        parent, fg_color=COLORS['surface'],
        corner_radius=10, width=width, height=80,
        border_width=1, border_color=COLORS['border'],
    )
    card.pack_propagate(False)

    inner = ctk.CTkFrame(card, fg_color='transparent')
    inner.pack(expand=True, fill='both', padx=14, pady=10)

    ctk.CTkLabel(
        inner, text=title,
        font=FONTS['tiny'], text_color=COLORS['text_muted'],
    ).pack(anchor='w')

    ctk.CTkLabel(
        inner, textvariable=value_var,
        font=FONTS['stat_big'], text_color=COLORS['text'],
        wraplength=width - 30,
    ).pack(anchor='w', pady=(2, 4))

    # Accent bar at bottom
    ctk.CTkFrame(
        inner, fg_color=accent,
        height=3, corner_radius=2,
    ).pack(fill='x', side='bottom')

    return card


# ---------------------------------------------------------------------------
# matplotlib Figure + canvas pair (used 3x by ScreenResults)
# ---------------------------------------------------------------------------
def make_figure_canvas(parent):
    """Returns (Figure, FigureCanvasTkAgg) styled for the dark theme.
    The canvas is already packed; the caller only needs to retain the figure."""
    fig = Figure(figsize=(9.2, 3.6), dpi=120, facecolor=COLORS['bg'])
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack(fill='both', expand=True)
    return fig, canvas


# ---------------------------------------------------------------------------
# Style matplotlib axes to match the dark theme
# ---------------------------------------------------------------------------
def style_ax(ax):
    ax.set_facecolor(COLORS['surface'])
    ax.tick_params(colors=COLORS['text_muted'], labelsize=8,
                   length=3, width=0.6, pad=4)
    # Hide top/right spines for a cleaner look; keep bottom/left thin
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_edgecolor(COLORS['border_light'])
    ax.spines['left'].set_edgecolor(COLORS['border_light'])
    ax.spines['bottom'].set_linewidth(0.8)
    ax.spines['left'].set_linewidth(0.8)
    ax.xaxis.label.set_color(COLORS['text_secondary'])
    ax.yaxis.label.set_color(COLORS['text_secondary'])
    ax.title.set_color(COLORS['text'])
    ax.grid(True, color=COLORS['chart_grid'], alpha=0.4,
            linewidth=0.6, linestyle='--')
    ax.set_axisbelow(True)
