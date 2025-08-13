from pathlib import Path

def main(images_dir:Path, base:Path):
    markdown_lines = []
    for file in images_dir.iterdir():
        filename = file.name
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp')):
            relative_path = file.relative_to(base).as_posix()
            markdown_lines.append(f"![{file.stem.replace("_", " ").title()}]({relative_path})")

    print("\n".join(markdown_lines))

if __name__ == "__main__":
    main(Path(__file__).parent/"images", 
         Path(r"c:\Users\DevAnbarasu\Documents\GitHub\netflix_engagement_report")
         )
