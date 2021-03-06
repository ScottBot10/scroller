from abc import ABC, abstractmethod


class Scroller(ABC):
    def __init__(self, width, text, filler=' ', callback=None):
        self.width = width
        self.text = text
        self.filler = filler

        self.callback = callback or self.print_line

        self._index = 0

    @property
    def max_index(self):
        return len(self.text) + self.width

    def get_begin_end(self, index=None):
        index = index if index is not None else self._index
        return index - self.width, -(index - len(self.text))

    def print_line(self, display_text):
        print(f"\r.{display_text}.", end='\n' if self._index == self.max_index else '')

    @abstractmethod
    def __next__(self):
        raise NotImplementedError


class RepeatingScroller(Scroller):

    def __init__(self, width, text, wait, filler=' ', callback=None, include_first=True, include_last=True):
        self.wait = wait
        from time import sleep as _sleep
        self._sleep = _sleep
        self.include_first = include_first
        self.include_last = include_last
        super().__init__(width, text, filler=filler, callback=callback or self.print_line)
        self._index = int(not self.include_first)
        self.print_newline = lambda display_text, prefix='.', suffix='.': self.print_line(display_text,
                                                                                          prefix, suffix,
                                                                                          end='\n')

    def print_line(self, display_text, prefix='.', suffix='.', end=''):
        print(f"\r{prefix}{display_text}{suffix}",
              end=end if self._index == self.max_index - int(not self.include_last) else '')

    def run(self):
        for _ in range(int(not self.include_first), self.max_index + int(self.include_last)):
            self.__next__()

    def repeat(self, times=-1):
        while times != 0:
            self.run()
            times -= 1

    @abstractmethod
    def get_text(self, begin, end):
        raise NotImplementedError

    def __next__(self):
        begin, end = self.get_begin_end(self._index)
        display_text = self.get_text(begin, end)
        self.callback(display_text)
        self._index += 1
        if self._index > self.max_index - int(not self.include_last):
            self._index = int(not self.include_first)
        self._sleep(self.wait)


class RightScroller(RepeatingScroller):

    def get_text(self, begin, end):
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


class LeftScroller(RepeatingScroller):

    def get_text(self, begin, end):
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
    r_scroller = LeftScroller(10, "https://github.com/ScottBot10/scroller", .3)
    r_scroller.callback = lambda display_text: r_scroller.print_line(display_text, prefix='|', suffix='|', end='\n')
    r_scroller.run()


if __name__ == '__main__':
    main()
