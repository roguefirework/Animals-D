import duckdb

from utils.printutils import *
from utils.textutils import normalize

DB = "./GBIF/database/backbone.db"
OUT = "./GBIF/keywords/animal_keywords.txt"

# Creates a nice little dictionary containing only animalia
def main() -> None:
    status("Connecting to database...")
    con = duckdb.connect(DB)
    status("Connected to database.")
    # Pull scientific + vernacular for Animalia only
    q = """
    WITH taxa AS (
        SELECT taxonID, scientificName
        FROM taxon
        WHERE lower(kingdom) = 'animalia'
    ),
    vern AS (
        SELECT v.taxonID, v.vernacularName
        FROM vernacular v
        JOIN taxa t ON t.taxonID = v.taxonID
        WHERE v.vernacularName IS NOT NULL AND length(trim(v.vernacularName)) > 0
    )
    SELECT taxonID::TEXT AS tid, vernacularName AS name FROM vern;
    """
    status("Executing query")
    rows = con.execute(q).fetchall()
    status("Writing keywords to file...")
    seen = set()
    for _, name in rows:
        k = normalize(name)
        if not k or k in seen:
            continue

        seen.add(k)

    with open(OUT, 'w', newline='') as f_output:
        for name in seen:
            f_output.write(f"{name}\n")
    info(f"wrote {len(seen):,} keywords to {OUT}")

if __name__ == "__main__":
    main()