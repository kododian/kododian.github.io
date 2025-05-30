from pathlib import Path
import pandas as pd
from IPython.display import Markdown
from tabulate import tabulate
import sqlite3

# Get the absolute path to the data folder
this_file = Path(__file__).resolve()
project_root = this_file.parents[1]  # go up from lib/ to shared/
db_path = str(project_root / "data" / "genetic_code.db")

def db_fetch(statement):
  con = sqlite3.connect(db_path)
  df = pd.read_sql_query(statement, con)
  con.close()
  return df

def db_df(statement, **kwargs):
  return db_fetch(statement)

def db_table(statement, headers=None, **kwargs):
  df = db_fetch(statement)
  # Determine headers: use provided headers, or default to df.columns
  header_row = headers if headers is not None else df.columns
  return Markdown(tabulate(df.values, headers=header_row, showindex=False, **kwargs))
