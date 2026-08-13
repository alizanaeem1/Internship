from pathlib import Path
from ingest import index_file

index_file(Path("data/QHSE/03_Quality/04_QA_vs_QC.md"), force=True)