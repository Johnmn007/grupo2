from flask import Blueprint

reporte_alumno_bp = Blueprint(
    'reporte_alumno',
    __name__,
    url_prefix='/alumno/reporte'
)

from . import routes
