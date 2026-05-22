import queue
import threading
import time
import customtkinter as ctk

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Patch

from gui.widgets import (COLORS, FONTS, primary_button, danger_button,
                          secondary_button, ghost_button, accent_button,
                          make_progress_bar, style_ax, stat_card)
from config.labels import PROBLEM_LABELS, ALGORITHM_SHORT

# Category colors (up to 10)
_CAT_COLORS = ['#818cf8', '#f87171', '#34d399', '#fb923c', '#a78bfa',
               '#f472b6', '#22d3ee', '#fbbf24', '#6366f1', '#e879f9']


# ---------------------------------------------------------------------------
# Problem-specific visualization helpers
# ---------------------------------------------------------------------------

def _draw_continuous(ax, problem, sol):
    lb, ub = problem.bounds[0]
    if problem.dimensions == 1:
        xs = np.linspace(lb, ub, 300)
        ys = [problem.evaluate(np.array([x])) for x in xs]
        ax.plot(xs, ys, color=COLORS['chart_line1'], linewidth=1.8, alpha=0.9)
        ax.fill_between(xs, ys, alpha=0.08, color=COLORS['chart_fill1'])
        best_y = problem.evaluate(sol)
        ax.scatter([sol[0]], [best_y], color='#f87171', s=80, zorder=5,
                   label='Mejor', edgecolors='white', linewidths=1.5)
        ax.set_xlabel('x1', fontsize=8)
        ax.set_ylabel('f(x1)', fontsize=8)
        ax.set_title(f'f(x)  |  Mejor: x1 = {sol[0]:.5f}', fontsize=9)
        ax.legend(fontsize=7, facecolor=COLORS['surface2'],
                  labelcolor=COLORS['text'], edgecolor=COLORS['border'])
    else:
        lb2, ub2 = problem.bounds[1]
        x1s = np.linspace(lb, ub, 60)
        x2s = np.linspace(lb2, ub2, 60)
        X1, X2 = np.meshgrid(x1s, x2s)
        Z = np.vectorize(lambda a, b: problem.evaluate(np.array([a, b])))(X1, X2)
        cs = ax.contourf(X1, X2, Z, levels=25, cmap='cool')
        ax.figure.colorbar(cs, ax=ax, pad=0.02).ax.tick_params(
            labelsize=6, colors=COLORS['text_muted'])
        ax.scatter([sol[0]], [sol[1]], color='#f87171', s=100, zorder=5,
                   marker='*', label='Mejor', edgecolors='white', linewidths=1)
        ax.set_xlabel('x1', fontsize=8)
        ax.set_ylabel('x2', fontsize=8)
        ax.set_title(f'Contorno f(x1,x2)  |  Mejor: ({sol[0]:.3f}, {sol[1]:.3f})',
                     fontsize=9)
        ax.legend(fontsize=7, facecolor=COLORS['surface2'],
                  labelcolor=COLORS['text'], edgecolor=COLORS['border'])


def _draw_knapsack(ax, problem, sol):
    n = problem.n
    selected = [round(v) == 1 for v in sol]
    colors = [COLORS['success'] if s else COLORS['text_dim'] for s in selected]
    labels = [f'Item {i+1}' for i in range(n)]
    values = list(problem._values)

    ax.barh(labels, values, color=colors,
            edgecolor=COLORS['border'], linewidth=0.5)
    ax.set_xlabel('Valor', fontsize=8)

    w_used  = float(np.dot(problem._weights, np.array(sol, dtype=float)))
    v_total = float(np.dot(problem._values,  np.array(sol, dtype=float)))
    ax.set_title(
        f'Items seleccionados  |  Peso: {w_used:.1f} / {problem.W:.1f}  |  '
        f'Valor total: {v_total:.1f}',
        fontsize=9)

    handles = [Patch(color=COLORS['success'], label='Seleccionado'),
               Patch(color=COLORS['text_dim'], label='No seleccionado')]
    ax.legend(handles=handles, fontsize=7,
              facecolor=COLORS['surface2'], labelcolor=COLORS['text'],
              edgecolor=COLORS['border'])


def _draw_categorical(ax, problem, sol):
    if problem.dimensions == 1:
        lb, ub = problem._cont_bounds[0]
        xs = np.linspace(lb, ub, 200)
        for k in range(problem.num_options):
            d_val = problem.option_values[k]
            ys = [problem.evaluate(np.array([x, float(k)])) for x in xs]
            ax.plot(xs, ys, color=_CAT_COLORS[k % len(_CAT_COLORS)],
                    linewidth=1.4, label=f'Cat {k+1}  (D={d_val})')
        best_cat = int(round(sol[-1])) % problem.num_options
        best_y   = problem.evaluate(sol)
        ax.scatter([sol[0]], [best_y], color='white', s=100, zorder=5,
                   marker='*', label='Mejor', edgecolors=COLORS['primary'],
                   linewidths=1.5)
        ax.set_xlabel('x1', fontsize=8)
        ax.set_ylabel('f(x1, D)', fontsize=8)
        ax.set_title(f'f(x) por categoria  |  Mejor: Cat {best_cat+1}'
                     f'  x1={sol[0]:.4f}', fontsize=9)
        ax.legend(fontsize=7, facecolor=COLORS['surface2'],
                  labelcolor=COLORS['text'], ncol=2, edgecolor=COLORS['border'])
    else:
        ax.text(0.5, 0.5, 'Visualizacion 2D categorica\nno disponible',
                transform=ax.transAxes, ha='center', va='center',
                color=COLORS['text_muted'], fontsize=10)
        ax.set_title('Categorica 2D', fontsize=9)


def _draw_tsp(ax, problem, sol):
    coords = problem.coords
    route = [int(round(c)) % problem.n for c in sol]

    for i in range(len(route)):
        a = coords[route[i]]
        b = coords[route[(i + 1) % len(route)]]
        progress = i / max(len(route) - 1, 1)
        color = COLORS['chart_line1'] if progress < 0.5 else COLORS['chart_line2']
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color,
                linewidth=1.2, alpha=0.7)

    ax.scatter(coords[:, 0], coords[:, 1], color=COLORS['chart_line2'],
               s=35, zorder=3, edgecolors=COLORS['surface'], linewidths=0.8)

    if problem.n <= 20:
        for i, (x, y) in enumerate(coords):
            ax.annotate(str(i), (x, y), textcoords='offset points',
                        xytext=(4, 4), fontsize=6, color=COLORS['text_muted'])

    start = coords[route[0]]
    ax.scatter([start[0]], [start[1]], color='#f87171', s=90, zorder=5,
               label='Inicio', edgecolors='white', linewidths=1.5)

    dist = problem.evaluate(sol)
    ax.set_title(f'Ruta TSP  |  Distancia: {dist:.1f}  |  n = {problem.n} ciudades',
                 fontsize=9)
    ax.set_aspect('equal', adjustable='datalim')
    ax.set_xlabel('x', fontsize=8)
    ax.set_ylabel('y', fontsize=8)
    ax.legend(fontsize=7, facecolor=COLORS['surface2'],
              labelcolor=COLORS['text'], edgecolor=COLORS['border'])


# ---------------------------------------------------------------------------
# ScreenResults
# ---------------------------------------------------------------------------

class ScreenResults(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS['bg'])
        self._app = app
        self._cancel_event: threading.Event | None = None
        self._result_queue: queue.Queue | None = None
        self._total = 100
        self._build()

    def _build(self):
        # ── Title row ──
        top = ctk.CTkFrame(self, fg_color='transparent')
        top.pack(fill='x', padx=32, pady=(14, 0))

        top_left = ctk.CTkFrame(top, fg_color='transparent')
        top_left.pack(side='left')

        self._title_lbl = ctk.CTkLabel(
            top_left, text='Ejecucion',
            font=FONTS['heading'], text_color=COLORS['text'],
        )
        self._title_lbl.pack(anchor='w')

        self._func_lbl = ctk.CTkLabel(
            top_left, text='',
            font=FONTS['tiny'], text_color=COLORS['text_secondary'],
        )
        self._func_lbl.pack(anchor='w')

        # Top-right action buttons: Cancelar + Nuevo Experimento side by side
        self._new_btn = accent_button(
            top, 'Nuevo Experimento',
            lambda: self._app.show_screen('problem'), width=180, height=34,
        )
        self._new_btn.pack(side='right')

        self._cancel_btn = danger_button(
            top, 'Cancelar', self._cancel, width=110, height=34,
        )
        self._cancel_btn.pack(side='right', padx=(0, 10))

        # ── Stat cards row ──
        stats_row = ctk.CTkFrame(self, fg_color='transparent')
        stats_row.pack(fill='x', padx=32, pady=(10, 0))

        self._stat_vars = {
            'fitness':  ctk.StringVar(value='-'),
            'fx':       ctk.StringVar(value='-'),
            'iters':    ctk.StringVar(value='-'),
            'status':   ctk.StringVar(value='Esperando'),
        }

        stat_card(stats_row, 'Fitness', self._stat_vars['fitness'],
                  COLORS['primary']).pack(side='left', padx=(0, 8), fill='y')
        stat_card(stats_row, 'f(x)', self._stat_vars['fx'],
                  COLORS['secondary']).pack(side='left', padx=(0, 8), fill='y')
        stat_card(stats_row, 'Iteraciones', self._stat_vars['iters'],
                  COLORS['accent_warm']).pack(side='left', padx=(0, 8), fill='y')

        # Progress in a stat-like card
        prog_card = ctk.CTkFrame(
            stats_row, fg_color=COLORS['surface'],
            corner_radius=10, width=280, height=80,
            border_width=1, border_color=COLORS['border'],
        )
        prog_card.pack(side='left', fill='both', expand=True)
        prog_card.pack_propagate(False)

        prog_inner = ctk.CTkFrame(prog_card, fg_color='transparent')
        prog_inner.pack(expand=True, fill='both', padx=14, pady=10)

        prog_top = ctk.CTkFrame(prog_inner, fg_color='transparent')
        prog_top.pack(fill='x')

        self._progress_lbl = ctk.CTkLabel(
            prog_top, text='Esperando...',
            font=FONTS['tiny'], text_color=COLORS['text_secondary'],
        )
        self._progress_lbl.pack(side='left')

        self._pct_lbl = ctk.CTkLabel(
            prog_top, text='0%',
            font=FONTS['body_bold'], text_color=COLORS['primary'],
        )
        self._pct_lbl.pack(side='right')

        self._progress = make_progress_bar(prog_inner, height=6)
        self._progress.pack(fill='x', pady=(6, 0))
        self._progress.set(0)

        ctk.CTkLabel(
            prog_inner, textvariable=self._stat_vars['status'],
            font=FONTS['tiny'], text_color=COLORS['text_muted'],
        ).pack(anchor='w', pady=(4, 0))

        # ── Tabview for charts ──
        self._tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS['surface'],
            segmented_button_fg_color=COLORS['surface2'],
            segmented_button_selected_color=COLORS['primary'],
            segmented_button_selected_hover_color=COLORS['primary_hover'],
            segmented_button_unselected_color=COLORS['surface2'],
            segmented_button_unselected_hover_color=COLORS['surface_hover'],
            text_color=COLORS['text'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border'],
        )
        self._tabview.pack(fill='both', expand=True, padx=32, pady=(8, 0))

        tab_conv = self._tabview.add('Convergencia')
        tab_sol  = self._tabview.add('Solucion')
        tab_evo  = self._tabview.add('Evolucion')

        self._fig = Figure(figsize=(9.2, 3.6), dpi=120, facecolor=COLORS['bg'])
        self._conv_canvas = FigureCanvasTkAgg(self._fig, master=tab_conv)
        self._conv_canvas.get_tk_widget().pack(fill='both', expand=True)

        self._viz_fig = Figure(figsize=(9.2, 3.6), dpi=120, facecolor=COLORS['bg'])
        self._viz_canvas = FigureCanvasTkAgg(self._viz_fig, master=tab_sol)
        self._viz_canvas.get_tk_widget().pack(fill='both', expand=True)

        self._live_fig = Figure(figsize=(9.2, 3.6), dpi=120, facecolor=COLORS['bg'])
        self._live_canvas = FigureCanvasTkAgg(self._live_fig, master=tab_evo)
        self._live_canvas.get_tk_widget().pack(fill='both', expand=True)
        self._last_live_t = 0.0

        # ── Solution text panel ──
        sol_frame = ctk.CTkFrame(
            self, fg_color=COLORS['surface'],
            corner_radius=10, border_width=1, border_color=COLORS['border'],
        )
        sol_frame.pack(fill='x', padx=32, pady=(6, 0))

        sol_inner = ctk.CTkFrame(sol_frame, fg_color='transparent')
        sol_inner.pack(fill='x', padx=16, pady=10)

        ctk.CTkLabel(
            sol_inner, text='Mejor solucion encontrada',
            font=FONTS['tiny'], text_color=COLORS['text_muted'],
        ).pack(anchor='w')

        self._sol_var = ctk.StringVar(value='-')
        self._sol_val_lbl = ctk.CTkLabel(
            sol_inner, textvariable=self._sol_var,
            font=FONTS['body_bold'], text_color=COLORS['text'],
            wraplength=800, anchor='w', justify='left',
        )
        self._sol_val_lbl.pack(anchor='w', pady=(2, 0))


    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def start_run(self, runner, total_iterations: int):
        p = PROBLEM_LABELS.get(self._app.state.get('problem', ''), '?')
        a = ALGORITHM_SHORT.get(self._app.state.get('algorithm', ''), '?')
        obj = 'Max' if self._app.state.get('maximize') else 'Min'
        self._title_lbl.configure(text=f'{p}  /  {a}  ({obj})')

        self._total = total_iterations
        prob_inst = self._app.state.get('problem_instance')
        prob_type = self._app.state.get('problem', '')
        if prob_inst is not None:
            if prob_type == 'continuous':
                func_text = f'f(x) = {prob_inst.expression_str}  ({prob_inst.dimensions}D)'
            elif prob_type == 'knapsack':
                func_text = f'n = {prob_inst.n} objetos  |  W = {prob_inst.W}'
            elif prob_type == 'categorical':
                func_text = (f'f(x, D) = {prob_inst.expression_str}'
                             f'  ({prob_inst.num_options} opciones)')
            elif prob_type == 'tsp':
                func_text = f'n = {prob_inst.n} ciudades'
            else:
                func_text = ''
        else:
            func_text = ''
        self._func_lbl.configure(text=func_text)

        self._progress.set(0)
        self._progress.configure(progress_color=COLORS['primary'])
        self._pct_lbl.configure(text='0%', text_color=COLORS['primary'])
        self._progress_lbl.configure(text='Iniciando...')
        self._cancel_btn.configure(state='normal')

        for key in self._stat_vars:
            self._stat_vars[key].set('-')
        self._stat_vars['status'].set('Ejecutando...')
        self._sol_var.set('-')

        self._fig.clear()
        self._conv_canvas.draw()
        self._viz_fig.clear()
        self._viz_canvas.draw()
        self._last_live_t = 0.0

        self._live_fig.clear()
        self._live_fig.patch.set_facecolor(COLORS['bg'])
        live_ax = self._live_fig.add_subplot(111)
        style_ax(live_ax)
        prob = self._app.state.get('problem', '')
        if prob == 'tsp':
            live_ax.text(0.5, 0.5, 'Iniciando simulacion TSP...',
                         transform=live_ax.transAxes, ha='center', va='center',
                         color=COLORS['text_muted'], fontsize=11)
            self._tabview.set('Evolucion')
        else:
            live_ax.text(0.5, 0.5, 'Solo disponible para TSP',
                         transform=live_ax.transAxes, ha='center', va='center',
                         color=COLORS['text_muted'], fontsize=11)
            self._tabview.set('Convergencia')
        self._live_canvas.draw()

        self._cancel_event  = threading.Event()
        self._result_queue  = queue.Queue()
        runner.start(self._result_queue, self._cancel_event)
        self._app.root.after(80, self._check_queue)

    # ------------------------------------------------------------------
    # Queue polling
    # ------------------------------------------------------------------

    def _check_queue(self):
        try:
            while True:
                msg = self._result_queue.get_nowait()
                if msg['type'] == 'progress':
                    self._update_progress(msg)
                elif msg['type'] == 'done':
                    self._show_results(msg)
                    return
                elif msg['type'] == 'error':
                    self._progress_lbl.configure(text=f'Error: {msg["message"]}')
                    self._cancel_btn.configure(state='disabled')
                    self._stat_vars['status'].set('Error')
                    return
        except queue.Empty:
            pass
        self._app.root.after(80, self._check_queue)

    def _update_progress(self, msg: dict):
        pct = msg['iteration'] / max(msg['total'], 1)
        self._progress.set(pct)
        self._pct_lbl.configure(text=f'{pct * 100:.0f}%')
        self._progress_lbl.configure(
            text=f"Iteracion {msg['iteration']} de {msg['total']}")

        if (self._app.state.get('problem') == 'tsp'
                and msg.get('best_solution') is not None):
            now = time.monotonic()
            if now - self._last_live_t >= 0.25:
                self._last_live_t = now
                self._redraw_live_tsp(msg['best_solution'], msg['iteration'])

    def _redraw_live_tsp(self, sol, iteration: int):
        prob = self._app.state.get('problem_instance')
        if prob is None:
            return
        self._live_fig.clear()
        self._live_fig.patch.set_facecolor(COLORS['bg'])
        ax = self._live_fig.add_subplot(111)
        style_ax(ax)
        try:
            _draw_tsp(ax, prob, sol)
            dist = prob.evaluate(sol)
            ax.set_title(
                f'Iter {iteration}  |  Distancia: {dist:.1f}  |  n = {prob.n} ciudades',
                fontsize=9)
            ax.title.set_color(COLORS['text'])
        except Exception:
            pass
        self._live_fig.tight_layout(pad=1.2)
        self._live_canvas.draw_idle()

    # ------------------------------------------------------------------
    # Final results
    # ------------------------------------------------------------------

    def _show_results(self, msg: dict):
        self._cancel_btn.configure(state='disabled')
        self._progress.set(1.0)
        self._progress.configure(progress_color=COLORS['success'])
        self._pct_lbl.configure(text='100%', text_color=COLORS['success'])

        history   = msg['history']
        converged = msg['converged']
        cancelled = msg['cancelled']

        self._draw_charts(history.get_segments())
        self._draw_viz(history)
        self._fill_panel(history, converged, cancelled)
        self._tabview.set('Solucion')

        if converged:
            self._progress_lbl.configure(text='Convergencia alcanzada')
            self._stat_vars['status'].set('Convergio')
        elif cancelled:
            self._progress_lbl.configure(text='Cancelado por el usuario')
            self._stat_vars['status'].set('Cancelado')
        else:
            self._progress_lbl.configure(text='Ejecucion completada')
            self._stat_vars['status'].set('Completado')

    def _draw_charts(self, segments: list):
        self._fig.clear()
        self._fig.patch.set_facecolor(COLORS['bg'])
        axes = self._fig.subplots(2, 2)

        for ax, seg in zip(axes.flat, segments):
            style_ax(ax)
            ax.set_title(seg['title'], color=COLORS['text'],
                         fontsize=9.5, pad=8, fontweight='bold', loc='left')

            if seg['iterations']:
                iters = seg['iterations']
                best  = seg['best_so_far']
                avg   = seg['avg_fitness']

                # Use baseline = min(best) so fill stays inside the data range
                baseline = min(best)
                ax.fill_between(iters, best, baseline,
                                alpha=0.12, color=COLORS['chart_fill1'],
                                linewidth=0)
                ax.plot(iters, avg,
                        color=COLORS['chart_line2'], linewidth=1.2,
                        alpha=0.75, label='Promedio',
                        solid_capstyle='round', solid_joinstyle='round')
                ax.plot(iters, best,
                        color=COLORS['chart_line1'], linewidth=2.0,
                        label='Mejor', alpha=1.0,
                        solid_capstyle='round', solid_joinstyle='round')

                # End-of-series marker emphasises convergence point
                ax.scatter([iters[-1]], [best[-1]],
                           color=COLORS['chart_line1'], s=22, zorder=5,
                           edgecolors=COLORS['bg'], linewidths=1.0)

                ax.set_xlabel('Iteracion', fontsize=8)
                ax.set_ylabel('Fitness',   fontsize=8)
                ax.margins(x=0.02, y=0.08)

                leg = ax.legend(fontsize=7.5, facecolor=COLORS['surface2'],
                                labelcolor=COLORS['text'],
                                edgecolor=COLORS['border'],
                                framealpha=0.9, loc='best',
                                handlelength=1.6, borderpad=0.5)
                leg.get_frame().set_linewidth(0.6)
            else:
                ax.text(0.5, 0.5, 'Sin datos', transform=ax.transAxes,
                        ha='center', va='center', color=COLORS['text_dim'],
                        fontsize=10, style='italic')
                ax.set_xticks([])
                ax.set_yticks([])

        self._fig.tight_layout(pad=1.6, h_pad=2.0, w_pad=2.0)
        self._conv_canvas.draw()

    def _draw_viz(self, history):
        prob_type = self._app.state.get('problem', '')
        prob      = self._app.state.get('problem_instance')
        sol       = history.best_solution
        if prob is None or sol is None:
            return

        self._viz_fig.clear()
        self._viz_fig.patch.set_facecolor(COLORS['bg'])
        ax = self._viz_fig.add_subplot(111)
        style_ax(ax)

        dispatch = {
            'continuous':  _draw_continuous,
            'knapsack':    _draw_knapsack,
            'categorical': _draw_categorical,
            'tsp':         _draw_tsp,
        }
        fn = dispatch.get(prob_type)
        if fn:
            try:
                fn(ax, prob, sol)
            except Exception as exc:
                ax.text(0.5, 0.5, f'Error al generar visualizacion:\n{exc}',
                        transform=ax.transAxes, ha='center', va='center',
                        color=COLORS['text_muted'], fontsize=9, wrap=True)

        self._viz_fig.tight_layout(pad=1.2)
        self._viz_canvas.draw()

    def _fill_panel(self, history, converged: bool, cancelled: bool):
        sol       = history.best_solution
        prob      = self._app.state.get('problem', '')
        prob_inst = self._app.state.get('problem_instance')

        if prob == 'continuous' and sol is not None:
            sol_text = '  '.join(f'x{i+1} = {v:.6f}' for i, v in enumerate(sol))
        elif prob == 'knapsack' and sol is not None:
            selected = [i + 1 for i, v in enumerate(sol) if round(v) == 1]
            vec      = ''.join(str(int(round(v))) for v in sol)
            sol_text = f'[{vec}]  Items: {selected}'
        elif prob == 'categorical' and sol is not None:
            parts    = [f'x{i+1} = {sol[i]:.4f}' for i in range(len(sol) - 1)]
            cat_idx  = int(round(sol[-1])) % (prob_inst.num_options if prob_inst else 1)
            d_val    = prob_inst.option_values[cat_idx] if prob_inst else '?'
            sol_text = '  '.join(parts) + f'  Cat {cat_idx+1} (D={d_val})'
        elif prob == 'tsp' and sol is not None:
            n     = prob_inst.n if prob_inst else len(sol)
            route = [int(round(c)) % n for c in sol]
            if n <= 10:
                sol_text = ' > '.join(str(c) for c in route) + f' > {route[0]}'
            else:
                head = ' > '.join(str(c) for c in route[:5])
                sol_text = f'{head} > ...  ({n} ciudades)'
        else:
            sol_text = str(sol)

        self._sol_var.set(sol_text)
        self._sol_val_lbl.configure(
            wraplength=max(self._sol_val_lbl.winfo_width(), 400))
        self._stat_vars['fitness'].set(f'{history.best_fitness:.4f}')
        self._stat_vars['fx'].set(f'{history.best_fx:.4f}')

        if cancelled:
            self._stat_vars['iters'].set(
                f'{history.total_recorded}/{self._total}')
        elif converged:
            self._stat_vars['iters'].set(
                f'{history.best_iteration}/{self._total}')
        else:
            self._stat_vars['iters'].set(str(self._total))

    def _cancel(self):
        if self._cancel_event:
            self._cancel_event.set()
        self._cancel_btn.configure(state='disabled')
        self._progress_lbl.configure(text='Cancelando...')
