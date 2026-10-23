import os
import pikepdf
from pikepdf import Operator, Name

FILL_OPS = {'g', 'rg', 'k', 'sc', 'scn'}
STROKE_OPS = {'G', 'RG', 'K', 'SC', 'SCN'}

def lum(op, args):
    v = [float(a) for a in args if isinstance(a, (int, float)) or hasattr(a, '__float__')]
    if op in ('g', 'G'):
        return v[0]
    if op in ('rg', 'RG'):
        return 0.299 * v[0] + 0.587 * v[1] + 0.114 * v[2]
    if op in ('k', 'K'):
        c, m, y, k = v
        r, g, b = (1 - c) * (1 - k), (1 - m) * (1 - k), (1 - y) * (1 - k)
        return 0.299 * r + 0.587 * g + 0.114 * b
    return None

def recolor(instructions, thr=0.85, convert_text=True, convert_vector=True):
    out = []
    in_text = False
    
    for operands, operator in instructions:
        op = str(operator)
        if op == 'BT':
            in_text = True
            out.append((operands, operator))
            continue
        elif op == 'ET':
            in_text = False
            out.append((operands, operator))
            continue
            
        if op in FILL_OPS | STROKE_OPS:
            should_convert = (in_text and convert_text) or (not in_text and convert_vector)
            if should_convert:
                L = lum(op, operands) if op in ('g', 'G', 'rg', 'RG', 'k', 'K') else None
                white = (L is not None and L >= thr)
                val = 1 if white else 0
                out.append(([val], Operator('g' if op in FILL_OPS else 'G')))
            else:
                out.append((operands, operator))
        else:
            out.append((operands, operator))

    return out

def process_stream(obj, thr, convert_text=True, convert_vector=True):
    ins = pikepdf.parse_content_stream(obj)
    new_ins = recolor(ins, thr, convert_text=convert_text, convert_vector=convert_vector)
    obj.write(pikepdf.unparse_content_stream(new_ins))

def process_image(xo, mode="black"):
    xo['/ColorSpace'] = Name('/DeviceGray')
    xo['/BitsPerComponent'] = 8
    xo['/Width'] = 1
    xo['/Height'] = 1
    for key in ['/Filter', '/DecodeParms', '/SMask', '/Mask']:
        if key in xo:
            del xo[key]
    val = b'\x00' if mode == "black" else b'\xff'
    xo.write(val)

def walk_resources(res, thr, pdf, seen, convert_text=True, convert_vector=True, convert_images=True, image_mode="black"):
    if res is None or '/XObject' not in res:
        return
    for _, xo in res.XObject.items():
        subtype = xo.get('/Subtype')
        if subtype == '/Form' and xo.objgen not in seen:
            seen.add(xo.objgen)
            if convert_text or convert_vector:
                process_stream(xo, thr, convert_text, convert_vector)
            walk_resources(xo.get('/Resources'), thr, pdf, seen, convert_text, convert_vector, convert_images, image_mode)
        elif subtype == '/Image' and convert_images:
            if xo.objgen != (0, 0):
                if xo.objgen in seen:
                    continue
                seen.add(xo.objgen)
            process_image(xo, mode=image_mode)
    
def convert_to_black(inp_path, out_path, white_above=0.85, convert_text=True, convert_vector=True, convert_images=True, image_mode="black"):
    if not os.path.exists(inp_path):
        raise FileNotFoundError(f"Input file not found: {inp_path}")
        
    pdf = pikepdf.open(inp_path)
    seen = set()
    total_pages = len(pdf.pages)
    
    for i, page in enumerate(pdf.pages, 1):
        if '/Contents' in page.obj and (convert_text or convert_vector):
            page.contents_coalesce()
            process_stream(page.obj.Contents, white_above, convert_text, convert_vector)
        walk_resources(
            page.obj.get('/Resources'),
            white_above,
            pdf,
            seen,
            convert_text=convert_text,
            convert_vector=convert_vector,
            convert_images=convert_images,
            image_mode=image_mode
        )
            
    pdf.save(out_path)

def main():
    input_file = "1.pdf"
    output_file = "1_black.pdf"

    white_above = 0.85

    convert_text = True    # text color to black/white
    convert_vector = True  # vector paths, lines, and shapes to black/white
    convert_images = False  # Convert raster images

    image_mode = "black"

    convert_to_black(
        inp_path=input_file,
        out_path=output_file,
        white_above=white_above,
        convert_text=convert_text,
        convert_vector=convert_vector,
        convert_images=convert_images,
        image_mode=image_mode
    )

if __name__ == "__main__":
    main()