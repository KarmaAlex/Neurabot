from pytree.tree import main as phys_main
from sys import argv
from time import sleep

def main(ticks: int=30):
    print(f"Running simulation of behaviour tree for {ticks} ticks")
    sleep(1)
    phys_main(ticks)
    print("Simulation finished")


if __name__ == "__main__":
    try:
        main(int(argv[1]))
    except IndexError:
        main()
    except ValueError:
        print("Invalid number of ticks to simulate")
