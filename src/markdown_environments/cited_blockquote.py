import re
import xml.etree.ElementTree as etree
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from mixins import HtmlClassMixin


class CitedBlockquote(BlockProcessor, HtmlClassMixin):
    """
    A blockquote with a citation underneath. Note that the citation goes in a line below the blockquote, so this is
    not designed for formal in-text citations.

    Usage:
        ```
        
        \begin{cited_blockquote}
        <quote>

        \begin{citation}
        <citation>
        \end{citation}

        \end{cited_blockquote}

        ```
        - HTML output:
            ```
            <blockquote class="[html_class]">
              <quote>
            </blockquote>
            <cite class="[citation_html_class]">
              <citation>
            </cite>
            ```
        - Note that the `citation` block can be placed anywhere within the `cited_blockquote` block
    """

    RE_BLOCKQUOTE_START = r"^\\begin{cited_blockquote}"
    RE_BLOCKQUOTE_END = r"^\\end{cited_blockquote}"
    RE_CITATION_START = r"^\\begin{citation}"
    RE_CITATION_END = r"^\\end{citation}"

    def __init__(self, *args, html_class: str="", citation_html_class: str="", **kwargs):
        super().__init__(*args, **kwargs)
        self.init_html_class(html_class)
        self.citation_html_class = citation_html_class

    def test(self, parent, block):
        return re.match(self.RE_BLOCKQUOTE_START, block, re.MULTILINE)

    def run(self, parent, blocks):
        org_blocks = list(blocks)

        # remove blockquote starting delimiter
        blocks[0] = re.sub(self.RE_BLOCKQUOTE_START, "", blocks[0], flags=re.MULTILINE)

        # find and remove citation starting delimiter
        citation_start_i = None
        for i, block in enumerate(blocks):
            if re.match(self.RE_CITATION_START, block, re.MULTILINE):
                # remove ending delimiter and note which block citation started on
                # (as citation content itself is an unknown number of blocks)
                citation_start_i = i
                blocks[i] = re.sub(self.RE_CITATION_START, "", block, flags=re.MULTILINE)
                break

        # if no starting delimiter for citation, restore and do nothing
        if citation_start_i is None:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove citation ending delimiter, and extract element
        elem_citation = None
        for i, block in enumerate(blocks[citation_start_i:], start=citation_start_i):
            if re.search(self.RE_CITATION_END, block, flags=re.MULTILINE):
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_CITATION_END, "", block, flags=re.MULTILINE)
                # build HTML for citation
                elem_citation = etree.Element("cite")
                elem_citation.set("class", self.citation_html_class)
                self.parser.parseBlocks(elem_citation, blocks[citation_start_i:i + 1])
                # remove used blocks
                for _ in range(citation_start_i, i + 1):
                    blocks.pop(citation_start_i)
                break

        # if no ending delimiter for citation, restore and do nothing
        if elem_citation is None:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove blockquote ending delimiter, and extract element
        for i, block in enumerate(blocks):
            if re.search(self.RE_BLOCKQUOTE_END, block, flags=re.MULTILINE):
                # remove ending delimiter
                blocks[i] = re.sub(self.RE_BLOCKQUOTE_END, "", block, flags=re.MULTILINE)
                # build HTML for blockquote
                elem_blockquote = etree.SubElement(parent, "blockquote")
                elem_blockquote.set("class", self.html_class)
                self.parser.parseBlocks(elem_blockquote, blocks[:i + 1])
                parent.append(elem_citation) # make sure citation comes after everything else
                # remove used blocks
                for _ in range(i + 1):
                    blocks.pop(0)
                return True

        # if no ending delimiter for blockquote, restore and do nothing
        blocks.clear()
        blocks.extend(org_blocks)
        return False


class CitedBlockquoteExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
                CitedBlockquote(
                        md.parser, html_class="md-cited-blockquote",
                        citation_html_class="md-cited-blockquote__citation"),
                "cited_blockquote", 105)


def makeExtension(**kwargs):
    return CitedBlockquoteExtension(**kwargs)
