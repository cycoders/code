"""Custom Textual widgets."""

from textual.widget import Widget
from textual.reactive import reactive
from textual.message import Message
from textual.dom import DOM

from .models import UnicodeChar


class CharItem(DOM):
    """Selectable char list item."""

    DEFAULT_CSS = """
    CharItem {
        height: 3;
        padding: 1;
    }
    """

    char = reactive(UnicodeChar, repr=False)
    is_fav = reactive(False, repr=False)

    def watch_char(self, char: UnicodeChar) -> None:
        self.mutated()

    def watch_is_fav(self) -> None:
        self.mutated()

    def render(self) -> str:
        from .render import render_list_item
        return render_list_item(self.char, self.is_fav)


class CharDetail(Widget):
    """Details panel."""

    DEFAULT_CSS = """
    CharDetail {
        height: 1fr;
        padding: 2;
    }
    """

    char = reactive(UnicodeChar, repr=False)
    is_fav = reactive(False, repr=False)

    def on_mount(self) -> None:
        self.styles.background = "ansi_black"

    def render(self) -> str:
        from .render import render_detail
        return render_detail(self.char, self.is_fav)
