# app/processing/table_extractor.py

import pandas as pd
from io import StringIO
# -------------------------
# HTML TABLE EXTRACTION
# -------------------------
def extract_tables_from_html(html):
    """
    Extract tables from HTML using pandas
    """
    tables_data = []

    try:
       

        tables = pd.read_html(StringIO(html))

        for table in tables:
            tables_data.append(table.to_dict(orient="records"))

    except Exception as e:
        print("⚠️ HTML table extraction failed:", e)

    return tables_data


# -------------------------
# PDF TABLE EXTRACTION
# -------------------------
import camelot

def extract_tables_from_pdf(pdf_path):
    """
    Extract tables from PDF using Camelot
    """
    tables_data = []

    try:
        tables = camelot.read_pdf(pdf_path, pages="all")

        for table in tables:
            df = table.df
            tables_data.append(df.to_dict(orient="records"))

    except Exception as e:
        print("⚠️ PDF table extraction failed:", e)

    return tables_data