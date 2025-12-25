# consultar_ciclos.py
from app import create_app
from app.models import Ciclo

# Crear la app Flask
app = create_app()

# Abrir el contexto de la app
with app.app_context():
    ciclos = Ciclo.query.all()
    print("Códigos de ciclo existentes en la base de datos:")
    for c in ciclos:
        print(f"codigo_ciclo: {c.codigo_ciclo}, id: {c.id}")
