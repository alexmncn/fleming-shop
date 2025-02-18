import os, time, glob, re, math, uuid
import pandas as pd
from dbfread import DBF
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Article, Family, Article_import_log, Article_import, User

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
    selected_columns = article_column_to_attribute_map.keys() # Set the needed columns from keys of defined map
    
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
        interval = 0.1 # 0.5 segundos
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
        print(status_info)
    
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
                    article_import_log = Article_import_log(import_id=import_id, type=log_type, ref=ref, codebar=None, detalle=detalle, info='Código de barras ausente')
                    conflict_logs.append(article_import_log)
                    continue
                
                # Validar y limpiar los datos de la fila
                is_valid, clean_row, logs_info = validate_clean_article_data(row)
                if not is_valid:
                    for log_info in logs_info:
                        log_type = 1 # NO Válido
                        article_import_log = Article_import_log(import_id=import_id, type=log_type, ref=ref, codebar=codebar, detalle=detalle, info=log_info)
                        conflict_logs.append(article_import_log)
                    continue
                else:
                    for log_info in logs_info:
                        log_type = 0 # Válido
                        article_import_log = Article_import_log(import_id=import_id, type=log_type, ref=ref, codebar=codebar, detalle=detalle, info=log_info)
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
                article_import_log = Article_import_log(import_id=import_id, type=log_type, ref=row['CREF'], codebar=row['CCODEBAR'], detalle=row['CDETALLE'], info=log_info)
                conflict_logs.append(article_import_log)
                
            # Eliminar duplicados, manteniendo solo la primera ocurrencia
            clean_articles_csv = clean_articles_csv.drop_duplicates(subset=['CCODEBAR'], keep='first')
                
            
            # Cargamos todos los artículos existentes en la DB
            db_articles = {article.codebar: article for article in Article.query.all()}
            deleted_articles = set(db_articles.keys()) # Inicializamos los artículos a eliminar
            
            # Actualizar o crear los artículos en la DB
            new_articles = []
            updated_articles = []
            
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
    elapsed_time = (end_time - start_time)
    
    # Log general
    status_message = f"Nuevos: {len(new_articles)}, Actualizados: {len(updated_articles)}, Eliminados: {len(deleted_articles)}, Duplicados: {len(duplicated_rows)}, Errores: {len(conflict_logs)}"
    print(status_message)
    
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
        
    return status, status_info
        
        
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
    with open(log_file_path, mode='w', newline='', encoding='utf-8') as log_file:
        log_writer = pd.DataFrame(conflict_logs)
        log_writer.to_csv(log_file, index=False)
        
    # Delete old conflict logs
    pattern = os.path.join(f"{str.split(log_file_path,'_')[0]}_{str.split(log_file_path,'_')[1]}_*.csv") # Get old file versions

    for file_ in glob.glob(pattern):
        file_name = os.path.basename(file_)
        new_file_name = os.path.basename(log_file_path)

        if file_name != new_file_name: # Remove all except the new one
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
    families_csv_path = families_dbf_to_csv(families_dbf)
    time.sleep(2)
    data = pd.read_csv(families_csv_path)
    for index, row in data.iterrows():
        family = Family(
            codfam=row['CCODFAM'],
            nomfam=row['CNOMFAM']  
        )
        db.session.add(family)
    db.session.commit()
    


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


def update_stocks(stocks_dbf):
    stocks_csv_path = stocks_dbf_to_csv(stocks_dbf)
    time.sleep(2)
    session = db.session
    
    article_stocks = session.query(Article).with_entities(Article.ref, Article.stock).all()
    stocks_csv = pd.read_csv(stocks_csv_path)
    
    article_stocks_dict = {ref: stock for ref, stock in article_stocks}
    
    updates = 0
    errors = 0
    for _, row in stocks_csv.iterrows():
        if 'CREF' and 'NSTOCK' in row:
            try:
                ref = int(row['CREF'])
                new_stock = row['NSTOCK']
                
                if ref in article_stocks_dict:
                    current_stock = article_stocks_dict[ref]
                    
                    if current_stock != new_stock:
                        article = session.query(Article).filter_by(ref=ref).first()
                        article.stock = new_stock
                        session.add(article)
                        updates += 1
                        print(f"Actualizado {ref}: Stock cambiado de {current_stock} a {new_stock}")
            except Exception as e:
                errors += 1
                print(f'Error: {e}')
            
    print(f'\nSe han actualizado {updates} articulos.\nSe han encontrado {errors} errores.')
                
    
    session.commit()