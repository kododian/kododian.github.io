import yaml
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from chemformula import ChemFormula

class FlexibleGridPlot:
  def __init__(self, config_file):
    self.cells = []

    with open(config_file, 'r') as f:
      config = yaml.safe_load(f)
    self.n_rows = config.get("n_rows", 12)
    self.n_cols = config.get("n_cols", 12)
    self.cell_size = config.get("cell_size", 1)
    self.groups = {g["group"]: g["color"] for g in config.get("groups", [])}
    self.cells = config.get("cells", [])
    self.merged_cells = config.get("merged_cells", [])
  
  def index_to_coords(self, index):
    """Map 1-based index to 2x2 supercell coordinates"""
    row = 1 + ((index - 1) // 4) * 2
    col = 1 + ((index - 1) % 4) * 2
    return row, col
 
  def draw_block(self, ax, row, col, rowspan, colspan, text, color="white", edgecolor="black"):
    x = col
    y = row
    w = colspan
    h = rowspan
    rect = patches.Rectangle((x, y), w, h, linewidth=1,
                             edgecolor=edgecolor, facecolor=color)
    ax.add_patch(rect)
    if text:
      ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=10)

  def draw_subtexts(self, ax, row, col, texts, sizes):
    positions = [
      (col + 0.5, row + 0.5),    # top-left
      (col + 1.5, row + 0.5),    # top-right
      (col + 0.5, row + 1.5),    # bottom-left
      (col + 1.5, row + 1.5)     # bottom-right
    ]
    for i, text in enumerate(texts):
      if text:
        size = sizes[i] if sizes and i < len(sizes) else 12
        ax.text(*positions[i], text, ha='center', va='center', fontsize=size)
        
  def draw(self):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, self.n_cols)
    ax.set_ylim(0, self.n_rows)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Draw merged cells manually
    for cell in self.merged_cells:
      self.draw_block(ax, cell["row"], cell["col"], 2, 2, cell.get("text", ""), cell.get("color", "white"))
    
    # Draw indexed 2x2 cells
    for cell in self.cells:
      row, col = self.index_to_coords(cell["index"])
      color = self.groups.get(cell["group"], "white")
      # Outer rectangle
      self.draw_block(ax, row, col, 2, 2, "", color=color, edgecolor='black')
      # Chemical Formula
      formula = ChemFormula(cell.get("formula", ""), charge = 0, name = None, cas = None)
      # Subcell texts
      texts = [
        cell.get("text", ""),
        cell.get("name", ""),
        formula.unicode,
        str(cell.get("value", ""))
      ]
      sizes = [
        24,
        14,
        12,
        20
      ]
      self.draw_subtexts(ax, row, col, texts, sizes)
    
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
