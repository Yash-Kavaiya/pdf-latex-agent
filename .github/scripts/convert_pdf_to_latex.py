#!/usr/bin/env python3
import os
import sys
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_nvidia_ai_endpoints import ChatNVIDIA

def page_to_latex(llm, page_content: str) -> str:
    """Convert a single page content to LaTeX."""
    prompt = """You are a LaTeX expert. Convert ONLY this PDF page content to valid LaTeX code.
Preserve:
- Structure (sections, lists as itemize/enumerate)
- Tables (tabular/tabularx)
- Math/formulas (align/equation)
- Figures (figure with placeholder)
- Bold/italics (\\textbf/\\textit)
- Special characters escaped properly

Output ONLY pure LaTeX code, no markdown, no explanations.

Content:
{page_content}""".format(page_content=page_content[:3000])
    
    response = llm.invoke(prompt)
    return response.content.strip()

def convert_pdf_to_latex(pdf_path: str, llm) -> str:
    """Convert entire PDF to LaTeX document."""
    loader = PyMuPDFLoader(pdf_path)
    pages = loader.load()
    
    latex_parts = []
    for i, page in enumerate(pages):
        print(f"  Converting page {i+1}/{len(pages)}...")
        latex_content = page_to_latex(llm, page.page_content)
        latex_parts.append(latex_content)
    
    tex_content = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,amsfonts,amsthm}
\usepackage{geometry,graphicx,tabularx,booktabs,float,listings}
\usepackage{hyperref}
\geometry{margin=1in}

\begin{document}

""" + "\n\n\\newpage\n\n".join(latex_parts) + r"""

\end{document}
"""
    return tex_content

def main():
    if len(sys.argv) < 2:
        print("No PDF files provided")
        sys.exit(0)
    
    # Get PDF files from command line (space-separated)
    pdf_files = sys.argv[1].split()
    
    if not pdf_files:
        print("No PDF files to process")
        sys.exit(0)
    
    # Initialize LLM
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        print("ERROR: NVIDIA_API_KEY not set")
        sys.exit(1)
    
    llm = ChatNVIDIA(
        model="mistralai/mistral-large-3-675b-instruct-2512",
        api_key=api_key
    )
    
    for pdf_path in pdf_files:
        if not os.path.exists(pdf_path):
            print(f"⚠️ File not found: {pdf_path}")
            continue
        
        print(f"📄 Processing: {pdf_path}")
        
        try:
            tex_content = convert_pdf_to_latex(pdf_path, llm)
            
            # Save .tex file (same location, different extension)
            tex_path = os.path.splitext(pdf_path)[0] + ".tex"
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_content)
            
            print(f"✅ Generated: {tex_path}")
        
        except Exception as e:
            print(f"❌ Error processing {pdf_path}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
```

## Step 3: Add Your API Key as Secret

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `NVIDIA_API_KEY`
5. Value: `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`

## Folder Structure
```
your-repo/
├── .github/
│   ├── workflows/
│   │   └── pdf-to-latex.yml
│   └── scripts/
│       └── convert_pdf_to_latex.py
├── docs/
│   └── example.pdf  ← Push this, it converts & deletes
└── README.md
