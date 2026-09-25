import sys
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import markdown

def convert_md_to_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    html_content = markdown.markdown(md_text, extensions=['extra', 'codehilite'])
    
    html_page = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                line-height: 1.6;
                padding: 40px;
                max-width: 800px;
                margin: 0 auto;
                color: #333;
            }}
            h1, h2, h3, h4 {{
                color: #24292e;
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
            }}
            h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
            h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }}
            p {{ margin-top: 0; margin-bottom: 16px; }}
            a {{ color: #0366d6; text-decoration: none; }}
            ul, ol {{ padding-left: 2em; margin-bottom: 16px; }}
            code {{ font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; font-size: 85%; background-color: rgba(27,31,35,.05); border-radius: 3px; padding: .2em .4em; }}
            pre {{ background-color: #f6f8fa; border-radius: 3px; padding: 16px; overflow: auto; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_page)
        page.pdf(path=pdf_path, format="A4", margin={"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"})
        browser.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python md_to_pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    
    md_path = sys.argv[1]
    pdf_path = sys.argv[2]
    
    if not os.path.exists(md_path):
        print(f"Error: {md_path} does not exist.")
        sys.exit(1)
        
    convert_md_to_pdf(md_path, pdf_path)
    print(f"Successfully created {pdf_path}")
