from collections import defaultdict

# This is very inefficient and stupid but oh well
# It also doesnt work and I am significantly less interested in this problem now
def main() -> None:
    print("Starting")
    animals : set[str]
    with open("../GBIF/keywords/animal_keywords.txt") as f:
        animals = set(f.read().splitlines())
    animal_counts : dict[str, int] = defaultdict(int)
    print("Finished reading the awful file, starting the awful checks")
    with open("in") as f:
        filedata = f.readlines()
        i = 0
        for animal in animals:
            i += 1
            if i % (len(animals) // 100) == 0:
                print(f"{i} / {len(animals):,}")
            count = filedata.count(animal)
            if (count != 0):
                animal_counts[animal] = count

    with open("animals :D", "w") as out:
        for animal in animal_counts:
            out.write(animal + ":" + str(animal_counts[animal]) + "\n")
    print(f"wrote {len(animal_counts)}")

if __name__ == "__main__":
    main()