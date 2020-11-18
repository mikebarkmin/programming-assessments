import os
import collections
from uuid import uuid4
from ..loader import Loader
from .env import env
from ..helper import make_dir, copy_dir, copy_file
from ..analyzer import Analyzer


def get_graph(dd):
    nodes = []
    edges = []
    for key, value in dd.items():
        if key == "_meta" or not isinstance(value, dict):
            continue
        if not value.get("id"):
            value["id"] = uuid4().hex
        nodes.append({
            "id": value.get("id"),
            "size": value.get("count", 0),
            "label": key
        })
        for key2, value2 in value.items():
            if isinstance(value2, dict):
                if not value2.get("id"):
                    value2["id"] = uuid4().hex
                edges.append({
                    "from": value.get("id"),
                    "to": value2.get("id")
                })
        sub_nodes, sub_edges = get_graph(value)
        nodes.extend(sub_nodes)
        edges.extend(sub_edges)
    return nodes, edges


class Builder(Loader):
    def __init__(self, path="src", output="build"):
        super().__init__(path=path)
        self.output = output

    def build(self):
        self.build_markdown()
        self.build_site()

    def build_markdown(self):
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
        make_dir(self.output, clean=True)

        script_dir = os.path.dirname(__file__)
        copy_dir(os.path.join(script_dir, "static"),
                 os.path.join(self.output, "static"))

        assessments = self.load_flat("assessments", full=True)
        for assessment in assessments:
            authors = assessment.get("authors", [])
            assessment["citekey"] = self.gen_citekey(authors)
        answer_formats = self.load_single("", "answer_formats").items()
        target_groups = self.load_single("", "target_groups").items()
        classifications = self.load_flat("classifications", full=True)
        for classification in classifications:
            authors = classification.get("_meta", {}).get("authors", [])
            classification["citekey"] = self.gen_citekey(authors)

        # INDEX
        index_tmpl = env.get_template("index.html.j2")
        with open(os.path.join("build", "index.html"), "w") as f:
            f.write(index_tmpl.render(assessments=assessments,
                                      answer_formats=answer_formats, target_groups=target_groups, classifications=classifications))

        # ANSWER_FORMATS
        make_dir(os.path.join(self.output, "answer_formats"))

        # TARGET_GROUPS
        make_dir(os.path.join(self.output, "target_groups"))

        # CLASSIFICATIONS
        make_dir(os.path.join(self.output, "classifications"))
        classification_tmpl = env.get_template("classification.html.j2")
        for classification in classifications:
            classification = Analyzer.count_classification(
                classification, assessments)
            nodes, edges = get_graph(classification)
            with open(os.path.join("build", "classifications", classification.get("file") + ".html"), "w") as f:
                f.write(classification_tmpl.render(
                    classification=classification, nodes=nodes, edges=edges))

        # ASSESSMENTS
        make_dir(os.path.join(self.output, "assessments"))
