# vaik-text-generator

Generate text image for training deep learning.

## Example

![text-generator-demo](https://user-images.githubusercontent.com/116471878/215615685-264bccd7-a8b7-4ca6-8bdb-36b3a32522fa.png)

## Install

``` shell
pip install git+https://github.com/vaik-info/vaik-text-generator.git
```

### Example(Simple)

```python
import os
from PIL import Image
from vaik_text_generator.text_generator import TextGenerator

text_generator = TextGenerator()
text_image = text_generator.write('aａアｱあゃキャ、亜唖|弌乘')

Image.fromarray(text_image).save(os.path.expanduser('~/Desktop/text.png'))
```

### Example(Option)
- ~/Desktop/font/*.otf
- ~/Desktop/font/*.ttf

```python
import os
from PIL import Image
from vaik_text_generator.text_generator import TextGenerator

text_generator = TextGenerator(ex_font_dir_path=os.path.expanduser('~/Desktop/font'),
                               font_size_ratio=(16, 128), font_same_ratio=0.5, font_scale_ratio=(0.9, 1.1), font_random_color_ratio=0.5,
                               space_ratio=(-0.1, 0.1), interval_ratio=(-0.3, 0.3), center_height_ratio=(0.4, 0.6))
text_image = text_generator.write('aａアｱあゃキャ、亜唖|弌乘')

Image.fromarray(text_image).save(os.path.expanduser('~/Desktop/text.png'))
```
