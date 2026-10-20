# Figure provenance

All figures in this book are original, created for this project. No figure
from the review or another paper is reproduced. The physics sources are
cited in the surrounding chapters and captions. Original figures are
licensed CC BY 4.0 with attribution to Ze-Yu Xing.

| Asset stem | Content and provenance | Generator |
| --- | --- | --- |
| `brickwork` | Schematic alternating gates and local measurements; chosen measurement locations are illustrative. | `scripts/make_figures.py` |
| `pairings` | Original identity/swap index-pairing diagram. | `scripts/make_figures.py` |
| `membrane` | Schematic competing interval entanglement cuts; shapes do not encode a fitted line tension. | `scripts/make_figures.py` |
| `operator-front` | Analytic erfc profile illustrating drift and diffusive broadening, with chosen v=0.7, D=0.18. This is not numerical or experimental data. | `scripts/make_figures.py` |
| `entanglement-lab` | Exact state-vector Julia simulation, open L=8 chain, T=32 layers, 128 trajectories per measurement rate, MersenneTwister seeds 20261021–20261024. Shading is ±2 standard errors. Input: `data/entanglement.csv`. | `scripts/circuits.jl`, `scripts/make_figures.py` |

Each asset has a vector PDF and SVG and a high-resolution PNG. The HTML
uses PNG for broad compatibility; the combined PDF uses the vector PDF via
Quarto's extensionless figure references. These selections are checked
during rendering.
