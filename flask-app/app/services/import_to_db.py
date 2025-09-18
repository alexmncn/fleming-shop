import re
import math
import os, time, glob, re, math, uuid
from datetime import datetime
import pandas as pd
from dbfread import DBF
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Article, Family, Article_import_log, Article_import, DailySales, Ticket, TicketItem, User, ImportFile
from app.services.pushover_alerts import send_alert

from app.config import DATA_ROUTE, DATA_LOGS_ROUTE


# dbf to equivalent DB keys names
article_column_to_attribute_map = {
    'CREF': 'ref',
    'CDETALLE': 'detalle',
    'CCODFAM': 'codfam',
    'NCOSTEDIV': 'pcosto',
    'NPVP': 'pvp',
    'CCODEBAR': 'codebar',
    'DACTUALIZA': 'factualizacion'
}


def process_import_file(import_file_id, username, max_retries=0):
    from app.app import create_app
    app = create_app()
    with app.app_context():
        
        valid_import_file_types = {
            'articles': update_articles,
            'families': update_families,
            'stocks': update_stocks,
            'cierre': update_cierre,
            'movimt': update_movimt,
            'hticketl': update_hticketl,
        }

        session = db.session

        # Recuperar registro
        import_file = session.get(ImportFile, import_file_id)
        if not import_file:
            raise ValueError(f"No se encontró ImportFile con id={import_file_id}")
        # Inicializamos
        import_file.status = "processing"
        import_file.status_message = None
        import_file.attempts = 0
        session.commit()

        # Datos del archivo
        file_path = import_file.filepath
        file_name = import_file.filename
        filetype = import_file.filetype

        # Determinar la función de procesamiento
        task_func = valid_import_file_types[filetype]

        # Bucle de intentos
        while import_file.attempts <= max_retries:
            try:
                status, status_info, import_resume = task_func(file_path, file_name, filetype, username)
                if status == 0:
                    # Exito
                    import_file = session.get(ImportFile, import_file_id)
                    import_file.status = "done"
                    import_file.status_message = import_resume
                    import_file.attempts += 1
                    date = datetime.now()
                    import_file.last_attempt = date
                    import_file.processed_at = date
                    session.commit()
                    
                    message = f"✅ <b>Importacion de {filetype.capitalize()}</b>\n{import_resume}"
                    send_alert(message, 0)
                    return True
                else:
                    # Error, comprobamos si toca reintentar
                    import_file = session.get(ImportFile, import_file_id)
                    import_file.attempts += 1
                    import_file.last_attempt = datetime.now()
                    if import_file.attempts > max_retries:
                        import_file.status = "failed"

                    import_file.status_message = status_info
                    session.commit()
                    
                    message = f"⚠️ <b>Importacion de {filetype.capitalize()}</b>\n{status_info}"
                    send_alert(message, 0)
                    
            except Exception as e:
                # Excepción inesperada
                import_file = session.get(ImportFile, import_file_id)
                import_file.attempts += 1
                import_file.last_attempt = datetime.now()
                if import_file.attempts > max_retries:
                    import_file.status = "failed"

                import_file.status_message = f"Error inesperado: {str(e)}"
                session.commit()
                
                message = f"❌ Error inesperado en la importación de <b>{filetype}</b>: {str(e)}"
                send_alert(message, 1)

        return False


def articles_dbf_to_csv(articles_dbf_path, articles_dbf_name, filetype):
    dbf_table = DBF(articles_dbf_path, encoding='latin1') # Read dbf as a table
    df = pd.DataFrame(iter(dbf_table)) # dbf table to pandas dataframe
    
    csv_path = os.path.join(DATA_ROUTE, f'no_filtered_{articles_dbf_name}.csv') # No filtered csv path
    df.to_csv(csv_path, index=False) # Save raw data as csv
    
    df = pd.read_csv(csv_path) # Read the csv data
    df.columns = df.columns.str.strip()
    
    # Convertir a string y quitar ".0" para columnas específicas
    columns_to_fix = ['CREF', 'CCODEBAR']
    for col in columns_to_fix:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
    
    selected_columns = article_column_to_attribute_map.keys()  # Set the needed columns from keys of defined map
    
    try:
        df_filtered = df[selected_columns] # Get selected columns
    except KeyError as e:
        missing_cols = list(set(selected_columns) - set(df.columns)) # Num missing columns
        raise KeyError(f"Las siguientes columnas faltan en el DataFrame: {missing_cols}") from e
    
    filtered_csv_path = os.path.join(DATA_ROUTE, f'{articles_dbf_name}.csv') # Filtered csv path
    df_filtered.to_csv(filtered_csv_path, index=False) # Save filtered csv data
    
    os.remove(csv_path) # Remove no filtered csv file
    
    pattern = os.path.join(DATA_ROUTE, f"{filetype}_*.csv") # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(filtered_csv_path)
        if file_name != new_file_name: # Remove all except the new one
            os.remove(file_)
    
    return filtered_csv_path


def validate_clean_article_data(row):
    """
    Valida y limpia los datos de una fila del artículo (pandas.Series).
    - Ref y Codebar deben contener solo dígitos (como texto).
    - El resto de campos se validan según reglas conocidas.
    """
    
    fixes = []  # Correcciones aplicadas
    errors = []  # Errores encontrados

    # === CCODEBAR ===
    codebar = row.get('CCODEBAR')
    if not isinstance(codebar, (int, str)):
        errors.append(f"El campo 'CCODEBAR' no es del tipo esperado (int, str): Type -> {type(codebar)}.")
    else:
        original = str(codebar).strip()
        cleaned = re.sub(r'\D', '', original)
        if not cleaned:
            errors.append("El campo 'CCODEBAR' está vacío o no contiene números.")
        elif cleaned != original:
            fixes.append("Se han eliminado caracteres no numéricos del campo 'CCODEBAR'.")
            row['CCODEBAR'] = cleaned
        else:
            row['CCODEBAR'] = original

    # === CREF ===
    ref = row.get('CREF')
    if not isinstance(ref, (int, str)):
        errors.append(f"El campo 'CREF' no es del tipo esperado (int, str): Type -> {type(ref)}.")
    else:
        original = str(ref).strip()
        cleaned = re.sub(r'\D', '', original)
        if not cleaned:
            errors.append("El campo 'CREF' está vacío o no contiene números.")
        elif cleaned != original:
            fixes.append("Se han eliminado caracteres no numéricos del campo 'CREF'.")
            row['CREF'] = cleaned
        else:
            row['CREF'] = original

    # === CDETALLE ===
    detalle = row.get('CDETALLE')
    if detalle is not None and (not isinstance(detalle, str) or len(detalle) > 100):
        errors.append("El campo 'CDETALLE' debe ser una cadena de texto de máximo 100 caracteres.")

    # === CCODFAM ===
    codfam = row.get('CCODFAM')
    try:
        if codfam is not None:
            row['CCODFAM'] = int(codfam)
    except (ValueError, TypeError):
        errors.append("El campo 'CCODFAM' debe ser un entero o nulo.")

    # === NCOSTEDIV y NPVP ===
    for key in ['NCOSTEDIV', 'NPVP']:
        value = row.get(key)
        try:
            if value is not None:
                value = float(value)
                if value >= 0:
                    # Corrige a 2 decimales ANTES de mandarlo al FLOAT de la BD
                    row[key] = round(value + 1e-9, 2)
                else:
                    errors.append(f"El campo '{key}' debe ser un número positivo.")
        except (ValueError, TypeError):
            errors.append(f"Error desconocido. El campo '{key}' debe ser un número positivo.")

    # === Resultado final ===
    if errors:
        return False, row, errors
    
    return True, row, fixes

# Para logs
def clean_nan_value(value):
    # pd.isna() retorna True para np.nan, None, etc.
    if pd.isna(value):
        return None
    return value

def update_articles(articles_dbf_path, articles_dbf_name, filetype, username):
    start_time = time.perf_counter() # Inicializar contador de tiempo
        
    articles_csv_path = articles_dbf_to_csv(articles_dbf_path, articles_dbf_name, filetype) # DBF to CSV
    import_id = str(uuid.uuid4()) # Genera uuid de importación para logs
    status = 0
    status_info = ''

    # Leer los datos del CSV
    articles_csv = None
    try:
        timeout = 5 # 5 segundos
        interval = 0.1 # 0.1 segundos
        while True:
            if os.path.exists(articles_csv_path) and os.path.getsize(articles_csv_path) > 0:
                break
            if time.perf_counter() - start_time > timeout:
                raise TimeoutError(f"El archivo {articles_csv_path} no estuvo disponible en {timeout} segundos.")
            time.sleep(interval)
        
        articles_csv = pd.read_csv(articles_csv_path)
    except Exception as e:
        status = 1
        status_info = f"Error al leer el CSV: {str(e)}"
    
    # Inicializar las que sirven para el log 
    # (Aunque de error general y esten vacías, poder guardar el import_log general)
    new_articles = []
    updated_articles = []
    deleted_articles = []
    duplicated_rows = []
    conflict_logs = []
    
    # Si se ha leído correctamente
    if articles_csv is not None and status == 0:
        try:
            clean_rows = []
            
            # Limpiamos los datos del CSV
            for _, row in articles_csv.iterrows():
                codebar = row.get('CCODEBAR')
                ref = row.get('CREF')
                detalle = row.get('CDETALLE')
                # Si no hay código de barras, se descarta directamente
                if pd.isna(codebar):
                    log_type = 2 # No CODEBAR
                    log_info = 'Código de barras ausente'
                    article_import_log = Article_import_log(import_id=import_id, type=log_type, ref=clean_nan_value(ref), codebar=None, detalle=clean_nan_value(detalle), info='Código de barras ausente')
                    conflict_logs.append(article_import_log)
                    continue
                
                # Validar y limpiar los datos de la fila
                is_valid, clean_row, logs_info = validate_clean_article_data(row)
                if not is_valid:
                    for log_info in logs_info:
                        log_type = 1 # NO Válido
                        article_import_log = Article_import_log(import_id=import_id, type=log_type, ref=clean_nan_value(ref), codebar=clean_nan_value(codebar), detalle=clean_nan_value(detalle), info=log_info)
                        conflict_logs.append(article_import_log)
                    continue
                else:
                    for log_info in logs_info:
                        log_type = 0 # Válido
                        article_import_log = Article_import_log(import_id=import_id, type=log_type, ref=clean_nan_value(ref), codebar=clean_nan_value(codebar), detalle=clean_nan_value(detalle), info=log_info)
                        conflict_logs.append(article_import_log)
                
                # Si es valida se añade a la nueva lista
                clean_rows.append(clean_row)
                
            # Crear un nuevo DataFrame con las filas limpias
            clean_articles_csv = pd.DataFrame(clean_rows, columns=articles_csv.columns)
            
            
            # Identificar filas duplicadas
            duplicated_rows = clean_articles_csv[clean_articles_csv.duplicated(subset=['CCODEBAR'], keep='first')]
            for _, row in duplicated_rows.iterrows():
                log_type = 3 # DUPLICADO
                log_info = 'Código de barras duplicado'
                article_import_log = Article_import_log(import_id=import_id, type=log_type, ref=clean_nan_value(row['CREF']), codebar=clean_nan_value(row['CCODEBAR']), detalle=clean_nan_value(row['CDETALLE']), info=log_info)
                conflict_logs.append(article_import_log)
                
            # Eliminar duplicados, manteniendo solo la primera ocurrencia
            clean_articles_csv = clean_articles_csv.drop_duplicates(subset=['CCODEBAR'], keep='first')
                
            
            # Cargamos todos los artículos existentes en la DB
            db_articles = {article.codebar: article for article in Article.query.all()}
            deleted_articles = set(db_articles.keys()) # Inicializamos los artículos a eliminar
            
            # Actualizar o crear los artículos en la DB
            new_articles = []
            updated_articles = []
            
            # Recorrer los artículos del CSV
            for _, article_csv in clean_articles_csv.iterrows():
                codebar = article_csv['CCODEBAR']
                
                # Si el artículo ya existe, se actualiza
                if codebar in db_articles:
                    article_db = db_articles[codebar] # Obtener el artículo de la lista de la DB
                    deleted_articles.remove(codebar) # Eliminar de la lista de articulos a eliminar
                    
                    changes = {}
                    for col, attr in article_column_to_attribute_map.items():
                        if col != 'CCODEBAR': # Filtramos el codebar (simpre coincidirán)
                            new_value = article_csv[col] # Valor 'nuevo' del CSV
                            db_value = getattr(article_db, attr) # Valor actual en la DB
                            
                            # Convertir la fecha a string sin la hora, para comparar con el CSV
                            if attr == 'factualizacion':
                                db_value = db_value.strftime('%Y-%m-%d')
                                
                            # Si cambia el valor, se guarda en 'changes'
                            if new_value != db_value:
                                changes[attr] = new_value
                            
                    # Si hay cambios, se actualiza el artículo y se guarda en la lista de actualizados
                    if changes:
                        for attr, new_value in changes.items():
                            setattr(article_db, attr, new_value)
                        updated_articles.append(article_db)
                        
                else:
                    # Inserta como nuevo artículo 
                    article = Article(
                        ref=article_csv['CREF'],
                        detalle=article_csv['CDETALLE'],
                        codfam=article_csv['CCODFAM'],
                        pcosto=article_csv['NCOSTEDIV'],
                        pvp=article_csv['NPVP'],
                        codebar=article_csv['CCODEBAR'],
                        factualizacion=article_csv['DACTUALIZA']
                    )
                    new_articles.append(article)
                
            # Aplicar cambios en la base de datos
            try:
                session = db.session
                session.add_all(new_articles) # Insertar los nuevos artículos
                session.add_all(updated_articles) # Actualizar los artículos modificados 

                for codebar in deleted_articles:
                    session.delete(db_articles[codebar]) # Eliminar los artículos que ya no existen
                    
                session.commit() # Confirmar los cambios
                
                status_info = "Importación completada con exito."
            except SQLAlchemyError as e:
                session.rollback()
                status = 1
                status_info = f"Error en la base de datos: {str(e)}"
            finally:
                session.close()
                
        except Exception as e:
            status = 1
            status_info = f"Error inesperado procesando los datos: {str(e)}"
        
        
    # Calcular tiempo de ejecución
    end_time = time.perf_counter()
    elapsed_time = round((end_time - start_time), 2)
    
    # Log resumen
    import_resume = f'Tiempo: {elapsed_time}s.\nNuevos: {len(new_articles)}, Actualizados: {len(updated_articles)}, Eliminados: {len(deleted_articles)}, Duplicados: {len(duplicated_rows)}, Errores: {len(conflict_logs)}'
    print(status_info)
    print(import_resume)
    
    # Save LOGs
    save_article_import_log(
        import_id, 
        username, 
        status, 
        status_info, 
        len(new_articles), 
        len(updated_articles), 
        len(deleted_articles), 
        len(duplicated_rows), 
        conflict_logs, 
        elapsed_time, 
        articles_csv_path
    ) 
        
    return status, status_info, import_resume
        
        
def save_article_import_log(import_id, user, status, info, n_new, n_updated, n_deleted, n_duplicated, conflict_logs, elapsed_time, articles_csv_path):
    # Get user id of the user who made the import
    user = User.query.filter(User.username==user['username']).first()
    user_id = user.id
    
    if user_id is not None:
        # Create article_import object with import info
        article_import = Article_import(
            id=import_id, 
            user_id=user_id,
            status=status,
            info=info,
            new_rows=n_new, 
            updated_rows=n_updated, 
            deleted_rows=n_deleted, 
            duplicated_rows=n_duplicated,
            errors=len(conflict_logs),
            corrected=len([log for log in conflict_logs if log.type == 0]), # Count corrected logs
            elapsed_time=elapsed_time
        )
        
        # Save logs in the DB
        try:
            session = db.session
            
            # Save article import first, then save the logs associated
            session.add(article_import)
            session.commit()
            
            # Save conflict logs
            session.add_all(conflict_logs)
            session.commit()
            
            print(f"Se han guardado los logs en la DB")
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error al guardar logs de la importación en la DB: {str(e)}")
    
    os.makedirs(DATA_LOGS_ROUTE, exist_ok=True)
    
    # Save logs in CSV file
    log_file_path = os.path.join(DATA_LOGS_ROUTE, f"conflicts_{os.path.basename(articles_csv_path)}")

    # Extraer atributos de cada objeto Article_import_log y construir una lista de diccionarios
    log_records = []
    for log in conflict_logs:
        log_records.append({
            'import_id': log.import_id,
            'type': log.type,
            'ref': log.ref,
            'codebar': log.codebar,
            'detalle': log.detalle,
            'info': log.info,
        })

    # Crear un DataFrame a partir de la lista de diccionarios
    df_logs = pd.DataFrame(log_records)

    # Guardar el DataFrame en un archivo CSV
    df_logs.to_csv(log_file_path, index=False, encoding='utf-8')

    # Delete old conflict logs
    pattern = os.path.join(f"{str.split(log_file_path,'_')[0]}_{str.split(log_file_path,'_')[1]}_*.csv")  # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(log_file_path)
        if file_name != new_file_name:  # Remove all except the new one
            os.remove(file_)
            
    print(f"Conflictos guardados en {log_file_path}")
        
    

def families_dbf_to_csv(families_dbf_path, families_dbf_name, filetype):
    dbf_table = DBF(families_dbf_path, encoding='latin1')
    df = pd.DataFrame(iter(dbf_table))
    
    csv_path = os.path.join(DATA_ROUTE, f'no_filtered_{families_dbf_name}.csv')
    df.to_csv(csv_path, index=False)
    
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    selected_columns = ['CCODFAM', 'CNOMFAM']
    
    try:
        df_filtered = df[selected_columns]
    except KeyError as e:
        missing_cols = list(set(selected_columns) - set(df.columns))
        raise KeyError(f"Las siguientes columnas faltan en el DataFrame: {missing_cols}") from e
    
    filtered_csv_path = DATA_ROUTE + families_dbf_name + '.csv'
    df_filtered.to_csv(filtered_csv_path, index=False)
    
    os.remove(csv_path) # Remove no filtered csv file
    
    pattern = os.path.join(DATA_ROUTE, f"{filetype}_*.csv") # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(filtered_csv_path)

        if file_name != new_file_name: # Remove all except the new one
            os.remove(file_)
    
    return filtered_csv_path

    
def update_families(families_dbf_path, families_dbf_name, filetype, username):
    start_time = time.perf_counter() # Inicializar contador de tiempo
    families_csv_path = families_dbf_to_csv(families_dbf_path, families_dbf_name, filetype) # DBF to CSV
    
    status = 0
    status_info = ''
    
    families_csv = None
    try:
        timeout = 5 # 5 segundos
        interval = 0.1 # 0.1 segundos
        while True:
            if os.path.exists(families_csv_path) and os.path.getsize(families_csv_path) > 0:
                break
            if time.perf_counter() - start_time > timeout:
                raise TimeoutError(f"El archivo {families_csv_path} no estuvo disponible en {timeout} segundos.")
            time.sleep(interval)
        
        families_csv = pd.read_csv(families_csv_path) # Read CSV    
    except Exception as e:
        status = 1
        status_info = f"Error al leer el CSV: {str(e)}"

    new_families = []
    updated_families = []
    deleted_families = []

    if families_csv is not None:
        try:
            # Cargamos todos los artículos existentes en la DB
            db_families = {family.codfam: family for family in Family.query.all()}
            deleted_families = set(db_families.keys()) # Inicializamos las familias a eliminar
            
            # Recorrer las familias del CSV
            for _, row in families_csv.iterrows():
                codfam = row['CCODFAM']
                
                # Si ya existe en la DB
                if codfam in db_families:
                    family_db = db_families[codfam]
                    deleted_families.remove(codfam) # Eliminar de la lista a elimin
                    
                    # Si cambia el nombre, se actualiza                
                    if row['CNOMFAM'] != family_db.nomfam:
                        setattr(family_db, 'nomfam', row['CNOMFAM'])
                        updated_families.append(family_db) # Guardar en la lista de actualizados
                else:
                    # Insertar como nueva familia
                    family = Family(
                        codfam=row['CCODFAM'], 
                        nomfam=row['CNOMFAM']
                    )
                    new_families.append(family)
                    
            # Aplicar cambios en la base de datos
            try:
                session = db.session
                session.add_all(new_families) # Insertar nuevas
                session.add_all(updated_families) # Actualizar modificadas 

                for codfam in deleted_families:
                    session.delete(db_families[codfam]) # Eliminar las que ya no existen
                    
                session.commit() # Confirmar los cambios
                
                status_info = "Importación completada con exito."
            except SQLAlchemyError as e:
                session.rollback()
                status = 1
                status_info = f"Error en la base de datos: {str(e)}"
            finally:
                session.close()
        
        except Exception as e:
            status = 1
            status_info = f"Error inesperado procesando los datos: {str(e)}"
            
            
    # Calcular tiempo de ejecución
    end_time = time.perf_counter()
    elapsed_time = round((end_time - start_time), 2)
    
    # Log resumen
    import_resume = f'Tiempo: {elapsed_time}s.\nNuevas: {len(new_families)}, Actualizadas: {len(updated_families)}, Eliminadas: {len(deleted_families)}'
    print(status_info)
    print(import_resume)
    
    return status, status_info, import_resume        


def stocks_dbf_to_csv(stocks_dbf_path, stocks_dbf_name, filetype):
    dbf_table = DBF(stocks_dbf_path, encoding='latin1')
    df = pd.DataFrame(iter(dbf_table))

    csv_path = os.path.join(DATA_ROUTE, f'no_filtered_{stocks_dbf_name}.csv')
    df.to_csv(csv_path, index=False)
    
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    selected_columns = ['CREF', 'NSTOCK']
    
    try:
        df_filtered = df[selected_columns]
    except KeyError as e:
        missing_cols = list(set(selected_columns) - set(df.columns))
        raise KeyError(f"Las siguientes columnas faltan en el DataFrame: {missing_cols}") from e
    
    filtered_csv_path = DATA_ROUTE + stocks_dbf_name + '.csv'
    df_filtered.to_csv(filtered_csv_path, index=False)
    
    os.remove(csv_path) # Remove no filtered csv file
    
    pattern = os.path.join(DATA_ROUTE, f"{filetype}_*.csv") # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(filtered_csv_path)

        if file_name != new_file_name: # Remove all except the new one
            os.remove(file_)
    
    return filtered_csv_path

import re

def validate_clean_stocks_data(row):
    fixes = []  # Lista de correcciones realizadas
    errors = []  # Lista de errores encontrados
    
    # === CREF ===
    ref = row.get('CREF')
    if not isinstance(ref, (int, str)):
        errors.append(f"El campo 'CREF' no es del tipo esperado (int, str): Type -> {type(ref)}.")
    else:
        original = str(ref).strip()
        cleaned = re.sub(r'\D', '', original)
        if not cleaned:
            errors.append("El campo 'CREF' está vacío o no contiene números.")
        elif cleaned != original:
            fixes.append("Se han eliminado caracteres no numéricos del campo 'CREF'.")
            row['CREF'] = cleaned
        else:
            row['CREF'] = original

    # === NSTOCK ===
    stock = row.get('NSTOCK')
    try:
        if stock is not None:
            row['NSTOCK'] = int(stock)
    except (ValueError, TypeError):
        errors.append("El campo 'NSTOCK' debe ser un entero o nulo.")

    if errors:
        return False, row, errors
    
    return True, row, fixes

def update_stocks(stocks_dbf_path, stocks_dbf_name,  filetype, username):
    start_time = time.perf_counter() # Inicializar contador de tiempo
    stocks_csv_path = stocks_dbf_to_csv(stocks_dbf_path, stocks_dbf_name, filetype) # DBF to CSV
    
    status = 0
    status_info = ''

    # Leer los datos del CSV
    stocks_csv = None
    try:
        timeout = 5 # 5 segundos
        interval = 0.1 # 0.1 segundos
        while True:
            if os.path.exists(stocks_csv_path) and os.path.getsize(stocks_csv_path) > 0:
                break
            if time.perf_counter() - start_time > timeout:
                raise TimeoutError(f"El archivo {stocks_csv_path} no estuvo disponible en {timeout} segundos.")
            time.sleep(interval)
        
        stocks_csv = pd.read_csv(stocks_csv_path)
    except Exception as e:
        status = 1
        status_info = f"Error al leer el CSV: {str(e)}"
    
    updated_article_stocks = []
    errors = 0
    
    if stocks_csv is not None:
        try:
            # Cargamos todos los artículos de la DB
            db_articles = {article.ref: article for article in Article.query.all()}

            # Recorremos todos los stocks del CSV
            for _, row in stocks_csv.iterrows():
                ref = row['CREF']
                
                # Si no hay referencia, se descarta directamente
                if pd.isna(ref):
                    errors += 1
                    continue
                
                # Validar y limpiar los datos de la fila
                is_valid, clean_row, logs_info = validate_clean_stocks_data(row)
                if not is_valid:
                    # Si no es valida se descarta
                    errors += 1
                    continue
                
                ref = clean_row['CREF']
                
                # Si existe el articulo, se actualiza su stock
                if ref in db_articles:
                    article_db = db_articles[ref]
                    if clean_row['NSTOCK'] != article_db.stock:
                        setattr(article_db, 'stock', row['NSTOCK'])
                        updated_article_stocks.append(article_db)
            
            
            # Aplicar cambios en la base de datos
            try:
                session = db.session
                session.add_all(updated_article_stocks) # Actualizar modificados 
                    
                session.commit() # Confirmar los cambios
                
                status_info = "Importación completada con exito."
            except SQLAlchemyError as e:
                session.rollback()
                status = 1
                status_info = f"Error en la base de datos: {str(e)}"
            finally:
                session.close()
        
        except Exception as e:
            status = 1
            status_info = f"Error inesperado procesando los datos: {str(e)}"
    
    
    # Calcular tiempo de ejecución
    end_time = time.perf_counter()
    elapsed_time = round((end_time - start_time), 2)
    
    # Log resumen
    import_resume = f'Tiempo: {elapsed_time}s.\nActualizados: {len(updated_article_stocks)}, Errores: {errors}.'
    print(status_info)
    print(import_resume)
    
    return status, status_info, import_resume


def cierre_dbf_to_csv(cierre_dbf_path, cierre_dbf_name, filetype):
    dbf_table = DBF(cierre_dbf_path, encoding='latin1')
    df = pd.DataFrame(iter(dbf_table))
    
    csv_path = os.path.join(DATA_ROUTE, f'no_filtered_{cierre_dbf_name}.csv')
    df.to_csv(csv_path, index=False)

    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    selected_columns = ['DFECHA', 'NCONTADOR', 'CHORA', 'NTICKINI', 'NTICKFIN', 'NTOTAL', 'NSALDOANT', 'NSALDOACT']

    try:
        df_filtered = df[selected_columns].copy()
    except KeyError as e:
        missing_cols = list(set(selected_columns) - set(df.columns))
        raise KeyError(f"Las siguientes columnas faltan en el DataFrame: {missing_cols}") from e

    # Parseamos fechas como datetime para detectar errores
    df_filtered['parsed_date'] = pd.to_datetime(df_filtered['DFECHA'], errors='coerce')

    # Detectar año más común
    common_year = df_filtered['parsed_date'].dropna().dt.year.mode()[0]
    current_year = datetime.now().year

    def fix_date(date):
        if pd.isna(date):
            return None
        year = date.year
        if year < current_year - 50:
            return date.replace(year=common_year)
        return date

    # Aplicar la corrección
    df_filtered['parsed_date'] = df_filtered['parsed_date'].apply(fix_date)

    # Eliminar filas no corregibles
    df_filtered = df_filtered[df_filtered['parsed_date'].notna()]

    # Reconstruir fecha como string
    df_filtered['DFECHA'] = df_filtered['parsed_date']

    # Eliminar columna temporal
    df_filtered.drop(columns=['parsed_date'], inplace=True)

    filtered_csv_path = DATA_ROUTE + cierre_dbf_name + '.csv'
    df_filtered.to_csv(filtered_csv_path, index=False)

    os.remove(csv_path) # Remove no filtered csv file
    
    pattern = os.path.join(DATA_ROUTE, f"{filetype}_*.csv") # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(filtered_csv_path)
        if file_name != new_file_name:
            os.remove(file_)
    
    return filtered_csv_path

def update_cierre(cierre_dbf_path, cierre_dbf_name, filetype, username):
    start_time = time.perf_counter()
    cierre_csv_path = cierre_dbf_to_csv(cierre_dbf_path, cierre_dbf_name, filetype)

    timeout = 5.0   # segundos
    interval = 0.1  # segundos
    while True:
        if os.path.exists(cierre_csv_path) and os.path.getsize(cierre_csv_path) > 0:
            break
        if time.perf_counter() - start_time > timeout:
            raise TimeoutError(f"El CSV {cierre_csv_path} no estuvo disponible en {timeout}s")
        time.sleep(interval)

    df = pd.read_csv(cierre_csv_path)

    # Inicializamos estado
    status = 0
    status_info = ''
    inserted = 0
    errors = 0

    # Parseamos la fecha y hora
    df['parsed_date'] = pd.to_datetime(df['DFECHA'], errors='coerce').dt.date
    df['parsed_time'] = pd.to_datetime(df['CHORA'], format='%H:%M', errors='coerce').dt.time
    
    # Ahora reasignamos el counter para evitar duplicados según fecha y hora
    df_sorted = df.sort_values(by=['parsed_date', 'parsed_time'])
    
    # Creamos un nuevo counter por fecha basado en orden horario
    df_sorted['new_counter'] = df_sorted.groupby('parsed_date').cumcount() + 1
    
    # Recogemos las claves existentes para evitar insertar duplicados
    existing_keys = set(
        (row.date, row.counter)
        for row in DailySales.query.with_entities(DailySales.date, DailySales.counter).all()
    )
    
    new_records = []
    errors = 0
    for _, row in df_sorted.iterrows():
        try:
            date_ = row['parsed_date']
            time_ = row['parsed_time']
            counter_ = int(row['new_counter'])
            
            if (date_, counter_) in existing_keys:
                # Si existe, saltar
                continue

            record = DailySales(
                date=date_,
                counter=counter_,
                time=time_,
                first_ticket=int(row['NTICKINI']),
                last_ticket=int(row['NTICKFIN']),
                total_sold=float(row['NTOTAL']),
                previous_balance=float(row['NSALDOANT']),
                current_balance=float(row['NSALDOACT'])
            )
            new_records.append(record)
        except Exception:
            errors += 1

    session = db.session
    try:
        session.add_all(new_records)
        session.commit()
        inserted = len(new_records)
        status_info = f"Importación completada con exito"
    except SQLAlchemyError as e:
        session.rollback()
        status = 1
        status_info = f"Error en base de datos: {e}"
    finally:
        session.close()

    elapsed = round(time.perf_counter() - start_time, 2)
    resume = f"Tiempo: {elapsed}s. Insertados: {inserted}. Errores: {errors}."

    return status, status_info, resume


def movimt_dbf_to_csv(movimt_dbf_path, movimt_dbf_name, filetype):
    dbf_table = DBF(movimt_dbf_path, encoding='latin1')
    df = pd.DataFrame(iter(dbf_table))
    
    csv_path = os.path.join(DATA_ROUTE, f'no_filtered_{movimt_dbf_name}.csv')
    df.to_csv(csv_path, index=False)
    
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    selected_columns = ['NNUMTICKET', 'DFECHA', 'NIMPORTE', 'DFECCIERRE']
    
    try:
        df_filtered = df[selected_columns].copy()
    except KeyError as e:
        missing_cols = list(set(selected_columns) - set(df.columns))
        raise KeyError(f"Las siguientes columnas faltan en el DataFrame: {missing_cols}") from e

    # Parseamos fechas como datetime para detectar errores
    df_filtered['parsed_date'] = pd.to_datetime(df_filtered['DFECCIERRE'], errors='coerce')

    # Detectar año más común
    common_year = df_filtered['parsed_date'].dropna().dt.year.mode()[0]
    current_year = datetime.now().year

    def fix_date(date):
        if pd.isna(date):
            return None
        year = date.year
        if year < current_year - 50:
            return date.replace(year=common_year)
        return date

    # Aplicar la corrección
    df_filtered['parsed_date'] = df_filtered['parsed_date'].apply(fix_date)

    # Eliminar filas no corregibles
    df_filtered = df_filtered[df_filtered['parsed_date'].notna()]

    # Reconstruir fecha como string
    df_filtered['DFECCIERRE'] = df_filtered['parsed_date']

    # Eliminar columna temporal
    df_filtered.drop(columns=['parsed_date'], inplace=True)

    
    filtered_csv_path = DATA_ROUTE + movimt_dbf_name + '.csv'
    df_filtered.to_csv(filtered_csv_path, index=False)
    
    os.remove(csv_path) # Remove no filtered csv file
    
    pattern = os.path.join(DATA_ROUTE, f"{filetype}_*.csv") # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(filtered_csv_path)

        if file_name != new_file_name: # Remove all except the new one
            os.remove(file_)
    
    return filtered_csv_path

def update_movimt(movimt_dbf_path, movimt_dbf_name, filetype, username):
    start_time = time.perf_counter()
    movimt_csv_path = movimt_dbf_to_csv(movimt_dbf_path, movimt_dbf_name, filetype)

    status = 0
    status_info = ''
    import_resume = ''

    new_tickets = []
    unprocessed_tickets = 0
    errors = 0

    try:
        timeout = 5
        interval = 0.1
        while True:
            if os.path.exists(movimt_csv_path) and os.path.getsize(movimt_csv_path) > 0:
                break
            if time.perf_counter() - start_time > timeout:
                raise TimeoutError(f"El archivo {movimt_csv_path} no estuvo disponible en {timeout} segundos.")
            time.sleep(interval)

        movimt_csv = pd.read_csv(movimt_csv_path)

        # Convertimos la columna NNUMTICKET a int y eliminamos nulos
        movimt_csv = movimt_csv.dropna(subset=['NNUMTICKET'])

        # Obtenemos los tickets que ya existen
        existing_tickets = {
            ticket.number for ticket in Ticket.query.with_entities(Ticket.number).all()
        }
                
        # Agrupar por número de ticket y fecha (por si hay duplicados por día)
        movimt_csv = movimt_csv.groupby(['NNUMTICKET', 'DFECHA'], as_index=False).agg({
            'NIMPORTE': 'sum',
            'DFECCIERRE': 'first'
        })
        
        for _, row in movimt_csv.iterrows():
            try:
                ticket_number = int(row['NNUMTICKET'])

                if ticket_number in existing_tickets:
                    continue  # Ya está en la base de datos
                
                # Si la fecha de cierre no está definida, lo dejamos para la próxima
                if pd.notna(row['DFECCIERRE']):
                    closed_at = pd.to_datetime(row['DFECCIERRE']).date()
                else:
                    unprocessed_tickets += 1
                    continue

                new_ticket = Ticket(
                    number=ticket_number,
                    date=pd.to_datetime(row['DFECHA']).date(),
                    amount=float(row['NIMPORTE']),
                    closed_at=closed_at,
                )

                new_tickets.append(new_ticket)

            except Exception as e:
                print(f"Error procesando fila: {row}. Error: {str(e)}")
                errors += 1
                continue

        # Insertar nuevos tickets
        try:
            session = db.session
            session.add_all(new_tickets)
            session.commit()
            status_info = "Importación de tickets completada con exito."
        except SQLAlchemyError as e:
            session.rollback()
            status = 1
            status_info = f"Error en la base de datos: {str(e)}"
        finally:
            session.close()

    except Exception as e:
        status = 1
        status_info = f"Error inesperado al procesar el archivo: {str(e)}"

    end_time = time.perf_counter()
    elapsed_time = round(end_time - start_time, 2)
    import_resume = f'Tiempo: {elapsed_time}s.\nInsertados: {len(new_tickets)}, No procesados: {unprocessed_tickets}, Errores: {errors}.'
    
    return status, status_info, import_resume


def hticketl_dbf_to_csv(hticketl_dbf_path, hticketl_dbf_name, filetype):
    dbf_table = DBF(hticketl_dbf_path, encoding='latin1')
    df = pd.DataFrame(iter(dbf_table))

    csv_path = os.path.join(DATA_ROUTE, f'no_filtered_{hticketl_dbf_name}.csv')
    df.to_csv(csv_path, index=False)
    
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    
    # Convertir a string y quitar ".0" para columnas específicas
    columns_to_fix = ['CCODBAR','CREF']
    for col in columns_to_fix:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
    
    selected_columns = ['NNUMTICKET', 'CCODBAR', 'CREF', 'CDETALLE', 'NCANT', 'NPREUNIT']
    
    try:
        df_filtered = df[selected_columns]
    except KeyError as e:
        missing_cols = list(set(selected_columns) - set(df.columns))
        raise KeyError(f"Las siguientes columnas faltan en el DataFrame: {missing_cols}") from e
    
    filtered_csv_path = DATA_ROUTE + hticketl_dbf_name + '.csv'
    df_filtered.to_csv(filtered_csv_path, index=False)
    
    os.remove(csv_path) # Remove no filtered csv file
    
    pattern = os.path.join(DATA_ROUTE, f"{filetype}_*.csv") # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(filtered_csv_path)

        if file_name != new_file_name: # Remove all except the new one
            os.remove(file_)
    
    return filtered_csv_path

def validate_clean_hticketl_data(row):    
    fixes = [] # Lista de erorres corregidos
    errors = []
    
    # === CCODBAR ===
    codebar = row.get('CCODBAR')
    if not isinstance(codebar, (int, str)):
        errors.append(f"El campo 'CCODBAR' no es del tipo esperado (int, str): Type -> {type(codebar)}.")
    else:
        original = str(codebar).strip()
        cleaned = re.sub(r'\D', '', original)
        if not cleaned:
            errors.append("El campo 'CCODBAR' está vacío o no contiene números.")
        elif cleaned != original:
            fixes.append("Se han eliminado caracteres no numéricos del campo 'CCODBAR'.")
            row['CCODBAR'] = cleaned
        else:
            row['CCODBAR'] = original

    # === CREF ===
    ref = row.get('CREF')
    if not isinstance(ref, (int, str)):
        errors.append(f"El campo 'CREF' no es del tipo esperado (int, str): Type -> {type(ref)}.")
    else:
        original = str(ref).strip()
        cleaned = re.sub(r'\D', '', original)
        if not cleaned:
            errors.append("El campo 'CREF' está vacío o no contiene números.")
        elif cleaned != original:
            fixes.append("Se han eliminado caracteres no numéricos del campo 'CREF'.")
            row['CREF'] = cleaned
        else:
            row['CREF'] = original
    
    # CDETALLE: cadena de hasta 100 caracteres, puede contener cualquier carácter UTF-8
    detalle = row.get('CDETALLE')
    if detalle is not None and (not isinstance(detalle, str) or len(detalle) > 100):
        errors.append("El campo 'CDETALLE' debe ser una cadena de texto de máximo 100 caracteres.")
        
    # === NPREUNIT ===
    for key in ['NPREUNIT']:
        value = row.get(key)
        try:
            if value is not None:
                value = float(value)
                if value >= 0:
                    row[key] = math.trunc(value * 100) / 100  # Truncar a 2 decimales
                else:
                    errors.append(f"El campo '{key}' debe ser un número positivo.")
        except (ValueError, TypeError):
            errors.append(f"Error desconocido. El campo '{key}' debe ser un número positivo.")
        
    return True, row, fixes

def update_hticketl(hticketl_dbf_path, hticketl_dbf_name, filetype, username):
    start_time = time.perf_counter()
    hticketl_csv_path = hticketl_dbf_to_csv(hticketl_dbf_path, hticketl_dbf_name, filetype)

    status = 0
    status_info = ''
    import_resume = ''

    hticketl_csv = None
    try:
        timeout = 5
        interval = 0.1
        while True:
            if os.path.exists(hticketl_csv_path) and os.path.getsize(hticketl_csv_path) > 0:
                break
            if time.perf_counter() - start_time > timeout:
                raise TimeoutError(f"El archivo {hticketl_csv_path} no estuvo disponible en {timeout} segundos.")
            time.sleep(interval)

        hticketl_csv = pd.read_csv(hticketl_csv_path)
    except Exception as e:
        status = 1
        status_info = f"Error al leer el CSV: {str(e)}"
        return status, status_info, import_resume

    new_items = []
    errors = 0
    format_errors = 0
    unprocessed_ticket_items = 0
    total_inserted = 0

    try:
        session = db.session
        clean_rows = []
            
        # Limpiamos los datos del CSV
        for _, row in hticketl_csv.iterrows():
            # Validar y limpiar los datos de la fila
            is_valid, clean_row, logs_info = validate_clean_hticketl_data(row)
            if not is_valid:
                format_errors += 1
                continue
            else:
                # Si es valida se añade a la nueva lista
                clean_rows.append(clean_row)
            
        # Crear un nuevo DataFrame con las filas limpias
        clean_hticketl_csv = pd.DataFrame(clean_rows, columns=hticketl_csv.columns)
        
        # Elimina ".0"
        for col in ['CCODBAR', 'CREF']:
            if col in clean_hticketl_csv.columns:
                clean_hticketl_csv[col] = (
                    clean_hticketl_csv[col]
                    .astype(str)
                    .str.rstrip('.0')
                    .replace({'nan': None, 'None': None})
                )

        # Obtener tickets válidos
        existing_tickets = {ticket.number for ticket in Ticket.query.with_entities(Ticket.number).all()}
        
        # Obtener combinaciones existentes
        existing_items = {
            (item.ticket_number, item.codebar)
            for item in TicketItem.query.with_entities(TicketItem.ticket_number, TicketItem.codebar).all()
        }
        
        for _, row in clean_hticketl_csv.iterrows():

            try:
                ticket_number=int(row['NNUMTICKET'])
                codebar=row['CCODBAR'] if not pd.isna(row['CCODBAR']) else None # Puede ser None
                ref=row['CREF'] if not pd.isna(row['CREF']) else None # Puede ser None
                detalle=str(row['CDETALLE']).strip() if not pd.isna(row['CDETALLE']) else None # Puede ser None
                quantity=int(row['NCANT'])
                unit_price=row['NPREUNIT']

                if ticket_number not in existing_tickets or codebar is None:
                    unprocessed_ticket_items += 1
                    continue

                key = (ticket_number, codebar) # Claves del csv
                if key in existing_items:
                    continue  # Ya existe, no lo insertamos

                item = TicketItem(
                    ticket_number=ticket_number,
                    codebar=codebar,
                    ref=ref,
                    detalle=detalle,
                    quantity=quantity,
                    unit_price=unit_price
                )

                new_items.append(item)
                existing_items.add(key)
                total_inserted += 1

            except Exception:
                errors += 1
                continue

        session.add_all(new_items)
        session.commit()

        status_info = "Articulos de tickets actualizados correctamente."
    except SQLAlchemyError as e:
        session.rollback()
        status = 1
        status_info = f"Error en la base de datos: {str(e)}"
    except Exception as e:
        status = 1
        status_info = f"Error inesperado al procesar el archivo: {str(e)}"
    finally:
        session.close()

    end_time = time.perf_counter()
    elapsed = round(end_time - start_time, 2)
    import_resume = f"Tiempo: {elapsed}s.\n Insertados: {total_inserted}, No procesados: {unprocessed_ticket_items}, Errores: {errors}, Errores de formato: {format_errors}."

    return status, status_info, import_resume