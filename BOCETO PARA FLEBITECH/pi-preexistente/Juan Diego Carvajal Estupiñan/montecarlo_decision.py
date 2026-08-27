"""
Montecarlo de decisión — Hackathon Colsubsidio 2026
Reto 01 (Crédito Hiperpersonalizado) vs Reto 02 (Venta Automatizada de Seguros)

Qué hace:
  Simula el puntaje ponderado del jurado (0-100) para cada reto sobre N escenarios,
  usando distribuciones Beta-PERT por criterio calibradas con datos reales del mercado
  y con las capacidades reales del equipo. Reporta puntaje esperado, dispersión,
  probabilidad de que un reto supere al otro, y qué criterio explica la diferencia.

Honestidad metodológica (regla de Juan: no inventar datos):
  Los números "duros" (penetración de crédito 35.5%, seguros 3.29% del PIB, 1.6M
  afiliados, etc.) vienen de fuentes citadas en el dossier. Los (min, moda, max) de
  cada criterio NO son hechos: son PRIORS calibrados = juicio experto explícito sobre
  rangos plausibles. El Montecarlo existe precisamente para cuantificar esa incertidumbre,
  no para esconderla. Cambia los priors en CALIBRACION y el resultado se recalcula.
"""

import numpy as np
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RNG = np.random.default_rng(42)
N = 200_000  # escenarios

# --- Pesos del jurado (Punto 12 de los TyC) ---
PESOS = {
    "Impacto":        0.30,
    "Innovacion":     0.20,
    "Viab_tecnica":   0.20,
    "Viab_implement": 0.20,
    "Pitch":          0.10,
}
assert abs(sum(PESOS.values()) - 1.0) < 1e-9

# --- CALIBRACION: (min, moda, max) en escala 0-10 por criterio y reto ---
# Racional resumido (detalle en el dossier):
#  R01 Crédito: acceso a crédito 35.5% y consumo 19% => techo de impacto alto y datos
#    de comportamiento ricos (categorías A/B/C, libranza). Pero implementación choca con
#    regulación (Habeas Data, SFC) y modelos de riesgo reales => implementación media.
#  R02 Seguros: penetración 3.29% del PIB vs 9.3% OCDE => brecha enorme = impacto alto.
#    Funnel conversacional + cotización/cierre encaja con el stack no-code/UX de Juan =>
#    técnica e implementación fuertes; demo "quedé asegurado 24/7" = pitch más limpio.
CALIBRACION = {
    "Reto 01 — Crédito Hiperpersonalizado": {
        "Impacto":        (6.0, 8.0, 9.5),
        "Innovacion":     (5.0, 6.5, 8.5),
        "Viab_tecnica":   (6.5, 8.0, 9.0),
        "Viab_implement": (4.0, 6.0, 8.0),
        "Pitch":          (6.5, 8.0, 9.5),
    },
    "Reto 02 — Venta Automatizada de Seguros": {
        "Impacto":        (6.0, 7.5, 9.5),
        "Innovacion":     (5.5, 7.0, 9.0),
        "Viab_tecnica":   (6.5, 8.5, 9.5),
        "Viab_implement": (6.0, 7.5, 9.0),
        "Pitch":          (7.0, 8.5, 9.5),
    },
}

# Factor de ejecución compartido: cómo rinde el equipo ese fin de semana afecta a ambos
# retos por igual => induce correlación positiva y hace realista la comparación cabeza a cabeza.
EXEC_SIGMA = 0.6  # desviación en puntos (0-10) del shock común


def pert_sample(mn, mode, mx, size, lamb=4.0):
    """Muestrea de una distribución Beta-PERT en [mn, mx] con moda 'mode'."""
    if mx <= mn:
        return np.full(size, mode)
    alpha = 1 + lamb * (mode - mn) / (mx - mn)
    beta_ = 1 + lamb * (mx - mode) / (mx - mn)
    return mn + RNG.beta(alpha, beta_, size) * (mx - mn)


# Shock de ejecución común a ambos retos (mismo equipo, mismo fin de semana)
exec_shock = RNG.normal(0.0, EXEC_SIGMA, N)

resultados = {}
criterios = list(PESOS.keys())

for reto, params in CALIBRACION.items():
    draws = {}
    total = np.zeros(N)
    for c in criterios:
        mn, mode, mx = params[c]
        base = pert_sample(mn, mode, mx, N)
        val = np.clip(base + exec_shock, 0, 10)  # aplica shock común y acota a [0,10]
        draws[c] = val
        total += PESOS[c] * val
    resultados[reto] = {"draws": draws, "score": total * 10.0}  # escala a 0-100

retos = list(resultados.keys())
r1, r2 = retos[0], retos[1]
s1, s2 = resultados[r1]["score"], resultados[r2]["score"]

# --- Estadísticos ---
def resumen(score):
    return {
        "media": float(np.mean(score)),
        "std": float(np.std(score)),
        "p5": float(np.percentile(score, 5)),
        "p50": float(np.percentile(score, 50)),
        "p95": float(np.percentile(score, 95)),
    }

stats = {r: resumen(resultados[r]["score"]) for r in retos}

diff = s2 - s1  # Reto 02 menos Reto 01
p_r2_gana = float(np.mean(s2 > s1))
p_r1_gana = 1.0 - p_r2_gana

# --- Sensibilidad: cuánto explica cada criterio la ventaja de un reto sobre otro ---
# Correlación entre el draw (diferencia por criterio) y el margen total.
sens = {}
for c in criterios:
    dcrit = resultados[r2]["draws"][c] - resultados[r1]["draws"][c]
    if np.std(dcrit) > 1e-9:
        corr = float(np.corrcoef(dcrit, diff)[0, 1])
    else:
        corr = 0.0
    # contribución esperada al margen (en puntos 0-100)
    contrib = float(PESOS[c] * np.mean(dcrit) * 10.0)
    sens[c] = {"contrib_margen_pts": contrib, "corr_con_margen": corr}

# --- Salida en consola ---
print("=" * 64)
print(f"MONTECARLO DECISIÓN — N = {N:,} escenarios")
print("=" * 64)
for r in retos:
    st = stats[r]
    print(f"\n{r}")
    print(f"  Media {st['media']:.1f} | Desv {st['std']:.1f} | "
          f"P5 {st['p5']:.1f} | Mediana {st['p50']:.1f} | P95 {st['p95']:.1f}")
print("\n" + "-" * 64)
print(f"P(Reto 02 > Reto 01) = {p_r2_gana*100:.1f}%")
print(f"P(Reto 01 > Reto 02) = {p_r1_gana*100:.1f}%")
print(f"Margen medio (R02 - R01) = {np.mean(diff):+.2f} pts  "
      f"[P5 {np.percentile(diff,5):+.1f}, P95 {np.percentile(diff,95):+.1f}]")
print("\nSensibilidad (qué explica el margen R02 - R01):")
for c in sorted(sens, key=lambda k: -abs(sens[k]["contrib_margen_pts"])):
    print(f"  {c:16s} contrib {sens[c]['contrib_margen_pts']:+.2f} pts | "
          f"corr {sens[c]['corr_con_margen']:+.2f}")

# --- Guardar JSON de resultados ---
out = {
    "N": N,
    "pesos": PESOS,
    "exec_sigma": EXEC_SIGMA,
    "calibracion": CALIBRACION,
    "stats": stats,
    "p_reto02_gana": p_r2_gana,
    "p_reto01_gana": p_r1_gana,
    "margen_medio_r2_menos_r1": float(np.mean(diff)),
    "margen_p5": float(np.percentile(diff, 5)),
    "margen_p95": float(np.percentile(diff, 95)),
    "sensibilidad": sens,
}
with open("montecarlo_resultados.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

# --- Gráfica 1: distribuciones de puntaje ---
plt.figure(figsize=(9, 5))
plt.hist(s1, bins=80, alpha=0.55, label=r1, color="#2563eb", density=True)
plt.hist(s2, bins=80, alpha=0.55, label=r2, color="#16a34a", density=True)
plt.axvline(np.mean(s1), color="#2563eb", ls="--", lw=1.5)
plt.axvline(np.mean(s2), color="#16a34a", ls="--", lw=1.5)
plt.xlabel("Puntaje ponderado del jurado (0-100)")
plt.ylabel("Densidad")
plt.title("Distribución de puntaje esperado por reto — Montecarlo")
plt.legend()
plt.tight_layout()
plt.savefig("mc_distribuciones.png", dpi=130)
plt.close()

# --- Gráfica 2: histograma del margen ---
plt.figure(figsize=(9, 5))
plt.hist(diff, bins=90, color="#7c3aed", alpha=0.75, density=True)
plt.axvline(0, color="black", lw=1.2)
plt.axvline(np.mean(diff), color="#dc2626", ls="--", lw=1.6,
            label=f"Margen medio {np.mean(diff):+.1f} pts")
plt.xlabel("Margen de puntaje (Reto 02 − Reto 01)")
plt.ylabel("Densidad")
plt.title(f"Ventaja de Reto 02 sobre Reto 01  |  P(R02 gana) = {p_r2_gana*100:.0f}%")
plt.legend()
plt.tight_layout()
plt.savefig("mc_margen.png", dpi=130)
plt.close()

# --- Gráfica 3: contribución esperada por criterio al margen ---
orden = sorted(criterios, key=lambda k: sens[k]["contrib_margen_pts"])
vals = [sens[c]["contrib_margen_pts"] for c in orden]
colores = ["#16a34a" if v >= 0 else "#dc2626" for v in vals]
plt.figure(figsize=(9, 5))
plt.barh(orden, vals, color=colores)
plt.axvline(0, color="black", lw=1)
plt.xlabel("Contribución al margen R02 − R01 (puntos)")
plt.title("Qué criterio inclina la balanza (verde = favorece Seguros)")
plt.tight_layout()
plt.savefig("mc_sensibilidad.png", dpi=130)
plt.close()

print("\nArchivos: montecarlo_resultados.json, mc_distribuciones.png, "
      "mc_margen.png, mc_sensibilidad.png")
