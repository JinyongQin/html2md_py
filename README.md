# html2md_py

## dependencies
- beautifulsoup4
- lxml

```bash
pip install beautifulsoup4 lxml
```

## htm2md.py

Convert a HTML file to Markdown, preserving the structure and formatting of the original document.

### Usage

```bash
python htm2md.py input.html output.md
```
**example:**
```bash
python htm2md.py input.html output.md
```
> this will convert the input.html file to output.md

## htms2mds.py

Convert some HTML files in a folder to Markdown

### Usage

```bash
python htms2mds.py input_folder output_folder [number_of_files]
```

**example:**

```bash
python htms2mds.py input_folder output_folder 5
```

> this will convert the first 5 HTML files in the input_folder to Markdown files in the output_folder
