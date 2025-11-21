import updatebackbone
import updatedb
import makeanimalsfile

# Tries to download a new animal dataset if needed and creates/updates the database discouragingly
def main() -> None:
    updatebackbone.main()
    updatedb.main()
    makeanimalsfile.main()

if __name__ == "__main__":
    main()