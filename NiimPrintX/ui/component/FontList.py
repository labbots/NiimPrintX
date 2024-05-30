import platform
import subprocess
import re
from collections import defaultdict
import os
import sys


def fonts():
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
        imagemagick_base_path = os.path.join(base_path, 'imagemagick')
        if platform.system() == "Darwin":
            magick_path = os.path.join(imagemagick_base_path, 'bin', 'magick')
        elif platform.system() == "Windows":
            magick_path = os.path.join(imagemagick_base_path, 'magick.exe')
        elif platform.system() == "Linux":
            magick_path = os.path.join(os.sep, 'usr', 'local', 'bin', 'convert')
        else:
            magick_path = 'magick'
    else:
        if platform.system() == "Linux":
            magick_path = 'convert'
        else:
            magick_path = 'magick'

    # magick_path = 'imagemagick/bin/magick'

    # Path to the local ImageMagick binary within the collected data
    result = subprocess.run([magick_path, '-list', 'font'], stdout=subprocess.PIPE, text=True)
    output = result.stdout
    fonts_details = parse_font_details(output)
    grouped_fonts = group_fonts_by_family(fonts_details)
    return grouped_fonts


def parse_font_details(output):
    font_details = []
    font = {}
    for line in output.splitlines():
        if line.startswith('  Font:'):
            if font:
                font_details.append(font)
                font = {}
            font['name'] = line.split(':')[1].strip()
        elif line.startswith('    family:'):
            font['family'] = line.split(':')[1].strip()
        elif line.startswith('    style:'):
            font['style'] = line.split(':')[1].strip()
        elif line.startswith('    stretch:'):
            font['stretch'] = line.split(':')[1].strip()
        elif line.startswith('    weight:'):
            font['weight'] = line.split(':')[1].strip()
        elif line.startswith('    glyphs:'):
            font['glyphs'] = line.split(':')[1].strip()
    if font:
        font_details.append(font)
    return font_details


def group_fonts_by_family(fonts_details):
    variant_pattern = re.compile(r"-(Bold-Italic|Italic|Bold|Regular|Oblique)$")
    grouped_fonts = defaultdict(lambda: {'family_name': '', 'fonts': {}})

    for font in fonts_details:
        family = font.get('family', 'Unknown')
        if family.startswith('.') or family.startswith('System'):
            continue
        name = font['name']
        variant_match = variant_pattern.search(name)
        variant = variant_match.group(1) if variant_match else 'Other'
        base_name = name[:variant_match.start()] if variant_match else name
        font_name_key = base_name.replace('-', ' ')

        if font_name_key not in grouped_fonts[family]['fonts']:
            grouped_fonts[family]['fonts'][font_name_key] = {
                'name': base_name,
                'main': variant == 'Other',
                'variants': []
            }

        if variant == 'Other':
            grouped_fonts[family]['fonts'][font_name_key]['main'] = True
        else:
            grouped_fonts[family]['fonts'][font_name_key]['variants'].append(variant)

        grouped_fonts[family]['family_name'] = family

    sorted_grouped_fonts = {}
    for family in sorted(grouped_fonts):
        sorted_grouped_fonts[family] = grouped_fonts[family]
        sorted_grouped_fonts[family]['fonts'] = dict(sorted_grouped_fonts[family]['fonts'])

    return sorted_grouped_fonts
