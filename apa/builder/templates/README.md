![Lint](https://github.com/mikebarkmin/awesome-programming-assessments/workflows/Lint/badge.svg)

# Awesome Programming Assessments [![Awesome](https://awesome.re/badge-flat.svg)](https://awesome.re)

 > A curated list of assessments, classifications and papers regarding programming asssessments

## Contents

- [Assessments](#assessments)
- [Classifications](#classifications)
- [Papers](#papers)


## Assessments

{% for assessment in assessments -%}
### [{{ assessment.citekey }}: {{ assessment.title | e }}](content/assessment/{{ assessment.file }}.md) ![{{ assessment.openpatch.status }}](assessment.openpatch.url)
{{ assessment.badges|badges }}

{% for paper in assessment.papers -%}
- [{{ paper.citekey }}](#{{ paper.id }}): {{ paper.category}}
{% endfor %}
{% endfor %}

## Classifications

{% for classification in classifications -%}
- [{{ classification.title | e }}](content/classifications/{{ classification.id }}.md)
{% endfor %}

## Papers

{% for paper in papers -%}
- <a id="{{paper.file}}">{{ paper.citekey }}</a>: [{{ paper.title | e }}](https://doi.org/{{ paper.id }})
{% endfor %}

## Contributors

{{ contributors|contributor_table }}

## Contribute

Contributions welcome! Read the [contribution guidelines](contributing.md) first.


## License

[![CC BY-SA 4.0](https://mirrors.creativecommons.org/presskit/buttons/88x31/svg/by-sa.svg)](https://creativecommons.org/licenses/by-sa/4.0)

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially.

Under the following terms:

- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.
- **No additional restrictions** — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

The licensor cannot revoke these freedoms as long as you follow the license terms.

