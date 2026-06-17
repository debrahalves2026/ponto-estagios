import sqlite3
import os

def conectar():

    caminho = os.path.abspath("ponto.db")

    print("BANCO:", caminho)

    return sqlite3.connect(caminho)