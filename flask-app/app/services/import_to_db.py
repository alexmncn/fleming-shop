import os, time, csv, glob
import pandas as pd
from dbfread import DBF
from datetime import datetime

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
    
    # Asegúrate de que CREF es un entero positivo
    try:
        row['CREF'] = int(row['CREF'])
    except (ValueError, TypeError):
        return False, "El campo 'CREF' debe ser un entero positivo."
    
    if row['CREF'] < 0:
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
                row[key] = float(value)  # Convertir a float
        except (ValueError, TypeError):
            return False, f"El campo '{key}' debe ser un número positivo."

        # Verificar si es negativo
        if value is not None and row[key] < 0:
            return False, f"El campo '{key}' debe ser un número positivo."

    # CCODEBAR: debe ser un entero positivo y único
    try:
        row['CCODEBAR'] = int(row['CCODEBAR'])
    except (ValueError, TypeError):
        return False, "El campo 'CCODEBAR' debe ser un entero positivo."

    if row['CCODEBAR'] < 0:
        return False, "El campo 'CCODEBAR' debe ser un entero positivo."
    
    # Si todo está bien, devolver True
    return True, None


def update_articles(articles_dbf):
    articles_csv_path = articles_dbf_to_csv(articles_dbf)
    time.sleep(2)
    session = db.session

    files = sorted([f for f in os.listdir(DATA_ROUTE) if f.startswith('articulo') and f.endswith('.csv')], reverse=True)
    return

    if len(files) < 2:
        print("No se encontró un archivo anterior. Insertando todos los datos.")
        csv_new = pd.read_csv(articles_csv_path)
        conflict_log = []
        change_log = []

        for _, row in csv_new.iterrows():
            if 'CCODEBAR' in row:
                if pd.isna(row['CCODEBAR']):
                    conflict_log.append({
                        'Error': 'Código de barras faltante',
                        'CREF': row.get('CREF'),
                        'CCODEBAR': row.get('CCODEBAR'),
                        'Detalle': 'El código de barras está ausente'
                    })
                    continue  # Skip this iteration if codebar is NaN

                    
                # Validar y limpiar datos antes de intentar insertar
                is_valid, error_detail = validate_and_clean_data(row)
                if not is_valid:
                    conflict_log.append({
                        'Error': 'Datos inválidos',
                        'CREF': row.get('CREF'),
                        'CCODEBAR': row.get('CCODEBAR'),
                        'Detalle': error_detail
                    })
                    continue
                
                existing_article = session.query(Article).filter_by(codebar=row['CCODEBAR']).first()
                if existing_article:
                    conflict_log.append({
                        'Error': 'Codebar duplicado',
                        'CREF': row['CREF'],
                        'CCODEBAR': row['CCODEBAR'],
                        'Detalle': 'El código de barras ya existe en la base de datos'
                    })
                else:
                    try:
                        article = Article(
                            ref=row['CREF'],
                            detalle=row['CDETALLE'],
                            codfam=row['CCODFAM'],
                            pcosto=row['NCOSTEDIV'],
                            pvp=row['NPVP'],
                            codebar=row['CCODEBAR'],
                            factualizacion=row['DACTUALIZA']
                        )
                        session.add(article)
                        change_log.append({
                            'CREF': row['CREF'],
                            'CCODEBAR': row['CCODEBAR'],
                            'Cambio': 'Nuevo artículo añadido'
                        })
                    except Exception as e:
                        conflict_log.append({
                            'Error': 'Error al insertar el artículo',
                            'CREF': row.get('CREF'),
                            'CCODEBAR': row.get('CCODEBAR'),
                            'Detalle': f'Excepción: {str(e)}'
                        })

        session.commit()
        session.close()

        if conflict_log:
            log_file_path = os.path.join(DATA_LOGS_ROUTE, f"conflicts_{os.path.basename(articles_csv_path)}")
            with open(log_file_path, mode='w', newline='', encoding='utf-8') as log_file:
                log_writer = csv.DictWriter(log_file, fieldnames=['Error', 'CREF', 'CCODEBAR', 'Detalle'])
                log_writer.writeheader()
                for conflict in conflict_log:
                    log_writer.writerow(conflict)
            print(f"Conflictos guardados en {log_file_path}")

        if change_log:
            change_log_file_path = os.path.join(DATA_LOGS_ROUTE, f"changes_{os.path.basename(articles_csv_path)}")
            with open(change_log_file_path, mode='w', newline='', encoding='utf-8') as change_log_file:
                change_writer = csv.DictWriter(change_log_file, fieldnames=['CREF', 'CCODEBAR', 'Cambio'])
                change_writer.writeheader()
                for change in change_log:
                    change_writer.writerow(change)
            print(f"Cambios guardados en {change_log_file_path}")

        print("Datos insertados y conflictos procesados.")
        return
    
    articles_csv_filename = os.path.basename(articles_csv_path)
    last_file = None

    for file in files:
        if file != articles_csv_filename:
            last_file = file
            break

    if last_file is None:
        raise ValueError("No se encontró un archivo anterior diferente para comparar.")

    print(f"Archivo nuevo: {articles_csv_filename}")
    print(f"Archivo anterior: {last_file}")

    csv_new = pd.read_csv(os.path.join(DATA_ROUTE, articles_csv_filename))
    csv_last = pd.read_csv(os.path.join(DATA_ROUTE, last_file))
    
    if 'CCODEBAR' not in csv_new.columns or 'CCODEBAR' not in csv_last.columns:
        raise KeyError("Falta la columna 'CCODEBAR' en uno de los archivos")

    new_entries = csv_new[~csv_new['CCODEBAR'].isin(csv_last['CCODEBAR'])]
    merged_csv = csv_new.merge(csv_last, on='CCODEBAR', suffixes=('_new', '_last'))

    common_columns_new = [f'{col}_new' for col in csv_new.columns if f'{col}_new' in merged_csv.columns]
    common_columns_last = [f'{col}_last' for col in csv_new.columns if f'{col}_last' in merged_csv.columns]

    changes = merged_csv.loc[(merged_csv[common_columns_new].values != merged_csv[common_columns_last].values).any(axis=1)]
    changes = changes.dropna(subset=['CCODEBAR'])

    change_log = []
    conflict_log = []

    # Manejo de nuevas entradas
    for _, row in new_entries.iterrows():
        if 'CCODEBAR' in row:
            if pd.isna(row['CCODEBAR']):
                conflict_log.append({
                    'Error': 'Código de barras faltante',
                    'CREF': row.get('CREF'),
                    'CCODEBAR': row.get('CCODEBAR'),
                    'Detalle': 'El código de barras está ausente'
                })
                continue  # Skip this iteration if codebar is NaN
            
            # Validar y limpiar datos antes de intentar insertar
            is_valid, error_detail = validate_and_clean_data(row)
            if not is_valid:
                conflict_log.append({
                    'Error': 'Datos inválidos',
                    'CREF': row['CREF'],
                    'CCODEBAR': row['CCODEBAR'],
                    'Detalle': error_detail
                })
                continue

            existing_article = session.query(Article).filter_by(codebar=row['CCODEBAR']).first()
            if existing_article:
                conflict_log.append({
                    'Error': 'Codebar duplicado',
                    'CREF': row['CREF'],
                    'CCODEBAR': row['CCODEBAR'],
                    'Detalle': 'El código de barras ya existe en la base de datos'
                })
            else:
                try:
                    article = Article(
                        ref=row['CREF'],
                        detalle=row['CDETALLE'],
                        codfam=row['CCODFAM'],
                        pcosto=row['NCOSTEDIV'],
                        pvp=row['NPVP'],
                        codebar=row['CCODEBAR'],
                        factualizacion=row['DACTUALIZA']
                    )
                    session.add(article)
                    change_log.append({
                        'CREF': row['CREF'],
                        'CCODEBAR': row['CCODEBAR'],
                        'Cambio': 'Nuevo artículo añadido'
                    })
                except Exception as e:
                    conflict_log.append({
                        'Error': 'Error al insertar el artículo',
                        'CREF': row.get('CREF'),
                        'CCODEBAR': row.get('CCODEBAR'),
                        'Detalle': f'Excepción: {str(e)}'
                    })

    print(f"Subidas {len(new_entries)} nuevas entradas.")


    # Manejo de cambios en las entradas existentes
    for _, row in changes.iterrows():
        codebar = row.get('CCODEBAR', None)
        if pd.notna(codebar):
            article = session.query(Article).filter_by(codebar=codebar).first()
            if article:
                updated = False
                for col in csv_new.columns:
                    if col == 'CCODEBAR':
                            continue  # Saltar la actualización del codebar
                        
                    new_value = row.get(f'{col}_new', None)
                    last_value = row.get(f'{col}_last', None)

                    if pd.isna(new_value):
                        conflict_log.append({
                            'Error': 'Valor NaN encontrado',
                            'CREF': row.get('CREF_new', None),
                            'CCODEBAR': codebar,
                            'Detalle': f'El valor de {col} es NaN y no puede ser actualizado'
                        })
                        continue

                    if new_value != last_value:
                        attribute_name = article_column_to_attribute_map.get(col)
                        if attribute_name:    
                            #print(f"Antes de asignar: {attribute_name} = {getattr(article, attribute_name)}")
                            setattr(article, attribute_name, new_value)
                            #print(f"Después de asignar: {attribute_name} = {getattr(article, attribute_name)}")
                            updated = True
                            change_log.append({
                                'CREF': row.get('CREF_new', None),
                                'CCODEBAR': codebar,
                                'Cambio': f"{col} actualizado de {last_value} a {new_value}"
                            })

                # Validar y limpiar los datos después de haber identificado los cambios
                if updated:
                    is_valid, error_detail = validate_and_clean_data(pd.Series(article.to_dict_og_keys()))
                    if not is_valid:
                        conflict_log.append({
                            'Error': 'Datos inválidos después de la actualización',
                            'CREF': row.get('CREF_new', None),
                            'CCODEBAR': codebar,
                            'Detalle': error_detail
                        })
                        continue  # Saltar la adición del artículo si la validación falla

                    try:
                        session.add(article)  # Agregar el artículo a la sesión para actualizarlo
                        session.flush()  # Asegurarse de que los cambios se envíen a la base de datos
                    except Exception as e:
                        session.rollback()  # Deshacer cambios si ocurre un error
                        conflict_log.append({
                            'Error': 'Error al actualizar el artículo',
                            'CREF': row.get('CREF_new', None),
                            'CCODEBAR': codebar,
                            'Detalle': f'Excepción: {str(e)}'
                        })
                
                if updated:
                    session.add(article)
                    session.flush()

            else:
                conflict_log.append({
                    'Error': 'Artículo no encontrado',
                    'CREF': row.get('CREF_new', None),
                    'CCODEBAR': codebar,
                    'Detalle': 'El artículo con este código de barras no existe para ser actualizado'
                })

    session.commit()
    session.close()

    # Guardado de conflictos y cambios
    if conflict_log:
        log_file_path = os.path.join(DATA_LOGS_ROUTE, f"conflicts_{os.path.basename(articles_csv_path)}")
        with open(log_file_path, mode='w', newline='', encoding='utf-8') as log_file:
            log_writer = csv.DictWriter(log_file, fieldnames=['Error', 'CREF', 'CCODEBAR', 'Detalle'])
            log_writer.writeheader()
            for conflict in conflict_log:
                log_writer.writerow(conflict)
        print(f"Conflictos guardados en {log_file_path}")

    if change_log:
        change_log_file_path = os.path.join(DATA_LOGS_ROUTE, f"changes_{os.path.basename(articles_csv_path)}")
        with open(change_log_file_path, mode='w', newline='', encoding='utf-8') as change_log_file:
            change_writer = csv.DictWriter(change_log_file, fieldnames=['CREF', 'CCODEBAR', 'Cambio'])
            change_writer.writeheader()
            for change in change_log:
                change_writer.writerow(change)
        print(f"Cambios guardados en {change_log_file_path}")

    print("Comparación, actualización y registro de conflictos completados.")
    

def families_dbf_to_csv(families_dbf):
    selected_columns = ['CCODFAM', 'CNOMFAM']
    families_dbf_name = families_dbf[:-4]
    table = DBF(UPLOAD_ROUTE + families_dbf, encoding='latin1')
    df = pd.DataFrame(iter(table))
    csv_path = DATA_ROUTE + 'no_filtered_' + families_dbf_name + '.csv'
    df.to_csv(csv_path, index=False)
    
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    
    try:
        df_filtered = df[selected_columns]
    except KeyError as e:
        missing_cols = list(set(selected_columns) - set(df.columns))
        raise KeyError(f"Las siguientes columnas faltan en el DataFrame: {missing_cols}") from e
    
    filtered_csv_path = DATA_ROUTE + families_dbf_name + '.csv'
    df_filtered.to_csv(filtered_csv_path, index=False)
    
    os.remove(csv_path)
    
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
    selected_columns = ['CREF', 'NSTOCK']
    stocks_dbf_name = stocks_dbf[:-4]
    table = DBF(UPLOAD_ROUTE + stocks_dbf, encoding='latin1')
    df = pd.DataFrame(iter(table))
    csv_path = DATA_ROUTE + 'no_filtered_' + stocks_dbf_name + '.csv'
    df.to_csv(csv_path, index=False)
    
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    
    try:
        df_filtered = df[selected_columns]
    except KeyError as e:
        missing_cols = list(set(selected_columns) - set(df.columns))
        raise KeyError(f"Las siguientes columnas faltan en el DataFrame: {missing_cols}") from e
    
    filtered_csv_path = DATA_ROUTE + stocks_dbf_name + '.csv'
    df_filtered.to_csv(filtered_csv_path, index=False)
    
    os.remove(csv_path)
    
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