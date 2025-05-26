import sqlite3
import pandas as pd
from IPython.display import Markdown
from tabulate import tabulate

def db_fetch(statement):
  con = sqlite3.connect("data/genetic_code.db")
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
