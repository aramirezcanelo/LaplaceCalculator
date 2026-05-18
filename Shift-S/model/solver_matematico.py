import sympy as sp
from view.utilidades_html import generar_html, GUIA_ERRORES_HTML

class SolverLaplace:
    def __init__(self):
        self.t = sp.symbols('t', positive=True)
        self.s = sp.symbols('s', positive=True)
        self.a, self.b, self.k, self.n = sp.symbols('a b k n', real=True)
        self.ctx = {
            't': self.t, 's': self.s, 'a': self.a, 'b': self.b, 'n': self.n, 'k': self.k, 'pi': sp.pi,
            'exp': sp.exp, 'sin': sp.sin, 'cos': sp.cos, 'sinh': sp.sinh, 'cosh': sp.cosh
        }

    def procesar_expresion(self, expr_str):
        expr_str = expr_str.replace('^', '**')
        
        try:
            f_input = sp.sympify(expr_str, locals=self.ctx)

            simbolos_permitidos = {self.t, self.s, self.a, self.b, self.k, self.n}
            if not f_input.free_symbols.issubset(simbolos_permitidos):
                return "error_sintaxis", generar_html(GUIA_ERRORES_HTML)
        except Exception:
            return "error_sintaxis", generar_html(GUIA_ERRORES_HTML)

        es_inversa = self.s in getattr(f_input, 'free_symbols', [])

        if es_inversa:
            html_inversa = f"""
            <div style='color: #b91c1c; font-weight: bold; font-size: 16px; margin-bottom: 10px;'>
                La expresión ingresada no corresponde a una Transformada Directa.
            </div>
            <p><b>Tipo de ecuación de frecuencias detectada:</b> Transformada Inversa de Laplace $\\mathcal{{L}}^{{-1}}\\{{{sp.latex(f_input)}\\}}$</p>
            <p style='color: #475569;'>Este resolvedor está configurado únicamente para calcular transformadas directas en el dominio del tiempo $t$.</p>
            """
            return "inversa", generar_html(html_inversa)

        try:
            pasos = []
            pasos.append(f"<b>Problema:</b> Calcular la Transformada Directa $\\mathcal{{L}}\\{{{sp.latex(f_input)}\\}}$")
            # CASO 1: 
            if f_input.is_Number or f_input in [self.a, self.b, self.k]:
                pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{c\\} = \\frac{{c}}{{s}}$")
                f_out = f_input / self.s
                pasos.append(f"<b>Sustituyendo:</b> $F(s) = \\frac{{{sp.latex(f_input)}}}{{s}}$")

            # CASO 2: Propiedad de linealidad (sumas y restas de términos independientes)
            elif isinstance(f_input, sp.Add):
                pasos.append("<b>Propiedad de Linealidad aplicada:</b> $\\mathcal{{L}}\\{f(t) \\pm g(t)\\} = \\mathcal{{L}}\\{f(t)\\} \\pm \\mathcal{{L}}\\{g(t)\\}$")
                terminos_proc = [f"\\mathcal{{L}}\\{{{sp.latex(term)}\\}}" for term in f_input.args]
                pasos.append(f"<b>Separando t&eacute;rminos:</b> ${' + '.join(terminos_proc)}$")
                
                # Cálculo de las transformadas
                f_out = sp.laplace_transform(f_input, self.t, self.s, noconds=True)
                if f_out.has(sp.LaplaceTransform):
                    raise ValueError("Sin solución analítica")
                
                f_out_simp = sp.simplify(f_out)
                
                # Conversión a cadenas de texto LaTeX para la comparación visual
                latex_original = sp.latex(f_out)
                latex_simplificado = sp.latex(f_out_simp)
                
                # 1. Se agrega siempre el resultado en fracciones separadas
                pasos.append(f"<b>Resultado directo combinado:</b> $F(s) = {latex_original}$")
                
                # 2. Condición matemática: Mostrar el paso extra SOLO si el formato es distinto
                if latex_original != latex_simplificado:
                    pasos.append(f"<b>Simplificaci&oacute;n algebraica (Denominador com&uacute;n):</b> $F(s) = {latex_simplificado}$")
            
            # CASO 3: Teorema de traslacion
            elif isinstance(f_input, sp.Mul) and any(isinstance(arg, sp.Pow) and arg.base == sp.E or arg.func == sp.exp for arg in f_input.args):
                pasos.append("<b>Primer Teorema de Traslaci&oacute;n aplicado:</b> $\\mathcal{{L}}\\{e^{{at}} f(t)\\} = \\mathcal{{L}}\\{f(t)\\}|_{{s \\to s - a}}$")
                exp_term = [arg for arg in f_input.args if isinstance(arg, sp.Pow) and arg.base == sp.E or arg.func == sp.exp][0]
                rest_term = sp.Mul(*[arg for arg in f_input.args if arg != exp_term])
                
                exponente = exp_term.args[0] if exp_term.func == sp.exp else exp_term.exp
                shift = sp.Wild('shift')
                match = exponente.match(shift * self.t)
                valor_a = match[shift] if match else exponente / self.t
                
                f_s_sin_exp = sp.laplace_transform(rest_term, self.t, self.s, noconds=True)
                if f_out.has(sp.LaplaceTransform):
                    raise ValueError("Sin solución analítica")
                pasos.append(f"1. Transformada base: $\\mathcal{{L}}\\{{{sp.latex(rest_term)}\\}} = {sp.latex(f_s_sin_exp)}$")
                pasos.append(f"2. Desplazamiento de frecuencias: $s \\to s - ({sp.latex(valor_a)})$")
                f_out = f_s_sin_exp.subs(self.s, self.s - valor_a)
                pasos.append(f"<b>Resultado final:</b> $F(s) = {sp.latex(sp.simplify(f_out))}$")

            # CASO 4: Funciones elementales directas (Seno, Coseno, Potencias solitarias)
            else:
                if isinstance(f_input, sp.Pow) and f_input.base == self.t:
                    pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{t^n\\} = \\frac{{n!}}{{s^{{n+1}}}}$")
                        
                        # NUEVO FILTRO: Si el exponente es exactamente la letra 'n', forzamos la estética clásica
                    if f_input.exp == self.n:
                        f_out_latex = "\\frac{n!}{s^{n+1}}"
                    else:
                        f_out = sp.laplace_transform(f_input, self.t, self.s, noconds=True)
                        f_out_latex = sp.latex(sp.simplify(f_out))
                            
                    pasos.append(f"<b>Resultado evaluado:</b> $F(s) = {f_out_latex}$")
                        
                else:
                        # Para el resto de funciones (sin, cos, sinh, cosh) se calcula normal
                    if f_input.func == sp.sin:
                        pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{\\sin(kt)\\} = \\frac{{k}}{{s^2 + k^2}}$")
                    elif f_input.func == sp.cos:
                        pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{\\cos(kt)\\} = \\frac{{s}}{{s^2 + k^2}}$")
                    elif f_input.func == sp.sinh:
                        pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{\\sinh(kt)\\} = \\frac{{k}}{{s^2 - k^2}}$")
                    elif f_input.func == sp.cosh:
                        pasos.append("<b>F&oacute;rmula empleada:</b> $\\mathcal{{L}}\\{\\cosh(kt)\\} = \\frac{{s}}{{s^2 - k^2}}$")
                        
                    f_out = sp.laplace_transform(f_input, self.t, self.s, noconds=True)
                    pasos.append(f"<b>Resultado evaluado:</b> $F(s) = {sp.latex(sp.simplify(f_out))}$")

            html_procedimiento = "".join([f"<p style='margin: 8px 0;'>{p}</p>" for p in pasos])
            return "directa", generar_html(html_procedimiento)

        except Exception:
            return "error_matematico", generar_html("<p style='color: #b91c1c; font-weight: bold;'>La expresión ingresada no posee una solución analítica directa.</p>")