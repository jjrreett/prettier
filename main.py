from dataclasses import dataclass

from rich import print


class Doc:
    def length(self):
        text = self.render()
        return max([len(line) for line in text.splitlines()])

    def render(self, limit) -> str:
        raise NotImplementedError

    def __mul__(self, right):
        return Cons(self, right)

    def breadthfirst(self, search, apply, stop_at=None):
        if isinstance(self, search):
            apply(self)

        if stop_at and isinstance(self, stop_at):
            return

        for child in self.children():
            if not child:
                continue
            child.breadthfirst(search, apply, stop_at)

    def children(self):
        return [None]


@dataclass
class String(Doc):
    text: str

    def render(self, limit):
        return self.text


@dataclass
class Line(Doc):
    render_char: str = " "

    def render(self, limit):
        return self.render_char


@dataclass
class Cons(Doc):
    left: Doc
    right: Doc

    def render(self, limit):
        return self.left.render(limit) + self.right.render(limit)

    def children(self):
        return [self.left, self.right]


@dataclass
class Nest(Doc):
    level: int
    internals: Doc

    def render(self, limit):
        def add_indentation(doc: Line):
            if "\n" in doc.render_char:
                doc.render_char = doc.render_char.replace("\n", "\n" + " " * self.level)

        self.internals.breadthfirst(Line, add_indentation)
        return self.internals.render(limit)

    def children(self):
        return [self.internals]


@dataclass
class Group(Doc):
    internals: Doc
    flat: bool = True

    def render(self, limit):
        return self.internals.render(limit)

    def children(self):
        return [self.internals]


def new_data():
    data = Group(
        String("begin")
        * Nest(
            4,
            Line()
            * Group(
                String("stmt;") * Line() * String("stmt;") * Line() * String("stmt;")
            ),
        )
        * Line()
        * String("end")
    )

    def bin_op(op):
        return Line() * String(op + " ")

    data = Group(
        String("hello")
        * bin_op("+")
        * Group(String("world") * bin_op("*") * String("total"))
        * bin_op("+")
        * String("eclipse")
        * bin_op("+")
        * Group(
            String("qwerty")
            * bin_op("*")
            * String("asdf")
            * bin_op("*")
            * String("aslasdf")
        )
        * bin_op("+")
        * Group(
            Group(
                String("(")
                * Nest(
                    4,
                    Line()
                    * String("foo")
                    * bin_op("*")
                    * Group(
                        String("(")
                        * Nest(4, Line() * String("bar") * bin_op("+") * String("baz"))
                        * Line()
                        * String(")")
                    ),
                )
                * Line()
                * String(")")
                * bin_op("%")
                * String("qux")
            )
        )
    )
    return data


def make_line_newline(doc: Line):
    doc.render_char = "\n"


def make_next_group_not_flat(doc: Group):
    if doc.flat:
        doc.flat = False
    else:
        for c in doc.children():
            c.breadthfirst(Group, make_next_group_not_flat, Group)
            c.breadthfirst(Line, make_line_newline, Group)


def reset_lines(doc: Line):
    doc.render_char = " "


def render_doc(doc: Doc, limit: int):
    text = doc.render(limit)
    length = max([len(line) for line in text.splitlines()])

    if length <= limit:
        return text

    doc.breadthfirst(Group, make_next_group_not_flat, Group)

    return render_doc(doc, limit)


def print_limit(data, limit):
    text = render_doc(data, limit)
    length = max([len(line) for line in text.splitlines()])
    print()
    print(length)
    print(text)
    print()
    print()


print(new_data())
print_limit(new_data(), 80)
print_limit(new_data(), 60)
print_limit(new_data(), 24)
