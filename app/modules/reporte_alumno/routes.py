from flask import render_template, abort, request
from flask_login import login_required, current_user
from sqlalchemy import func

from . import reporte_alumno_bp
from app.models import (
    Estudiante,
    Inscripcion,
    Curso,
    Nota,
    Asistencia,
    Ciclo
)
from app.extensions import db


@reporte_alumno_bp.route('/')
@login_required
def index():

    # -------------------------------------------------
    # CONTROL DE ACCESO
    # -------------------------------------------------
    rol = str(current_user.rol).lower()
    if 'administrador' not in rol and 'coordinador' not in rol:
        abort(403)

    # -------------------------------------------------
    # LISTA DE CICLOS (PARA COMBO)
    # -------------------------------------------------
    ciclos = (
        Ciclo.query
        .order_by(Ciclo.fecha_inicio.desc())
        .all()
    )

    # -------------------------------------------------
    # CICLO SELECCIONADO
    # -------------------------------------------------
    ciclo_id = request.args.get('ciclo_id')
    ciclo_seleccionado = None

    if ciclo_id:
        ciclo_seleccionado = Ciclo.query.get(ciclo_id)

    # -------------------------------------------------
    # ESTUDIANTE SELECCIONADO
    # -------------------------------------------------
    estudiante = None
    estudiante_id = request.args.get('estudiante_id')

    if estudiante_id:
        estudiante = Estudiante.query.get(estudiante_id)

    # -------------------------------------------------
    # LISTA DE ALUMNOS (PARA COMBO)
    # -------------------------------------------------
    alumnos = (
        Estudiante.query
        .order_by(Estudiante.apellidos, Estudiante.nombres)
        .all()
    )

    # -------------------------------------------------
    # CONSTRUCCIÓN DEL REPORTE
    # -------------------------------------------------
    cursos_reporte = []
    suma_ponderada = 0.0
    total_creditos = 0
    promedio_general = 0.0  # ← IMPORTANTE inicializar

    if estudiante and ciclo_seleccionado:

        inscripciones = (
            Inscripcion.query
            .join(Curso)
            .filter(
                Inscripcion.estudiante_id == estudiante.id,
                Curso.ciclo_id == ciclo_seleccionado.id,
                Inscripcion.estado == 'ACTIVO'
            )
            .all()
        )

        for inscripcion in inscripciones:

            # PROMEDIO DEL CURSO
            promedio = (
                db.session.query(func.avg(Nota.nota))
                .filter(Nota.inscripcion_id == inscripcion.id)
                .scalar()
            )

            promedio = round(float(promedio), 2) if promedio else 0.0

            # ACUMULADORES PARA PROMEDIO PONDERADO
            if promedio > 0:
                suma_ponderada += promedio * inscripcion.curso.creditos
                total_creditos += inscripcion.curso.creditos

            # ASISTENCIAS
            total_asistencias = (
                Asistencia.query
                .filter_by(inscripcion_id=inscripcion.id)
                .count()
            )

            asistencias_presentes = (
                Asistencia.query
                .filter_by(inscripcion_id=inscripcion.id, presente=True)
                .count()
            )

            porcentaje_asistencia = (
                (asistencias_presentes / total_asistencias) * 100
                if total_asistencias > 0 else 0.0
            )

            cursos_reporte.append({
                'curso': inscripcion.curso,
                'promedio': promedio,
                'porcentaje_asistencia': round(porcentaje_asistencia, 2)
            })

        # PROMEDIO GENERAL PONDERADO
        if total_creditos > 0:
            promedio_general = round(suma_ponderada / total_creditos, 2)

    # -------------------------------------------------
    # RENDER
    # -------------------------------------------------
    return render_template(
        'reporte_alumno/index.html',
        alumnos=alumnos,
        ciclos=ciclos,
        estudiante=estudiante,
        ciclo=ciclo_seleccionado,
        cursos=cursos_reporte,
        promedio_general=promedio_general,
        total_creditos=total_creditos
    )
