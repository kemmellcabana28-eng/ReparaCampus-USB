"""Abre el .docx con LibreOffice, actualiza el índice (con números de página) y exporta a PDF."""
import subprocess, sys, time, pathlib, uno
from com.sun.star.beans import PropertyValue

def prop(n, v):
    p = PropertyValue(); p.Name = n; p.Value = v; return p

origen = pathlib.Path(sys.argv[1]).resolve(); pdf = pathlib.Path(sys.argv[2]).resolve()
proc = subprocess.Popen(["soffice", "--headless", "--invisible", "--norestore",
    "--accept=socket,host=localhost,port=2002;urp;"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    ctx = None
    for _ in range(40):
        try:
            local = uno.getComponentContext()
            res = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
            ctx = res.resolve("uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext"); break
        except Exception:
            time.sleep(0.5)
    desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    doc = desktop.loadComponentFromURL(origen.as_uri(), "_blank", 0, (prop("Hidden", True),))
    for _ in range(2):  # dos pasadas: el índice cambia la paginación
        idx = doc.getDocumentIndexes()
        for i in range(idx.getCount()):
            idx.getByIndex(i).update()
    doc.storeToURL(origen.as_uri(), (prop("FilterName", "MS Word 2007 XML"),))
    doc.storeToURL(pdf.as_uri(), (prop("FilterName", "writer_pdf_Export"),))
    doc.close(True)
finally:
    proc.terminate()
print("PDF:", pdf)
