from markdown_environments.mixins import HtmlClassMixin


class HtmlClassMixinImpl(HtmlClassMixin):
    def get_html_class(self):
        return self.html_class


def test_init_html_class():
    html_class = "im running out of things to put here"
    html_class_mixin_impl = HtmlClassMixinImpl()
    html_class_mixin_impl.init_html_class(html_class)
    assert html_class_mixin_impl.get_html_class() == html_class
