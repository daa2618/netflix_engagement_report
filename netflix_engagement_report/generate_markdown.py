from pathlib import Path

def main(images_dir:Path):
    markdown_lines = []
    for file in images_dir.iterdir():
        filename = file.name
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp')):
            markdown_lines.append(f"![{filename}]({str(file)})")

    print("\n".join(markdown_lines))

if __name__ == "__main__":
    main(Path(__file__).resolve().parent/"images")
