# 🔍 AUDITORIA COMPLETA DO CÓDIGO

## 🔴 PROBLEMAS CRÍTICOS

### 1. **Gerenciamento de Cursores Deficiente**
- ❌ Linha 786 (dashboard_administrador): `cursor` usado FORA de `with db_cursor()`
- ❌ Linha 825 (dashboard_administrador): 3 queries sem context manager
- ❌ Linha 857-897: Multiple cursors sem proper cleanup
- ❌ Linhas 1061-1063: Cursor não fechado após fetchone()

**Impacto**: Memory leak, conexões abertas, deadlocks no Supabase

---

### 2. **Tratamento de Erros INEXISTENTE**
- ❌ `login_gestor_nucleo()`: fetchone() pode retornar None, acessa índices sem checagem
- ❌ `salvar_colaborador()`: sem try/except para erros de banco
- ❌ `gerar_pdf()`, `gerar_excel()`: sem tratamento se tempfile falhar
- ❌ `download_folhas_assinadas()`: os.path.exists() pode falhar em concorrência

**Impacto**: 500 Internal Server Errors frequentes

---

### 3. **Vulnerabilidades de Segurança**
- ⚠️  Linha 51: Regex quebrada (`%s` literal na pattern)
- ⚠️  String formatting SQL: `f"""...{filtro_todos}..."""` (potencial SQL injection se filtro for não-sanitizado)
- ⚠️  Session hijacking: sem CSRF tokens
- ⚠️  Senhas armazenadas em PLAIN TEXT (não hashed)

---

### 4. **Duplicação de Código**
- `_registros_folha_colaborador()` - lógica duplicada em gerar_pdf, gerar_excel, visualizar_relatorio
- 4x queries idênticas para status de colaboradores
- Dashboard logic duplicado (admin vs gestor)

**Impacto**: Dificuldade de manutenção, bugs inconsistentes

---

### 5. **Problemas de Lógica**
- ⚠️  Linha 918: `cursor` definido ANTES do `with`, usado DEPOIS
- ⚠️  Linha 1390-1398: regex pattern `%s=.*[a-z]` sempre FALSO (syntax error)
- ⚠️  `_data_br_para_date()` sem try/except para formato inválido
- ⚠️  `primo_acesso()` retorna template sem variables

---

### 6. **Context Manager Quebrado**
```python
# ERRADO:
@contextmanager
def db_cursor(commit=False):
    conn = get_db_connection()  # Reusa conexão global
    cursor = conn.cursor()
    # Se exception acontece antes de commit, rollback() pode falhar
```
- Problema: Se rollback falhar, conexão fica travada
- Problema: Múltiplas requisições compartilham a mesma conexão via `g.db_conn`

---

## ⚠️ PROBLEMAS DE DESIGN

### 1. Sem Abstração de Dados
Diretamente consultando colunas por índice:
```python
gestor = cursor.fetchone()
session['gestor_id'] = gestor[0]  # Magic number!
```

### 2. Sem Validação em Camada de Banco
Campo `status` inserido sem valores pré-definidos

### 3. Imports de Middleware Não Usados
```python
from .app_utils import (
    login_required,    # ← NUNCA USADO
    validate_password, # ← NUNCA USADO
)
```

### 4. Sem Type Hints
Impossível saber o que cada função retorna

### 5. Timezone Hardcoded
Sempre "America/Sao_Paulo" - não configurável

---

## 📋 LISTA DE FIXES NECESSÁRIOS

### Urgente (Breaking):
- [ ] Corrigir cursores abertos em dashboard_administrador
- [ ] Adicionar try/except em login functions
- [ ] Fixar regex de senha (linhas 1390, 1416, 1454)
- [ ] Melhorar context manager db_cursor

### Importante (Data Integrity):
- [ ] Hash de senhas com bcrypt
- [ ] Validação de enums para status
- [ ] Constraint NOT NULL nas colunas críticas
- [ ] Índices nas tabelas

### Nice to Have:
- [ ] Refatorar routes.py em módulos
- [ ] Adicionar type hints
- [ ] Remover código duplicado
- [ ] Docstrings

---

## 📊 ESTATÍSTICAS

- **Linhas de código**: 3182
- **Funções**: 95+
- **Duplicações**: ~15 segmentos de código
- **TODOs implícitos**: ~40
- **Try/except blocks**: 2 (deveria ter 30+)
- **SQL queries**: 150+
- **Context managers corretos**: ~30%

