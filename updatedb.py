#!/usr/bin/env python3
import glob
import os
import sys
import duckdb
from typing import *
from utils.printutils import *
# Return first existing path matching any of the patterns
def find_one(patterns : List[str]) -> Optional[str]:
    for p in patterns:
        hits = glob.glob(p)
        if hits:
            return hits[0]
    return None
# Creates a duckdb database containing all of the data for nicer usage :D
def main(reset_database : bool = False) -> None:
    GBIF_DIR = os.path.join(os.path.dirname(__file__),"GBIF","backbone")
    DB  = os.path.join(os.path.dirname(__file__),"GBIF","database","backbone.db")

    gbif_dir = os.path.abspath(GBIF_DIR)
    if not os.path.isdir(gbif_dir):
        error(f"GBIF dir not found: {gbif_dir}")
        sys.exit(1)

    # Try to find the taxon file apparently the names can vary?
    taxon_tsv = find_one([
        os.path.join(gbif_dir, "Taxon.tsv"),
        os.path.join(gbif_dir, "*Taxon*.tsv"),
        os.path.join(gbif_dir, "taxon.txt"),
        os.path.join(gbif_dir, "*Taxon*.txt"),
    ])
    if not taxon_tsv or not os.path.exists(taxon_tsv):
        error("Could not find Taxon.tsv (or variant) in the GBIF backbone folder.")
        sys.exit(1)

    vern_tsv = find_one([
        os.path.join(gbif_dir, "VernacularName.tsv"),
        os.path.join(gbif_dir, "*Vernacular*.tsv"),
        os.path.join(gbif_dir, "vernacularname.txt"),
        os.path.join(gbif_dir, "*Vernacular*.txt"),
    ])
    has_vernacular = vern_tsv is not None and os.path.exists(vern_tsv)

    # Make the database
    db_path = os.path.abspath(DB)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = duckdb.connect(db_path)

    con.execute("PRAGMA temp_directory='.';")

    if reset_database:
        con.execute("DROP VIEW IF EXISTS names;")
        con.execute("DROP TABLE IF EXISTS vernacular;")
        con.execute("DROP TABLE IF EXISTS taxon;")

    # Import the taxon data
    info(f"Importing Taxon from: {taxon_tsv}")
    con.execute(f"""
        CREATE OR REPLACE TABLE taxon AS
        SELECT *,
               lower(scientificName) AS scientificName_lc
        FROM read_csv_auto('{taxon_tsv}', delim='\t', header=True, ignore_errors=True);
    """)

    # Index key columns (including lowercase)
    con.execute("CREATE INDEX IF NOT EXISTS idx_taxon_scientificName_lc ON taxon(scientificName_lc);")
    con.execute("CREATE INDEX IF NOT EXISTS idx_taxon_taxonID ON taxon(taxonID);")

    # Import the common names if they exist
    if has_vernacular:
        info(f"Importing VernacularName from: {vern_tsv}")
        con.execute(f"""
            CREATE OR REPLACE TABLE vernacular AS
            SELECT *,
                   lower(vernacularName) AS vernacularName_lc
            FROM read_csv_auto('{vern_tsv}', delim='\t', header=True, ignore_errors=True);
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_vernacularName_lc ON vernacular(vernacularName_lc);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_vernacular_taxonID ON vernacular(taxonID);")
    else:
        error("VernacularName file not found. This probably isn't good, continuing without common-name table.")

    # Create a nice way to lookup animals
    info("Creating `names` view...")
    if has_vernacular:
        con.execute("""
            CREATE OR REPLACE VIEW names AS
            SELECT
                t.taxonID::TEXT AS taxonID,
                t.acceptedNameUsageID::TEXT AS acceptedNameUsageID,
                t.scientificName AS name,
                t.scientificName_lc AS name_lc,
                'scientific' AS name_type,
                t.taxonomicStatus,
                t.taxonRank,
                t.kingdom, t.phylum, t.class, t."order", t.family, t.genus
            FROM taxon t
            UNION ALL
            SELECT
                v.taxonID::TEXT AS taxonID,
                NULL AS acceptedNameUsageID,
                v.vernacularName AS name,
                v.vernacularName_lc AS name_lc,
                'vernacular' AS name_type,
                NULL AS taxonomicStatus,
                NULL AS taxonRank,
                NULL AS kingdom, NULL AS phylum, NULL AS class, NULL AS "order", NULL AS family, NULL AS genus
            FROM vernacular v
            WHERE v.vernacularName_lc IS NOT NULL AND length(trim(v.vernacularName_lc)) > 0;
        """)
    else:
        con.execute("""
            CREATE OR REPLACE VIEW names AS
            SELECT
                t.taxonID::TEXT AS taxonID,
                t.acceptedNameUsageID::TEXT AS acceptedNameUsageID,
                t.scientificName AS name,
                t.scientificName_lc AS name_lc,
                'scientific' AS name_type,
                t.taxonomicStatus,
                t.taxonRank,
                t.kingdom, t.phylum, t.class, t."order", t.family, t.genus
            FROM taxon t;
        """)


    # Stats
    total_names = con.execute("SELECT COUNT(*) FROM names;").fetchone()[0]
    taxon_count = con.execute("SELECT COUNT(*) FROM taxon;").fetchone()[0]
    success(f"Database: {db_path}")
    success(f" - taxon rows: {taxon_count}")
    if has_vernacular:
        vern_count = con.execute("SELECT COUNT(*) FROM vernacular;").fetchone()[0]
        success(f" - vernacular rows: {vern_count}")
    success(f" - names (view) rows: {total_names}")

if __name__ == "__main__":
    main()
