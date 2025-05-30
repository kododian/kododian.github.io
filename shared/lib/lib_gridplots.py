import yaml
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from chemformula import ChemFormula
import traceback

class FlexibleGridPlot:
  def __init__(self, config_file='', df=None):
    self.cells = []
    self.df = df

    with open(config_file, 'r') as f:
      config = yaml.safe_load(f)
    self.n_rows = config.get("n_rows", 12)
    self.n_cols = config.get("n_cols", 12)
    self.cells_offset = config.get("cells_offset", [0, 0])
    self.cells_display = config.get("cells_display", ["tl", "tr", "bl", "br"])
    self.groups = {g["family"]: g["color"] for g in config.get("groups", [])}
    self.cells = config.get("cells", [])
    self.merged_cells = config.get("merged_cells", [])
    self.sizes = config.get("sizes", [24, 14, 11, 20])
  
  def index_to_coords(self, index):
    """Map 1-based index to 2x2 supercell coordinates"""
    row = self.cells_offset[0] + ((index - 1) // 4) * 2
    col = self.cells_offset[1] + ((index - 1) % 4) * 2
    return row, col
  
  def format_texts(self, values):
    return "\n".join(
      f.strip()
      for f in values.split(", ") if f.strip()
    ) if values.strip() else ""
        
  def format_formulas(self, values):
    return "\n".join(
      ChemFormula(f.strip(), charge=0, name=None, cas=None).unicode
      for f in values.split(", ") if f.strip()
    ) if values.strip() else ""
 
  def draw_block(self, ax, row, col, rowspan, colspan, main, sub, color="white", edgecolor="black"):
    x = col
    y = row
    w = colspan
    h = rowspan
    rect = patches.Rectangle((x, y), w, h, linewidth=1,
                             edgecolor=edgecolor, facecolor=color)
    ax.add_patch(rect)
    if main and sub:
      ax.text(x + w/2, y + 1/3*h, main, ha='center', va='center', fontsize=self.sizes[0])
      ax.text(x + w/2, y + 2/3*h, sub, ha='center', va='center', fontsize=self.sizes[0]*0.7)
    elif main:
      ax.text(x + w/2, y + 1/2*h, main, ha='center', va='center', fontsize=self.sizes[0])

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
    try:
      df = self.df
      fig, ax = plt.subplots(figsize=(10, 10))
      ax.set_xlim(0, self.n_cols)
      ax.set_ylim(0, self.n_rows)
      ax.set_aspect('equal')
      ax.axis('off')
      
      # Draw merged cells manually
      for cell in self.merged_cells:
        value_col = cell.get("value", None)
        mainids = cell.get("mainids", [])
        subdivider = cell.get("subdivider", 1)
        valueadd = cell.get("valueadd", 0)
        total = df[df["id"].isin(mainids)][value_col].sum() if value_col != None else 0
        total = total + valueadd
        mainprefix = str(total) if total > 0 else ""
        subresult = int(total/subdivider) if total % subdivider == 0 else total/subdivider
        subprefix = (
          f"{int(subresult)}" if float(subresult).is_integer() else f"{subresult:.2f}"
        ) if total > 0 else ""
        
        self.draw_block(ax, 
          cell["row"], cell["col"], 
          cell.get("rowspan", 1), 
          cell.get("colspan", 1), 
          mainprefix + cell.get("main", ""), 
          subprefix + cell.get("sub", ""), 
          cell.get("color", "white")
        )
      
      # Draw indexed 2x2 cells
      for cell in self.cells:
        row, col = self.index_to_coords(cell.get("index", 0))
        id = cell.get("id", None)
        tl_col = cell.get("tl", None)
        tr_col = cell.get("tr", None)
        bl_col = cell.get("bl", None)
        br_col = cell.get("br", None)
        value_col = cell.get("value", None)
        group_col = cell.get("group", None)
        valueadd = cell.get("valueadd", 0)
        
        tl = df.loc[df["id"] == id, tl_col].iloc[0] if tl_col != None else ""
        tr = df.loc[df["id"] == id, tr_col].iloc[0] if tr_col != None else ""
        bl = df.loc[df["id"] == id, bl_col].iloc[0] if bl_col != None else ""
        br = df.loc[df["id"] == id, br_col].iloc[0] if br_col != None else ""
        value = br = df.loc[df["id"] == id, value_col].iloc[0] if value_col != None else 0
        value = value + valueadd
        group = df.loc[df["id"] == id, group_col].iloc[0] if group_col != None else ""
        
        color = self.groups.get(group, "white")
        # Outer rectangle
        self.draw_block(ax, row, col, 2, 2, "", "", color=color, edgecolor='black')
        # Chemical Formula
        formula = "\n".join(
          ChemFormula(f.strip(), charge=0, name=None, cas=None).unicode
          for f in bl.split(", ") if f.strip()
        ) if bl.strip() else ""
        
        # Subcell texts
        texts = [
          self.format_texts(str(tl)) if "tl" in self.cells_display else "",
          self.format_texts(str(tr)) if "tr" in self.cells_display else "",
          self.format_formulas(bl) if "bl" in self.cells_display else "",
          self.format_texts(str(br)) if "br" in self.cells_display else ""
        ]
        sizes = self.sizes
        self.draw_subtexts(ax, row, col, texts, sizes)
      
      plt.gca().invert_yaxis()
      plt.tight_layout()
      plt.show()
    except Exception:
      traceback.print_exc()
