import sqlite3

conn = sqlite3.connect("ponto.db")
cursor = conn.cursor()

cursor.execute("""
SELECT
    id,
    colaborador_id,
    data
FROM registros_ponto
WHERE colaborador_id = 2
ORDER BY id DESC
""")

for linha in cursor.fetchall():
    print(linha)

conn.close()