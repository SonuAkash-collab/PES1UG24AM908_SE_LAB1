import math
import pygame

# Procedurally drawn gesture icons. Every shape is built from pygame.draw primitives,
# scaled by `size` (the icon's approximate width/height in pixels) around (cx, cy).

ROCK_OUTLINE = [
    (-0.95, 0.10), (-0.75, -0.45), (-0.30, -0.80), (0.25, -0.85), (0.70, -0.55),
    (0.95, -0.05), (0.80, 0.50), (0.35, 0.80), (-0.25, 0.85), (-0.75, 0.60),
]
ROCK_HIGHLIGHT = [(-0.60, -0.35), (-0.25, -0.65), (0.25, -0.70), (0.55, -0.45), (0.10, -0.35), (-0.35, -0.15)]


def _pt(cx, cy, half, x, y):
    return (int(cx + x * half), int(cy + y * half))


def draw_rock(surface, cx, cy, size):
    half = size / 2
    pts = [_pt(cx, cy, half, x, y) for x, y in ROCK_OUTLINE]
    pygame.draw.polygon(surface, (18, 20, 26), [(x + 3, y + 4) for x, y in pts])
    pygame.draw.polygon(surface, (128, 122, 116), pts)
    pygame.draw.polygon(surface, (162, 156, 149), [_pt(cx, cy, half, x, y) for x, y in ROCK_HIGHLIGHT])
    pygame.draw.polygon(surface, (70, 66, 62), pts, 3)

    crack = [_pt(cx, cy, half, x, y) for x, y in [(0.05, -0.10), (0.30, 0.25), (0.20, 0.55)]]
    pygame.draw.lines(surface, (78, 74, 70), False, crack, 2)
    crack2 = [_pt(cx, cy, half, x, y) for x, y in [(-0.55, 0.20), (-0.25, 0.40)]]
    pygame.draw.lines(surface, (78, 74, 70), False, crack2, 2)


def draw_paper(surface, cx, cy, size):
    w, h = size * 0.62, size * 0.80
    left, top = cx - w / 2, cy - h / 2
    fold = size * 0.18

    body = [(left, top), (left + w - fold, top), (left + w, top + fold), (left + w, top + h), (left, top + h)]
    pygame.draw.polygon(surface, (18, 20, 26), [(x + 3, y + 4) for x, y in body])
    pygame.draw.polygon(surface, (240, 238, 228), body)
    pygame.draw.polygon(surface, (150, 150, 160), body, 2)

    corner = [(left + w - fold, top), (left + w - fold, top + fold), (left + w, top + fold)]
    pygame.draw.polygon(surface, (205, 203, 195), corner)
    pygame.draw.polygon(surface, (150, 150, 160), corner, 2)

    for i in range(5):
        y = top + h * 0.30 + i * h * 0.13
        end = left + w * (0.55 if i == 4 else 0.82)
        pygame.draw.line(surface, (150, 170, 205), (left + w * 0.16, y), (end, y), 2)


def _blade(px, py, tx, ty, width):
    dx, dy = tx - px, ty - py
    length = math.hypot(dx, dy) or 1
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    back = (px - ux * width * 1.6, py - uy * width * 1.6)
    return [(tx, ty), (px + nx * width, py + ny * width), back, (px - nx * width * 0.4, py - ny * width * 0.4)]


def draw_scissors(surface, cx, cy, size):
    half = size / 2
    px, py = cx, cy + 0.05 * half
    handle_r = int(0.27 * half)
    ring_w = max(3, int(0.10 * half))

    # Each blade runs up through the pivot and continues down into the opposite handle
    for side in (-1, 1):
        hx, hy = cx - side * 0.45 * half, cy + 0.58 * half
        pygame.draw.line(surface, (190, 60, 60), (px, py), (hx, hy), max(3, int(0.12 * half)))
        pygame.draw.circle(surface, (205, 65, 65), (int(hx), int(hy)), handle_r, ring_w)

    for side in (-1, 1):
        tip = (cx + side * 0.55 * half, cy - 0.95 * half)
        blade = _blade(px, py, tip[0], tip[1], 0.13 * half)
        pygame.draw.polygon(surface, (205, 210, 220), blade)
        pygame.draw.polygon(surface, (110, 115, 125), blade, 2)

    pygame.draw.circle(surface, (60, 60, 70), (int(px), int(py)), max(3, int(0.08 * half)))


ICON_DRAWERS = {"ROCK": draw_rock, "PAPER": draw_paper, "SCISSORS": draw_scissors}


def draw_icon(surface, name, cx, cy, size):
    drawer = ICON_DRAWERS.get(name)
    if drawer and size > 0:
        drawer(surface, cx, cy, size)
