import sqlite3
import os


def conectar():
    caminho = os.path.abspath("ponto.db")

    print("BANCO:", caminho)

    conn = sqlite3.connect(caminho, timeout=30.0, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn