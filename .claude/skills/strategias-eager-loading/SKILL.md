---
name: sqlalchemy-eager-loading
description: >
  Use this skill whenever a task envolve carregar relações no SQLAlchemy 2 com
  joinedload, selectinload, subqueryload ou lazyload. Cobre diagnóstico de
  produto cartesiano, escolha da estratégia certa por tipo de relação
  (*-to-one vs *-to-many), encadeamento de opções aninhadas, uso de .unique()
  em sessões async, e conversão de queries legadas (SQLAlchemy 1.x / Flask-
  SQLAlchemy .query style) para o estilo select() do SQLAlchemy 2.
  Triggers: "joinedload", "selectinload", "eager load", "N+1", "produto
  cartesiano em query", "relações duplicadas", "options()", "lazyload",
  "subqueryload", "contains_eager", "orm query carregamento".
---

# SQLAlchemy 2 — Estratégias de Eager Loading

## Regra central

**joinedload** é para relações `*-to-one` (muitos-para-um, um-para-um).
**selectinload** é para coleções `*-to-many` (um-para-muitos, muitos-para-muitos).

Misturar os dois na mesma árvore é permitido e esperado.

---

## Por que joinedload em coleções é problemático

Quando há múltiplas coleções independentes na mesma task (ex: `Task.tags`,
`Task.assignees`, `Task.comments`), cada JOIN extra multiplica as linhas:

```
task_1 | tag_A | user_X | comment_1   <- linha 1
task_1 | tag_A | user_X | comment_2   <- linha 2  (comment duplicado)
task_1 | tag_A | user_Y | comment_1   <- linha 3  (assignee duplicado)
task_1 | tag_B | user_X | comment_1   <- linha 4  (tag duplicada)
```

Com 3 tags × 2 assignees × 5 comments = **30 linhas** para representar 1 task.
O ORM descarta os duplicados com `.unique()`, mas os dados trafegam todos.
Em tabelas grandes isso degrada performance e pode causar timeout.

---

## Guia de escolha por tipo de relação

| Tipo de relação   | Estratégia recomendada | Motivo                                      |
|-------------------|------------------------|---------------------------------------------|
| many-to-one       | `joinedload`           | 1 linha extra por JOIN, sem multiplicação   |
| one-to-one        | `joinedload`           | idem                                        |
| one-to-many       | `selectinload`         | SELECT separado, sem produto cartesiano     |
| many-to-many      | `selectinload`         | idem                                        |
| coleção grande    | `selectinload`         | mais eficiente que subqueryload em geral    |
| coleção filtrada  | `contains_eager`       | quando o JOIN já existe no WHERE/filter     |

`subqueryload` era preferido no SQLAlchemy 1.x. No 2.x, `selectinload` é
mais eficiente na maioria dos casos e deve ser o padrão para coleções.

---

## Template canônico — SQLAlchemy 2 async

```python
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import select

stmt = (
    select(User)
    .options(
        # to-one: joinedload
        joinedload(User.profile),

        # to-many: selectinload, aninhado recursivamente
        selectinload(User.projects).options(
            selectinload(Project.tasks).options(
                selectinload(Task.comments).options(
                    selectinload(Comment.reactions),
                    selectinload(Comment.attachments),
                ),
                selectinload(Task.tags),
                selectinload(Task.assignees).joinedload(User.profile),
            )
        ),
    )
    .where(User.id == user_id)
)

result = await session.execute(stmt)
user = result.unique().scalar_one_or_none()
```

### Pontos obrigatórios

- `.unique()` é **sempre necessário** em sessões async quando há qualquer
  `joinedload` na query. Sem ele o SQLAlchemy levanta `InvalidRequestError`.
- Em sessão síncrona, `.unique()` também é recomendado mas não obrigatório.
- Use `scalar_one_or_none()` em vez de `.first()` no SQLAlchemy 2. `.first()`
  ainda funciona mas é estilo legado.

---

## Template canônico — SQLAlchemy 2 síncrono (Flask-SQLAlchemy 3+)

```python
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import select

stmt = (
    select(User)
    .options(
        joinedload(User.profile),
        selectinload(User.projects).options(
            selectinload(Project.tasks).options(
                selectinload(Task.comments).options(
                    selectinload(Comment.reactions),
                    selectinload(Comment.attachments),
                ),
                selectinload(Task.tags),
                selectinload(Task.assignees).joinedload(User.profile),
            )
        ),
    )
    .where(User.id == user_id)
)

user = db.session.execute(stmt).unique().scalar_one_or_none()
```

---

## Conversão de código legado (SQLAlchemy 1.x / .query style)

O estilo `.query` ainda funciona no SQLAlchemy 2, mas está depreciado.
Converter para `select()`:

```python
# Legado (1.x)
user = (
    User.query
    .options(joinedload(User.projects).joinedload(Project.tasks))
    .filter(User.id == user_id)
    .first()
)

# SQLAlchemy 2
stmt = (
    select(User)
    .options(
        selectinload(User.projects).selectinload(Project.tasks)
    )
    .where(User.id == user_id)
)
user = session.execute(stmt).unique().scalar_one_or_none()
```

Mapeamento direto de métodos:

| Legado (.query)       | SQLAlchemy 2 (select)              |
|-----------------------|------------------------------------|
| `.filter(...)`        | `.where(...)`                      |
| `.first()`            | `.scalar_one_or_none()`            |
| `.all()`              | `.scalars().all()`                 |
| `.one()`              | `.scalar_one()`                    |
| `.count()`            | `select(func.count()).where(...)`  |
| `.join(...)`          | `.join(...)` (igual)               |

---

## contains_eager — quando o JOIN já existe

Use quando você mesmo adicionou o JOIN para filtrar e quer que o ORM
reaproveite esse JOIN para carregar a relação (evita um segundo SELECT):

```python
stmt = (
    select(User)
    .join(User.orders)
    .options(contains_eager(User.orders))
    .where(Order.status == "pending")
)
```

**Atenção:** `contains_eager` com filtro parcial faz o ORM acreditar que
carregou a coleção completa. Acesso posterior a `user.orders` não vai
disparar novo SELECT — vai retornar apenas os itens filtrados. Use somente
quando isso é o comportamento desejado.

---

## Diagnóstico de N+1

N+1 ocorre quando relações ficam em `lazy="select"` (padrão) e são acessadas
dentro de um loop:

```python
# BUG: dispara 1 SELECT por task
tasks = session.scalars(select(Task)).all()
for task in tasks:
    print(task.assignees)  # lazy load aqui = N queries extras
```

Solução: adicionar `selectinload(Task.assignees)` na query principal.

Para detectar N+1 em desenvolvimento, configure o logging do SQLAlchemy:

```python
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
```

Ou use a extensão `sqlalchemy-query-count` / middleware do framework para
contar queries por request.

---

## Regras de encadeamento de .options()

```python
# CORRETO: .options() recebe múltiplos loaders como argumentos separados
selectinload(Task.comments).options(
    selectinload(Comment.reactions),
    selectinload(Comment.attachments),
)

# ERRADO: encadear .joinedload() após .selectinload() na mesma relação
# (sintaxe do SQLAlchemy 1.x que não funciona corretamente no 2.x para coleções)
selectinload(Task.comments).joinedload(Comment.reactions)  # evitar
```

Para relação to-one dentro de selectinload, use `.joinedload()` encadeado
diretamente (sem `.options()`):

```python
selectinload(Task.assignees).joinedload(User.profile)  # correto
```

---

## Checklist antes de entregar uma query com relações

- [ ] Toda coleção (`*-to-many`) usa `selectinload`, não `joinedload`
- [ ] Relações `*-to-one` podem usar `joinedload`
- [ ] Sessão async: `.unique()` presente antes de `.scalar_one_or_none()`
- [ ] Não há `.query` style (depreciado no SQLAlchemy 2)
- [ ] Loops que acessam relações têm eager load correspondente na query
- [ ] `contains_eager` usado somente quando o JOIN já existe e o filtro parcial é intencional
