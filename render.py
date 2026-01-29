from pdf2image import convert_from_path

pages = convert_from_path("input.pdf", dpi=300)
pages[0].save("page1_preview.png")
print("Gespeichert: page1_preview.png")
