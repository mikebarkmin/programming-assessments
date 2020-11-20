# Contribution Guidelines

Please note that this project is released with a
[Contributor Code of Conduct](code-of-conduct.md). By participating in this
project you agree to abide by its terms.

---

Ensure your pull request adheres to the following guidelines:

If you want to submit a new paper, assessment or author. Create an issue, provide all necessary information (see below) and make sure to include links to all relevant resources.

Thank you for your suggestions!

## Add an Assessment

Create a new file, e.g. `mueller_2020.yaml` in `src/assessments`. The content of the file should look like this:

```yaml
title: Ahadi 2013 - 1
openpatch:
  status: approved
authors:
  - ahadi_alireza
  - lister_raymond
content:
  - assignment
items:
  count: 9
  formats:
    - coding
    - short_answer
target_groups:
  - university
classifications:
  commp_model:
    - language.java.syntax
    - language.java.semantic
    - elements.program_components.variables
    - elements.program_components.statements.assignment
    - elements.data_types.scalars.integer
    - high_level_paradigm.imperative
resources:
  - title: Assessment
    link: 'https://groups.google.com/forum/#!forum/cs1-concept-inventory-and-assessment-replications'
papers:
  - id: ahadi_2013
    category: original
```

## Add a Paper

### Automatic
Run `pipenv run add_paper` and paste bibtex data for the paper.

### Manually
Create a new file, e.g. `mueller_2020.yaml` in `src/papers`. The content of the file should look like this:

```yaml
ISBN: '9781450322430'
authors:
- ahadi_alireza
- lister_raymond
collection_number: null
collection_title: ICER '13
container_title: Proceedings of the ninth annual international ACM conference on International
  computing education research
event_place: San Diego, San California, USA
id: 10.1145/2493394.2493416
issue: null
issued: 2013-08-12
number: null
number_of_pages: 6
original_date: 2013-08-12
page: 123-128
publisher: Association for Computing Machinery
publisher_place: New York, NY, USA
title: 'Geek genes, prior knowledge, stumbling points and learning edge momentum:
  parts of the one elephant?'
type: PAPER_CONFERENCE
volume: null
```

A file for each author must be available in `src/authors`.

## Add an Author

Create a new file, e.g. `mueller_jill.yaml` in `src/authors`. The content of the file should look like this:

```yaml
family: Jill
given: Mueller
```

The authors can now be reference by using the file name without the extensions. So in our example: `mueller_jill`

## Add a Classification

Create a new file, e.g. `blooms_taxonomy.yaml` in `src/classifications`. The content of the file should look like this.

```yaml
_meta:
    title: Bloom's Taxonomy
    description: Based on this Wikipedia article https://en.wikipedia.org/wiki/Bloom%27s_taxonomy
    authors:
        - bloom_benjamin
knowledge:
    _meta:
        description: >
            Knowledge involves recognizing or remembering facts, terms, basic concepts, or answers without necessarily understanding what they mean.
comprehension:
    _meta:
        description: >
            Comprehension involves demonstrating an understanding of facts and ideas by organizing, summarizing, translating, generalizing, giving descriptions, and stating the main ideas. 
application:
    _meta:
        description: >
            Application involves using acquired knowledge—solving problems in new situations by applying acquired knowledge, facts, techniques and rules. Learners should be able to use prior knowledge to solve problems, identify connections and relationships and how they apply in new situations. 
analysis:
    _meta:
        description: >
            Analysis involves examining and breaking information into component parts, determining how the parts relate to one another, identifying motives or causes, making inferences, and finding evidence to support generalizations.
synthesis:
    _meta:
        description: >
            Synthesis involves building a structure or pattern from diverse elements; it also refers to the act of putting parts together to form a whole.
evaluation:
    _meta:
        description: >
            Evaluation involves presenting and defending opinions by making judgments about information, the validity of ideas, or quality of work based on a set of criteria.
```

## Linting

You can check if everything went right and the links between the documents are correct by running `pipenv run lint`. If you want to continuously check for errors or warning you can run `pipenv run lint -w`.

## Updating your PR

A lot of times, making a PR adhere to the standards above can be difficult.
If the maintainers notice anything that we'd like changed, we'll ask you to
edit your PR before we merge it. There's no need to open a new PR, just edit
the existing one. If you're not sure how to do that,
[here is a guide](https://github.com/RichardLitt/knowledge/blob/master/github/amending-a-commit-guide.md)
on the different ways you can update your PR so that we can merge it.
