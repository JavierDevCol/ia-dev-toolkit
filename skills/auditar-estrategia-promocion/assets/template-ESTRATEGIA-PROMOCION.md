<!--
  Plantilla para ESTRATEGIA-PROMOCION-{nombre_repo}.md.
  Los placeholders tienen formato {{PLACEHOLDER}}.
-->

# Estrategia de Paso de Ambientes — {{REPO_NAME}}

> **Fecha:** {{DATE}}

## 1. Resumen

{{SUMMARY}}

- **Repositorio:** {{REPO_URL}}
- **Ramas detectadas:** {{DETECTED_BRANCHES}}
- **CI/CD detectado:** {{DETECTED_CICD}}

## 2. Señales detectadas

### Git

| Señal | Detectado |
|-------|-----------|
| {{GIT_SIGNAL}} | {{GIT_VALUE}} |

### CI/CD

| Señal | Detectado |
|-------|-----------|
| {{CICD_SIGNAL}} | {{CICD_VALUE}} |

## 3. Respuestas del cuestionario

| Pregunta | Respuesta |
|----------|-----------|
| {{QUESTION}} | {{ANSWER}} |

## 4. Ranking de estrategias

| # | Estrategia | Acoplamiento | Resumen |
|---|-----------|--------------|---------|
| {{RANK}} | {{STRATEGY_NAME}} | {{SCORE}}/100 | {{ONE_LINE_SUMMARY}} |

## 5. Detalle por estrategia

### {{STRATEGY_NAME}}

**Score:** {{SCORE}}/100

- **Señales que suman:** {{POSITIVE_SIGNALS}}
- **Señales que restan:** {{NEGATIVE_SIGNALS}}
- **Qué cambiar para adoptarla:** {{CHANGES_NEEDED}}

## 6. Recomendación

{{RECOMMENDATION}}

---

*Documento generado con auditar-estrategia-promocion skill — {{DATE}}*
