import unidecode
import os
import yaml
import bibtexparser
from .helper import editor_input


def import_authors(authors, path="src"):
    imported_authors = []
    authors = authors.split(" and ")
    for author in authors:
        author_name = author.split(",")
        author = {
            "family": author_name[0].strip(),
            "given": author_name[1].strip() if len(author_name) > 1 else None,
        }
        family = (
            unidecode.unidecode(
                author.get("family").lower().replace(" ", "-").replace(".", "")
            )
            if author.get("family") is not None
            else None
        )
        given = (
            unidecode.unidecode(
                author.get("given").lower().replace(" ", "-").replace(".", "")
            )
            if author.get("given") is not None
            else None
        )
        author_filename = "_".join(filter(None, (family, given)))
        imported_authors.append(
            {
                "id": author_filename,
                "family": author.get("family"),
                "given": author.get("given"),
            }
        )

        file_path = os.path.join(path, "authors", author_filename + ".yaml")
        if not os.path.exists(file_path):
            with open(file_path, "w+") as f:
                f.write(
                    yaml.dump(
                        {"family": author.get("family"), "given": author.get("given")}
                    )
                )
            print("New Author imported: " + file_path)
    return imported_authors


def add_paper(path="src"):
    bibtex_raw = editor_input("Paste bibtex here")
    bibtex_entries = bibtexparser.loads(bibtex_raw).entries
    bibtex_entry = bibtex_entries[0]

    # imnport author
    authors = bibtex_entry["author"]
    authors = import_authors(authors, path)
    bibtex_entry["author"] = [author.get("id") for author in authors]
    main_author = authors[0]

    # write to paper file
    file_name = main_author["family"].lower() + "_" + bibtex_entry["year"] + ".yaml"
    file_path = os.path.join(path, "papers", file_name)

    counter = 1
    while os.path.exists(file_path):
        file_name = (
            main_author["family"].lower()
            + "_"
            + bibtex_entry["year"]
            + "_"
            + str(counter)
            + ".yaml"
        )
        file_path = os.path.join(path, "papers", file_name)
        counter += 1

    stream = open(file_path, "w")
    yaml.dump(bibtex_entry, stream)
    print("Successfully import: " + file_path)
