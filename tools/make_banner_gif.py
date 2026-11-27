"""Animated campaign GIF for itesmedia.am from the poster PDF.
py -3.12 tools/make_banner_gif.py  ->  assets/banner-ruben.gif"""
import io, pymupdf
from PIL import Image

PDF = r"C:\Users\user\Desktop\ruben for mayor\editor\poster-intro\public\poster.pdf"
W, H = 600, 300
d = pymupdf.open(PDF); p = d[0]
z = W / p.rect.width
poster = Image.open(io.BytesIO(p.get_pixmap(matrix=pymupdf.Matrix(z, z)).tobytes("png"))).convert("RGB")
s = W / 2000  # crop boxes measured on a 2000x1000 preview
box = lambda x0, y0, x1, y1: tuple(round(v * s) for v in (x0, y0, x1, y1))
BG = poster.getpixel((5, 5))
NAME, TWO, RIGHT = box(150, 90, 905, 530), box(150, 690, 340, 910), box(880, 50, 2000, 1000)
name, two, right = (poster.crop(b) for b in (NAME, TWO, RIGHT))
# the name's last letter reaches into the photo crop: blank it there
right.paste(BG, (0, 0, NAME[2] - RIGHT[0] + 2, NAME[3] - RIGHT[1]))

ease = lambda t: 1 - (1 - max(0, min(1, t))) ** 3
def frame(t):  # t in seconds
    im = Image.new("RGB", (W, H), BG)
    a = ease(t / 0.5)                      # photo slides in from the right
    im.paste(right, (RIGHT[0] + round((1 - a) * (W - RIGHT[0])), RIGHT[1]))
    b = ease((t - 0.35) / 0.45)            # name drops from above
    if b > 0:
        im.paste(name, (NAME[0], NAME[1] - round((1 - b) * 140)))
    c = (t - 0.8) / 0.3                    # "2" slams in (scale 1.8 -> 1)
    if c > 0:
        k = 1 + 0.8 * (1 - ease(c))
        tw = two.resize((round(two.width * k), round(two.height * k)), Image.LANCZOS)
        cx, cy = (TWO[0] + TWO[2]) // 2, (TWO[1] + TWO[3]) // 2
        im.paste(tw, (cx - tw.width // 2, cy - tw.height // 2))
    return im

fps = 20
times = [i / fps for i in range(int(1.2 * fps))]
frames = [frame(t) for t in times]
durs = [1000 // fps] * len(frames)
# hold, then a quick "pulse" of the 2 twice
for _ in range(2):
    frames.append(frame(5)); durs.append(900)
    for k in (1.12, 1.0):
        im = frame(5); tw = two.resize((round(two.width * k), round(two.height * k)), Image.LANCZOS)
        cx, cy = (TWO[0] + TWO[2]) // 2, (TWO[1] + TWO[3]) // 2
        im.paste(Image.new("RGB", (round(two.width * 1.15), round(two.height * 1.15)), BG), (cx - round(two.width * .575), cy - round(two.height * .575)))
        im.paste(tw, (cx - tw.width // 2, cy - tw.height // 2)); frames.append(im); durs.append(90)
frames.append(frame(5)); durs.append(1600)

pal = frames[-1].quantize(colors=128, method=Image.Quantize.MEDIANCUT)
q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
out = r"C:\Users\user\Desktop\ruben for mayor\itesmedia-site\assets\banner-ruben.gif"
q[0].save(out, save_all=True, append_images=q[1:], duration=durs, loop=0, optimize=True, disposal=1)
print(len(q), "frames", sum(durs), "ms")
