import re
import xml.etree.ElementTree as etree

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from . import util


class CitedBlockquoteProcessor(BlockProcessor):

    START_PATTERN = re.compile(r"^\\begin{cited_blockquote}", flags=re.MULTILINE)
    END_PATTERN = re.compile(r"^\\end{cited_blockquote}", flags=re.MULTILINE)
    CITATION_START_PATTERN = re.compile(r"^\\begin{citation}", flags=re.MULTILINE)
    CITATION_END_PATTERN = re.compile(r"^\\end{citation}", flags=re.MULTILINE)

    def __init__(self, *args, html_class: str, citation_html_class: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.html_class = html_class
        self.citation_html_class = citation_html_class

    def test(self, parent, block):
        return self.START_PATTERN.match(block)

    def run(self, parent, blocks):
        org_blocks = list(blocks)

        # remove blockquote starting delim
        blocks[0] = self.START_PATTERN.sub("", blocks[0])

        # find and remove citation starting delim
        delim_found = False
        citation_start_i = None
        for i, block in enumerate(blocks):
            if self.CITATION_START_PATTERN.match(block):
                delim_found = True
                # remove ending delim and note which block citation started on
                # (as citation content itself is an unknown number of blocks)
                citation_start_i = i
                blocks[i] = self.CITATION_START_PATTERN.sub("", block)
                break
        # if no starting delim for citation, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove citation ending delim, and extract element
        # start search at citation starting delim; citation is at end so this is a good optimization
        delim_found = False
        for i, block in enumerate(blocks[citation_start_i:], start=citation_start_i):
            if self.CITATION_END_PATTERN.search(block):
                delim_found = True
                # remove ending delim
                blocks[i] = self.CITATION_END_PATTERN.sub("", block)
                # build HTML for citation
                citation_elem = etree.Element("cite")
                if self.citation_html_class != "":
                    citation_elem.set("class", self.citation_html_class)
                blocks[i] = blocks[i].rstrip() # remove trailing whitespace from the newline into `\end{}`
                self.parser.parseBlocks(citation_elem, blocks[citation_start_i:i + 1])
                # remove used blocks
                for _ in range(citation_start_i, i + 1):
                    blocks.pop(citation_start_i)
                break
        # if no ending delim for citation, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove blockquote ending delim, and extract element
        delim_found = False
        for i, block in enumerate(blocks):
            if self.END_PATTERN.search(block):
                delim_found = True
                # remove ending delim
                blocks[i] = self.END_PATTERN.sub("", block)
                # build HTML for blockquote
                blockquote_elem = etree.SubElement(parent, "blockquote")
                if self.html_class != "":
                    blockquote_elem.set("class", self.html_class)
                self.parser.parseBlocks(blockquote_elem, blocks[:i + 1])
                parent.append(citation_elem) # make sure citation comes at the end
                # remove used blocks
                for _ in range(i + 1):
                    blocks.pop(0)
                break
        # if no ending delim for blockquote, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False
        return True


class CitedBlockquoteExtension(Extension):
    r"""
    A blockquote with a citation/quote attribution underneath.

    Usage:
        .. code-block:: py

            import markdown
            from markdown_environments import CitedBlockquoteExtension

            input_text = ...
            output_text = markdown.markdown(input_text, extensions=[
                CitedBlockquoteExtension(html_class="give", citation_html_class="you")
            ])

    Markdown usage:
        .. code-block:: md

            \begin{cited_blockquote}
            <quote>

            \begin{citation}
            <citation>
            \end{citation}

            \end{cited_blockquote}

        becomes…

        .. code-block:: html

            <blockquote class="[html_class]">
              [quote]
            </blockquote>
            <cite class="[citation_html_class]">
              [citation]
            </cite>

    Note:
        The `citation` block can be placed anywhere within the `cited_blockquote` block, as long as, of course, there are
        blank lines before and after the `citation` block.
    """

    def __init__(self, **kwargs):
        """
        Initialize cited blockquote extension, with configuration options passed as the following keyword arguments:

            - **html_class** (*str*) -- HTML `class` attribute to add to blockquotes. Defaults to `""`.
            - **citation_html_class** (*str*) -- HTML `class` attribute to add to captions. Defaults to `""`.
        """

        self.config = {
            "html_class": [
                "",
                "HTML `class` attribute to add to cited blockquote. Defaults to `\"\"`."
            ],
            "citation_html_class": [
                "",
                "HTML `class` attribute to add to cited blockquote's citation. Defaults to `\"\"`."
            ]
        }
        util.init_extension_with_configs(self, **kwargs)

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(CitedBlockquoteProcessor(md.parser, **self.getConfigs()), "cited_blockquote", 105)


def makeExtension(**kwargs):
    return CitedBlockquoteExtension(**kwargs)
