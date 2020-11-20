import click

from .linter import Linter
from .builder import Builder
from .analyzer import Analyzer
from .importer import add_paper


@click.group()
@click.pass_context
def apa(ctx):
    ctx.ensure_object(dict)


@apa.command()
@click.option("-w", "--watch", is_flag=True)
@click.pass_context
def lint(ctx, watch):
    linter = Linter(path="src")
    linter.run(watch=watch)


@apa.command()
@click.option("-m", "--max-level", default=1)
def analyze(max_level):
    analyzer = Analyzer(max_level=max_level)
    analyzer.analyze()


@apa.group()
def build():
    pass


@build.command()
def markdown():
    Builder(path="src").build_markdown()


@build.command()
def site():
    Builder(path="src").build_site()


@build.command()
def all():
    Builder(path="src").build()


@apa.group()
def add():
    pass


@add.command()
def paper():
    add_paper(path="src")


if __name__ == "__main__":
    apa()
