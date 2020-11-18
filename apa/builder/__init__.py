import os
from ..loader import Loader
from .env import env
from ..helper import make_dir


class Builder(Loader):
    def __init__(self, path="src", output="build"):
        super().__init__(path=path)
        self.output = output

    def build(self):
        self.build_markdown()
        self.build_site()

    def build_markdown(self):
        # make folder structure
        make_dir(self.output)
        make_dir(os.path.join(self.output, "classifications"))
        make_dir(os.path.join(self.output, "assessments"))

        script_dir = os.path.dirname(__file__)

        categories = self.load_single("", "categories")

        papers_extended = self.load_flat("papers", full=True)
        for paper in papers_extended:
            authors = paper.get("authors", [])
            year = paper.get("issued").year
            paper["citekey"] = self.gen_citekey(authors, year)

        papers_extended.sort(key=lambda p: p["citekey"])

        assessments_extended = self.load_flat("assessments", full=True)
        assessments_extended.sort(key=lambda p: p["title"])
        for assessment in assessments_extended:
            authors = assessment.get("authors", [])
            assessment["citekey"] = self.gen_citekey(authors)
            papers = assessment.get("papers", [])
            openpatch = assessment.get("openpatch", {})

            badges = []

            badge = {"alt": openpatch.get("status")}
            if openpatch.get("status") == "approved":
                badge[
                    "img"
                ] = "https://img.shields.io/badge/openpatch-approved-98ff98"
                badge["url"] = openpatch.get("url", "#")
            elif openpatch.get("status") == "rejected":
                badge["img"] = "https://img.shields.io/badge/openpatch-rejected-red"
            elif openpatch.get("status") == "requested":
                badge[
                    "img"
                ] = "https://img.shields.io/badge/openpatch-requested-yellow"
            elif openpatch.get("status") == "todo":
                badge[
                    "img"
                ] = "https://img.shields.io/badge/openpatch-todo-lightgrey"

            badges.append(badge)

            assessment["badges"] = badges

            for paper in papers:
                ps = [p for p in papers_extended if p["file"] == paper["id"]]
                if len(ps) > 0:
                    category = paper["category"]
                    paper["citekey"] = ps[0]["citekey"]
                    paper["category"] = categories["papers"][category]["short"]

        # create README
        with open("README.md", "w") as readme:
            template = env.get_template("README.md.j2")

            readme.write(
                template.render(
                    classifications=self.load_classifications(full=True),
                    assessments=assessments_extended,
                    papers=papers_extended,
                    contributors=self.contributors,
                )
            )

    def gen_citekey(self, authors, year=None):
        citekey = ""
        if len(authors) == 1:
            author = self.load_single("authors", authors[0])
            citekey += author.get("family")
        elif len(authors) > 1:
            author = self.load_single("authors", authors[0])
            citekey += author.get("family") + " et.al"
        else:
            citekey += "N.A."

        if year:
            citekey += f" ({year})"

        return citekey

    def build_site(self):
        pass
