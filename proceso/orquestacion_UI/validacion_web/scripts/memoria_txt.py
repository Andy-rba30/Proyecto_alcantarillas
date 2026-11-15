"""Convierte la memoria HTML de la app a texto plano y extrae los 'Resultado X = v'
por punto (para escalones descartados, cuya hidraulica solo esta en la memoria)."""
import re, html, sys, json
def texto(ruta):
    s = open(ruta).read()
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', s); t = html.unescape(t)
    return re.sub(r'\s+', ' ', t)
def resultados(ruta, ids):
    t = texto(ruta); out = {}
    # cortar por punto: la memoria tiene una seccion por id
    pos = sorted((t.find(f' {i} '), i) for i in ids)
    for k, (p, i) in enumerate(pos):
        fin = pos[k+1][0] if k + 1 < len(pos) else len(t)
        trozo = t[p:fin]
        out[i] = re.findall(r'Resultado ([A-Za-z_À-ſ/0-9 ]{1,30}?) = (-?[0-9.]+) ?([a-zA-Z0-9/%]*)', trozo)
    return out
if __name__ == '__main__':
    r = resultados(sys.argv[1], sys.argv[2:])
    for i, v in r.items():
        print(i)
        for x in v: print('   ', x)

def por_punto(ruta, etiquetas=('TW', 'y_normal', 'y_c', 'HW_entrada', 'HW_salida', 'HW_remanso', 'HW', 'V_salida', 'V_sedimentacion', 'V_erosion')):
    """{id: {etiqueta: (valor, unidad/texto siguiente)}} leyendo la seccion <h3>id ... de la memoria
    (primer 'Resultado <etiqueta> = ...' de cada punto). Para escalones DESCARTADOS, cuya
    hidraulica solo esta en la memoria."""
    s = open(ruta).read()
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S)
    partes = re.split(r'<h3>([A-Za-z0-9_.\-]+) &nbsp;\|', s)
    out = {}
    for k in range(1, len(partes), 2):
        pid, cuerpo = partes[k], partes[k + 1]
        cuerpo = cuerpo.split('<h2')[0]
        t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', cuerpo)))
        d = {}
        for m in re.finditer(r'Resultado ([A-Za-z_/]+) = (-?[0-9.]+|no alcanza)( [^ ]+ [^ ]+ [^ ]+ [^ ]+ [^ ]+ [^ ]+ [^ ]+ [^ ]+)?', t):
            if m.group(1) in etiquetas and m.group(1) not in d:
                v = m.group(2)
                d[m.group(1)] = (float(v) if v[0] in '-0123456789' else v, (m.group(3) or '').strip())
        if 'y_c' not in d:
            m = re.search(r'y_c = (-?[0-9.]+) m tirante critico', t)
            if m: d['y_c'] = (float(m.group(1)), 'leido de la sustitucion del paso 4.x')
        if 'y_normal' not in d:
            m = re.search(r'y_n = (-?[0-9.]+) m tirante normal del paso 4.1', t)
            if m: d['y_normal'] = (float(m.group(1)), 'leido de la sustitucion')
        g = re.search(r'gobierna el control de (entrada|salida)', t)
        d['control'] = g.group(1) if g else None
        out[pid] = d
    return out
