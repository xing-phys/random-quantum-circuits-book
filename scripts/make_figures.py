"""Render original textbook figures and plot the Julia-generated CSV.
No external images or datasets are downloaded. Run from any directory.
"""
from pathlib import Path
import csv
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
FIGS = ROOT / "figs"
FIGS.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False,
    "savefig.facecolor": "white", "axes.labelsize": 11,
    "pdf.fonttype": 42, "svg.fonttype": "none"})
TEAL, BLUE, CORAL, GOLD = "#087e8b", "#2864a0", "#c85443", "#aa7b16"

def save(fig, name):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(FIGS / f"{name}.{ext}", bbox_inches="tight", dpi=190)
    plt.close(fig)

def arrow(ax, start, end, color=BLUE, **kwargs):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13,
                                 color=color, linewidth=1.4, **kwargs))

fig, ax = plt.subplots(figsize=(8,4.6))
for x in range(8):
    ax.plot([x,x],[-.4,4.6],color="#aab5bd",lw=1.5,zorder=0)
    ax.text(x,-.65,str(x+1),ha="center",fontsize=10)
for layer in range(4):
    y = layer + .4
    for x in range(layer%2,7,2):
        ax.add_patch(Rectangle((x-.13,y-.17),1.26,.34,facecolor=TEAL,edgecolor="white",zorder=2))
        ax.text(x+.5,y,"U",ha="center",va="center",color="white",fontsize=10)
for x,y in [(2,1.85),(5,2.85),(0,3.85),(6,.85)]:
    ax.add_patch(Rectangle((x-.18,y-.07),.36,.14,facecolor=CORAL,zorder=4))
arrow(ax,(-.7,0),(-.7,4.4),color="#334155")
ax.text(-1.05,2.2,"time (layers)",rotation=90,ha="center",va="center")
ax.text(3.5,-1.05,"space: sites along an open chain",ha="center")
ax.text(7.6,3.6,"two-site\nunitary",color=TEAL,va="center")
ax.text(7.6,1.9,"local\nmeasurement",color=CORAL,va="center")
ax.set(xlim=(-1.4,9.1),ylim=(-1.2,4.8)); ax.axis("off")
save(fig,"brickwork")

fig, axes = plt.subplots(1,2,figsize=(8,3.7))
for ax, swap in zip(axes,(False,True)):
    for x in (0,1):
        target=1-x if swap else x
        ax.plot([x,target],[0,1],color=TEAL if x==0 else BLUE,lw=2.6)
        ax.scatter([x,target],[0,1],color=TEAL if x==0 else BLUE,s=45,zorder=3)
    ax.text(0,-.2,r"$a_1$",ha="center"); ax.text(1,-.2,r"$a_2$",ha="center")
    ax.text(0,1.18,r"$b_1$",ha="center"); ax.text(1,1.18,r"$b_2$",ha="center")
    ax.set_title("Swap pairing" if swap else "Identity pairing",pad=23)
    ax.set(xlim=(-.4,1.4),ylim=(-.35,1.4)); ax.axis("off")
fig.subplots_adjust(wspace=.35)
save(fig,"pairings")

fig, ax = plt.subplots(figsize=(7.6,4.2))
ell,t=4,3
ax.fill_between([0,ell],[t,t],[t+.35,t+.35],color=TEAL,alpha=.25)
ax.plot([-2,6],[0,0],color="#718096",lw=1.5)
ax.plot([-2,6],[t,t],color="#718096",lw=1.5)
ax.plot([0,0],[0,t],color=BLUE,lw=2.7)
ax.plot([ell,ell],[0,t],color=BLUE,lw=2.7)
ax.plot([0,ell/2,ell],[t,t-1.35,t],color=CORAL,lw=2.7)
ax.text(ell/2,t+.5,r"interval $A$, length $\ell$",ha="center",color=TEAL)
ax.text(-.25,1.2,"growth cuts",ha="right",color=BLUE)
ax.text(ell/2,t-1.65,"saturation cut",ha="center",color=CORAL)
ax.text(-1.8,-.35,"initial product state",color="#334155")
arrow(ax,(-2.4,0),(-2.4,t+.2),color="#334155")
ax.text(-2.75,1.5,"time",rotation=90,ha="center",va="center")
ax.set(xlim=(-3,6),ylim=(-.6,t+.9));ax.axis("off")
save(fig,"membrane")

fig,ax = plt.subplots(figsize=(7.5,3.8))
x=np.linspace(-2,12,500)
for t,c in [(2,BLUE),(5,TEAL),(9,CORAL)]:
    v,D=.7,.18
    y=np.array([.5*math.erfc((xx-v*t)/math.sqrt(4*D*t)) for xx in x])
    ax.plot(x,y,color=c,label=f"t = {t}")
ax.set(xlabel="position x",ylabel="schematic normalized OTOC",ylim=(-.03,1.08))
ax.legend(frameon=False); ax.grid(alpha=.13)
ax.text(.02,.06,"Illustration of drift and broadening; not simulation data",transform=ax.transAxes,fontsize=9)
save(fig,"operator-front")

with (ROOT/"data/entanglement.csv").open() as f:
    rows=list(csv.DictReader(f))
fig,axes=plt.subplots(1,2,figsize=(10,3.9))
for p,c in zip((0,.15,.6,1),(BLUE,TEAL,CORAL,GOLD)):
    group=[r for r in rows if float(r["p"])==p]
    t=np.array([int(r["layers"]) for r in group])
    s=np.array([float(r["S1_mean"]) for r in group]); e=np.array([float(r["S1_se"]) for r in group])
    axes[0].plot(t,s,color=c,label=f"p = {p:g}")
    axes[0].fill_between(t,s-2*e,s+2*e,color=c,alpha=.14)
axes[0].axhline(4*math.log(2),color="#6b7280",ls="--",lw=1)
axes[0].text(14,4*math.log(2)+.06,r"$4\ln 2$ (upper bound)",fontsize=9,color="#4b5563")
axes[0].set(xlabel="time (one brickwork layer)",ylabel=r"mean half-chain $S_1$ (nats)",ylim=(-.08,3.1))
axes[0].legend(frameon=False,fontsize=9,loc="center right")
group=[r for r in rows if float(r["p"])==0]
t=np.array([int(r["layers"]) for r in group])
axes[1].plot(t,[float(r["S1_mean"]) for r in group],label=r"$\overline{S_1}$",color=BLUE)
axes[1].plot(t,[float(r["S2_mean"]) for r in group],label=r"$\overline{S_2}$",color=TEAL)
axes[1].plot(t,[float(r["annealed_S2"]) for r in group],label=r"$-\ln\overline{\mathrm{Tr}\rho_A^2}$",color=CORAL,ls="--")
axes[1].set(xlabel="time (one brickwork layer)",ylabel="entropy (nats)",title="Different averages, p = 0",ylim=(-.08,3.1))
axes[1].legend(frameon=False,fontsize=9,loc="lower right")
for ax in axes:ax.grid(alpha=.13)
fig.tight_layout()
save(fig,"entanglement-lab")
print("Wrote five original figures in PNG, PDF, and SVG formats.")
