import os
import yaml


class Loader:
    def __init__(self, *args, path="src", **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.load()

    def load(self):
        with open(os.path.join(self.path, "categories.yaml"), "r") as f:
            self.categories = yaml.full_load(f)

        with open(os.path.join(self.path, "answer_formats.yaml"), "r") as f:
            self.formats = yaml.full_load(f)

        with open(os.path.join(self.path, "target_groups.yaml"), "r") as f:
            self.target_groups = yaml.full_load(f)

        self.authors = self.load_flat("authors")
        self.assessments = self.load_flat("assessments")
        self.papers = self.load_flat("papers")
        self.classifications = self.load_classifications()
        self.contributors = self.load_single("", "contributors")

        self.used_papers = []
        self.used_authors = []

        for classification in self.load_flat("classifications", full=True):
            if classification is None:
                continue

            authors = classification.get("_meta", {}).get("authors", [])
            for author in authors:
                if author not in self.used_authors:
                    self.used_authors.append(author)
            papers = classification.get("_meta", {}).get("papers", [])
            for paper in papers:
                if paper not in self.used_papers:
                    self.used_papers.append(paper)

        for assessment in self.load_flat("assessments", full=True):
            if assessment is None:
                continue
            authors = assessment.get("authors", [])

            for author in authors:
                if author not in self.used_authors:
                    self.used_authors.append(author)

            papers = assessment.get("papers", [])

            for paper in papers:
                if paper["id"] not in self.used_papers:
                    self.used_papers.append(paper["id"])

        for paper in self.load_flat("papers", full=True):
            authors = paper.get("author", [])

            for author in authors:
                if author not in self.used_authors:
                    self.used_authors.append(author)

    def load_single(self, path, file):
        full_path = os.path.join(self.path, path, f"{file}.yaml")
        with open(full_path) as f:
            return yaml.full_load(f)

    def load_flat(self, path, full=False):
        entries = []
        for (dirpath, dirnames, filenames) in os.walk(os.path.join(self.path, path)):
            entries = [os.path.splitext(filename)[0] for filename in filenames]

        if full:
            entries_full = []
            for entry_id in entries:
                full_path = os.path.join(self.path, path, f"{entry_id}.yaml")
                with open(full_path) as f:
                    entry = yaml.full_load(f)

                    if entry is not None:
                        entry["file"] = entry_id
                        entries_full.append(entry)
            return entries_full

        return entries

    def load_classifications(self, full=False):
        classifications = []
        for f in os.listdir(os.path.join(self.path, "classifications")):
            name = os.path.splitext(f)[0]
            classifications.append(name)

        if full:
            classifications_full = []
            for classification in classifications:
                path = os.path.join(
                    self.path, "classifications", classification + ".yaml"
                )
                if os.path.exists(path):
                    with open(path) as f:
                        f = yaml.full_load(f)
                        f["file"] = classification
                        classifications_full.append(f)
            return classifications_full

        return classifications
