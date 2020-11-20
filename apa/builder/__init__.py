import os
import collections
from uuid import uuid4
from ..loader import Loader
from .env import env
from ..helper import make_dir, copy_dir, copy_file
from ..analyzer import Analyzer


def get_graph_for_classification(dd, root=True):
    nodes = []
    edges = []
    for key, value in dd.items():
        if key == "_meta" or not isinstance(value, dict):
            continue
        if not value.get("id"):
            value["id"] = uuid4().hex
        nodes.append(
            {
                "id": value.get("id"),
                "size": value.get("count", 0),
                "label": key,
                "color": colors[0] if not root else "palevioletred",
            }
        )
        for key2, value2 in value.items():
            if isinstance(value2, dict):
                if not value2.get("id"):
                    value2["id"] = uuid4().hex
                edges.append({"from": value.get("id"), "to": value2.get("id")})
        sub_nodes, sub_edges = get_graph_for_classification(value, root=False)
        nodes.extend(sub_nodes)
        edges.extend(sub_edges)
    return nodes, edges


def edge_exists(my_edge, edges):
    for edge in edges:
        if edge["to"] == my_edge["to"] and edge["from"] == my_edge["from"]:
            return True
    return False


colors = ["#769a76", "#8fbc8f", "#a2c7a1", "#b4d2b3", "#c7ddc6", "#d9e9d9", "#ecf4ec"]


def get_graph_for_assessment(dd):
    nodes = {}
    edges = []

    for classification, tags in dd.get("classifications").items():
        if classification == "_meta":
            continue
        classification_id = uuid4()
        nodes[classification] = {
            "label": classification,
            "id": classification_id,
            "color": "palevioletred",
        }
        for tag in tags:
            tag_parts = tag.split(".")
            last_node_id = None
            depth = 0
            for tag_part in tag_parts:
                current_node_id = uuid4().hex
                if tag_part not in nodes:
                    nodes[tag_part] = {
                        "label": tag_part,
                        "id": current_node_id,
                        "color": colors[depth % len(colors)],
                    }
                else:
                    current_node_id = nodes[tag_part]["id"]
                if last_node_id:
                    edge = {"from": last_node_id, "to": current_node_id}
                    if not edge_exists(edge, edges):
                        edges.append(edge)
                else:
                    edge = {"from": classification_id, "to": current_node_id}
                    if not edge_exists(edge, edges):
                        edges.append(edge)
                last_node_id = current_node_id
                depth += 1
    return nodes.values(), edges


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
            authors = paper.get("author", [])
            year = paper.get("year")
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
                badge["img"] = "https://img.shields.io/badge/openpatch-approved-98ff98"
                badge["url"] = openpatch.get("url", "#")
            elif openpatch.get("status") == "rejected":
                badge["img"] = "https://img.shields.io/badge/openpatch-rejected-red"
            elif openpatch.get("status") == "requested":
                badge["img"] = "https://img.shields.io/badge/openpatch-requested-yellow"
            elif openpatch.get("status") == "todo":
                badge["img"] = "https://img.shields.io/badge/openpatch-todo-lightgrey"

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

    def gen_authors(self, authors):
        authors_str = []
        for author in authors:
            author = self.load_single("authors", author)
            author_str = ""
            if author.get("family"):
                author_str += author.get("family")
            if author.get("given"):
                author_str += ", " + author.get("given")
            authors_str.append(author_str)

        return " and ".join(authors_str)

    def build_site(self):
        make_dir(self.output, clean=True)

        script_dir = os.path.dirname(__file__)
        copy_dir(
            os.path.join(script_dir, "static"), os.path.join(self.output, "static")
        )

        assessments = self.load_flat("assessments", full=True)
        for assessment in assessments:
            authors = assessment.get("authors", [])
            assessment["citekey"] = self.gen_citekey(authors)
        answer_formats = self.load_single("", "answer_formats").items()
        target_groups = self.load_single("", "target_groups").items()
        classifications = self.load_flat("classifications", full=True)
        contributors = self.load_single("", "contributors")
        for classification in classifications:
            authors = classification.get("_meta", {}).get("authors", [])
            classification["citekey"] = self.gen_citekey(authors)

        # INDEX
        index_tmpl = env.get_template("index.html.j2")
        with open(os.path.join("build", "index.html"), "w") as f:
            f.write(
                index_tmpl.render(
                    assessments=assessments,
                    answer_formats=answer_formats,
                    target_groups=target_groups,
                    classifications=classifications,
                    contributors=contributors,
                )
            )

        # ANSWER_FORMATS
        make_dir(os.path.join(self.output, "answer_formats"))
        answer_format_tmpl = env.get_template("answer_format.html.j2")
        for answer_format, answer_format_detail in answer_formats:
            assessments_filtered = [
                a
                for a in assessments
                if answer_format in a.get("items", {}).get("formats", [])
            ]

            with open(
                os.path.join("build", "answer_formats", answer_format + ".html"), "w"
            ) as f:
                f.write(
                    answer_format_tmpl.render(
                        answer_format=answer_format_detail,
                        assessments=assessments_filtered,
                    )
                )

        # TARGET_GROUPS
        make_dir(os.path.join(self.output, "target_groups"))
        target_group_tmpl = env.get_template("target_group.html.j2")
        for target_group, target_group_detail in target_groups:
            assessments_filtered = [
                a for a in assessments if target_group in a.get("target_groups", [])
            ]

            with open(
                os.path.join("build", "target_groups", target_group + ".html"), "w"
            ) as f:
                f.write(
                    target_group_tmpl.render(
                        target_group=target_group_detail,
                        assessments=assessments_filtered,
                    )
                )

        # CLASSIFICATIONS
        make_dir(os.path.join(self.output, "classifications"))
        classification_tmpl = env.get_template("classification.html.j2")
        for classification in classifications:
            classification = Analyzer.count_classification(classification, assessments)
            authors = classification.get("_meta", {}).get("authors")
            classification["authors"] = self.gen_authors(authors)
            papers = []
            for paper in classification.get("_meta", {}).get("papers", []):
                paper_file = self.load_single("papers", paper)
                paper = {}
                paper["citekey"] = self.gen_citekey(
                    paper_file["author"], paper_file.get("year")
                )
                paper["title"] = paper_file["title"]
                paper["url"] = paper_file.get("url", "#")
                papers.append(paper)

            classification.get("_meta", {})["papers"] = papers

            nodes, edges = get_graph_for_classification(classification)
            with open(
                os.path.join(
                    "build", "classifications", classification.get("file") + ".html"
                ),
                "w",
            ) as f:
                f.write(
                    classification_tmpl.render(
                        classification=classification, nodes=nodes, edges=edges
                    )
                )

        # ASSESSMENTS
        make_dir(os.path.join(self.output, "assessments"))
        assessment_tmpl = env.get_template("assessment.html.j2")
        for assessment in assessments:
            authors = assessment.get("authors", [])
            assessment["citekey"] = self.gen_citekey(authors)
            assessment["authors"] = self.gen_authors(authors)
            assessment["my_items"] = assessment["items"]
            categories = self.load_single("", "categories")["papers"]
            for paper in assessment.get("papers", []):
                paper_file = self.load_single("papers", paper["id"])
                paper["citekey"] = self.gen_citekey(
                    paper_file["author"], paper_file.get("year")
                )
                paper["title"] = paper_file["title"]
                paper["url"] = paper_file.get("url", "#")
                if not categories[paper["category"]].get("count"):
                    categories[paper["category"]]["count"] = 1
                else:
                    categories[paper["category"]]["count"] += 1

            assessment["paper_categories"] = categories.values()
            nodes, edges = get_graph_for_assessment(assessment)
            with open(
                os.path.join("build", "assessments", assessment.get("file") + ".html"),
                "w",
            ) as f:
                f.write(
                    assessment_tmpl.render(
                        assessment=assessment, nodes=nodes, edges=edges
                    )
                )
