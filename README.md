# Brew Recipe API

Uma Django REST API para armazenar e gerenciar **receitas completas de cerveja artesanal/homebrew** — ingredientes, perfis de mostura, cronogramas de fermentação, química da água e muito mais.

---

## Stack

- Python 3.10+
- Django 5.2
- Django REST Framework 3.14
- django-filter
- drf-nested-routers
- SQLite

---

## Configuração

```bash
git clone <seu-repositorio>
cd brewrecipeapi

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # opcional – para /admin
python manage.py runserver
```

---

## Visão Geral do Modelo de Dados

```
Recipe
 ├── style          → BeerStyle (FK)
 ├── malts          → RecipeMalt → Malt
 ├── hops           → RecipeHop  → Hop
 ├── yeasts         → RecipeYeast → Yeast
 ├── mash_steps     → MashStep   (ordenado)
 ├── fermentation_steps → FermentationStep (ordenado)
 └── water_profile  → WaterProfile (1:1)
```

### Catálogo de Ingredientes (reutilizáveis entre receitas)

| Model       | Campos Principais                                           |
|-------------|-------------------------------------------------------------|
| `BeerStyle` | name, bjcp_code, description                                |
| `Malt`      | name, type, color_ebc, potential_sg, producer               |
| `Hop`       | name, type, form, alpha_acid_pct, aroma_profile |
| `Yeast`     | name, code, type, temp range                                |

### Campos da Receita

| Campo            | Descrição                                |
|------------------|------------------------------------------|
| `batch_size_l`   | Volume final do lote (litros)            |
| `boil_volume_l`  | Volume pré-fervura (litros)              |
| `boil_time_min`  | Duração da fervura (minutos)             |
| `efficiency_pct` | Eficiência do brewhouse (%)              |
| `og` / `fg`      | Densidade Original / Final               |
| `abv`            | Teor alcoólico (%)                       |
| `ibu`            | Unidades Internacionais de Amargor       |
| `ebc` / `srm`    | Cor                                      |

---

## Rotas da API

### Endpoints do Catálogo

| Método | Rota                | Descrição                 |
|--------|---------------------|---------------------------|
| GET    | `/api/styles/`      | Listar estilos de cerveja |
| POST   | `/api/styles/`      | Criar estilo de cerveja   |
| GET    | `/api/malts/`       | Listar maltes             |
| POST   | `/api/malts/`       | Criar malte               |
| GET    | `/api/hops/`        | Listar lúpulos            |
| POST   | `/api/hops/`        | Criar lúpulo              |
| GET    | `/api/yeasts/`      | Listar leveduras          |
| POST   | `/api/yeasts/`      | Criar levedura            |

Todos os endpoints do catálogo também suportam `GET /{id}/`, `PUT /{id}/`, `PATCH /{id}/`, `DELETE /{id}/`.

---

### Endpoints de Receita

| Método | Rota                                            | Descrição                                |
|--------|-------------------------------------------------|------------------------------------------|
| GET    | `/api/recipes/`                                 | Listar receitas (leve)                   |
| POST   | `/api/recipes/`                                 | Criar receita (com dados aninhados)      |
| GET    | `/api/recipes/{id}/`                            | Detalhe completo da receita              |
| PUT    | `/api/recipes/{id}/`                            | Atualizar receita (substitui aninhados)  |
| PATCH  | `/api/recipes/{id}/`                            | Atualização parcial                      |
| DELETE | `/api/recipes/{id}/`                            | Excluir receita                          |

### Endpoints Aninhados de Ingredientes (por receita)

| Método | Rota                                                   | Descrição                     |
|--------|--------------------------------------------------------|-------------------------------|
| GET    | `/api/recipes/{id}/malts/`                             | Listar maltes da receita      |
| POST   | `/api/recipes/{id}/malts/`                             | Adicionar malte à receita     |
| GET    | `/api/recipes/{id}/hops/`                              | Listar lúpulos da receita     |
| POST   | `/api/recipes/{id}/hops/`                              | Adicionar lúpulo à receita    |
| GET    | `/api/recipes/{id}/yeasts/`                            | Listar leveduras da receita   |
| POST   | `/api/recipes/{id}/yeasts/`                            | Adicionar levedura à receita  |
| GET    | `/api/recipes/{id}/mash-steps/`                        | Listar etapas de mostura      |
| POST   | `/api/recipes/{id}/mash-steps/`                        | Adicionar etapa de mostura    |
| GET    | `/api/recipes/{id}/fermentation-steps/`                | Listar etapas de fermentação  |
| POST   | `/api/recipes/{id}/fermentation-steps/`                | Adicionar etapa de fermentação|

---

## Exemplo: Criar uma Receita Completa (POST /api/recipes/)

```json
{
  "name": "American IPA",
  "style": 1,
  "author": "Matheus",
  "batch_size_l": 20,
  "boil_volume_l": 25,
  "boil_time_min": 60,
  "efficiency_pct": 75,
  "og": 1.065,
  "fg": 1.012,
  "abv": 7.0,
  "ibu": 65,
  "ebc": 12,
  "description": "West Coast IPA tropical e cítrica",
  "malts": [
    { "malt": 1, "amount_kg": 5.0, "percentage": 85 },
    { "malt": 2, "amount_kg": 0.5, "percentage": 8 },
    { "malt": 3, "amount_kg": 0.4, "percentage": 7 }
  ],
  "hops": [
    { "hop": 1, "amount_g": 30, "use": "boil",      "time_min": 60 },
    { "hop": 2, "amount_g": 20, "use": "boil",      "time_min": 15 },
    { "hop": 2, "amount_g": 40, "use": "dry_hop",   "time_min": 4 }
  ],
  "yeasts": [
    { "yeast": 1, "amount": 1, "starter": false }
  ],
  "mash_steps": [
    { "name": "Mash In", "step_type": "infusion",    "temp_c": 67, "time_min": 60, "water_l": 15, "water_temp_c": 72, "order": 1 },
    { "name": "Mash Out", "step_type": "temperature", "temp_c": 76, "time_min": 10, "order": 2 }
  ],
  "fermentation_steps": [
    { "stage": "primary",    "temp_c": 19, "duration_days": 7,  "order": 1 },
    { "stage": "dry_hop",    "temp_c": 19, "duration_days": 4,  "order": 2 },
    { "stage": "lagering",   "temp_c": 2,  "duration_days": 3,  "order": 3 }
  ],
  "water_profile": {
    "calcium_ppm": 75,
    "magnesium_ppm": 5,
    "sodium_ppm": 10,
    "chloride_ppm": 50,
    "sulfate_ppm": 150,
    "bicarbonate_ppm": 50,
    "ph": 5.3
  }
}
```

---

## Admin

Acesse `/admin/` para gerenciar todos os dados pelo painel administrativo do Django (requer superusuário).
