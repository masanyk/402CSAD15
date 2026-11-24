"""
Малює осцилограму з VCD-файлу GHDL у SVG (без сторонніх бібліотек).
Використання:
  python vcd2svg.py wave.vcd out.svg t0_ns t1_ns "Заголовок"
Відображаються сигнали верхнього рівня tb_spi; шини — шістнадцятковими значеннями.
"""
import sys
from xml.sax.saxutils import escape

SIGNALS = [  # (ім'я у VCD, підпис)
    ("clk", "CLK"), ("rst", "RESET"), ("start", "start"), ("m_txd", "tx_data (M)"),
    ("busy", "busy"), ("ss_n", "SS_N"), ("sclk", "SCLK"), ("mosi", "MOSI"), ("miso", "MISO"),
    ("m_rxv", "rx_valid (M)"), ("m_rxd", "rx_data (M)"), ("s_rxv", "rx_valid (S)"), ("s_rxd", "rx_data (S)"),
]


def parse(path):
    ids, waves, scope, t = {}, {}, [], 0
    timescale_fs = 1
    with open(path) as fh:
        lines = iter(fh.read().split("\n"))
        for line in lines:
            tok = line.split()
            if not tok:
                continue
            if tok[0] == "$timescale":
                spec = " ".join(tok[1:]).replace("$end", "").strip() or next(lines).strip()
                num = int("".join(c for c in spec if c.isdigit()) or 1)
                unit = spec.lstrip("0123456789").strip()
                timescale_fs = num * {"fs": 1, "ps": 1000, "ns": 10**6, "us": 10**9}[unit]
            elif tok[0] == "$scope":
                scope.append(tok[2])
            elif tok[0] == "$upscope":
                scope.pop()
            elif tok[0] == "$var" and scope == ["tb_spi"]:
                name = tok[4].split("[")[0]
                ids[tok[3]] = name
                waves[name] = {"width": int(tok[2]), "ch": []}
            elif tok[0].startswith("#"):
                t = int(tok[0][1:]) * timescale_fs / 1e6   # -> нс
            elif tok[0][0] in "01xzuXZU" and len(tok) == 1 and tok[0][1:] in ids:
                waves[ids[tok[0][1:]]]["ch"].append((t, tok[0][0]))
            elif tok[0][0] in "bB" and len(tok) == 2 and tok[1] in ids:
                waves[ids[tok[1]]]["ch"].append((t, tok[0][1:]))
    return waves


def value_at(ch, t):
    v = None
    for tt, val in ch:
        if tt > t:
            break
        v = val
    return v


def to_hex(bits, width):
    if bits is None or any(c not in "01" for c in bits):
        return "X"
    return f"{int(bits, 2):0{(width + 3) // 4}X}"


def render(waves, t0, t1, title, out):
    LW, RW, ROW, H = 120, 1080, 30, 18
    W = LW + RW + 20
    Ht = 50 + ROW * len(SIGNALS) + 30
    x = lambda t: LW + (t - t0) / (t1 - t0) * RW
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Ht}" font-family="Consolas, monospace" font-size="12">',
         f'<rect width="{W}" height="{Ht}" fill="#ffffff"/>',
         f'<text x="10" y="22" font-size="15" font-family="Segoe UI, Arial" font-weight="bold">{escape(title)}</text>']
    # сітка часу
    span = t1 - t0
    step = next(s for s in (10, 20, 50, 100, 200, 500, 1000, 2000, 5000) if span / s <= 14)
    tt = (int(t0 // step) + 1) * step
    while tt < t1:
        o.append(f'<line x1="{x(tt):.1f}" y1="38" x2="{x(tt):.1f}" y2="{Ht - 24}" stroke="#e4e4e4"/>')
        o.append(f'<text x="{x(tt):.1f}" y="{Ht - 8}" text-anchor="middle" fill="#666">{tt:g} нс</text>')
        tt += step
    for i, (name, label) in enumerate(SIGNALS):
        w = waves[name]
        y0 = 50 + i * ROW
        yh, yl = y0, y0 + H
        o.append(f'<text x="8" y="{y0 + 13}" fill="#222">{escape(label)}</text>')
        pts = [(t0, value_at(w["ch"], t0))] + [(t, v) for t, v in w["ch"] if t0 < t < t1] + [(t1, None)]
        col = "#1f6feb" if name in ("sclk", "mosi", "miso", "ss_n") else "#2da44e" if name == "clk" else "#444"
        if w["width"] == 1:
            path, prev_y = [], None
            for (ta, va), (tb, _) in zip(pts, pts[1:]):
                yv = yh if va == "1" else yl if va == "0" else (yh + yl) / 2
                if prev_y is not None and prev_y != yv:
                    path.append(f"L{x(ta):.1f},{yv:.1f}")
                path.append(("M" if prev_y is None else "L") + f"{x(ta):.1f},{yv:.1f} L{x(tb):.1f},{yv:.1f}")
                prev_y = yv
            o.append(f'<path d="{" ".join(path)}" fill="none" stroke="{col}" stroke-width="1.6"/>')
        else:
            for (ta, va), (tb, _) in zip(pts, pts[1:]):
                xa, xb = x(ta), x(tb)
                d = min(3, (xb - xa) / 2)
                o.append(f'<path d="M{xa:.1f},{(yh + yl) / 2} L{xa + d:.1f},{yh} L{xb - d:.1f},{yh} L{xb:.1f},{(yh + yl) / 2} '
                         f'L{xb - d:.1f},{yl} L{xa + d:.1f},{yl} Z" fill="#fff8e1" stroke="#b08800" stroke-width="1"/>')
                if xb - xa > 22:
                    o.append(f'<text x="{(xa + xb) / 2:.1f}" y="{y0 + 13}" text-anchor="middle">{to_hex(va, w["width"])}</text>')
    o.append("</svg>")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(o))


if __name__ == "__main__":
    vcd, out, t0, t1, title = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    render(parse(vcd), t0, t1, title, out)
    print("written", out)
