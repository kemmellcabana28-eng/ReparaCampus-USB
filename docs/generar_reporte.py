"""Genera docs/reporte-pruebas.md a partir de reporte-pytest.xml y de los docstrings de tests/."""
import ast, glob, re, subprocess, sys, datetime
import xml.etree.ElementTree as ET

xml = ET.parse("reporte-pytest.xml").getroot()
resultados = {}
for caso in xml.iter("testcase"):
    nombre = caso.get("name").split("[")[0]
    fallo = caso.find("failure") is not None or caso.find("error") is not None
    r = resultados.setdefault(nombre, [0, 0])
    r[0] += 1
    r[1] += 1 if fallo else 0

filas = []
for archivo in sorted(glob.glob("tests/test_*.py")):
    arbol = ast.parse(open(archivo, encoding="utf-8").read())
    for f in arbol.body:
        if isinstance(f, ast.FunctionDef) and f.name.startswith("test_t"):
            doc = (ast.get_docstring(f) or "").strip()
            m = re.match(r"(AC-S\d\d-\d\d(?:/\d\d)?)\s*:\s*(.*)", doc)
            ac, esc = (m.group(1), m.group(2)) if m else ("S00 (transversal)", doc)
            idt = re.match(r"test_(t\d+b?)_", f.name).group(1).upper()
            n, fallos = resultados.get(f.name, [0, 0])
            filas.append((idt, ac, esc, n, "Cumple" if n and not fallos else "No cumple",
                          "integración" if "integracion" in f.name else "automatizada"))

try:
    sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True,
                                  stderr=subprocess.DEVNULL).strip()
except Exception:
    sha = "no disponible (sin repositorio Git)"
filas.sort(key=lambda f: (int(re.sub(r"\D", "", f[0])), f[0]))
total = sum(f[3] for f in filas)
fecha = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
sal = [f"**Comando:** `python -m pytest -v --junitxml=reporte-pytest.xml`  ",
       f"**Fecha de ejecución:** {fecha}  ", f"**SHA:** {sha}  ",
       f"**Resultado:** {total} casos ejecutados en {len(filas)} escenarios; "
       f"{sum(f[3] for f in filas if f[4]=='Cumple')} casos aprobados.", "",
       "| ID | SPEC / AC | Escenario y resultado esperado | Casos | Observado |",
       "|:----|:----------|:----------------------------------------------|:---:|:-----------|"]
for idt, ac, esc, n, est, tipo in filas:
    marca = " (integración)" if tipo == "integración" else ""
    sal.append(f"| {idt}{marca} | {ac} | {esc} | {n} | {est} |")
open("docs/reporte-pruebas.md", "w", encoding="utf-8").write("\n".join(sal) + "\n")
print(f"{len(filas)} escenarios, {total} casos")
