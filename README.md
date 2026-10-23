# PDF text to pure Black

A script designed to force all text, vector graphics, and/or raster elements in a PDF into **pure solid black** (`#000000`).

## Why

I was using my Brother HL-1110 (a budget monochrome laser printer), and PDF text wasn't printing as sharply as I expected. I tested printing from Adobe Acrobat and Chrome, and then tried writing text in Word and Excel—which printed perfectly clear. After a few hours of troubleshooting, I realized the issue that the PDF text was dark grey (#202020) instead of solid black (#000000). To fix this, I wrote a script to convert all text and vector graphics to pure black, and now it prints sharp.


## Features

- **Selective Conversion**: Choose whether to recolor **Text**, **Vector graphics** (lines, tables, borders), and/or **Raster Images** independently.
- **Thresholding**: Preserves white backgrounds while forcing anything darker than the threshold (`white_above=0.85`) to solid black.
- **Form XObject Support**: Recurses through reusable sub-components (headers, repeated table templates, logos).
- **Image Processing**: Converts raster images/banners into solid black or transparent white.


require pikepdf

```bash
pip install pikepdf
```

```python
# file paths
input_file = "1.pdf"
output_file = "1_black.pdf"

# >= 0.85 becomes white, < 0.85 becomes black
white_above = 0.85

# selective conversion
convert_text = True       # Convert text color to solid black
convert_vector = True     # Convert vector paths, tables, and borders
convert_images = True     # Convert raster images/banners

# image conversion ('black' for solid black, 'white' to clear backgrounds)
image_mode = "black"

# run
convert_to_black(
    inp_path=input_file,
    out_path=output_file,
    white_above=white_above,
    convert_text=convert_text,
    convert_vector=convert_vector,
    convert_images=convert_images,
    image_mode=image_mode
)
```
