from jinja2 import Environment, PackageLoader
from ..helper import split_list

env = Environment(loader=PackageLoader("apa.builder", "templates"))
base_url = os.getenv("BASE_URL", "/")


def badges_filter(badges):
    md_badges = []
    template = "[![{alt}]({img})]({url})"
    for badge in badges:
        md_badges.append(
            template.format(
                alt=badge.get("alt", ""),
                url=badge.get("url", "#"),
                img=badge.get("img"),
            )
        )

    return " ".join(md_badges)


def table_filter(array):
    markdown = "\n" + str("| ")

    for e in array[0]:
        to_add = " " + str(e) + str(" |")
        markdown += to_add
    markdown += "\n"

    markdown += "|"
    for i in range(len(array[0])):
        markdown += str("-------------- | ")
    markdown += "\n"

    for entry in array[1:]:
        markdown += str("| ")
        for e in entry:
            to_add = str(e) + str(" | ")
            markdown += to_add
        markdown += "\n"

    return markdown + "\n"


def author_table_filter(authors, per_row=6):
    rows = split_list(authors, per_row)

    return table_filter(rows)


def format_name(c):
    name = []
    if c.get("given"):
        name.append(c.get("given"))
    if c.get("family"):
        name.append(c.get("family"))
    return " ".join(name)


def get_img(c):
    img = "assets/awesome_user.svg"
    if c.get("img"):
        img = c.get("img")
    name = format_name(c)
    template = '[<img alt="{}" src="{}" width="100px">]({})'
    return template.format(name, img, c.get("url"))


def get_url(c):
    return base_url + c


def get_static(c):
    return base_url + "static/" + c


def get_name(c):
    name = format_name(c)
    template = "[{}]({})"
    return template.format(name, c.get("url"))


def contributor_table_filter(contributors, per_row=6):
    rows = split_list(contributors, per_row)

    md_rows = []
    for row in rows:
        imgs = [*map(get_img, row)]
        names = [*map(get_name, row)]

        md_rows.append(table_filter([imgs, names]))

    return "\n".join(md_rows)


env.filters["author_table"] = author_table_filter
env.filters["contributor_table"] = contributor_table_filter
env.filters["badges"] = badges_filter
env.filters["get_static"] = get_static
env.filters["get_url"] = get_url
