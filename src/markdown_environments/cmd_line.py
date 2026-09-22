import re
import xml.etree.ElementTree as etree

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from . import utils


class CmdLineProcessor(BlockProcessor):

    START_PATTERN = re.compile(r"^\\begin{cmd_line}", flags=re.MULTILINE)
    END_PATTERN = re.compile(r"^\\end{cmd_line}", flags=re.MULTILINE)
    CMD_START_PATTERN = re.compile(r"^\\begin{cmd}", flags=re.MULTILINE)
    CMD_END_PATTERN = re.compile(r"^\\end{cmd}", flags=re.MULTILINE)

    def __init__(self, *args, html_class: str, cmd_html_class: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.html_class = html_class
        self.cmd_html_class = cmd_html_class

    def test(self, parent, block):
        return self.START_PATTERN.match(block)

    def run(self, parent, blocks):
        org_blocks = list(blocks)

        # remove cmd line starting delim
        blocks[0] = self.START_PATTERN.sub("", blocks[0])

        # find and remove cmd starting delim
        delim_found = False
        cmd_start_i = None
        for i, block in enumerate(blocks):
            if self.CMD_START_PATTERN.match(block):
                delim_found = True
                # remove ending delim and note which block cmd started on
                # (as cmd content itself is an unknown number of blocks)
                cmd_start_i = i
                blocks[i] = self.CMD_START_PATTERN.sub("", block)
                break
        # if no starting delim for cmd, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove cmd ending delim, and extract element
        # start search at cmd starting delim
        delim_found = False
        for i, block in enumerate(blocks[cmd_start_i:], start=cmd_start_i):
            if self.CMD_END_PATTERN.search(block):
                delim_found = True
                # remove ending delim
                blocks[i] = self.CMD_END_PATTERN.sub("", block)
                # build HTML for cmd
                cmd_elem = etree.Element("div")
                if self.cmd_html_class != "":
                    cmd_elem.set("class", self.cmd_html_class)
                blocks[i] = blocks[i].rstrip() # remove trailing whitespace from the newline into `\end{}`
                self.parser.parseBlocks(cmd_elem, blocks[cmd_start_i:i + 1])
                # remove used blocks
                for _ in range(cmd_start_i, i + 1):
                    blocks.pop(cmd_start_i)
                break
        # if no ending delim for cmd, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False

        # find and remove cmd line ending delim, and extract element
        delim_found = False
        for i, block in enumerate(blocks):
            if self.END_PATTERN.search(block):
                delim_found = True
                # remove ending delim
                blocks[i] = self.END_PATTERN.sub("", block)
                # build HTML for cmd line
                cmd_line_elem = etree.SubElement(parent, "div")
                if self.html_class != "":
                    cmd_line_elem.set("class", self.html_class)
                self.parser.parseBlocks(cmd_line_elem, blocks[:i + 1])
                parent.insert(0, cmd_elem) # make sure cmd comes at the beginning
                # remove used blocks
                for _ in range(i + 1):
                    blocks.pop(0)
                break
        # if no ending delim for cmd line, restore and do nothing
        if not delim_found:
            blocks.clear()
            blocks.extend(org_blocks)
            return False
        return True


class CmdLineExtension(Extension):
    r"""
    A command line box with a command and the command output underneath.

    Usage:
        .. code-block:: py

            import markdown
            from markdown_environments import CmdLineExtension

            input_text = ...
            output_text = markdown.markdown(input_text, extensions=[
                CmdLineExtension(html_class="meow", cmd_html_class="woof")
            ])

    Markdown usage:
        .. code-block:: md

            \begin{cmd_line}

            \begin{cmd}
            <cmd>
            \end{cmd}

            <cmd output>
            \end{cmd_line}

        becomes:

        .. code-block:: html

            <div class="[cmd_html_class]">
              [cmd]
            </div>
            <div class="[cmd_html_class]">
              [cmd output]
            </div>

    Note:
        The `cmd` block can be placed anywhere within the `cmd_line` block, as long as, of course, there are
        blank lines before and after the `cmd` block.
    """

    def __init__(self, **kwargs):
        """
        Initialize command line extension, with configuration options passed as the following keyword arguments:

            - **html_class** (*str*) -- HTML `class` attribute to add to command line boxes. Defaults to `""`.
            - **cmd_html_class** (*str*) -- HTML `class` attribute to add to commands. Defaults to `""`.
        """

        self.config = {
            "html_class": [
                "",
                "HTML `class` attribute to add to command line boxes. Defaults to `\"\"`."
            ],
            "cmd_html_class": [
                "",
                "HTML `class` attribute to add to commands. Defaults to `\"\"`."
            ]
        }
        utils.init_extension_with_configs(self, **kwargs)

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(
            CmdLineProcessor(md.parser, **self.getConfigs()), "cmd_line", 105
        )


def makeExtension(**kwargs):
    return CmdLineExtension(**kwargs)
