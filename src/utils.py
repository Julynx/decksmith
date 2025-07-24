from PIL import Image, ImageDraw, ImageFont


def get_wrapped_text(text: str, font: ImageFont.ImageFont, line_length: int):
    lines = [""]
    for word in text.split():
        line = f"{lines[-1]} {word}".strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)
    return "\n".join(lines)
