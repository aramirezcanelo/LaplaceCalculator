PLANTILLA_BASE = """
<html>
<head>
    <script type="text/x-mathjax-config">
        MathJax.Hub.Config({{
            messageStyle: "none",
            tex2jax: {{
                inlineMath: [ ['$','$'], ["\\\\(","\\\\)"] ],
                displayMath: [ ['$$','$$'], ["\\\\[","\\\\]"] ],
                processEscapes: true
            }}
        }});
    </script>
    <script type="text/javascript" async
        src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.9/MathJax.js?config=TeX-MML-AM_SVG">
    </script>
    <style>
        #MathJax_ProcessMessage {{ display: none !important; }}
        body {{
            margin: 15px;
            background-color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
            color: #0f172a;
            font-size: 15px;
            line-height: 1.6;
        }}
        b {{ color: #334155; }}
        /* Escala las ecuaciones SVG para que tengan buena legibilidad */
        svg {{ font-size: 17px; }} 
    </style>
</head>
<body>
    {contenido}
</body>
</html>
"""

GUIA_ERRORES_HTML = """
<div style='text-align: center; color: #b91c1c; font-weight: bold; margin-bottom: 15px;'>
    Error de sintaxis. Gu&iacute;a de escritura correcta:
</div>
<table style='width: 100%; border-collapse: collapse; font-size: 14px;'>
    <tr style='background-color: #0f172a; color: white;'>
        <th style='padding: 8px; border: 1px solid #ddd;'>Operaci&oacute;n</th>
        <th style='padding: 8px; border: 1px solid #ddd;'>Incorrecto</th>
        <th style='padding: 8px; border: 1px solid #ddd;'>Correcto (Python)</th>
    </tr>
    <tr>
        <td style='padding: 8px; border: 1px solid #ddd;'>Potencia ($t^2$)</td>
        <td style='padding: 8px; border: 1px solid #ddd; color: #b91c1c;'>t2 o t^2</td>
        <td style='padding: 8px; border: 1px solid #ddd; color: #10b981; font-weight: bold;'>t**2</td>
    </tr>
    <tr style='background-color: #f8fafc;'>
        <td style='padding: 8px; border: 1px solid #ddd;'>Multiplicaci&oacute;n ($2t$)</td>
        <td style='padding: 8px; border: 1px solid #ddd; color: #b91c1c;'>2t</td>
        <td style='padding: 8px; border: 1px solid #ddd; color: #10b981; font-weight: bold;'>2*t</td>
    </tr>
    <tr>
        <td style='padding: 8px; border: 1px solid #ddd;'>Exponencial ($e^{-3t}$)</td>
        <td style='padding: 8px; border: 1px solid #ddd; color: #b91c1c;'>e^(-3t)</td>
        <td style='padding: 8px; border: 1px solid #ddd; color: #10b981; font-weight: bold;'>exp(-3*t)</td>
    </tr>
    <tr style='background-color: #f8fafc;'>
        <td style='padding: 8px; border: 1px solid #ddd;'>Seno ($\\sin(2t)$)</td>
        <td style='padding: 8px; border: 1px solid #ddd; color: #b91c1c;'>sin2t</td>
        <td style='padding: 8px; border: 1px solid #ddd; color: #10b981; font-weight: bold;'>sin(2*t)</td>
    </tr>
</table>
"""

def generar_html(contenido_interno):
    return PLANTILLA_BASE.format(contenido=contenido_interno)