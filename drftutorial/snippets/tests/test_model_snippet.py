from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter

from drftutorial.snippets.models import Snippet
from .common import Common


class TestModelSnippet(Common):

    def test_should_compute_highlighted(self):
        title = 'test highlighted'
        style = 'dracula'
        code = 'print("test")'
        language = 'python'
        owner = self.create_user()
        snippet = Snippet.objects.create(
            language=language,
            style=style,
            code=code,
            title=title,
            owner=owner,
            linenos=True,
        )

        lexer = get_lexer_by_name(language)
        formatter = HtmlFormatter(style=style, linenos='table', full=True, title=title)
        highlighted = highlight(code, lexer, formatter)

        self.assertEqual(snippet.highlighted, highlighted)
