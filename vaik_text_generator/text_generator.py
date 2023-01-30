import glob
import os.path
import random
import numpy as np

from PIL import Image, ImageDraw, ImageFont


class TextGenerator:
    def __init__(self, fonts_dir_path=os.path.join(os.path.dirname(__file__), 'fonts'), ex_font_dir_path=None,
                 font_size_ratio=(16, 128), font_same_ratio=0.5, font_scale_ratio=(0.9, 1.1), font_random_color_ratio=0.5,
                 space_ratio=(-0.1, 0.1), interval_ratio=(-0.3, 0.3), center_height_ratio=(0.4, 0.6)):
        self.font_path_list = glob.glob(os.path.join(fonts_dir_path, '**/*.*'), recursive=True)
        if ex_font_dir_path is not None:
            self.font_path_list.extend(glob.glob(os.path.join(ex_font_dir_path, '**/*.*'), recursive=True))
        self.font_size_ratio = font_size_ratio
        self.font_same_ratio = font_same_ratio
        self.font_random_color_ratio = font_random_color_ratio
        self.space_ratio = space_ratio
        self.interval_ratio = interval_ratio
        self.font_scale_ratio = font_scale_ratio
        self.center_height_ratio = center_height_ratio

    def write(self, text):
        base_font_size = random.uniform(self.font_size_ratio[0], self.font_size_ratio[1])
        max_font_size = int(base_font_size * self.font_scale_ratio[1])
        text_image = np.ones((int(max_font_size + max_font_size * self.space_ratio[1]), int(max_font_size * self.space_ratio[1]), 3), dtype=np.uint8) * 255

        if self.font_same_ratio > random.uniform(0.0, 1.0):
            font_path = random.choice(self.font_path_list)
        else:
            font_path = None
        if self.font_random_color_ratio > random.uniform(0.0, 1.0):
            color = (random.randint(0, 253), random.randint(0, 253), random.randint(0, 253))
        else:
            color = None

        for character in text:
            font = ImageFont.truetype(random.choice(self.font_path_list) if font_path is None else font_path, max_font_size)

            character_image = self.get_char_image(character, font, self.font_scale_ratio[1] - self.font_scale_ratio[0], color)
            text_image = self.__merge(text_image, character_image,
                                      int(character_image.shape[1] * random.uniform(self.interval_ratio[0], self.interval_ratio[1])),
                                      random.uniform(self.center_height_ratio[0], self.center_height_ratio[1]))
        crop_text_image = self.__copy_make_border(text_image, base_font_size, self.space_ratio)
        return crop_text_image

    def get_char_image(self, character, font, decay_ratio, color=None):
        canvas = Image.new("RGB", (font.size * 2, font.size * 2), (255, 255, 255))
        draw_canvas = ImageDraw.Draw(canvas)
        if color is None:
            color = (random.randint(0, 253), random.randint(0, 253), random.randint(0, 253))
        draw_canvas.text((0, 0), character, font=font, fill=color)
        xmin, _, xmax, ymax = self.__get_bbox_cordinate(np.asarray(canvas.convert('L')) < 254)
        draw_image = np.asarray(canvas)[:ymax, xmin:xmax, :]
        resize_size = (max(1, int(draw_image.shape[1]*random.uniform(1-decay_ratio, 1))), max(1, int(draw_image.shape[0]*random.uniform(1-decay_ratio, 1))))
        draw_image = Image.fromarray(draw_image).resize(resize_size)
        return np.asarray(draw_image)

    def __get_bbox_cordinate(self, bool_image):
        xmin, ymin, xmax, ymax = None, None, None, None

        x_sum_bool_image = np.sum(bool_image, axis=0)
        y_sum_bool_image = np.sum(bool_image, axis=1)

        for i in range(x_sum_bool_image.shape[0]):
            if x_sum_bool_image[i] > 0:
                xmin = i
                break

        for i in range(y_sum_bool_image.shape[0]):
            if y_sum_bool_image[i] > 0:
                ymin = i
                break

        x_revert_sum_bool_image = x_sum_bool_image[::-1]
        y_revert_sum_bool_image = y_sum_bool_image[::-1]

        for i in range(x_revert_sum_bool_image.shape[0]):
            if x_revert_sum_bool_image[i] > 0:
                xmax = x_revert_sum_bool_image.shape[0] - i
                break

        for i in range(y_revert_sum_bool_image.shape[0]):
            if y_revert_sum_bool_image[i] > 0:
                ymax = y_revert_sum_bool_image.shape[0] - i
                break

        return xmin, ymin, xmax, ymax

    def __merge(self, text_image, character_image, override_width, center_height):
        canvas_image = np.ones(
            (text_image.shape[0], text_image.shape[1] + character_image.shape[1] + override_width, 3),
            dtype=np.uint8) * 255
        canvas_image[:text_image.shape[0], :text_image.shape[1], :] = text_image

        canvas_image_start_y = int(max(0, canvas_image.shape[0] * center_height - character_image.shape[0] / 2))
        canvas_image_end_y = min(text_image.shape[0], canvas_image_start_y + character_image.shape[0])
        canvas_image_start_x = int(max(0, text_image.shape[1] + override_width))
        canvas_image_end_x = min(canvas_image.shape[1], canvas_image_start_x + character_image.shape[1])

        character_image_start_x = 0
        character_image_end_x = character_image_start_x + canvas_image_end_x - canvas_image_start_x
        if (canvas_image_end_y - canvas_image_start_y) < character_image.shape[0]:
            character_image_start_y = int((character_image.shape[0] - (canvas_image_end_y - canvas_image_start_y)) / 2)
        else:
            character_image_start_y = 0
        character_image_end_y = character_image_start_y + canvas_image_end_y - canvas_image_start_y
        canvas_image[canvas_image_start_y:canvas_image_end_y, canvas_image_start_x:canvas_image_end_x, :] = np.minimum(canvas_image[canvas_image_start_y:canvas_image_end_y, canvas_image_start_x:canvas_image_end_x, :], character_image[character_image_start_y:character_image_end_y, character_image_start_x:character_image_end_x, :])
        return canvas_image

    def __copy_make_border(self, text_image, base_font_size, space_ratio):
        xmin, ymin, xmax, ymax = self.__get_bbox_cordinate(np.asarray(Image.fromarray(text_image).convert('L')) < 254)
        text_image = text_image[ymin:ymax, xmin:xmax, :]
        space = int(base_font_size * space_ratio[1] - space_ratio[0])
        canvas_image = np.ones((text_image.shape[0] + space * 2, text_image.shape[1] + space * 2, 3), dtype=np.uint8) * 255
        start_y = random.randint(0, canvas_image.shape[0] - text_image.shape[0])
        end_y = start_y + text_image.shape[0]
        start_x = random.randint(0, canvas_image.shape[1] - text_image.shape[1])
        end_x = start_x + text_image.shape[1]
        canvas_image[start_y:end_y, start_x:end_x, :] = text_image
        h_space = int(base_font_size * random.uniform(0, (space_ratio[1] - space_ratio[0])))
        w_space = int(base_font_size * random.uniform(0, (space_ratio[1] - space_ratio[0])))
        return canvas_image[h_space: canvas_image.shape[0]-h_space, w_space:canvas_image.shape[1]-w_space, :]