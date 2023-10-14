import csv
import os
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine, text

# Nombre del archivo CSV
archivo_csv = 'books.csv'

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Abrir el archivo CSV
with open(archivo_csv, 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)

    for row in csv_reader:
        # Supongamos que la tabla en la base de datos se llama 'mi_tabla'
        # y tiene las mismas columnas 'columna1', 'columna2', 'columna3'
        db.execute(text("INSERT INTO books (numisbn, title, author, year) VALUES (:isbn, :title, :author, :year)"),
                       {'isbn': row['isbn'], 'title': row['title'], 'author': row['author'], 'year': row['year']})

# Confirmar los cambios y cerrar la conexión
db.commit()
db.remove()


