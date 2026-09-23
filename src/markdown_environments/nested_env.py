import re
import xml.etree.ElementTree as etree

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from . import utils


class NestedEnvProcessor(BlockProcessor):

    def __init__(self, *args, types: dict, html_class: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.types = types
        self.html_class = html_class
        self.start_patterns = {}
        self.end_patterns = {}
        self.inner_start_patterns = {}
        self.inner_end_patterns = {}

        self.start_pattern = None
        self.end_pattern = None
        self.inner_start_pattern = None
        self.inner_end_pattern = None
        self.type_opts = None

        self.init_type_opts()

    def init_type_opts(self) -> None:
        for typ, opts in self.types.items():
            # set default options for each type nested within `types`
            opts.setdefault("html_class", "")
            opts.setdefault("inner_html_class", "")
            # add type to regex pattern choices
            self.start_patterns[typ] = re.compile(rf"^\\begin{{{typ}}}$", flags=re.MULTILINE)
            self.end_patterns[typ] = re.compile(rf"^\\end{{{typ}}}", flags=re.MULTILINE)
            self.inner_start_patterns[typ] = re.compile(
                rf"^\\begin{{{opts['inner']}}}$", flags=re.MULTILINE
            )
            self.inner_end_patterns[typ] = re.compile(
                rf"^\\end{{{opts['inner']}}}", flags=re.MULTILINE
            )

    def test(self, parent, block):
        matched_type = ""
        for typ, pattern in self.start_patterns.items():
            if pattern.match(block):
                matched_type = typ
                break
        if matched_type == "":
            return False

        self.start_pattern = self.start_patterns[matched_type]
        self.end_pattern = self.end_patterns[matched_type]
        self.inner_start_pattern = self.inner_start_patterns[matched_type]
        self.inner_end_pattern = self.inner_end_patterns[matched_type]
        self.type_opts = self.types[matched_type]
        return True

    def run(self, parent, blocks):
        # guard against index out of bounds on matching `self.inner_start_pattern` for recursive
        # `run()` parsing
        if len(blocks) < 2:
            return False
        org_blocks = list(blocks)

        # remove outer starting delim
        blocks[0] = self.start_pattern.sub("", blocks[0])

        # find and remove inner starting delim
        delim_found = False
        inner_start_i = None
        for i, block in enumerate(blocks):
            if self.inner_start_pattern.match(block):
                delim_found = True
                # remove ending delim and note which block inner started on
                # (as inner content itself is an unknown number of blocks)
                inner_start_i = i
                blocks[i] = self.inner_start_pattern.sub("", block)
                break
        # if no starting delim for inner, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove inner ending delim, and extract element
        # start search at inner starting delim
        delim_found = False
        for i, block in enumerate(blocks[inner_start_i:], start=inner_start_i):
            if self.inner_end_pattern.search(block):
                delim_found = True
                # remove ending delim
                blocks[i] = self.inner_end_pattern.sub("", block)
                # build HTML for inner
                inner_elem = etree.Element(self.type_opts["inner_html_tag"])
                if self.type_opts["inner_html_class"] != "":
                    inner_elem.set("class", self.type_opts["inner_html_class"])
                blocks[i] = blocks[i].rstrip() # remove whitespace from newline after `\end{}`
                self.parser.parseBlocks(inner_elem, blocks[inner_start_i:i + 1])
                # remove used blocks
                for _ in range(inner_start_i, i + 1):
                    blocks.pop(inner_start_i)
                break
        # if no ending delim for inner, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove outer ending delim, and extract element
        delim_found = False
        for i, block in enumerate(blocks):
            if self.end_pattern.search(block):
                delim_found = True
                # remove ending delim
                blocks[i] = self.end_pattern.sub("", block)
                # build HTML for outer
                outer_elem = etree.SubElement(parent, self.type_opts["html_tag"])
                if (self.html_class != "") or (self.type_opts["html_class"] != ""):
                    html_class = self.html_class + " " + self.type_opts["html_class"]
                    outer_elem.set("class", html_class)
                self.parser.parseBlocks(outer_elem, blocks[:i + 1])
                if self.type_opts["inner_pos"] == "start":
                    outer_elem.insert(0, inner_elem)
                elif self.type_opts["inner_pos"] == "end":
                    outer_elem.append(inner_elem)
                # remove used blocks
                for _ in range(i + 1):
                    blocks.pop(0)
                break
        # if no ending delim for outer, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False
        return True


class NestedEnvExtension(Extension):
    r"""
    A general-purpose environment supporting a nested inner one.

    Usage:
        .. code-block:: py

            import markdown
            from markdown_environments import NestedEnvExtension

            input_text = ...
            output_text = markdown.markdown(input_text, extensions=[
                NestedEnvExtension(html_class="meow", types={
                    type1: {
                        "html_tag": "div",
                        "html_class": "bleh",
                        "inner" = "type1_inner",
                        "inner_html_tag": "span",
                        "inner_html_class": "blah",
                        "inner_pos": "start"
                    }
                })
            ])

    Markdown usage:
        .. code-block:: md

            \begin{type1}

            \begin{type1_inner}
            <inner>
            \end{type1_inner}

            <outer>
            \end{type1}

        becomes:

        .. code-block:: html

            <[type1.html_tag] class="[html_class] [type1.html_class]">
              <[type1.inner_html_tag] class="[type1.inner_html_class]">
                [inner]
              </[type1.inner_html_tag]>

              [outer]
            </[type1.html_tag]>

    Note:
        The inner block can be placed anywhere within the outer block in the markdown, as long as,
        of course, there are blank lines before and after the inner block.
    """

    def __init__(self, **kwargs):
        """
        Initialize nested env extension, with configuration options passed as the following
        keyword arguments:

            - **types** (*dict*) -- Types of nested env environments to define. Defaults to `{}`.
            - **html_class** (*str*) -- HTML `class` attribute to add to outer parts of all
              nested envs. Defaults to `""`.

        The key for each type defined in `types` is inserted directly into the regex patterns
        that search for `\\begin{<type>}` and `\\end{<type>}`, so anything you specify will be
        interpreted as regex. (However, if the key is an empty string, its regex will never be
        matched against, so it is effectively useless.)

        In addition, each type's value is itself a dictionary with the following possible options:

            - **html_tag** (*str*) -- HTML tag to use for outer parts of all nested envs of
              that type. Must be set.
            - **html_class** (*str*) -- HTML `class` attribute to add to outer parts of all
              nested envs of that type. Defaults to `""`.
            - **inner** (*str*) -- name of inner part, also inserted directly into regex.
              Must be set.
            - **inner_html_tag** (*str*) -- HTML tag to use for inner parts of all nested envs of
              that type. Must be set.
            - **inner_html_class** (*str*) -- HTML `class` attribute to add to inner parts of all
              nested envs of that type. Defaults to `""`.
            - **inner_pos** (*str*) -- one of "start" or "end" specifying if the inner part should
              be placed at the start or end of the outer part. Must be set.
        """

        self.config = {
            "types": [
                {},
                "Types of nested env environments to define. Defaults to `{}`."
            ],
            "html_class": [
                "",
                (
                    "HTML `class` attribute to add to outer parts of all nested envs. "
                    "Defaults to `\"\"`."
                )
            ],
        }
        utils.init_extension_with_configs(self, **kwargs)

        # validate options and set defaults for each type nested within `types`
        # (note: validation doesn't seem to error properly sometimes when done in
        # `NestedEnvProcessor.__init__()`)
        for typ, opts in self.getConfig("types").items():
            if ((opts.get("html_tag") is None)
                    or (opts.get("inner") is None)
                    or (opts.get("inner_html_tag") is None)
                    or (opts.get("inner_pos") is None)):
                raise KeyError(
                    f"nested env: {typ}.html_tag, {typ}.inner, "
                    f"{typ}.inner_html_tag, or {typ}.inner_pos key was not defined"
                )
            if opts["inner_pos"] not in ["start", "end"]:
                raise KeyError(f"nested env: {typ}.inner_pos is not one of `start` or `end`")

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            NestedEnvProcessor(md.parser, **self.getConfigs()), "nested_env", 105
        )


def makeExtension(**kwargs):
    return NestedEnvExtension(**kwargs)
