import updatebackbone
import updatedb

# Tries to download a new animal dataset if needed and creates/updates the database discouragingly
def main() -> None:
    updatebackbone.main()
    updatedb.main()

if __name__ == "__main__":
    main()