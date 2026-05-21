import sympy as sp
from view.utilidades_html import generar_html, GUIA_ERRORES_HTML

# ── Notación de Laplace ───────────────────────────────────────────────────────
# Una sola constante controla el aspecto de la L en toda la app.
# Cambiar aquí para que el cambio se propague a todos los pasos automáticamente.
L_TEX = r'\mathscr{L}'


def _L(expr: str) -> str:
    """Envuelve expr en la notación de Laplace: L{expr}"""
    return L_TEX + r'\{' + expr + r'\}'


def _Linv(expr: str) -> str:
    """Notación de Transformada Inversa: L^{-1}{expr}"""
    return L_TEX + r'^{-1}\left\{ ' + expr + r' \right\}'


class SolverLaplace:
    def __init__(self):
        self.t = sp.symbols('t', positive=True)
        self.s = sp.symbols('s', positive=True)
        self.a, self.b, self.k, self.n = sp.symbols('a b k n', real=True)
        self.ctx = {
            't': self.t, 's': self.s, 'a': self.a, 'b': self.b,
            'n': self.n, 'k': self.k, 'pi': sp.pi,
            'exp': sp.exp, 'sin': sp.sin, 'cos': sp.cos,
            'sinh': sp.sinh, 'cosh': sp.cosh,
        }

    # ── Transformadas directas ────────────────────────────────────────────────
    def procesar_expresion(self, expr_str):
        expr_str = expr_str.replace('^', '**')

        if '=' in expr_str:
            return self.resolver_edo(expr_str)

        try:
            f_input = sp.sympify(expr_str, locals=self.ctx)
            simbolos_permitidos = {self.t, self.s, self.a, self.b, self.k, self.n}
            if not f_input.free_symbols.issubset(simbolos_permitidos):
                return "error_sintaxis", generar_html(GUIA_ERRORES_HTML)
        except Exception:
            return "error_sintaxis", generar_html(GUIA_ERRORES_HTML)

        es_inversa = self.s in getattr(f_input, 'free_symbols', [])

        if es_inversa:
            lbl = _Linv(sp.latex(f_input))
            html_inversa = (
                "<div style='color:#b91c1c;font-weight:bold;font-size:16px;margin-bottom:10px;'>"
                "La expresión ingresada no corresponde a una Transformada Directa.</div>"
                "<p><b>Tipo detectado:</b> Transformada Inversa de Laplace $" + lbl + "$</p>"
                "<p style='color:#475569;'>Este resolvedor solo calcula transformadas directas "
                "en el dominio del tiempo $t$.</p>"
            )
            return "inversa", generar_html(html_inversa)

        try:
            pasos = []
            pasos.append(
                "<b>Problema:</b> Calcular la Transformada Directa $"
                + _L(sp.latex(f_input)) + "$"
            )

            # CASO 1: Constante o literal simbólico
            if f_input.is_Number or f_input in [self.a, self.b, self.k]:
                pasos.append(
                    "<b>F&oacute;rmula empleada:</b> $" + _L("c") + r" = \frac{c}{s}$"
                )
                pasos.append(
                    r"<b>Sustituyendo:</b> $F(s) = \frac{"
                    + sp.latex(f_input) + r"}{s}$"
                )

            # CASO 2: Linealidad (sp.Add)
            elif isinstance(f_input, sp.Add):
                pasos.append(
                    "<b>Propiedad de Linealidad aplicada:</b> $"
                    + _L(r"f(t) \pm g(t)") + " = "
                    + _L("f(t)") + r" \pm " + _L("g(t)") + "$"
                )
                terminos_proc = ["$" + _L(sp.latex(term)) + "$" for term in f_input.args]
                pasos.append(
                    "<b>Separando t&eacute;rminos:</b> " + "$+$".join(terminos_proc)
                )

                f_out = sp.laplace_transform(f_input, self.t, self.s, noconds=True)
                if f_out.has(sp.LaplaceTransform):
                    raise ValueError("Sin solución analítica")

                f_out_simp = sp.simplify(f_out)
                latex_orig = sp.latex(f_out)
                latex_simp = sp.latex(f_out_simp)

                pasos.append("<b>Resultado combinado:</b> $F(s) = " + latex_orig + "$")
                if latex_orig != latex_simp:
                    pasos.append(
                        "<b>Simplificaci&oacute;n (denominador com&uacute;n):</b> "
                        "$F(s) = " + latex_simp + "$"
                    )

            # CASO 3: Primer Teorema de Traslación (Mul con exp)
            elif isinstance(f_input, sp.Mul) and any(
                (isinstance(arg, sp.Pow) and arg.base == sp.E) or arg.func == sp.exp
                for arg in f_input.args
            ):
                pasos.append(
                    "<b>Primer Teorema de Traslaci&oacute;n:</b> $"
                    + _L(r"e^{at} f(t)") + " = " + _L("f(t)") + r"|_{s \to s-a}$"
                )
                exp_term = next(
                    arg for arg in f_input.args
                    if (isinstance(arg, sp.Pow) and arg.base == sp.E) or arg.func == sp.exp
                )
                rest_term = sp.Mul(*[arg for arg in f_input.args if arg != exp_term])
                exponente = exp_term.args[0] if exp_term.func == sp.exp else exp_term.exp
                shift = sp.Wild('shift')
                m = exponente.match(shift * self.t)
                valor_a = m[shift] if m else exponente / self.t

                f_base = sp.laplace_transform(rest_term, self.t, self.s, noconds=True)
                pasos.append(
                    "1. Transformada base: $" + _L(sp.latex(rest_term))
                    + " = " + sp.latex(f_base) + "$"
                )
                pasos.append(
                    r"2. Desplazamiento: $s \to s - (" + sp.latex(valor_a) + ")$"
                )
                f_out = f_base.subs(self.s, self.s - valor_a)
                pasos.append(
                    "<b>Resultado:</b> $F(s) = " + sp.latex(sp.simplify(f_out)) + "$"
                )

            # CASO 4: Funciones elementales
            else:
                if isinstance(f_input, sp.Pow) and f_input.base == self.t:
                    pasos.append(
                        "<b>F&oacute;rmula empleada:</b> $"
                        + _L("t^n") + r" = \frac{n!}{s^{n+1}}$"
                    )
                    if f_input.exp == self.n:
                        f_out_latex = r"\frac{n!}{s^{n+1}}"
                    else:
                        f_out = sp.laplace_transform(f_input, self.t, self.s, noconds=True)
                        f_out_latex = sp.latex(sp.simplify(f_out))
                    pasos.append("<b>Resultado:</b> $F(s) = " + f_out_latex + "$")

                else:
                    formulas = {
                        sp.sin:  (r"\sin(kt)", r"\frac{k}{s^2+k^2}"),
                        sp.cos:  (r"\cos(kt)", r"\frac{s}{s^2+k^2}"),
                        sp.sinh: (r"\sinh(kt)", r"\frac{k}{s^2-k^2}"),
                        sp.cosh: (r"\cosh(kt)", r"\frac{s}{s^2-k^2}"),
                    }
                    if f_input.func in formulas:
                        arg_tex, res_tex = formulas[f_input.func]
                        pasos.append(
                            "<b>F&oacute;rmula empleada:</b> $"
                            + _L(arg_tex) + " = " + res_tex + "$"
                        )

                    f_out = sp.laplace_transform(f_input, self.t, self.s, noconds=True)
                    pasos.append(
                        "<b>Resultado evaluado:</b> $F(s) = "
                        + sp.latex(sp.simplify(f_out)) + "$"
                    )

            html_body = "".join("<p style='margin:8px 0;'>" + p + "</p>" for p in pasos)
            return "directa", generar_html(html_body)

        except Exception:
            return "error_matematico", generar_html(
                "<p style='color:#b91c1c;font-weight:bold;'>"
                "La expresión no posee solución analítica directa.</p>"
            )

    # ── Ecuaciones Diferenciales ──────────────────────────────────────────────
    def resolver_edo(self, expr_str):
        try:
            expr_str = expr_str.replace('y(t)', 'y')

            partes = expr_str.split(';')
            edo_principal = partes[0]

            y0, y1, y2, y3, y4, y5, y6, y7, y8, y9 = [0] * 10
            for condicion in partes[1:]:
                c = condicion.strip().replace(' ', '')
                if   "y'''''''''(0)=" in c: y9 = sp.sympify(c.split('=')[1], locals=self.ctx)
                elif "y''''''''(0)="  in c: y8 = sp.sympify(c.split('=')[1], locals=self.ctx)
                elif "y'''''''(0)="   in c: y7 = sp.sympify(c.split('=')[1], locals=self.ctx)
                elif "y''''''(0)="    in c: y6 = sp.sympify(c.split('=')[1], locals=self.ctx)
                elif "y'''''(0)="     in c: y5 = sp.sympify(c.split('=')[1], locals=self.ctx)
                elif "y''''(0)="      in c: y4 = sp.sympify(c.split('=')[1], locals=self.ctx)
                elif "y'''(0)="       in c: y3 = sp.sympify(c.split('=')[1], locals=self.ctx)
                elif "y''(0)="        in c: y2 = sp.sympify(c.split('=')[1], locals=self.ctx)
                elif "y'(0)="         in c: y1 = sp.sympify(c.split('=')[1], locals=self.ctx)
                elif "y(0)="          in c: y0 = sp.sympify(c.split('=')[1], locals=self.ctx)

            lhs_txt, rhs_txt = edo_principal.split('=')

            lhs_prepared = (
                lhs_txt
                .replace("y''''''''''", "y_dec_prime")
                .replace("y'''''''''",  "y_non_prime")
                .replace("y''''''''",   "y_oct_prime")
                .replace("y'''''''",    "y_sept_prime")
                .replace("y''''''",     "y_sext_prime")
                .replace("y'''''",      "y_quint_prime")
                .replace("y''''",       "y_quad_prime")
                .replace("y'''",        "y_triple_prime")
                .replace("y''",         "y_double_prime")
                .replace("y'",          "y_prime")
            )

            ctx_edo = self.ctx.copy()
            ctx_edo.update({
                'y_dec_prime':    sp.symbols('y_dec_prime'),
                'y_non_prime':    sp.symbols('y_non_prime'),
                'y_oct_prime':    sp.symbols('y_oct_prime'),
                'y_sept_prime':   sp.symbols('y_sept_prime'),
                'y_sext_prime':   sp.symbols('y_sext_prime'),
                'y_quint_prime':  sp.symbols('y_quint_prime'),
                'y_quad_prime':   sp.symbols('y_quad_prime'),
                'y_triple_prime': sp.symbols('y_triple_prime'),
                'y_double_prime': sp.symbols('y_double_prime'),
                'y_prime':        sp.symbols('y_prime'),
                'y':              sp.symbols('y'),
            })

            lhs_expr = sp.sympify(lhs_prepared, locals=ctx_edo)
            rhs_expr = sp.sympify(rhs_txt, locals=ctx_edo)

            Y = sp.symbols('Y')
            s = self.s

            rhs_laplace = sp.laplace_transform(rhs_expr, self.t, s, noconds=True)
            lhs_laplace = lhs_expr.subs({
                ctx_edo['y_dec_prime']:    s**10*Y - s**9*y0 - s**8*y1 - s**7*y2 - s**6*y3 - s**5*y4 - s**4*y5 - s**3*y6 - s**2*y7 - s*y8 - y9,
                ctx_edo['y_non_prime']:    s**9*Y  - s**8*y0 - s**7*y1 - s**6*y2 - s**5*y3 - s**4*y4 - s**3*y5 - s**2*y6 - s*y7 - y8,
                ctx_edo['y_oct_prime']:    s**8*Y  - s**7*y0 - s**6*y1 - s**5*y2 - s**4*y3 - s**3*y4 - s**2*y5 - s*y6 - y7,
                ctx_edo['y_sept_prime']:   s**7*Y  - s**6*y0 - s**5*y1 - s**4*y2 - s**3*y3 - s**2*y4 - s*y5 - y6,
                ctx_edo['y_sext_prime']:   s**6*Y  - s**5*y0 - s**4*y1 - s**3*y2 - s**2*y3 - s*y4 - y5,
                ctx_edo['y_quint_prime']:  s**5*Y  - s**4*y0 - s**3*y1 - s**2*y2 - s*y3 - y4,
                ctx_edo['y_quad_prime']:   s**4*Y  - s**3*y0 - s**2*y1 - s*y2 - y3,
                ctx_edo['y_triple_prime']: s**3*Y  - s**2*y0 - s*y1 - y2,
                ctx_edo['y_double_prime']: s**2*Y  - s*y0 - y1,
                ctx_edo['y_prime']:        s*Y - y0,
                ctx_edo['y']:             Y,
            })

            eq_laplace = sp.Eq(lhs_laplace, rhs_laplace)
            Y_sol = sp.solve(eq_laplace, Y)[0]
            Y_fracciones = sp.apart(Y_sol, s)
            y_t = sp.inverse_laplace_transform(Y_sol, s, self.t)
            y_t_expandido = sp.expand(y_t)

            # ── Reporte paso a paso ───────────────────────────────────────────
            pasos = []
            pasos.append(
                "<div style='color:#10b981;font-weight:bold;font-size:16px;margin-bottom:10px;'>"
                "Modelado de Ecuaci&oacute;n Diferencial Detectado</div>"
            )

            lhs_visual = (
                lhs_txt.replace('*', '')
                .replace("y''''''''''", "y^{(10)}")
                .replace("y'''''''''",  "y^{(9)}")
                .replace("y''''''''",   "y^{(8)}")
                .replace("y'''''''",    "y^{(7)}")
                .replace("y''''''",     "y^{(6)}")
                .replace("y'''''",      "y^{(5)}")
                .replace("y''''",       "y^{(4)}")
            )
            pasos.append(
                "<b>EDO Planteada:</b> $" + lhs_visual
                + " = " + sp.latex(rhs_expr) + "$"
            )

            ci_texto = "$y(0) = " + sp.latex(y0) + r", \quad y'(0) = " + sp.latex(y1)
            if   "y''''''''''"  in lhs_txt or "y'''''''''(0)=" in expr_str: ci_texto += r", \dots, \quad y^{(9)}(0) = " + sp.latex(y9) + "$"
            elif "y'''''''''"   in lhs_txt or "y''''''''(0)="  in expr_str: ci_texto += r", \dots, \quad y^{(8)}(0) = " + sp.latex(y8) + "$"
            elif "y''''''''"    in lhs_txt or "y'''''''(0)="   in expr_str: ci_texto += r", \dots, \quad y^{(7)}(0) = " + sp.latex(y7) + "$"
            elif "y'''''''"     in lhs_txt or "y''''''(0)="    in expr_str: ci_texto += r", \dots, \quad y^{(6)}(0) = " + sp.latex(y6) + "$"
            elif "y''''''"      in lhs_txt or "y'''''(0)="     in expr_str: ci_texto += r", \dots, \quad y^{(5)}(0) = " + sp.latex(y5) + "$"
            elif "y'''''"       in lhs_txt or "y''''(0)="      in expr_str: ci_texto += r", \dots, \quad y^{(4)}(0) = " + sp.latex(y4) + "$"
            elif "y''''"        in lhs_txt or "y'''(0)="       in expr_str: ci_texto += r", \quad y''(0) = " + sp.latex(y2) + r", \quad y'''(0) = " + sp.latex(y3) + "$"
            elif "y'''"         in lhs_txt or "y''(0)="        in expr_str: ci_texto += r", \quad y''(0) = " + sp.latex(y2) + "$"
            else: ci_texto += "$"
            pasos.append("<b>Condiciones Iniciales:</b> " + ci_texto)

            # Paso 1 — Aplicar L
            pasos.append("<b>1. Aplicando la Transformada de Laplace:</b>")
            pasos.append(
                "&bull; $" + _L(lhs_visual) + " = " + _L(sp.latex(rhs_expr)) + "$"
            )
            pasos.append("&nbsp;&nbsp;&nbsp;&nbsp;<i>Sustituyendo teoremas de derivaci&oacute;n:</i>")
            pasos.append("&nbsp;&nbsp;&nbsp;&nbsp;&bull; $" + _L("y") + " = Y(s)$")

            # Tabla de sustituciones — sin backslash dentro de f-string
            deriv_labels = ["y'", "y''", "y'''", "y^{(4)}", "y^{(5)}",
                            "y^{(6)}", "y^{(7)}", "y^{(8)}", "y^{(9)}", "y^{(10)}"]
            deriv_checks = ["y'", "y''", "y'''", "y''''", "y'''''",
                            "y''''''", "y'''''''", "y''''''''", "y'''''''''", "y''''''''''"]
            deriv_rhs = [
                "sY(s) - " + sp.latex(y0),
                "s^2Y(s) - " + sp.latex(y0 * s) + " - " + sp.latex(y1),
                "s^3Y(s) - " + sp.latex(y0 * s**2) + " - " + sp.latex(y1 * s) + " - " + sp.latex(y2),
                r"s^4Y(s) - \dots - " + sp.latex(y3),
                r"s^5Y(s) - \dots - " + sp.latex(y4),
                r"s^6Y(s) - \dots - " + sp.latex(y5),
                r"s^7Y(s) - \dots - " + sp.latex(y6),
                r"s^8Y(s) - \dots - " + sp.latex(y7),
                r"s^9Y(s) - \dots - " + sp.latex(y8),
                r"s^{10}Y(s) - \dots - " + sp.latex(y9),
            ]
            for chk, lbl, rhs_d in zip(deriv_checks, deriv_labels, deriv_rhs):
                if chk in lhs_txt:
                    pasos.append(
                        "&nbsp;&nbsp;&nbsp;&nbsp;&bull; $"
                        + _L(lbl) + " = " + rhs_d + "$"
                    )

            pasos.append(
                "&bull; Expresi&oacute;n algebraica: $"
                + sp.latex(lhs_laplace) + " = " + sp.latex(rhs_laplace) + "$"
            )

            # Paso 2 — Despejar Y(s)
            pasos.append("<b>2. Despejando $Y(s)$:</b>")
            pasos.append("&bull; $Y(s) = " + sp.latex(Y_sol) + "$")

            # Paso 3 — Fracciones parciales
            if Y_fracciones != Y_sol:
                pasos.append("<b>3. Expansi&oacute;n en Fracciones Parciales:</b>")
                try:
                    terminos = Y_fracciones.args if Y_fracciones.is_Add else [Y_fracciones]
                    alfabeto = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                    idx = 0
                    frac_gen, constantes = [], []

                    for termino in terminos:
                        num, den = termino.as_numer_denom()
                        base = den.base if (den.is_Pow and den.exp.is_Integer) else den
                        grado = sp.degree(base, s)
                        if grado == 1:
                            L_let = alfabeto[idx]; idx += 1
                            frac_gen.append(r"\frac{" + L_let + "}{" + sp.latex(den) + "}")
                            constantes.append(L_let + " = " + sp.latex(num))
                        elif grado == 2:
                            l1, l2 = alfabeto[idx], alfabeto[idx + 1]; idx += 2
                            frac_gen.append(r"\frac{" + l1 + "s+" + l2 + "}{" + sp.latex(den) + "}")
                            constantes.append(l1 + " = " + sp.latex(num.coeff(s)))
                            constantes.append(l2 + " = " + sp.latex(num.subs(s, 0)))
                        else:
                            frac_gen.append(sp.latex(termino))

                    if frac_gen and constantes:
                        pasos.append(
                            "&bull; Planteamiento: $Y(s) = " + " + ".join(frac_gen) + "$"
                        )
                        pasos.append(
                            r"&bull; Constantes: $" + r", \quad ".join(constantes) + "$"
                        )
                except Exception:
                    pass

                pasos.append(
                    "&bull; $Y(s) = " + sp.latex(Y_fracciones) + "$"
                )
                pasos.append("<b>4. Aplicando la Transformada Inversa:</b>")
                pasos.append("&bull; $y(t) = " + _Linv(sp.latex(Y_fracciones)) + "$")
            else:
                pasos.append("<b>3. Aplicando la Transformada Inversa:</b>")
                pasos.append("&bull; $y(t) = " + _Linv(sp.latex(Y_sol)) + "$")

            pasos.append(
                "<b>Soluci&oacute;n particular:</b> "
                "<span style='color:#60cdff;font-weight:bold;'>$y(t) = "
                + sp.latex(y_t_expandido) + "$</span>"
            )

            html_body = "".join("<p style='margin:6px 0;'>" + p + "</p>" for p in pasos)
            return "directa", generar_html(html_body)

        except Exception:
            return "error_matematico", generar_html(
                "<p style='color:#b91c1c;font-weight:bold;'>"
                "Error al resolver la EDO. Verifique la sintaxis.</p>"
            )
