import typer as typer

from faim_wako_searchfirst.single import run


def main(folder_path):
    run(folder_path, configfile="config.yml")


if __name__ == "__main__":
    typer.run(main)
