from .loader import Loader
from .helper import get_in_dict


class Analyzer(Loader):
    def __init__(self, *args, max_level=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_level = max_level

    def analyze(self):
        classifications = self.load_classifications(full=True)
        assessments = self.load_flat("assessments", full=True)

        items_count = 0
        formats = {}
        target_groups = {}
        papers_categories_count = {}
        categories = {}
        assessments_count = 0

        for assessment in assessments:
            if "_TEMPLATE" in assessment.get("file"):
                continue

            assessments_count += 1

            items = assessment.get("items", {})
            if items.get("count") != "?":
                items_count += items.get("count")

            for format in items.get("formats", []):
                if not format in formats:
                    formats[format] = 0

                formats[format] += 1

            for target_group in assessment.get("target_groups", []):
                if not target_group in target_groups:
                    target_groups[target_group] = 0

                target_groups[target_group] += 1

            for paper in assessment.get("papers", []):
                category = paper.get("category", "N.A")
                if not category in papers_categories_count:
                    papers_categories_count[category] = 0

                papers_categories_count[category] += 1

        print("SUMMARY".center(80, "="))
        self.report_single("Items", items_count, assessments_count)
        self.report_dict("Formats", formats, assessments_count)
        self.report_dict("Target", target_groups, assessments_count)
        self.report_dict("Papers", papers_categories_count, assessments_count)

        for classification in classifications:
            self.analyze_classification(classification, assessments)

    def analyze_classification(self, classification, assessments):
        print()
        print(f"CLASSIFICATION: {classification.get('file')}".center(80, "="))

        for assessment in assessments:
            if assessment.get("file") == "_TEMPLATE":
                continue
            classifications = assessment.get("classifications")
            classified = []
            if classification.get("file") in classifications:
                entries = classifications.get(classification.get("file"))
                for c in entries:
                    # trim path
                    parts = c.split(".")[: self.max_level]
                    for i in range(len(parts)):
                        path = ".".join(c.split(".")[: i + 1])
                        # count every classification only once
                        if path in classified:
                            continue
                        d = get_in_dict(path, classification)
                        if not "count" in d:
                            d["count"] = 0
                        d["count"] += 1
                        classified.append(path)

        print(classification)

        self.report_classification(classification, level=0)

    def report_classification(self, classification, level=0):
        for k, v in classification.items():
            if isinstance(v, dict) and not level == self.max_level and "_meta" not in k:
                print(f"{ '    ' * (level) }{k}: {v.get('count', 0)}")
                self.report_classification(v, level=level + 1)
            elif k != "_meta" and k != "count":
                print(f"{ '    ' * (level) }{k}: 0")

    def report_dict(self, name, d, total):
        subtotal = sum(d.values())
        self.report_single(name, subtotal, total)
        for key, value in d.items():
            self.report_single(" > " + key, value, subtotal)

    def report_single(self, name, n, total):
        max = 18
        name = name[:max] + (name[max:] and "..")
        name = name.ljust(max + 2, ".")
        a = round(n / float(total), 2)
        print(f"{name}:\t{n}\t{a}")
