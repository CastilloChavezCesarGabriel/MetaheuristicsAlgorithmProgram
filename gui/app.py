import tkinter as tk
import customtkinter as ctk

from gui.widgets import COLORS, FONTS, STEPS
from engine.convergence import default_patience
from engine.runner import Runner

class App:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title('Metaheuristic Lab')
        self.root.geometry('1280x820')
        self.root.minsize(1100, 720)
        self.root.configure(fg_color=COLORS['bg'])

        self.state = {
            'problem':   None,
            'algorithm': None,
            'maximize':  True,
            'params':    {},
        }

        self._current_step = 0

        # ── Step indicator bar ──
        self._step_bar = ctk.CTkFrame(
            self.root, fg_color=COLORS['bg_secondary'], height=52,
            corner_radius=0,
        )
        self._step_bar.pack(fill='x', side='top')
        self._step_bar.pack_propagate(False)
        self._step_indicators = []
        self._connectors = []
        self._build_step_bar()

        # ── Accent line ──
        ctk.CTkFrame(
            self.root, fg_color=COLORS['primary'], height=2, corner_radius=0,
        ).pack(fill='x', side='top')

        # ── Main container ──
        self.container = ctk.CTkFrame(self.root, fg_color=COLORS['bg'], corner_radius=0)
        self.container.pack(fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.screens = {}
        self._init_screens()
        self.show_screen('problem')

    # ------------------------------------------------------------------
    # Step bar with branding
    # ------------------------------------------------------------------

    def _build_step_bar(self):
        # Left: branding
        brand = ctk.CTkFrame(self._step_bar, fg_color='transparent')
        brand.pack(side='left', padx=(20, 0))

        # Logo circle
        ctk.CTkLabel(
            brand, text='\u2699',
            font=('SF Pro Display', 18) if FONTS['hero'][0] == 'SF Pro Display'
                 else ('Segoe UI', 18),
            text_color=COLORS['primary'],
            fg_color=COLORS['surface2'],
            width=32, height=32, corner_radius=16,
        ).pack(side='left', padx=(0, 8))

        ctk.CTkLabel(
            brand, text='Metaheuristic Lab',
            font=FONTS['body_bold'], text_color=COLORS['text'],
        ).pack(side='left')

        # Center: steps
        center = ctk.CTkFrame(self._step_bar, fg_color='transparent')
        center.place(relx=0.5, rely=0.5, anchor='center')

        for i, (label, _key) in enumerate(STEPS):
            step_frame = ctk.CTkFrame(center, fg_color='transparent')
            step_frame.pack(side='left', padx=2)

            circle = ctk.CTkLabel(
                step_frame, text=str(i + 1),
                width=26, height=26,
                fg_color=COLORS['surface2'],
                text_color=COLORS['text_dim'],
                font=FONTS['step'],
                corner_radius=13,
            )
            circle.pack(side='left', padx=(0, 5))

            name_lbl = ctk.CTkLabel(
                step_frame, text=label,
                text_color=COLORS['text_dim'],
                font=FONTS['small'],
            )
            name_lbl.pack(side='left')

            self._step_indicators.append((circle, name_lbl))

            if i < len(STEPS) - 1:
                connector = ctk.CTkFrame(
                    center, fg_color=COLORS['border'], width=28, height=2,
                    corner_radius=1,
                )
                connector.pack(side='left', padx=6, pady=1)
                self._connectors.append(connector)

    def _update_step_bar(self, step_index: int):
        self._current_step = step_index
        for i, (circle, name_lbl) in enumerate(self._step_indicators):
            if i < step_index:
                circle.configure(fg_color=COLORS['primary_dim'],
                                 text_color=COLORS['text'])
                name_lbl.configure(text_color=COLORS['text_secondary'])
            elif i == step_index:
                circle.configure(fg_color=COLORS['primary'],
                                 text_color=COLORS['text'])
                name_lbl.configure(text_color=COLORS['text'])
            else:
                circle.configure(fg_color=COLORS['surface2'],
                                 text_color=COLORS['text_dim'])
                name_lbl.configure(text_color=COLORS['text_dim'])

        for i, conn in enumerate(self._connectors):
            if i < step_index:
                conn.configure(fg_color=COLORS['primary_dim'])
            else:
                conn.configure(fg_color=COLORS['border'])

    # ------------------------------------------------------------------
    # Screens
    # ------------------------------------------------------------------

    def _init_screens(self):
        from gui.screen_problem   import ScreenProblem
        from gui.screen_algorithm import ScreenAlgorithm
        from gui.screen_objective import ScreenObjective
        from gui.screen_params    import ScreenParams
        from gui.screen_results   import ScreenResults

        for Cls, name in [
            (ScreenProblem,   'problem'),
            (ScreenAlgorithm, 'algorithm'),
            (ScreenObjective, 'objective'),
            (ScreenParams,    'params'),
            (ScreenResults,   'results'),
        ]:
            frame = Cls(self.container, self)
            self.screens[name] = frame
            frame.grid(row=0, column=0, sticky='nsew')

    def show_screen(self, name: str):
        step_index = next(
            (i for i, (_, key) in enumerate(STEPS) if key == name), 0
        )
        self._update_step_bar(step_index)

        screen = self.screens[name]
        if hasattr(screen, 'on_show'):
            screen.on_show()
        screen.tkraise()
        self._animate_entrance(screen)

    def _animate_entrance(self, screen):
        try:
            screen.configure(fg_color=COLORS['bg'])
        except (tk.TclError, ValueError):
            pass
        self._fade_step(screen, 0)

    def _fade_step(self, screen, step):
        fade_colors = [COLORS['bg_secondary'], COLORS['bg']]
        if step < len(fade_colors):
            try:
                screen.configure(fg_color=fade_colors[step])
            except (tk.TclError, ValueError):
                pass
            self.root.after(50, lambda: self._fade_step(screen, step + 1))

    # ------------------------------------------------------------------
    # Schema helpers
    # ------------------------------------------------------------------

    def get_param_schemas(self) -> tuple[list, list]:
        from config.param_definitions import get_param_schema
        return get_param_schema(
            self.state.get('problem', ''),
            self.state.get('algorithm', ''),
        )

    def is_combination_implemented(self) -> bool:
        from config.param_definitions import is_implemented
        return is_implemented(
            self.state.get('problem', ''),
            self.state.get('algorithm', ''),
        )

    # ------------------------------------------------------------------
    # Experiment lifecycle
    # ------------------------------------------------------------------

    def run_experiment(self, params: dict):
        self.state['params'] = params

        try:
            problem   = self._build_problem(params)
            algorithm = self._build_algorithm()
        except NotImplementedError as e:
            self.screens['params'].show_error(str(e))
            return

        self.state['problem_instance'] = problem

        total_iters = (
            params.get('generations') or params.get('iterations') or 100
        )
        patience = int(params.get('convergence_n', default_patience(total_iters)))

        # Slow TSP runs to ~20 fps so the live tour animation is visible
        step_delay = 0.05 if self.state.get('problem') == 'tsp' else 0.0

        runner = Runner(problem, algorithm, params, self.state['maximize'],
                        patience, step_delay=step_delay)
        self.screens['results'].start_run(runner, total_iters)
        self.show_screen('results')

    @staticmethod
    def _parse_dims_and_bounds(params: dict):
        """Reads 'dimensions' and per-dim 'lower_bound_xN'/'upper_bound_xN'
        from the params dict. Returns (dims, [(lo, hi), ...])."""
        dims = int(params['dimensions'])
        bounds = [(float(params['lower_bound_x1']),
                   float(params['upper_bound_x1']))]
        if dims == 2:
            bounds.append((float(params['lower_bound_x2']),
                           float(params['upper_bound_x2'])))
        return dims, bounds

    def _build_problem(self, params: dict):
        p = self.state['problem']
        if p == 'continuous':
            from problems.continuous import ContinuousProblem
            dims, bounds = self._parse_dims_and_bounds(params)
            return ContinuousProblem(params['expression'], dims, bounds)
        elif p == 'knapsack':
            from problems.knapsack import KnapsackProblem
            n       = int(params['n'])
            weights = [float(v.strip()) for v in params['weights'].split(',')]
            values  = [float(v.strip()) for v in params['values'].split(',')]
            return KnapsackProblem(n, weights, values,
                                   float(params['W']), float(params['alpha']))
        elif p == 'categorical':
            from problems.categorical import CategoricalProblem
            dims, bounds = self._parse_dims_and_bounds(params)
            n_opts = int(params['num_options'])
            opt_v  = [float(v.strip()) for v in params['option_values'].split(',')]
            return CategoricalProblem(params['expression'], dims, bounds, n_opts, opt_v)
        elif p == 'tsp':
            from problems.tsp import TspProblem
            n  = int(params['n'])
            xs = [float(v.strip()) for v in params['coords_x'].split(',')]
            ys = [float(v.strip()) for v in params['coords_y'].split(',')]
            return TspProblem(n, list(zip(xs, ys)))

        raise NotImplementedError(f"Problema '{p}' aun no implementado")

    def _build_algorithm(self):
        from algorithms import ALGORITHM_CLASSES
        a = self.state['algorithm']
        cls = ALGORITHM_CLASSES.get(a)
        if cls is None:
            raise NotImplementedError(f"Algoritmo '{a}' aun no implementado")
        return cls()

    def run(self):
        self.root.mainloop()