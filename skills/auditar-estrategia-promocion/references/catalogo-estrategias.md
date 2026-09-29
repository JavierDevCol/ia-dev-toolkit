# Catálogo de estrategias de paso de ambientes

Cada estrategia tiene: descripción, requisitos para adoptarla y una tabla de señales
de scoring. Score final por estrategia = `clamp(50 + Σpuntos_señales_matcheadas, 0, 100)`.

No agregar señales fuera de estas tablas al puntuar — mantiene el score determinístico
y auditable entre corridas.

---

## 1. GitFlow + release branches

**Descripción:** rama `develop` persistente + ramas `release/vX.Y.Z` efímeras por
release, tags semver, típicamente con aprobación manual por ambiente.

**Requisitos:** disciplina de branching, alguien que gestione el ciclo de vida de las
ramas release, tolerancia a ceremonia extra en cada entrega.

| Señal | Origen | Puntos |
|---|---|---|
| Ya existen ramas `develop` + `release/*` (o equivalentes) | Git | +25 |
| Tags con convención semver detectados | Git | +10 |
| Aprobación manual entre ambientes | Cuestionario Q4 | +15 |
| Compliance/auditoría formal exigida | Cuestionario Q7 | +10 |
| Necesitan rollback instantáneo antes de llegar a prod | Cuestionario Q5 | +10 |
| Frecuencia deploy deseada = diaria/continua | Cuestionario Q3 | −20 |
| Equipo ≤3 personas | Cuestionario Q1 | −10 |

---

## 2. Trunk-Based + feature flags

**Descripción:** todos los cambios van directo a `main`/`trunk` en commits pequeños y
frecuentes; funcionalidad incompleta se oculta tras feature flags en vez de ramas de
larga vida.

**Requisitos:** CI robusto que actúe como gate en cada push, sistema de feature flags,
cultura de commits pequeños.

| Señal | Origen | Puntos |
|---|---|---|
| CI corre gate de tests en cada push a `main` | CI/CD | +20 |
| Ya usan o están dispuestos a usar feature flags | Cuestionario Q6 | +25 |
| Frecuencia deploy deseada = diaria/continua | Cuestionario Q3 | +15 |
| Aprobación automática (sin gate manual) | Cuestionario Q4 | +15 |
| Ramas de larga vida detectadas (feature branches viejas) | Git | −15 |
| Compliance exige aprobación manual por ambiente | Cuestionario Q7 | −20 |
| Sin feature flags y sin plan de adoptarlos | Cuestionario Q6 | −20 |

---

## 3. GitHub Flow (PR directo a main, deploy continuo)

**Descripción:** `main` siempre desplegable, PRs cortos desde feature branches, deploy
automático apenas se mergea.

**Requisitos:** pocos ambientes reales, buena cobertura de tests automatizados, buen
mecanismo de rollback rápido.

| Señal | Origen | Puntos |
|---|---|---|
| Sin ramas `develop`/`release` (solo `main` + features cortas) | Git | +20 |
| CI dispara deploy automático al mergear a `main` | CI/CD | +20 |
| ≤2 ambientes reales | Cuestionario Q2 | +15 |
| Equipo pequeño-mediano (≤8 personas) | Cuestionario Q1 | +10 |
| Aprobación automática (sin gate manual) | Cuestionario Q4 | +10 |
| Múltiples ambientes con aprobación formal | Cuestionario Q2+Q4 | −20 |
| Compliance exige ventanas de release fijas | Cuestionario Q7 | −15 |

---

## 4. Release Trains (ventanas fijas)

**Descripción:** releases salen en un calendario fijo (ej. cada 2 semanas); lo que no
llega a tiempo espera al próximo tren en vez de forzar una entrega ad-hoc.

**Requisitos:** múltiples equipos/features coordinando, tolerancia a que algo espere
al siguiente ciclo.

| Señal | Origen | Puntos |
|---|---|---|
| Historial de merges muestra cadencia regular (`git log` por periodo) | Git | +15 |
| Equipo grande / múltiples equipos coordinando | Cuestionario Q1 | +15 |
| Frecuencia deploy deseada = predecible, no continua | Cuestionario Q3 | +20 |
| Frecuencia deploy deseada = diaria/continua | Cuestionario Q3 | −25 |
| Equipo ≤5 personas | Cuestionario Q1 | −15 |

---

## 5. Environment Branches (develop→qa→main)

**Descripción:** una rama persistente por ambiente; promover = PR/merge de la rama de
un ambiente a la del siguiente.

**Requisitos:** disciplina para no commitear directo en ramas de ambiente, aprobación
por ambiente, tolerancia a mantener varias ramas vivas permanentemente.

| Señal | Origen | Puntos |
|---|---|---|
| Ya existen ramas persistentes por ambiente (`develop`/`qa`/`main` o similar) | Git | +30 |
| CI dispara distinto por cada rama (rama = ambiente) | CI/CD | +15 |
| Aprobación manual entre pasos | Cuestionario Q4 | +10 |
| Compliance/auditoría formal exigida | Cuestionario Q7 | +10 |
| Necesitan rollback instantáneo (ambientes intermedios validan antes) | Cuestionario Q5 | +10 |
| Ya usan tags como mecanismo principal de promoción | Git | −15 |
| Buscan reducir ramas de larga vida (respuesta abierta del usuario) | Cuestionario | −10 |

---

## 6. Promoción por tags/artefactos versionados

**Descripción:** el build produce un artefacto inmutable versionado (imagen, paquete)
una sola vez; promover un ambiente es desplegar el mismo artefacto, nunca rebuildear.

**Requisitos:** pipeline que separe build de deploy, versión de artefacto trazable,
valor especial cuando se exige que "lo que se probó en QA es exactamente lo que llega
a PROD".

| Señal | Origen | Puntos |
|---|---|---|
| Tags semver ya en uso de forma consistente | Git | +20 |
| Pipeline separa build de deploy (job de build único reusado) | CI/CD | +20 |
| ≥3 ambientes reales | Cuestionario Q2 | +15 |
| Compliance exige "mismo artefacto probado en QA llega a PROD" | Cuestionario Q7 | +15 |
| Pipeline rebuildea en cada ambiente (sin artefacto único) | CI/CD | −20 |
| No versionan builds hoy | Git | −10 |
