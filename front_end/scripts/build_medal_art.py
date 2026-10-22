"""用勋章模板生成各级、各档的透明 WebP。

初级偏铜，中级偏银，高级保持金色。档位数字印在图上，文件名用库存的整数档。
运行：back_end/saolei/.venv/Scripts/python.exe front_end/scripts/build_medal_art.py
"""
from collections import deque
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / 'src' / 'assets' / 'medal-templates'
OUTPUT_DIR = ROOT / 'public' / 'assets' / 'medals'
SIZE = 320
BVS_SCALE = 10000
THRP_SCALE = 100000
TIME = {
    'b': (20, 15, 12, 10, 8, 6, 5, 4, 3, 2, 1),
    'i': (150, 100, 80, 60, 50, 40, 30, 25, 20, 15, 12, 10),
    'e': (300, 200, 150, 120, 100, 90, 80, 70, 60, 50, 40, 30),
}
BVS = {
    'b': (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12),
    'i': (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8),
    'e': (1, 1.5, 2, 2.5, 3, 4, 5, 6),
}
BVS_NF = {
    'b': (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 9),
    'i': (1, 1.5, 2, 2.5, 3, 4, 5, 6, 7),
    'e': (1, 1.5, 2, 2.5, 3, 4, 5),
}
STNB = (10, 15, 20, 30, 40, 50, 60, 80, 100, 150, 200, 300)
THRP_NF = (0.5, 0.7, 0.8, 0.9, 0.95, 1)
THRP_FL = {
    'b': (0.5, 0.7, 0.8, 1, 1.2, 1.5, 1.8, 2, 2.3, 2.5),
    'i': (0.5, 0.7, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 1.9),
    'e': (0.5, 0.7, 0.8, 1, 1.2, 1.4, 1.5, 1.6),
}
THREE_NF = (0.9, 0.95, 1)
THREE_FL = (1, 1.2, 1.5)


def to_units(number, scale):
    return int((Decimal(str(number)) * scale).to_integral_value(rounding=ROUND_HALF_UP))


def trim_label(number):
    return f'{number:.5f}'.rstrip('0').rstrip('.')


def stage_units(kind, value):
    if kind == 'time':
        return value * 1000, str(value)
    if kind == 'bvs':
        units = to_units(value, BVS_SCALE)
        return units, trim_label(units / BVS_SCALE)
    if kind == 'stnb':
        return value, str(value)
    units = to_units(value, THRP_SCALE)
    return units, trim_label(units / THRP_SCALE)


def is_background(red, green, blue, kind):
    if kind == 'black':
        return red < 28 and green < 28 and blue < 28
    if max(red, green, blue) - min(red, green, blue) > 16:
        return False
    average = (red + green + blue) / 3
    return 110 <= average <= 220


def clear_background(image, kind):
    rgba = image.convert('RGBA')
    width, height = rgba.size
    pixels = rgba.load()
    seen = bytearray(width * height)
    queue = deque()

    def push(x, y):
        index = y * width + x
        if seen[index]:
            return
        red, green, blue, _alpha = pixels[x, y]
        if not is_background(red, green, blue, kind):
            return
        seen[index] = 1
        queue.append((x, y))

    for x in range(width):
        push(x, 0)
        push(x, height - 1)
    for y in range(height):
        push(0, y)
        push(width - 1, y)
    while queue:
        x, y = queue.popleft()
        pixels[x, y] = (0, 0, 0, 0)
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height:
                push(nx, ny)
    for _pass in range(8):
        pending = []
        for y in range(height):
            for x in range(width):
                red, green, blue, alpha = pixels[x, y]
                if alpha == 0 or not is_background(red, green, blue, kind):
                    continue
                neighbors = ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                if any(0 <= nx < width and 0 <= ny < height and pixels[nx, ny][3] == 0 for nx, ny in neighbors):
                    pending.append((x, y))
        for x, y in pending:
            pixels[x, y] = (0, 0, 0, 0)
        if not pending:
            break
    return rgba


def fit_square(image, size):
    image.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    canvas.paste(image, ((size - image.width) // 2, (size - image.height) // 2), image)
    return canvas


def prepare(path, kind):
    image = clear_background(Image.open(path), kind)
    box = image.getbbox()
    if box:
        image = image.crop(box)
    return fit_square(image, SIZE)


def recolor(image, metal):
    if metal == 'e':
        return image.copy()
    result = image.copy()
    pixels = result.load()
    width, height = result.size
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if alpha < 8:
                continue
            if red > 230 and green > 220 and blue > 200:
                continue
            if red <= blue + 25 or red < 70:
                continue
            luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
            if metal == 'i':
                target = (luminance * 0.90 + 16, luminance * 0.94 + 18, luminance * 1.00 + 24)
            else:
                target = (luminance * 1.12 + 36, luminance * 0.52 + 8, luminance * 0.20)
            mix = 0.8
            pixels[x, y] = tuple(max(0, min(255, int(channel * (1 - mix) + aim * mix))) for channel, aim in zip((red, green, blue), target)) + (alpha,)
    return result


def load_font(size):
    for path in (r'C:\Windows\Fonts\arialbd.ttf', r'C:\Windows\Fonts\segoeuib.ttf', r'C:\Windows\Fonts\arial.ttf'):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def stamp(base, text, metal, badge):
    image = base.copy()
    draw = ImageDraw.Draw(image)
    font = load_font(46 if len(text) <= 2 else 38 if len(text) <= 3 else 32)
    box = draw.textbbox((0, 0), text, font=font)
    text_width = box[2] - box[0]
    text_height = box[3] - box[1]
    plate_width = text_width + 28
    plate_height = text_height + 14
    center_x = image.width * (0.40 if badge else 0.50)
    center_y = image.height * (0.73 if badge else 0.80)
    left = int(center_x - plate_width / 2)
    top = int(center_y - plate_height / 2)
    fill, ink = {
        'b': ((78, 36, 14, 230), (236, 176, 108, 255)),
        'i': ((32, 40, 48, 230), (232, 238, 244, 255)),
        'e': ((24, 18, 6, 230), (243, 212, 138, 255)),
    }[metal]
    draw.rounded_rectangle((left, top, left + plate_width, top + plate_height), radius=8, fill=fill, outline=ink, width=2)
    draw.text((left + 14 - box[0], top + 7 - box[1]), text, font=font, fill=ink)
    return image


def write_levels(base, folder, kind, table, badge):
    for metal, values in table.items():
        colored = recolor(base, metal)
        for value in values:
            units, label = stage_units(kind, value)
            path = OUTPUT_DIR / folder / metal / f'{units}.webp'
            path.parent.mkdir(parents=True, exist_ok=True)
            stamp(colored, label, metal, badge).save(path, format='WEBP', quality=78, method=4)


def write_shareholder(base):
    """越晚偏铜，居中偏银，最早保持金色。不印编号。"""
    for stage, metal in ((100000, 'b'), (10000, 'i'), (1000, 'e')):
        path = OUTPUT_DIR / 'shareholder' / f'{stage}.webp'
        path.parent.mkdir(parents=True, exist_ok=True)
        recolor(base, metal).save(path, format='WEBP', quality=78, method=4)


def write_flat(base, folder, kind, values, badge):
    colored = recolor(base, 'e')
    for value in values:
        units, label = stage_units(kind, value)
        path = OUTPUT_DIR / folder / f'{units}.webp'
        path.parent.mkdir(parents=True, exist_ok=True)
        stamp(colored, label, 'e', badge).save(path, format='WEBP', quality=78, method=4)


def main():
    jobs = (
        ('breakthrough.png', 'black', 'breakthrough', 'time', TIME, False),
        ('breakthrough-nf.png', 'black', 'breakthrough-nf', 'time', TIME, True),
        ('speed.png', 'black', 'speed', 'bvs', BVS, False),
        ('speed-nf.png', 'black', 'speed-nf', 'bvs', BVS_NF, True),
        ('mastery.png', 'black', 'mastery', 'stnb', {level: STNB for level in 'bie'}, False),
        ('mastery-nf.png', 'black', 'mastery-nf', 'stnb', {level: STNB for level in 'bie'}, True),
        ('precision.png', 'checker', 'precision', 'thrp', THRP_FL, False),
        ('precision-nf.png', 'checker', 'precision-nf', 'thrp', {level: THRP_NF for level in 'bie'}, True),
    )
    count = 0
    for filename, background, folder, kind, table, badge in jobs:
        base = prepare(TEMPLATE_DIR / filename, background)
        write_levels(base, folder, kind, table, badge)
        count += sum(len(values) for values in table.values())
        print(folder, count)
    three = (
        ('precision-nf-three.png', 'checker', 'precision-nf-three', THREE_NF, True),
        ('precision-three.jpg', 'black', 'precision-three', THREE_FL, False),
    )
    for filename, background, folder, values, badge in three:
        base = prepare(TEMPLATE_DIR / filename, background)
        write_flat(base, folder, 'thrp', values, badge)
        count += len(values)
        print(folder, count)
    once = (
        ('registered.png', 'black', 'registered'),
        ('reviewed.png', 'checker', 'reviewed'),
        ('levels.png', 'black', 'levels'),
        ('levels-nf.png', 'checker', 'levels-nf'),
        ('modes.png', 'black', 'modes'),
        ('saolei.png', 'black', 'saolei'),
    )
    for filename, background, folder in once:
        path = TEMPLATE_DIR / filename
        if not path.exists():
            continue
        destination = OUTPUT_DIR / folder / '1.webp'
        destination.parent.mkdir(parents=True, exist_ok=True)
        prepare(path, background).save(destination, format='WEBP', quality=78, method=4)
        count += 1
        print(folder, count)
    shareholder = TEMPLATE_DIR / 'shareholder.png'
    if shareholder.exists():
        write_shareholder(prepare(shareholder, 'black'))
        count += 3
        print('shareholder', count)
    print('total', count)


if __name__ == '__main__':
    main()
