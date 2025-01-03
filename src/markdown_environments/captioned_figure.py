import re
import xml.etree.ElementTree as etree

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from . import util
from .mixins import HtmlClassMixin


class CaptionedFigureProcessor(BlockProcessor, HtmlClassMixin):

    RE_FIGURE_START = r"^\\begin{captioned_figure}"
    RE_FIGURE_END = r"^\\end{captioned_figure}"
    RE_CAPTION_START = r"^\\begin{caption}"
    RE_CAPTION_END = r"^\\end{caption}"

    def __init__(self, *args, html_class: str, caption_html_class: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_html_class(html_class)
        self.caption_html_class = caption_html_class

    def test(self, parent, block):
        return re.match(self.RE_FIGURE_START, block, re.MULTILINE)

    def run(self, parent, blocks):
        org_blocks = list(blocks)

        # remove figure starting delim
        blocks[0] = re.sub(self.RE_FIGURE_START, "", blocks[0], flags=re.MULTILINE)

        # find and remove caption starting delim
        caption_start_i = None
        for i, block in enumerate(blocks):
            if re.match(self.RE_CAPTION_START, block, re.MULTILINE):
                # remove ending delim and note which block captions started on
                # (as caption content itself is an unknown number of blocks)
                caption_start_i = i
                blocks[i] = re.sub(self.RE_CAPTION_START, "", block, flags=re.MULTILINE)
                break

        # if no starting delim for caption, restore and do nothing
        if caption_start_i is None:
            # `blocks = org_blocks` doesn't work since lists are passed by pointer in Python (value of reference)
            # so changing the address of `blocks` only updates the local copy of it (the pointer)
            # we need to change the values pointed to by `blocks` (its list elements)
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove caption ending delim, and extract element
        delim_found = False
        for i, block in enumerate(blocks[caption_start_i:], start=caption_start_i):
            if re.search(self.RE_CAPTION_END, block, flags=re.MULTILINE):
                delim_found = True
                # remove ending delim
                blocks[i] = re.sub(self.RE_CAPTION_END, "", block, flags=re.MULTILINE)
                # build HTML for caption
                elem_caption = etree.Element("figcaption")
                if self.caption_html_class != "":
                    elem_caption.set("class", self.caption_html_class)
                self.parser.parseBlocks(elem_caption, blocks[caption_start_i:i + 1])
                # remove used blocks
                for _ in range(caption_start_i, i + 1):
                    blocks.pop(caption_start_i)
                break
        # if no ending delim for caption, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove figure ending delim, and extract element
        delim_found = False
        for i, block in enumerate(blocks):
            if re.search(self.RE_FIGURE_END, block, flags=re.MULTILINE):
                delim_found = True
                # remove ending delim
                blocks[i] = re.sub(self.RE_FIGURE_END, "", block, flags=re.MULTILINE)
                # build HTML for figure
                elem_figure = etree.SubElement(parent, "figure")
                if self.html_class != "":
                    elem_figure.set("class", self.html_class)
                self.parser.parseBlocks(elem_figure, blocks[:i + 1])
                elem_figure.append(elem_caption) # make sure captions come after everything else
                # remove used blocks
                for _ in range(i + 1):
                    blocks.pop(0)
                break
        # if no ending delim for figure, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False
        return True


class CaptionedFigureExtension(Extension):
    r"""
    Any chunk of content, such as an image, with a caption underneath.

    Example:
        .. code-block:: py

            import markdown
            from markdown_environments import CaptionedFigureExtension

            input_text = ...
            output_text = markdown.markdown(input_text, extensions=[
                CaptionedFigureExtension(html_class="never", caption_html_class="gonna")
            ])

    Markdown usage:
        .. code-block:: md

            \begin{captioned_figure}
            <figure content>

            \begin{caption}
            <caption>
            \end{caption}

            \end{captioned_figure}

        becomes…

        .. code-block:: html

            <figure class="[html_class]">
              [figure content]
              <figcaption class="[caption_html_class]">
                [caption]
              </figcaption>
            </figure>

        Note that the `caption` block can be placed anywhere within the `captioned_figure` block, as long as, of course,
        there are blank lines before and after the `caption` block.
    """

    def __init__(self, **kwargs):
        """
        Initialize captioned figure extension, with configuration options passed as the following keyword arguments:

            - **html_class** (*str*) -- HTML `class` attribute to add to figures (default: `""`).
            - **caption_html_class** (*str*) -- HTML `class` attribute to add to captions (default: `""`).
        """

        self.config = {
            "html_class": [
                "",
                "HTML `class` attribute to add to captioned figure (default: `\"\"`)."
            ],
            "caption_html_class": [
                "",
                "HTML `class` attribute to add to captioned figure's caption (default: `\"\"`)."
            ]
        }
        util.init_extension_with_configs(self, **kwargs)

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(CaptionedFigureProcessor(md.parser, **self.getConfigs()), "captioned_figure", 105)


def makeExtension(**kwargs):
    return CaptionedFigureExtension(**kwargs)
