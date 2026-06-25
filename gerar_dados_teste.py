import sqlite3
from datetime import date, timedelta
import random

ID_COLABORADOR = 2

conn = sqlite3.connect("ponto.db")
cursor = conn.cursor()

inicio = date(2026, 5, 1)
fim = date(2026, 6, 30)

observacoes = [
    "Presencial",
    "Home Office",
    "Híbrido"
]

dia = inicio

while dia <= fim:

    # Segunda a sexta
    if dia.weekday() < 5:

        entrada_min = random.randint(0, 8)
        saida_min = random.randint(0, 8)

        entrada = f"08:{entrada_min:02d}"
        saida = f"14:{saida_min:02d}"

        observacao = random.choice(observacoes)

        cursor.execute("""
            INSERT INTO registros_ponto (
                colaborador_id,
                data,
                entrada,
                saida_final,
                observacao
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            ID_COLABORADOR,
            dia.strftime("%d/%m/%Y"),
            entrada,
            saida,
            observacao
        ))

    dia += timedelta(days=1)

conn.commit()
conn.close()

print("Registros criados com sucesso!")