# Luca's handwriting database

Source: "Note Oct 9, 2026" (alphabet, numbers, symbols sheet), scanned at 150 dpi.
Each character has about 7 to 15 real samples cut from that sheet. The renderer picks a random
sample each time and adds small rotation, size and baseline jitter.

Sources: Oct 9 alphabet/number sheet plus Oct 9 11:25 AM punctuation sheet.
Covered: A-Z, a-z, 0-9, # & - _ + . ( ) [ ] ! ? $ cent , : ; ' * = < > <= >= % /
Synthesized (not written yet, drawn as simple strokes): double quote
Not yet extracted from the sheet: square root, pi, braces, dy/dx, e^x.

Use:
    python3 fill_pdf.py input.pdf spec.json output.pdf
spec.json: [{"page":1,"x":104,"y":132.5,"text":"Luca Abruzzo","size":13,"width":300}]
x, y in PDF points from the top-left; y is the baseline of the first line; size is capital height in points;
width (optional) wraps text. Default ink is his red pen; set "color":[r,g,b] to change.
