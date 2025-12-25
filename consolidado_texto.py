import os
import datetime
import shutil

def es_archivo_texto(archivo):
    extensiones_texto = ['.py', '.txt', '.md', '.html', '.css', '.js', '.json', '.xml', '.yaml', '.yml', '.php', '.java', '.c', '.cpp', '.h', '.cs', '.sql', '.ts', '.jsx', '.tsx', '.vue']
    return any(archivo.lower().endswith(ext) for ext in extensiones_texto)

def deberia_excluir_carpeta(ruta_carpeta):
    """Define qué carpetas excluir"""
    carpetas_excluir = [
        '__pycache__', 'venv', '.git', 'node_modules', '.vscode',
        'bootstrap', 'bootstrap5', 'bootstrap-5',  # Bootstrap
        'jquery', 'jquery-ui',  # jQuery
        'fontawesome', 'fonts',  # Fuentes
        'dist', 'build',  # Carpetas de build
        'logs', 'temp', 'tmp',  # Temporales
        '.idea', '__pycache__', '.pytest_cache'  # IDE y cache
    ]
    
    nombre_carpeta = os.path.basename(ruta_carpeta).lower()
    return nombre_carpeta in carpetas_excluir

def deberia_excluir_archivo(nombre_archivo):
    """Define qué archivos excluir"""
    archivos_excluir = [
        'package-lock.json', 'yarn.lock',  # Lock files
        '.DS_Store', 'thumbs.db',  # Archivos del sistema
        '*.min.js', '*.min.css',
        'rojo.py','amarillo.py','verde.py'  # Archivos minificados
    ]
    
    nombre_archivo_lower = nombre_archivo.lower()
    
    # Excluir por nombre exacto
    if nombre_archivo_lower in archivos_excluir:
        return True
    
    # Excluir por patrón
    for patron in archivos_excluir:
        if '*' in patron and nombre_archivo_lower.endswith(patron.replace('*', '')):
            return True
    
    return False

# OPCIÓN 1: Archivo único consolidado
def generar_archivo_texto_consolidado(ruta_origen, ruta_destino_txt):
    with open(ruta_destino_txt, 'w', encoding='utf-8') as archivo_txt:
        archivo_txt.write(f"PROYECTO: {os.path.basename(ruta_origen)}\n")
        archivo_txt.write(f"FECHA: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        archivo_txt.write("CARPETAS EXCLUIDAS: bootstrap, jquery, fontawesome, node_modules, etc.\n")
        archivo_txt.write("=" * 80 + "\n\n")
        
        for root, dirs, files in os.walk(ruta_origen):
            # Excluir carpetas no deseadas
            dirs[:] = [d for d in dirs if not deberia_excluir_carpeta(os.path.join(root, d))]
            
            # Excluir archivos no deseados
            files = [f for f in files if not deberia_excluir_archivo(f) and not f.lower().startswith('readme')]
            
            for archivo in files:
                archivo_completo = os.path.join(root, archivo)
                
                if es_archivo_texto(archivo):
                    ruta_relativa = os.path.relpath(archivo_completo, ruta_origen)
                    
                    try:
                        with open(archivo_completo, 'r', encoding='utf-8') as f:
                            contenido = f.read()
                        
                        archivo_txt.write(f"\n{'='*60}\n")
                        archivo_txt.write(f"ARCHIVO: {ruta_relativa}\n")
                        archivo_txt.write(f"{'='*60}\n\n")
                        archivo_txt.write(contenido)
                        archivo_txt.write("\n\n")
                        
                    except Exception as e:
                        print(f"Error leyendo {ruta_relativa}: {e}")
    
    print(f"✓ Archivo único generado: {ruta_destino_txt}")

# OPCIÓN 2: Estructura de carpetas
def generar_estructura_txt(ruta_origen, ruta_destino_base):
    if os.path.exists(ruta_destino_base):
        shutil.rmtree(ruta_destino_base)
    os.makedirs(ruta_destino_base)
    
    archivos_procesados = 0
    
    for root, dirs, files in os.walk(ruta_origen):
        # Excluir carpetas
        dirs[:] = [d for d in dirs if not deberia_excluir_carpeta(os.path.join(root, d))]
        
        for archivo in files:
            if (not es_archivo_texto(archivo) or 
                deberia_excluir_archivo(archivo) or 
                archivo.lower().startswith('readme')):
                continue
                
            archivo_completo = os.path.join(root, archivo)
            ruta_relativa = os.path.relpath(archivo_completo, ruta_origen)
            
            archivo_destino = os.path.join(ruta_destino_base, ruta_relativa + '.txt')
            directorio_destino = os.path.dirname(archivo_destino)
            
            if not os.path.exists(directorio_destino):
                os.makedirs(directorio_destino)
            
            try:
                with open(archivo_completo, 'r', encoding='utf-8') as f_origen:
                    contenido = f_origen.read()
                
                with open(archivo_destino, 'w', encoding='utf-8') as f_destino:
                    f_destino.write(contenido)
                
                archivos_procesados += 1
                
            except Exception as e:
                print(f"Error procesando {ruta_relativa}: {e}")
    
    print(f"✓ Estructura generada: {ruta_destino_base}")
    print(f"✓ Archivos procesados: {archivos_procesados}")

# OPCIÓN 3: Archivos divididos (RECOMENDADO)
def generar_archivos_divididos(ruta_origen, ruta_destino_base, max_lineas=1000):
    if not os.path.exists(ruta_destino_base):
        os.makedirs(ruta_destino_base)
    
    archivo_actual = None
    contador_archivos = 1
    lineas_actuales = 0
    
    for root, dirs, files in os.walk(ruta_origen):
        # Excluir carpetas
        dirs[:] = [d for d in dirs if not deberia_excluir_carpeta(os.path.join(root, d))]
        
        # Excluir archivos
        files = [f for f in files if not deberia_excluir_archivo(f) and not f.lower().startswith('readme')]
        
        for archivo in files:
            archivo_completo = os.path.join(root, archivo)
            
            if es_archivo_texto(archivo):
                ruta_relativa = os.path.relpath(archivo_completo, ruta_origen)
                
                try:
                    with open(archivo_completo, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    
                    lineas_archivo = contenido.count('\n') + 1
                    
                    if archivo_actual is None or lineas_actuales + lineas_archivo > max_lineas:
                        if archivo_actual:
                            archivo_actual.close()
                        
                        nombre_archivo = f"proyecto_parte_{contador_archivos:02d}.txt"
                        ruta_archivo = os.path.join(ruta_destino_base, nombre_archivo)
                        archivo_actual = open(ruta_archivo, 'w', encoding='utf-8')
                        
                        archivo_actual.write(f"PARTE: {contador_archivos:02d}\n")
                        archivo_actual.write(f"PROYECTO: {os.path.basename(ruta_origen)}\n")
                        archivo_actual.write(f"FECHA: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        archivo_actual.write("CARPETAS EXCLUIDAS: bootstrap, jquery, fontawesome, etc.\n")
                        archivo_actual.write("=" * 80 + "\n\n")
                        
                        contador_archivos += 1
                        lineas_actuales = 5
                    
                    archivo_actual.write(f"\n{'='*60}\n")
                    archivo_actual.write(f"ARCHIVO: {ruta_relativa}\n")
                    archivo_actual.write(f"{'='*60}\n\n")
                    archivo_actual.write(contenido)
                    archivo_actual.write("\n\n")
                    
                    lineas_actuales += lineas_archivo + 5
                    
                except Exception as e:
                    print(f"Error procesando {ruta_relativa}: {e}")
    
    if archivo_actual:
        archivo_actual.close()
    
    print(f"✓ Archivos divididos generados en: {ruta_destino_base}")
    print(f"✓ Total de partes: {contador_archivos - 1}")

# CONFIGURACIÓN - MODIFICA ESTAS RUTAS:
ruta_proyecto = 'D:/SIGEA_DSI'  # Tu proyecto aquí

# ELIGE UNA OPCIÓN (quita el # para usar):

# Opción 1: Un solo archivo
# generar_archivo_texto_consolidado(ruta_proyecto, 'D:/SIGEA_DSI/proyecto_completo.txt')

# Opción 2: Estructura de carpetas  
# generar_estructura_txt(ruta_proyecto, 'D:/SIGEA_DSI/estructura_txt')

# Opción 3: Archivos divididos (RECOMENDADO)
generar_archivos_divididos(ruta_proyecto, 'D:/SIGEA_DSI/partes_proyecto', max_lineas=800)