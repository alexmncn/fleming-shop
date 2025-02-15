import os, time, csv, glob, re, math
import pandas as pd
from dbfread import DBF
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Article, Family

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


def validate_and_clean_data(row):
    """
    Valida y limpia los datos de una fila del artículo en formato pandas.Series.
    - Verifica que los valores cumplan con los tipos de datos y el formato.
    - Retorna True si la fila es válida, o False con un mensaje de error si hay un conflicto.
    """
    
    # CCODEBAR: debe ser un entero positivo y único
    codebar = row.get('CCODEBAR')
    if not isinstance(codebar, (int, str)):
        return False, "El campo 'CCODEBAR' debe ser un entero positivo."

    # Eliminar decimales (BUG de .0 a la derecha)
    codebar = codebar.split('.')[0]

    # Eliminar espacios y caracteres no numéricos
    codebar = re.sub(r'\D', '', str(codebar)).strip()

    # Verificar si después de limpiar hay un valor válido
    if not codebar:
        return False, "El campo 'CCODEBAR' debe ser un entero positivo."

    try:
        row['CCODEBAR'] = int(codebar)
    except ValueError:
        return False, "El campo 'CCODEBAR' debe ser un entero positivo."
    
    
    # CREF debe ser un entero positivo
    ref = row.get('CREF')
    if not isinstance(ref, (int, str)):
        return False, "El campo 'CREF' debe ser un entero positivo."

    # Eliminar espacios y caracteres no numéricos
    ref = re.sub(r'\D', '', str(ref)).strip()

    # Verificar si después de limpiar hay un valor válido
    if not ref:
        return False, "El campo 'CREF' debe ser un entero positivo."
    
    try:
        row['CREF'] = int(ref)
    except (ValueError, TypeError):
        return False, "El campo 'CREF' debe ser un entero positivo."
    
    
    # CDETALLE: cadena de hasta 50 caracteres, puede contener cualquier carácter UTF-8
    detalle = row.get('CDETALLE')
    if detalle is not None and (not isinstance(detalle, str) or len(detalle) > 50):
        return False, "El campo 'CDETALLE' debe ser una cadena de texto de máximo 50 caracteres."
    
    
    # CCODFAM: debe ser un entero, puede ser nulo
    try:
        if row.get('CCODFAM') is not None:
            row['CCODFAM'] = int(row['CCODFAM'])
    except (ValueError, TypeError):
        return False, "El campo 'CCODFAM' debe ser un entero o nulo."


    # NCOSTEDIV y NPVP: deben ser flotantes y positivos
    for key in ['NCOSTEDIV', 'NPVP']:
        value = row.get(key)
        try:
            if value is not None:
                value = float(value)  # Convertir a float
                row[key] = math.trunc(value * 100) / 100 # Truncar a 2 decimales
        except (ValueError, TypeError):
            return False, f"El campo '{key}' debe ser un número positivo."

        # Verificar si es negativo
        if value is not None and row[key] < 0:
            return False, f"El campo '{key}' debe ser un número positivo."


    # Si todo está bien, devolver True y los datos corregidos
    return True, row


def update_articles(articles_dbf):
    articles_csv_path = articles_dbf_to_csv(articles_dbf)
    time.sleep(2)

    # Leer los datos del CSV importado
    try:
        articles_csv = pd.read_csv(articles_csv_path)
    except Exception as e:
        print(f"Error al leer el CSV: {str(e)}")
        return
    
    
    # Limpiamos los datos del CSV
    clean_rows = []
    conflict_log = []

    for _, row in articles_csv.iterrows():
        codebar = row.get('CCODEBAR')
        ref = row.get('CREF')
        detalle = row.get('CDETALLE')
        # Si no hay código de barras, se descarta directamente
        if pd.isna(codebar):
            conflict_log.append({'Error': 'Código de barras faltante', 'CREF': ref, 'CCODEBAR': codebar, 'CDETALLE': detalle, 'Info': 'Código de barras ausente'})
            continue
        
        # Validar y limpiar los datos de la fila
        is_valid, clean_row = validate_and_clean_data(row)
        if not is_valid:
            conflict_log.append({'Error': 'Datos inválidos', 'CREF': ref, 'CCODEBAR': codebar, 'CDETALLE': detalle, 'Info': clean_row})
            continue
        
        # Si se es valida se añade a la nueva lista
        clean_rows.append(clean_row)
        
    # Crear un nuevo DataFrame con las filas limpias
    clean_articles_csv = pd.DataFrame(clean_rows, columns=articles_csv.columns)
    
    
    # Identificar filas duplicadas
    duplicated_rows = clean_articles_csv[clean_articles_csv.duplicated(subset=['CCODEBAR'], keep='first')]
    for _, row in duplicated_rows.iterrows():
        codebar = row['CCODEBAR']
        ref = row['CREF']
        detalle = row['CDETALLE']
        conflict_log.append({'Error': 'Duplicado', 'CREF': ref, 'CCODEBAR': codebar, 'CDETALLE': detalle, 'Info': 'Código de barras duplicado'})
        
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
            for col, attr in  {'CREF': 'ref', 'CDETALLE': 'detalle', 'CCODFAM': 'codfam', 'NCOSTEDIV': 'pcosto', 'NPVP': 'pvp', 'DACTUALIZA': 'factualizacion'}.items():
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
        
    # Guardar los cambios en la DB
    session = db.session
        
    # Aplicar cambios en la base de datos
    try:
        session.add_all(new_articles) # Insertar los nuevos artículos
        session.add_all(updated_articles) # Actualizar los artículos modificados 

        for codebar in deleted_articles:
            session.delete(db_articles[codebar]) # Eliminar los artículos que ya no existen
             
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error en la base de datos: {str(e)}")
    finally:
        session.close()
        
        
    # Registrar los cambios y errores en un archivo de log
    status_message = f"Nuevos: {len(new_articles)}, Actualizados: {len(updated_articles)}, Eliminados: {len(deleted_articles)}, Duplicados: {len(duplicated_rows)}, Errores: {len(conflict_log)}"
    
    if conflict_log:
        conflict_log.append({'Error': 'RESUMEN', 'CREF': '', 'CCODEBAR': '', 'CDETALLE': '', 'Info': status_message})
        
        # Save conflict log csv
        log_file_path = os.path.join(DATA_LOGS_ROUTE, f"conflicts_{os.path.basename(articles_csv_path)}")
        with open(log_file_path, mode='w', newline='', encoding='utf-8') as log_file:
            log_writer = pd.DataFrame(conflict_log)
            log_writer.to_csv(log_file, index=False)
            
        # Delete old conflict logs
        pattern = os.path.join(f"{str.split(log_file_path,'_')[0]}_{str.split(log_file_path,'_')[1]}_*.csv") # Get old file versions

        for file_ in glob.glob(pattern):
            file_name = os.path.basename(file_)
            new_file_name = os.path.basename(log_file_path)

            if file_name != new_file_name: # Remove all except the new one
                os.remove(file_)
                
        print(f"Conflictos guardados en {log_file_path}")
        
    print(status_message)
    

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