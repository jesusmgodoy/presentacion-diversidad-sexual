from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "datos/ficha_variable_3568_0_0_P18.xlsx"
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

with ZipFile(SOURCE) as archive:
    strings = ["".join(item.itertext()) for item in
               ET.fromstring(archive.read("xl/sharedStrings.xml")).findall("s:si", NS)]
    cells = {}
    for cell in ET.fromstring(archive.read("xl/worksheets/sheet1.xml")).findall(".//s:c", NS):
        value = cell.find("s:v", NS)
        if value is not None:
            cells[cell.get("r")] = (strings[int(value.text)]
                                   if cell.get("t") == "s" else float(value.text))

# C11:C19 contains the CIS percentages; keep their original denominator.
percentages = [cells[f"C{row}"] * 100 for row in range(11, 20)]
labels = ["Ninguna", "1 persona", "2 personas", "3 personas", "4 personas",
          "Entre 5 y 10", "Entre 11 y 20", "Entre 21 y 100", "Más de 100"]
assert len(percentages) == 9 and cells["C20"] == 0.047 and cells["C21"] == 0.03

plt.rcParams.update({"font.family": "Arial", "svg.fonttype": "path"})
fig, ax = plt.subplots(figsize=(12.8, 5.2), facecolor="white")
fig.subplots_adjust(left=0.235, right=0.92, top=0.97, bottom=0.15)
ax.barh(range(9), percentages, height=0.62, color="#CB2C30", zorder=3)
ax.set_yticks(range(9), labels, fontsize=18, color="#424242")
ax.invert_yaxis()
ax.set_xlim(0, 30)
ax.set_xticks([0, 10, 20, 30])
ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:.0f} %"))
ax.tick_params(axis="x", labelsize=17, colors="#666666", length=0, pad=10)
ax.tick_params(axis="y", length=0, pad=14)
ax.set_xlabel("Porcentaje del total de la muestra", fontsize=17, color="#424242", labelpad=12)
ax.set_axisbelow(True)
ax.grid(axis="x", color="#E6E6E6", linewidth=0.8)
for spine in ax.spines.values():
    spine.set_visible(False)
for index, value in enumerate(percentages):
    label = f"{value:.1f}".replace(".", ",") + " %"
    ax.text(value + 0.4, index, label, va="center", fontsize=18,
            fontweight="bold", color="#424242")
fig.savefig(ROOT / "imagenes/parejas-sexuales-p18.svg", facecolor="white")
plt.close(fig)
print("Porcentajes originales del CIS:", [round(value, 1) for value in percentages])
