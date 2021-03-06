# scroller
Simple horizontally scrolling text

## Installation
There is no pypi package for it so you can just clone straight from the repo
```sh
$ git clone https://github.com/ScottBot10/scroller.git
```
```py
from scroller import LeftScroller
```

## Usage
```py
from scroller import LeftScroller, RightScroller

# Scroll text from right to left every .3 seconds
l_scroller = LeftScroller(10, "This text will scroll from right to left", .3)
l_scroller.run()

# Scroll text from left to right 3 times
r_scroller = RightScroller(10, "This text will scroll from left to right", .3)
r_scroller.repeat(3)

# Add prefix and suffix
l_scroller = LeftScroller(10, "This text will scroll from right to left", .3, 
                          callback=lambda display_text: l_scroller.print_line(display_text, prefix='|', suffix='|', end='\n'))
l_scroller.run()
# Returns:
# |   This te| (...)
```