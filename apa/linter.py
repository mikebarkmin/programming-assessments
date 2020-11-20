import yaml
import time
import os
import sys
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from .loader import Loader


class Level:
    WARNING = "warning"
    ERROR = "error"


openpatch_status = ["todo", "requested", "rejected", "approved"]


class Rule:
    UNKNOWN = "unknown"
    AUTHOR_NOT_FOUND = "author-not-found"
    PAPER_NOT_FOUND = "paper-not-found"
    FORMAT_NOT_FOUND = "format-not-found"
    TARGET_GROUP_NOT_FOUND = "target-group-not-found"
    PAPER_CATEGORY_NOT_FOUND = "paper-category-not-found"
    CLASSIFICATION_NOT_FOUND = "classification-not-found"
    CLASSIFICATION_NOT_FOUND = "classification-not-found"
    NO_PAPER_CATEGORY = "no-paper-category"
    NO_PAPER = "no-paper"
    NO_AUTHOR = "no-author"
    NO_CLASSIFICATION = "no-classification"
    NO_ITEMS = "no-items"
    NO_ITEMS_COUNT = "no-items-count"
    NO_ITEMS_FORMATS = "no-items-formats"
    NO_OPENPATCH = "no-openpatch"
    NO_OPENPATCH_URL = "no-openpatch-url"
    INVALID_OPENPATCH_STATUS = "invalid-openpatch-status"
    ITEMS_FORMAT_NOT_FOUND = "items-format-not-found"
    INVALID_ITEMS_COUNT = "invalid-items-count"
    INVALID_CLASSIFICATION = "invalid-classification"
    PAPER_NEEDS_TO_BE_A_MAPPING = "paper-needs-to-be-a-mapping"
    UNUSED_PAPER = "unused-paper"
    UNUSED_AUTHOR = "unused-author"
    CLASSIFICATION_OVERLAP = "classification-overlap"


class Problem:
    def __init__(self, key="", level=Level.WARNING, rule=Rule.UNKNOWN, desc=""):
        self.key = key
        self.rule = rule
        self.level = level
        self.desc = desc


class Linter(Loader, PatternMatchingEventHandler):
    def __init__(self, path="src"):
        super().__init__(path=path, ignore_patterns=["*/.*"], ignore_directories=True)

    def on_modified(self, event):
        self.lint()

    def on_deleted(self, event):
        self.lint()

    def on_created(self, event):
        self.lint()

    def on_moved(self, event):
        self.lint()

    def lint_classification(self, classification, path):
        problems = []
        if isinstance(classification, list):
            classification = list(sorted(classification, key=len, reverse=True))
            for c in classification:
                for c2 in classification:
                    if c in c2 and not c == c2:
                        problems.append(
                            Problem(
                                key="classification",
                                level=Level.WARNING,
                                desc=f"{c} overlaps with {c2}",
                                rule=Rule.CLASSIFICATION_OVERLAP,
                            )
                        )
                with open(
                    os.path.join(self.path, "classifications", path + ".yaml")
                ) as f:
                    f = yaml.full_load(f)
                    if "_meta" not in c and not Linter.is_in_dict(c, f):
                        problems.append(
                            Problem(
                                key="classification",
                                level=Level.ERROR,
                                desc=f"{c} not found",
                                rule=Rule.CLASSIFICATION_NOT_FOUND,
                            )
                        )
        else:
            problems.append(
                Problem(
                    key="classification",
                    level=Level.ERROR,
                    desc=f"{classification} needs to be a list",
                    rule=Rule.INVALID_CLASSIFICATION,
                )
            )
        return problems

    def lint_assessment(self, file_path, assessment):
        problems = []
        # check assessment
        with open(file_path, "r") as f:
            f = yaml.full_load(f)
            # check only if there is content in the file
            if f is not None:
                # check openpatch status
                openpatch = f.get("openpatch", {})
                if (
                    openpatch is None
                    or not isinstance(openpatch, dict)
                    or len(openpatch.keys()) == 0
                ):
                    problems.append(
                        Problem(
                            key="openpatch",
                            rule=Rule.NO_OPENPATCH,
                            desc="No OpenPatch found",
                            level=Level.ERROR,
                        )
                    )
                else:
                    status = openpatch.get("status")
                    if not status or status not in openpatch_status:
                        problems.append(
                            Problem(
                                key="openpatch.status",
                                rule=Rule.INVALID_OPENPATCH_STATUS,
                                desc=f"{status} is not allowed. Use one of {openpatch_status}",
                                level=Level.ERROR,
                            )
                        )
                    elif status == "approved" and not openpatch.get("url"):
                        problems.append(
                            Problem(
                                key="openpatch.url",
                                rule=Rule.NO_OPENPATCH_URL,
                                desc="No OpenPatch url",
                                level=Level.WARNING,
                            )
                        )

                # check classifications
                classifications = f.get("classifications", {})
                if classifications is None or len(classifications.keys()) == 0:
                    problems.append(
                        Problem(
                            key="classifications",
                            rule=Rule.NO_CLASSIFICATION,
                            desc="No classification found",
                            level=Level.WARNING,
                        )
                    )
                else:
                    for (classification_id, classification,) in classifications.items():
                        if "_meta" in classification_id:
                            continue
                        if classification_id not in self.classifications:
                            problems.append(
                                Problem(
                                    key="classifications",
                                    rule=Rule.CLASSIFICATION_NOT_FOUND,
                                    desc=f"{classification_id} not found",
                                )
                            )
                        else:
                            problems.extend(
                                self.lint_classification(
                                    classification, classification_id
                                )
                            )

                # check authors
                authors = f.get("authors", [])
                if len(authors) == 0:
                    problems.append(
                        Problem(
                            key="authors",
                            rule=Rule.NO_AUTHOR,
                            desc="No author found",
                            level=Level.WARNING,
                        )
                    )
                else:
                    for author in authors:
                        if author not in self.authors:
                            problems.append(
                                Problem(
                                    key="authors",
                                    rule=Rule.AUTHOR_NOT_FOUND,
                                    desc=f"{author} not found",
                                    level=Level.ERROR,
                                )
                            )

                # check items
                items = f.get("items", None)
                if items is None:
                    problems.append(
                        Problem(
                            key="items",
                            rule=Rule.NO_ITEMS,
                            desc=f"No items found",
                            level=Level.WARNING,
                        )
                    )
                else:
                    count = items.get("count")
                    if not count:
                        problems.append(
                            Problem(
                                key="items",
                                rule=Rule.NO_ITEMS_COUNT,
                                level=Level.WARNING,
                            )
                        )
                    elif not isinstance(count, int) and count != "?":
                        problems.append(
                            Problem(
                                key="items.count",
                                rule=Rule.INVALID_ITEMS_COUNT,
                                desc=f"invalid type {type(count)} should be int or '?'",
                                level=Level.ERROR,
                            )
                        )

                # check papers
                papers = f.get("papers", [])
                if len(papers) == 0:
                    problems.append(
                        Problem(
                            key="papers",
                            rule=Rule.NO_PAPER,
                            desc="No paper found",
                            level=Level.WARNING,
                        )
                    )
                else:
                    for paper in papers:
                        if isinstance(paper, str):
                            problems.append(
                                Problem(
                                    key="papers",
                                    rule=Rule.PAPER_NEEDS_TO_BE_A_MAPPING,
                                    level=Level.ERROR,
                                    desc=f"{paper} needs to be a mapping (id, category)",
                                )
                            )
                        elif paper.get("id") not in self.papers:
                            problems.append(
                                Problem(
                                    key="papers",
                                    rule=Rule.PAPER_NOT_FOUND,
                                    desc=f"{paper['id']} not found",
                                    level=Level.ERROR,
                                )
                            )
                        elif paper.get("category") is None:
                            problems.append(
                                Problem(
                                    key="papers",
                                    rule=Rule.NO_PAPER_CATEGORY,
                                    desc=f"{paper['id']} has no category",
                                    level=Level.WARNING,
                                )
                            )
                        elif paper.get("category") not in self.categories["papers"]:
                            problems.append(
                                Problem(
                                    key="papers",
                                    rule=Rule.PAPER_CATEGORY_NOT_FOUND,
                                    level=Level.ERROR,
                                    desc=f"{paper['category']} for {paper['id']} not found ({[key for key in self.categories['papers'].keys() if not key.startswith('_')]})",
                                )
                            )
        return problems

    def lint_paper(self, file_path, paper):
        problems = []
        with open(file_path, "r") as f:
            # check paper
            f = yaml.full_load(f)
            # check authors
            authors = f.get("author", [])
            for author in authors:
                if author not in self.authors:
                    problems.append(
                        Problem(
                            key="author",
                            rule=Rule.AUTHOR_NOT_FOUND,
                            desc=f"{author} not found",
                            level=Level.ERROR,
                        )
                    )

        if not paper in self.used_papers and paper != "_TEMPLATE":
            problems.append(
                Problem(
                    key="",
                    rule=Rule.UNUSED_PAPER,
                    desc="Unused paper",
                    level=Level.WARNING,
                )
            )

        return problems

    def lint_author(self, file_path, author):
        problems = []

        if not author in self.used_authors and author != "_TEMPLATE":
            problems.append(
                Problem(
                    key="",
                    rule=Rule.UNUSED_AUTHOR,
                    desc="Unused author",
                    level=Level.WARNING,
                )
            )

        return problems

    def lint(self):
        # be sure that all new files are included
        self.load()
        os.system("cls" if os.name == "nt" else "clear")
        collected_problems = []

        for author in self.authors:
            author_path = os.path.join(self.path, "authors", f"{author}.yaml")
            problems = self.lint_author(author_path, author)
            collected_problems.append((problems, author_path))

        for paper in self.papers:
            paper_path = os.path.join(self.path, "papers", f"{paper}.yaml")
            problems = self.lint_paper(paper_path, paper)
            collected_problems.append((problems, paper_path))

        for assessment in self.assessments:
            assessment_path = os.path.join(
                self.path, "assessments", f"{assessment}.yaml"
            )
            problems = self.lint_assessment(assessment_path, assessment)
            collected_problems.append((problems, assessment_path))

        found_warnings = 0
        found_errors = 0

        for problems, file_path in collected_problems:
            if len(problems) > 0:
                warnings, errors = Linter.show_problems(problems, file_path)
                found_warnings += warnings
                found_errors += errors

        found_problems = found_errors + found_warnings
        if found_problems > 0:
            print(
                f"\033[31m{found_problems} problems ({found_warnings} warnings, {found_errors} errors)\033[0m"
            )
        else:
            print(f"\033[92mNo problems found\033[0m")
        print()

        return found_problems, found_warnings, found_errors

    def run(self, watch):
        problems, warnings, errors = self.lint()
        if watch:
            observer = Observer()
            observer.schedule(self, self.path, recursive=True)
            observer.start()

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()
        elif errors > 0:
            sys.exit(1)

    @staticmethod
    def is_in_dict(path, d):
        keys = path.split(".")
        value = d
        try:
            for key in keys:
                value = value[key]
        except KeyError:
            return False
        return True

    @staticmethod
    def format(problem, filename):
        line = "  \033[2m%s\033[0m" % (problem.key)
        line += max(30 - len(line), 0) * " "
        if problem.level == Level.WARNING:
            line += "\033[33m%s\033[0m" % problem.level
        else:
            line += "\033[31m%s\033[0m" % problem.level
        line += max(48 - len(line), 0) * " "
        line += problem.desc
        if problem.rule:
            line += "  \033[2m(%s)\033[0m" % problem.rule
        return line

    @staticmethod
    def show_problems(problems, file):
        first = True
        warnings = 0
        errors = 0
        for problem in problems:
            if problem.level == Level.WARNING:
                warnings += 1
            elif problem.level == Level.ERROR:
                errors += 1
            if first:
                print("\033[4m%s\033[0m" % file)
                first = False
            print(Linter.format(problem, file))
        print()
        return warnings, errors
