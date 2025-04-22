import os, time, glob, re, math, uuid
import pandas as pd
from dbfread import DBF
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Article, Family, Article_import_log, Article_import, DailySales, User, Ticket

from app.config import UPLOAD_ROUTE, DATA_ROUTE, DATA_LOGS_ROUTE


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


def articles_dbf_to_csv(articles_dbf):
    dbf_table = DBF(os.path.join(UPLOAD_ROUTE, articles_dbf), encoding='latin1') # Read dbf as a table
    df = pd.DataFrame(iter(dbf_table)) # dbf table to pandas dataframe
    
    articles_dbf_name, extension = os.path.splitext(articles_dbf) # Clean (with date) filename and extension
    clean_articles_dbf_name = str.split(articles_dbf_name,'_')[0]
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
    
    pattern = os.path.join(DATA_ROUTE, f"{clean_articles_dbf_name}_*.csv") # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(filtered_csv_path)
        if file_name != new_file_name: # Remove all except the new one
            os.remove(file_)
    
    return filtered_csv_path


def validate_clean_article_data(row):
    """
    Valida y limpia los datos de una fila del artículo en formato pandas.Series.
    - Verifica que los valores cumplan con los tipos de datos y el formato.
    - Si no son válidos, se intentan corregir
    """
    
    fixes = [] # Lista de erorres corregidos
    errors = []
    
    # CCODEBAR: debe ser un entero positivo y único
    codebar = row.get('CCODEBAR')
    
    if not isinstance(codebar, (int, str)): # Si no es valido lanzamos error
        errors.append(f"El campo 'CCODEBAR' no es del tipo esperado (int, str): Type -> {type(codebar)}.")
    else: # Si es valido...
        try:
            row['CCODEBAR'] = int(codebar) # Convertimos a entero y modificamos el valor original
        except: # Intentamos limpieza
            clean_codebar = codebar.split('.')[0] #  Eliminar decimales (BUG de .0 a la derecha)
            clean_codebar = re.sub(r'\D', '', str(clean_codebar)).strip() # Eliminar espacios y caracteres no numéricos

            # Verificar si después de limpiar hay un valor válido
            if not clean_codebar:
                errors.append("El campo 'CCODEBAR' debe ser un entero positivo.")
            else:
                # Si ha cambiado el valor original...
                if codebar != clean_codebar:
                    try:
                        row['CCODEBAR'] = int(clean_codebar) # Convertimos a entero y modificamos el valor original
                        
                        fixes.append(f"Se ha corregido el campo 'CCODEBAR'") # Se añade la corrección a la lsita    
                    except ValueError:
                        errors.append("El campo 'CCODEBAR' debe ser un entero positivo.") # Se añade el error al la lista
                        
    
    # CREF debe ser un entero positivo
    ref = row.get('CREF')
    
    if not isinstance(ref, (int, str)): # Si no es valido lanzamos error
        errors.append(f"El campo 'CREF' no es del tipo esperado (int, str): Type -> {type(ref)}.")
    else: # Si es valido...
        try:
            row['CREF'] = int(ref) # Convertimos a entero y modificamos el valor original
        except: # Intentamos limpieza
            clean_ref = ref.split('.')[0] #  Eliminar decimales (BUG de .0 a la derecha)
            clean_ref = re.sub(r'\D', '', str(clean_ref)).strip() # Eliminar espacios y caracteres no numéricos

            # Verificar si después de limpiar hay un valor válido
            if not clean_ref:
                errors.append("El campo 'CREF' debe ser un entero positivo.")
            else:
                # Si ha cambiado el valor original...
                if ref != clean_ref:
                    try:
                        row['CREF'] = int(clean_ref) # Convertimos a entero y modificamos el valor original
                        
                        fixes.append(f"Se ha corregido el campo 'CREF'") # Se añade la corrección a la lsita    
                    except ValueError:
                        errors.append("El campo 'CREF' debe ser un entero positivo.") # Se añade el error al la lista

    
    # CDETALLE: cadena de hasta 50 caracteres, puede contener cualquier carácter UTF-8
    detalle = row.get('CDETALLE')
    if detalle is not None and (not isinstance(detalle, str) or len(detalle) > 50):
        errors.append("El campo 'CDETALLE' debe ser una cadena de texto de máximo 50 caracteres.")
    
    
    # CCODFAM: debe ser un entero, puede ser nulo
    codfam = row.get('CCODFAM')
    try:
        if codfam is not None:
            row['CCODFAM'] = int(codfam)
    except (ValueError, TypeError):
        errors.append("El campo 'CCODFAM' debe ser un entero o nulo.")


    # NCOSTEDIV y NPVP: deben ser flotantes y positivos
    for key in ['NCOSTEDIV', 'NPVP']:
        value = row.get(key)
        try:
            if value is not None and row[key] >= 0:
                value = float(value)  # Convertir a float
                row[key] = math.trunc(value * 100) / 100 # Truncar a 2 decimales y actualizar
            else:
                errors.append(f"El campo '{key}' debe ser un número positivo.")
        except (ValueError, TypeError):
            errors.append(f"Error desconocido. El campo '{key}' debe ser un número positivo.")
            
    # Si ha habido errores, devolver False y los errores encontrados
    if len(errors) > 0:
        return False, row, errors

    # Si todo está bien, devolver True, los datos corregidos y las correcciones realizadas
    return True, row, fixes

# Para logs
def clean_nan_value(value):
    # pd.isna() retorna True para np.nan, None, etc.
    if pd.isna(value):
        return None
    return value

def update_articles(articles_dbf, user):
    start_time = time.perf_counter() # Inicializar contador de tiempo
    
    articles_csv_path = articles_dbf_to_csv(articles_dbf) # DBF to CSV
    import_id = str(uuid.uuid4()) # Genera uuid de importación
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
                
                status_info = "Importación completada con éxito."
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
        user, 
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
        
    

def families_dbf_to_csv(families_dbf):
    dbf_table = DBF(UPLOAD_ROUTE + families_dbf, encoding='latin1')
    df = pd.DataFrame(iter(dbf_table))
    
    families_dbf_name, extension = os.path.splitext(families_dbf) # Clean (with date) filename and extension
    clean_families_dbf_name = str.split(families_dbf_name,'_')[0]
    csv_path = DATA_ROUTE + 'no_filtered_' + families_dbf_name + '.csv'
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
    
    pattern = os.path.join(DATA_ROUTE, f"{clean_families_dbf_name}_*.csv") # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(filtered_csv_path)

        if file_name != new_file_name: # Remove all except the new one
            os.remove(file_)
    
    return filtered_csv_path

    
def update_families(families_dbf):
    start_time = time.perf_counter() # Inicializar contador de tiempo
    families_csv_path = families_dbf_to_csv(families_dbf) # DBF to CSV
    
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
                
                status_info = "Importación completada con éxito."
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


def stocks_dbf_to_csv(stocks_dbf):
    dbf_table = DBF(UPLOAD_ROUTE + stocks_dbf, encoding='latin1')
    df = pd.DataFrame(iter(dbf_table))
    
    stocks_dbf_name, extension = os.path.splitext(stocks_dbf) # Clean (with date) filename and extension
    clean_stocks_dbf_name = str.split(stocks_dbf_name,'_')[0]
    csv_path = DATA_ROUTE + 'no_filtered_' + stocks_dbf_name + '.csv'
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
    
    pattern = os.path.join(DATA_ROUTE, f"{clean_stocks_dbf_name}_*.csv") # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(filtered_csv_path)

        if file_name != new_file_name: # Remove all except the new one
            os.remove(file_)
    
    return filtered_csv_path

def validate_clean_stocks_data(row):
    fixes = [] # Lista de erorres corregidos
    errors = []                        
    
    # CREF debe ser un entero positivo
    ref = row.get('CREF')
    
    if not isinstance(ref, (int, str)): # Si no es valido lanzamos error
        errors.append(f"El campo 'CREF' no es del tipo esperado (int, str): Type -> {type(ref)}.")
    else: # Si es valido...
        try:
            row['CREF'] = int(ref) # Convertimos a entero y modificamos el valor original
        except: # Intentamos limpieza
            clean_ref = ref.split('.')[0] #  Eliminar decimales (BUG de .0 a la derecha)
            clean_ref = re.sub(r'\D', '', str(clean_ref)).strip() # Eliminar espacios y caracteres no numéricos

            # Verificar si después de limpiar hay un valor válido
            if not clean_ref:
                errors.append("El campo 'CREF' debe ser un entero positivo.")
            else:
                # Si ha cambiado el valor original...
                if ref != clean_ref:
                    try:
                        row['CREF'] = int(clean_ref) # Convertimos a entero y modificamos el valor original
                        
                        fixes.append(f"Se ha corregido el campo 'CREF'") # Se añade la corrección a la lsita    
                    except ValueError:
                        errors.append("El campo 'CREF' debe ser un entero positivo.") # Se añade el error al la lista
                        
    
    # NSTOCK: debe ser un entero, puede ser nulo
    stock = row.get('NSTOCK')
    try:
        if stock is not None:
            row['NSTOCK'] = int(stock)
    except (ValueError, TypeError):
        errors.append("El campo 'NSTOCK' debe ser un entero o nulo.")


    # Si ha habido errores, devolver False y los errores encontrados
    if len(errors) > 0:
        return False, row, errors

    # Si todo está bien, devolver True, los datos corregidos y las correcciones realizadas
    return True, row, fixes

def update_stocks(stocks_dbf):
    start_time = time.perf_counter() # Inicializar contador de tiempo
    stocks_csv_path = stocks_dbf_to_csv(stocks_dbf) # DBF to CSV
    
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
                
                status_info = "Importación completada con éxito."
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


def cierre_dbf_to_csv(cierre_dbf):
    dbf_table = DBF(UPLOAD_ROUTE + cierre_dbf, encoding='latin1')
    df = pd.DataFrame(iter(dbf_table))
    
    cierre_dbf_name, extension = os.path.splitext(cierre_dbf) # Clean (with date) filename and extension
    clean_cierre_dbf_name = str.split(cierre_dbf_name,'_')[0]
    csv_path = DATA_ROUTE + 'no_filtered_' + cierre_dbf_name + '.csv'
    df.to_csv(csv_path, index=False)
    
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    selected_columns = ['DFECHA', 'NCONTADOR', 'CHORA', 'NTICKINI', 'NTICKFIN', 'NTOTAL', 'NSALDOANT', 'NSALDOACT']
    
    try:
        df_filtered = df[selected_columns]
    except KeyError as e:
        missing_cols = list(set(selected_columns) - set(df.columns))
        raise KeyError(f"Las siguientes columnas faltan en el DataFrame: {missing_cols}") from e
    
    filtered_csv_path = DATA_ROUTE + cierre_dbf_name + '.csv'
    df_filtered.to_csv(filtered_csv_path, index=False)
    
    os.remove(csv_path) # Remove no filtered csv file
    
    pattern = os.path.join(DATA_ROUTE, f"{clean_cierre_dbf_name}_*.csv") # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(filtered_csv_path)

        if file_name != new_file_name: # Remove all except the new one
            os.remove(file_)
    
    return filtered_csv_path

def update_cierre(cierre_dbf):
    start_time = time.perf_counter()
    cierre_csv_path = cierre_dbf_to_csv(cierre_dbf)

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

    # Recogemos las fechas ya insertadas
    existing_dates = { row.date for row in DailySales.query.with_entities(DailySales.date).all() }

    new_records = []
    for _, row in df.iterrows():
        try:
            # Parsear fecha y hora
            date_ = pd.to_datetime(row['DFECHA']).date()
            time_ = pd.to_datetime(row['CHORA']).time()

            if date_ in existing_dates:
                continue

            record = DailySales(
                date=date_,
                counter=int(row['NCONTADOR']),
                time=time_,
                first_ticket=int(row['NTICKINI']),
                last_ticket=int(row['NTICKFIN']),
                total_sold=float(row['NTOTAL']),
                previous_balance=float(row['NSALDOANT']),
                current_balance=float(row['NSALDOACT'])
            )
            new_records.append(record)
        except Exception as e:
            errors += 1

    session = db.session
    try:
        session.add_all(new_records)
        session.commit()
        inserted = len(new_records)
        status_info = f"Importación completada con éxito"
    except SQLAlchemyError as e:
        session.rollback()
        status = 1
        status_info = f"Error en base de datos: {e}"
    finally:
        session.close()

    elapsed = round(time.perf_counter() - start_time, 2)
    resume = f"Tiempo: {elapsed}s. Insertados: {inserted}. Errores: {errors}."

    return status, status_info, resume


def movimt_dbf_to_csv(movimt_dbf):
    dbf_table = DBF(UPLOAD_ROUTE + movimt_dbf, encoding='latin1')
    df = pd.DataFrame(iter(dbf_table))
    
    movimt_dbf_name, extension = os.path.splitext(movimt_dbf) # Clean (with date) filename and extension
    clean_movimt_dbf_name = str.split(movimt_dbf_name,'_')[0]
    csv_path = DATA_ROUTE + 'no_filtered_' + movimt_dbf_name + '.csv'
    df.to_csv(csv_path, index=False)
    
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    selected_columns = ['NNUMTICKET', 'DFECHA', 'NIMPORTE', 'DFECCIERRE']
    
    try:
        df_filtered = df[selected_columns]
    except KeyError as e:
        missing_cols = list(set(selected_columns) - set(df.columns))
        raise KeyError(f"Las siguientes columnas faltan en el DataFrame: {missing_cols}") from e
    
    filtered_csv_path = DATA_ROUTE + movimt_dbf_name + '.csv'
    df_filtered.to_csv(filtered_csv_path, index=False)
    
    os.remove(csv_path) # Remove no filtered csv file
    
    pattern = os.path.join(DATA_ROUTE, f"{clean_movimt_dbf_name}_*.csv") # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(filtered_csv_path)

        if file_name != new_file_name: # Remove all except the new one
            os.remove(file_)
    
    return filtered_csv_path

def update_movimt(movimt_dbf):
    start_time = time.perf_counter()
    movimt_csv_path = movimt_dbf_to_csv(movimt_dbf)  # Esta función debe existir

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
            status_info = "Importación de tickets completada con éxito."
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


def hticketl_dbf_to_csv(hticketl_dbf):
    dbf_table = DBF(UPLOAD_ROUTE + hticketl_dbf, encoding='latin1')
    df = pd.DataFrame(iter(dbf_table))
    
    hticketl_dbf_name, extension = os.path.splitext(hticketl_dbf) # Clean (with date) filename and extension
    clean_hticketl_dbf_name = str.split(hticketl_dbf_name,'_')[0]
    csv_path = DATA_ROUTE + 'no_filtered_' + hticketl_dbf_name + '.csv'
    df.to_csv(csv_path, index=False)
    
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    selected_columns = ['NNUMTICKET', 'CCODBAR', 'CREF', 'CDETALLE', 'NCANT', 'NPREUNIT']
    
    try:
        df_filtered = df[selected_columns]
    except KeyError as e:
        missing_cols = list(set(selected_columns) - set(df.columns))
        raise KeyError(f"Las siguientes columnas faltan en el DataFrame: {missing_cols}") from e
    
    filtered_csv_path = DATA_ROUTE + hticketl_dbf_name + '.csv'
    df_filtered.to_csv(filtered_csv_path, index=False)
    
    os.remove(csv_path) # Remove no filtered csv file
    
    pattern = os.path.join(DATA_ROUTE, f"{clean_hticketl_dbf_name}_*.csv") # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(filtered_csv_path)

        if file_name != new_file_name: # Remove all except the new one
            os.remove(file_)
    
    return filtered_csv_path

def update_hticketl(hticketl_dbf):
    return 0, "Función aún no implementada", "Sin resumen"