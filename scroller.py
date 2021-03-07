from abc import ABC, abstractmethod
import typing as t

StrCallback = t.Callable[[str], None]


class ScrollerBase(ABC):
    """
    The base class for the scroller. Contains base methods that need to be overwritten.

    :param width: The width of the scroller in characters
    :param text: The text that will be scrolling
    :param filler: What to put in the spaces where there are no characters
    :param callback: Is called when on scrolling, usually used to display the scroller
    """
    def __init__(self, width: int, text: str, filler: str = ' ', callback: StrCallback = None):
        self.width: int = width
        self.text: str = text
        self.filler: str = filler

        self.callback: StrCallback = callback or self.print_line

        self._index: int = -1

    @property
    def max_index(self) -> int:
        """
        Get the maximum index of the scroll
        :return: The max index
        """
        return len(self.text) + self.width

    def get_begin_end(self, index: int = None) -> t.Tuple[int, int]:
        """
        Get the begin and end of the text
        :param index: The index used to get the begin and end
        :return: A tuple of begin and end
        """
        index = index if index is not None else self._index
        return index - self.width, -(index - len(self.text))

    def print_line(self, display_text: str) -> None:
        """
        Basic print function to print the current scroll
        :param display_text: The text of  the scroll
        """
        print(f"\r{display_text}", end='\n' if self._index == self.max_index else '')

    @abstractmethod
    def __next__(self) -> None:
        """
        Go the next scroll
        :raises NotImplementedError: Needs to be overwritten in a subclass
        """
        raise NotImplementedError

    @abstractmethod
    def __prev__(self) -> None:
        """
        Go to the previous scroll
        :raises NotImplementedError: Needs to be overwritten in a subclass
        """
        raise NotImplementedError


class Scroller(ScrollerBase):
    """
    Basic scroller class. Need to overwrite :function`Scroller.get_text` for it to work.

    :param width: The width of the scroller in characters
    :param text: The text that will be scrolling
    :param wait: The amount of time to wait between scrolling
    :param filler: What to put in the spaces where there are no characters
    :param callback: Is called when on scrolling, usually used to display the scroller
    :param include_first: Whether to include the first, empty scroll
    :param include_last: Whether to include the last, empty scroll
    """
    def __init__(self, width: int, text: str, wait: float, filler: str = ' ', callback: StrCallback = None,
                 include_first: bool = True, include_last: bool = True):
        self.wait: float = wait
        from time import sleep as _sleep
        self._sleep: t.Callable[[t.Any[int, float]], None] = _sleep
        self.include_first: bool = include_first
        self.include_last: bool = include_last
        super().__init__(width, text, filler=filler, callback=callback or self.print_line)
        self._index: int = int(not self.include_first)-1
        self.print_newline: StrCallback = lambda display_text, prefix='', suffix='': self.print_line(display_text,
                                                                                                     prefix, suffix,
                                                                                                     end='\n')

    def print_line(self, display_text: str, prefix: str = '.', suffix: str = '.', end: str = '') -> None:
        """
        A more comprehensive print function to display the scroll
        :param display_text: The text of the scroll
        :param prefix: This will be at the start of the line
        :param suffix: This will be at the end of the line
        :param end: What to end on on the last scroll
        """
        print(f"\r{prefix}{display_text}{suffix}",
              end=end if self._index == self.max_index - int(not self.include_last) else '')

    @property
    def range(self) -> t.Tuple[int, int]:
        """
        The range (min,max) of the indexes
        :return: A tuple of (min, max)
        """
        return int(not self.include_first), self.max_index + int(self.include_last)

    def run(self) -> None:
        """
        Fully scroll once
        """
        for _ in range(*self.range):
            self.__next__()

    def repeat(self, times: int = -1) -> None:
        """
        Fully scroll a number of (or infinite) times
        :param times: The number of times to repeat (-1 for infinite)
        """
        while times != 0:
            self.run()
            times -= 1

    @abstractmethod
    def get_text(self, begin: int, end: int) -> str:
        """
        Get the text of the current scroll
        :param begin: Beginning index
        :param end: Ending index
        :raises NotImplementedError: Needs to be overwritten in a subclass
        :return: The text to display
        """
        raise NotImplementedError

    def start(self) -> None:
        """
        Move the scrolling to the start
        """
        self._index = int(not self.include_first)-1
        self.__next__()

    def __next__(self) -> None:
        """
        Increases index, runs callback function and waits
        """
        self._index += 1
        if self._index > self.max_index - int(not self.include_last):
            self._index = int(not self.include_first)
        begin, end = self.get_begin_end(self._index)
        display_text = self.get_text(begin, end)
        self.callback(display_text)
        self._sleep(self.wait)

    def __prev__(self) -> None:
        """
        Decreases index, runs callback function and waits
        """
        self._index -= 1
        if self._index < int(not self.include_first):
            self._index = self.max_index - int(not self.include_last)
        begin, end = self.get_begin_end(self._index)
        display_text = self.get_text(begin, end)
        self.callback(display_text)
        self._sleep(self.wait)


class RightScroller(Scroller):
    """
    Fully working scroller class. Scrolls text from left to right.
    """
    def get_text(self, begin: int, end: int) -> str:
        """
        Get the text of the current scroll
        :param begin: Beginning index
        :param end: Ending index
        :return: The text to display
        """
        begin, end = self.get_begin_end(self._index)
        if begin < 0 and end < 0:
            display_text = self.filler * -end + self.text + self.filler * -begin
        elif begin < 0:
            display_text = ('' if self._index == 0 else self.text[-self._index:]) + self.filler * -begin
        elif end < 0:
            display_text = self.filler * -end + (self.text if begin == 0 else self.text[:-begin])
        else:
            display_text = (self.text[end:] if begin == 0 else self.text[end:-begin])
        return display_text


class LeftScroller(Scroller):
    """Fully working scroller class. Scrolls text from left to right."""
    def get_text(self, begin: int, end: int) -> str:
        """
        Get the text of the current scroll
        :param begin: Beginning index
        :param end: Ending index
        :return: The text to display
        """
        if begin < 0 and end < 0:
            display_text = self.filler * -begin + self.text + self.filler * -end
        elif begin < 0:
            display_text = self.filler * -begin + (self.text if end == 0 else self.text[:-end])
        elif end < 0:
            display_text = self.text[begin:] + self.filler * -end
        else:
            display_text = (self.text[begin:] if end == 0 else self.text[begin:-end])
        return display_text


def main():
    l_scroller = LeftScroller(10, "https://github.com/ScottBot10/scroller", .3, include_first=True, include_last=False)
    l_scroller.callback = lambda display_text: print(f".{display_text}.") # l_scroller.print_line(display_text, prefix='|', suffix='|', end='\n')
    l_scroller.run()


if __name__ == '__main__':
    main()
