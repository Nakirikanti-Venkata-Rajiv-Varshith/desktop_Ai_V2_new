import sqlite3

connection = sqlite3.connect(
    "data/semantic.db"
)

cursor = connection.cursor()

cursor.execute(
    """
    SELECT
        id,
        typeof(embedding),
        length(embedding)
    FROM documents
    """
)

for row in cursor.fetchall():

    print(row)

connection.close()