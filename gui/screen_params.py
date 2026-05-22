import tkinter as tk
import customtkinter as ctk
from gui.widgets import (COLORS, FONTS, primary_button, secondary_button,
                          accent_button, entry_field, styled_combobox)
from engine.convergence import default_patience
from config.labels import PROBLEM_LABELS, ALGORITHM_SHORT
from config.samples import (CONTINUOUS_SAMPLES, KNAPSACK_SAMPLES,
                             CATEGORICAL_SAMPLES, TSP_DATASETS)
from utils.validators import (
    validate_continuous_params, validate_ga_params,
    validate_population_size, validate_iterations,
    validate_convergence_n,
    validate_knapsack_params, validate_categorical_params, validate_tsp_params,
    validate_pso_params, validate_aco_params, validate_ais_params, validate_de_params,
)


_FORM_WIDTH = 760


class ScreenParams(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS['bg'])
        self._app = app
        self._fields: dict = {}
        self._global_err_var = ctk.StringVar()
        self._toast = None
        self._toast_after_id = None
        self._build_shell()

    # ------------------------------------------------------------------
    # Static shell
    # ------------------------------------------------------------------

    def _build_shell(self):
        # Centered title block
        top = ctk.CTkFrame(self, fg_color='transparent')
        top.pack(pady=(20, 0))

        self._title_lbl = ctk.CTkLabel(
            top, text='Configurar Parametros',
            font=FONTS['title'], text_color=COLORS['text'],
        )
        self._title_lbl.pack()

        self._subtitle_lbl = ctk.CTkLabel(
            top, text='',
            font=FONTS['small'], text_color=COLORS['text_secondary'],
        )
        self._subtitle_lbl.pack(pady=(2, 0))

        # Centered scrollable form, fixed max width
        form_wrap = ctk.CTkFrame(self, fg_color='transparent', width=_FORM_WIDTH)
        form_wrap.pack(fill='both', expand=True, pady=(12, 0))
        form_wrap.pack_propagate(False)

        self._scroll_frame = ctk.CTkScrollableFrame(
            form_wrap, fg_color='transparent',
            corner_radius=0,
            border_width=0,
            scrollbar_button_color=COLORS['surface2'],
            scrollbar_button_hover_color=COLORS['border_light'],
        )
        self._scroll_frame.pack(fill='both', expand=True)

        # Centered error label
        self._err_label = ctk.CTkLabel(
            self, textvariable=self._global_err_var,
            font=FONTS['small'], text_color=COLORS['error'],
            wraplength=_FORM_WIDTH,
        )
        self._err_label.pack(pady=(4, 0))

        # Centered button row \u2014 buttons sit next to each other
        btn_row = ctk.CTkFrame(self, fg_color='transparent')
        btn_row.pack(pady=(8, 14))

        accent_button(
            btn_row, '<  Regresar',
            lambda: self._app.show_screen('objective'), width=160, height=44,
        ).pack(side='left', padx=(0, 12))

        self._run_btn = primary_button(
            btn_row, 'Ejecutar Algoritmo  \u2192',
            self._execute, width=220, height=44,
        )
        self._run_btn.pack(side='left')

    # ------------------------------------------------------------------
    # Transient config toast (top-right)
    # ------------------------------------------------------------------

    def _show_config_toast(self, prob_label, algo_label, obj_label):
        if self._toast is not None:
            self._dismiss_toast()

        toast = ctk.CTkFrame(
            self, fg_color=COLORS['surface'],
            corner_radius=10, border_width=1, border_color=COLORS['primary'],
        )
        toast.place(relx=1.0, y=12, x=-24, anchor='ne')

        inner = ctk.CTkFrame(toast, fg_color='transparent')
        inner.pack(padx=14, pady=10)

        ctk.CTkLabel(
            inner, text='Configuracion',
            font=FONTS['small_bold'], text_color=COLORS['primary'],
            anchor='w',
        ).pack(anchor='w', pady=(0, 4))

        for line in (f'Problema: {prob_label}',
                     f'Algoritmo: {algo_label}',
                     f'Objetivo: {obj_label}'):
            ctk.CTkLabel(
                inner, text=line,
                font=FONTS['tiny'], text_color=COLORS['text_secondary'],
                anchor='w',
            ).pack(anchor='w')

        self._toast = toast
        self._toast_after_id = self._app.root.after(3500, self._dismiss_toast)

    def _dismiss_toast(self):
        if self._toast_after_id is not None:
            try:
                self._app.root.after_cancel(self._toast_after_id)
            except Exception:
                pass
            self._toast_after_id = None
        if self._toast is not None:
            try:
                self._toast.destroy()
            except Exception:
                pass
            self._toast = None

    # ------------------------------------------------------------------
    # on_show
    # ------------------------------------------------------------------

    def on_show(self):
        p = self._app.state.get('problem', '')
        a = self._app.state.get('algorithm', '')
        obj = 'Maximizar' if self._app.state.get('maximize') else 'Minimizar'
        p_label = PROBLEM_LABELS.get(p, p)
        a_label = ALGORITHM_SHORT.get(a, a)
        self._subtitle_lbl.configure(
            text=f"{p_label}  /  {a_label}  /  {obj}")
        self._global_err_var.set('')
        self._rebuild_form()
        self._show_config_toast(p_label, a_label, obj)

    def show_error(self, msg: str):
        self._global_err_var.set(msg)

    # ------------------------------------------------------------------
    # Form builder
    # ------------------------------------------------------------------

    def _rebuild_form(self):
        for w in self._scroll_frame.winfo_children():
            w.destroy()
        self._fields.clear()

        if not self._app.is_combination_implemented():
            ctk.CTkLabel(
                self._scroll_frame,
                text='Esta combinacion aun no esta implementada.',
                font=FONTS['body'], text_color=COLORS['error'],
            ).pack(pady=40)
            self._run_btn.configure(state='disabled')
            return

        self._run_btn.configure(state='normal')
        prob_schema, algo_schema = self._app.get_param_schemas()

        self._add_section('Parametros del Problema', prob_schema)
        self._add_section('Parametros del Algoritmo', algo_schema)

        p = self._app.state.get('problem', '')
        if p == 'tsp':
            self._add_dataset_loader()
        elif p == 'continuous':
            self._add_sample_loader('Funciones de Ejemplo', CONTINUOUS_SAMPLES)
        elif p == 'knapsack':
            self._add_sample_loader('Casos de Ejemplo', KNAPSACK_SAMPLES)
        elif p == 'categorical':
            self._add_sample_loader('Casos de Ejemplo', CATEGORICAL_SAMPLES)

        # Convergence N
        default_n = default_patience(
            next((s['default'] for s in algo_schema
                  if s['name'] in ('generations', 'iterations')), 100))
        conv_schema = {
            'name': 'convergence_n',
            'type': 'int',
            'min': 1,
            'default': default_n,
            'description': 'N de convergencia (sin mejora en N iters, parar)',
        }
        self._add_section('Criterio de Convergencia', [conv_schema])

    def _add_dataset_loader(self):
        self._add_section_header('Datasets Precargados')

        row_frame = ctk.CTkFrame(self._scroll_frame, fg_color='transparent')
        row_frame.pack(pady=(2, 12))

        self._dataset_var = ctk.StringVar(value=TSP_DATASETS[0][0])
        combo = styled_combobox(
            row_frame,
            variable=self._dataset_var,
            values=[label for label, _ in TSP_DATASETS],
            width=280,
        )
        combo.pack(side='left', padx=(0, 10))
        secondary_button(
            row_frame, 'Cargar', self._load_selected_dataset, width=100, height=34,
        ).pack(side='left')

    def _load_selected_dataset(self):
        label = self._dataset_var.get()
        name  = next((k for lbl, k in TSP_DATASETS if lbl == label), None)
        if name:
            self._load_tsp_dataset(name)

    def _load_tsp_dataset(self, name: str):
        from utils.tsp_loader import load_dataset
        n, coords = load_dataset(name)
        xs = ', '.join(f'{x:.1f}' for x, y in coords)
        ys = ', '.join(f'{y:.1f}' for x, y in coords)
        if 'n'        in self._fields: self._fields['n']['var'].set(str(n))
        if 'coords_x' in self._fields: self._fields['coords_x']['var'].set(xs)
        if 'coords_y' in self._fields: self._fields['coords_y']['var'].set(ys)
        self._global_err_var.set('')

    def _add_sample_loader(self, title: str, samples: list):
        self._add_section_header(title)

        row_frame = ctk.CTkFrame(self._scroll_frame, fg_color='transparent')
        row_frame.pack(pady=(2, 12))

        var = ctk.StringVar(value=samples[0][0])
        combo = styled_combobox(
            row_frame,
            variable=var,
            values=[lbl for lbl, _ in samples],
            width=320,
        )
        combo.pack(side='left', padx=(0, 10))

        def _load(v=var, s=samples):
            label = v.get()
            fields = next((f for lbl, f in s if lbl == label), None)
            if fields:
                self._load_sample_fields(fields)

        secondary_button(row_frame, 'Cargar', _load, width=100, height=34).pack(side='left')

    def _load_sample_fields(self, fields: dict):
        for name, value in fields.items():
            if name in self._fields:
                self._fields[name]['var'].set(str(value))
        self._global_err_var.set('')

    def _add_section_header(self, title: str):
        header_frame = ctk.CTkFrame(self._scroll_frame, fg_color='transparent')
        header_frame.pack(pady=(16, 6))

        # Accent dot
        ctk.CTkFrame(
            header_frame, fg_color=COLORS['primary'],
            width=4, height=16, corner_radius=2,
        ).pack(side='left', padx=(0, 8))

        ctk.CTkLabel(
            header_frame, text=title,
            font=FONTS['small_bold'], text_color=COLORS['text'],
            anchor='w',
        ).pack(side='left')

    def _add_section(self, title: str, schema: list):
        self._add_section_header(title)
        for param in schema:
            self._add_field(param)

    def _add_field(self, schema: dict):
        row = ctk.CTkFrame(self._scroll_frame, fg_color='transparent')
        row.pack(pady=3)

        desc = schema.get('description', schema['name'])
        var = ctk.StringVar(value=str(schema['default']))

        ctk.CTkLabel(
            row, text=desc,
            font=FONTS['small'], text_color=COLORS['text'],
            anchor='w', width=360,
        ).pack(side='left', padx=(0, 12))

        ent = entry_field(row, textvariable=var, width=200)
        ent.pack(side='left')

        err_lbl = ctk.CTkLabel(
            row, text='',
            font=FONTS['tiny'], text_color=COLORS['error'],
            anchor='w',
        )
        err_lbl.pack(side='left', padx=(8, 0))

        self._fields[schema['name']] = {'var': var, 'schema': schema, 'err': err_lbl}

    # ------------------------------------------------------------------
    # Collect + validate + run
    # ------------------------------------------------------------------

    def _execute(self):
        self._global_err_var.set('')
        params, type_errors = self._collect()
        if type_errors:
            return

        ok, msg = self._validate_domain(params)
        if not ok:
            self._global_err_var.set(msg)
            return

        self._app.run_experiment(params)

    def _collect(self) -> tuple[dict, bool]:
        params = {}
        has_errors = False
        for name, info in self._fields.items():
            raw = info['var'].get().strip()
            t   = info['schema']['type']
            try:
                if t == 'int':
                    params[name] = int(raw)
                elif t == 'float':
                    params[name] = float(raw)
                else:
                    params[name] = raw
                info['err'].configure(text='')
            except ValueError:
                info['err'].configure(text=f'Debe ser {t}')
                has_errors = True
        return params, has_errors

    def _validate_domain(self, params: dict) -> tuple[bool, str]:
        p = self._app.state['problem']
        a = self._app.state['algorithm']

        for check_fn, key in [
            (validate_population_size, 'population_size'),
            (validate_iterations,      'generations'),
            (validate_iterations,      'iterations'),
        ]:
            if key in params:
                ok, err = check_fn(params[key])
                if not ok:
                    return False, err

        if p == 'continuous':
            dims = params.get('dimensions', 1)
            bounds = [(params['lower_bound_x1'], params['upper_bound_x1'])]
            if dims == 2:
                bounds.append((params['lower_bound_x2'], params['upper_bound_x2']))
            ok, err = validate_continuous_params(params.get('expression', ''), dims, bounds)
            if not ok:
                return False, err

        elif p == 'knapsack':
            try:
                n  = params.get('n', 0)
                ws = [float(v.strip()) for v in params.get('weights', '').split(',')]
                vs = [float(v.strip()) for v in params.get('values',  '').split(',')]
                ok, err = validate_knapsack_params(n, ws, vs,
                                                   params.get('W', 0),
                                                   params.get('alpha', 0))
                if not ok:
                    return False, err
            except (ValueError, AttributeError):
                return False, 'Pesos y valores deben ser numeros separados por coma'

        elif p == 'categorical':
            dims = params.get('dimensions', 1)
            bounds_c = [(params.get('lower_bound_x1', 0),
                         params.get('upper_bound_x1', 1))]
            if dims == 2:
                bounds_c.append((params.get('lower_bound_x2', 0),
                                 params.get('upper_bound_x2', 1)))
            try:
                opts = [float(v.strip())
                        for v in params.get('option_values', '').split(',')]
                ok, err = validate_categorical_params(
                    params.get('expression', ''), dims, bounds_c,
                    params.get('num_options', 0), opts, '+')
                if not ok:
                    return False, err
            except (ValueError, AttributeError):
                return False, 'Valores de opciones deben ser numeros separados por coma'

        elif p == 'tsp':
            try:
                n  = params.get('n', 0)
                xs = [float(v.strip()) for v in params.get('coords_x', '').split(',')]
                ys = [float(v.strip()) for v in params.get('coords_y', '').split(',')]
                ok, err = validate_tsp_params(n, list(zip(xs, ys)))
                if not ok:
                    return False, err
            except (ValueError, AttributeError):
                return False, 'Coordenadas deben ser numeros separados por coma'

        if a == 'ga':
            ok, err = validate_ga_params(
                params.get('tournament_size', 3),
                params.get('population_size', 50),
                params.get('blx_alpha', 0.5),
            )
            if not ok:
                return False, err

        elif a == 'pso':
            ok, err = validate_pso_params(
                params.get('c1', 1.5), params.get('c2', 1.5),
                params.get('w', 0.7),  params.get('vmax', 5.0),
            )
            if not ok:
                return False, err

        elif a == 'aco':
            if p in ('continuous', 'categorical'):
                xi = params.get('xi', 0.85)
                if not (0 < xi < 2):
                    return False, 'xi debe estar en (0, 2)'
            else:
                ok, err = validate_aco_params(
                    params.get('alpha', 1.0), params.get('beta', 2.0),
                    params.get('rho', 0.1),   params.get('Q', 100.0),
                    params.get('tau0', 0.1),  params.get('num_ants', 20),
                )
                if not ok:
                    return False, err

        elif a == 'ais':
            ok, err = validate_ais_params(
                params.get('beta', 1.0), params.get('d', 0.1),
                params.get('rho', 3.0),
            )
            if not ok:
                return False, err

        elif a == 'de':
            ok, err = validate_de_params(
                params.get('F', 0.8), params.get('CR', 0.9),
                params.get('population_size', 50),
            )
            if not ok:
                return False, err

        total = params.get('generations') or params.get('iterations') or 100
        ok, err = validate_convergence_n(params.get('convergence_n', 10), total)
        if not ok:
            return False, err

        return True, ''
