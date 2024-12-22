from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTagInlineProcessor


class CustomInlineExtensions(Extension):
    def extendMarkdown(self, md):
        """
        Underlines text.

        Usage:
            ```
            __<text>__
            ```
        """
        regex = r"()__([\S\s]+?)__"
        md.inlinePatterns.register(SimpleTagInlineProcessor(regex, "u"), "underline", 105)

        """
        Strikes through text.
        
        Usage:
            ```
            ~~<text>~~
            ```
        """
        regex = r"()~~([\S\s]+?)~~"
        md.inlinePatterns.register(SimpleTagInlineProcessor(regex, "del"), "strikethrough", 105)
