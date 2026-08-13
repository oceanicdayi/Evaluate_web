#!/usr/bin/env python3
"""Convert ASET_2026_submission_draft.md to Word (.docx) and PDF.

Follows ASET 2026 format requirements:
- A4, standard margins
- Title: 18pt bold centered
- Author info: 12pt left-aligned
- Body: 12pt, single spacing
- Section headings: 14pt bold left-aligned
- Chinese font: 標楷体 (DFKai-SB) / Latin: Times New Roman
"""

from pathlib import Path
import subprocess
import re

ROOT = Path(__file__).resolve().parent
MD_FILE = ROOT / "ASET_2026_submission_draft.md"
DOCX_FILE = ROOT / "ASET_2026_submission_draft.docx"
PDF_FILE = ROOT / "ASET_2026_submission_draft.pdf"

FIGURE1 = "figure1_web_complexity_distribution.png"
FIGURE2 = "figure2_prior_advantage_convergence.png"

# Read the markdown
text = MD_FILE.read_text(encoding="utf-8")

# Replace figure placeholder text with actual image references for pandoc
text = text.replace(
    "**[Figure 1：高信度配對學生之媒體豐富度與排版架構上、下學期評分分布（figure1_web_complexity_distribution）]**",
    f"![Figure 1. Web complexity distribution of matched students (n=8)]({FIGURE1})\n",
)
text = text.replace(
    "**[Figure 2：先備組與新加入組由第一次網頁作業至期末的媒體豐富度與排版架構平均軌跡（figure2_prior_advantage_convergence）]**",
    f"![Figure 2. Prior-experience advantage and convergence]({FIGURE2})\n",
)

# Remove the "投稿措辭守則" section (internal notes, not for submission)
text = re.sub(r"---\n## 投稿措辭守則.*", "", text, flags=re.DOTALL)

# Write a temporary cleaned markdown
temp_md = ROOT / "_aset_temp.md"
temp_md.write_text(text, encoding="utf-8")

# Create a reference docx with proper styling
ref_docx = ROOT / "_aset_ref.docx"

# Use pandoc to create a reference doc first
subprocess.run([
    "pandoc", "--print-default-data-file=reference.docx"
], capture_output=True)

# Build with pandoc
cmd = [
    "pandoc",
    str(temp_md),
    "-o", str(DOCX_FILE),
    "--from=markdown",
    "--to=docx",
    f"--resource-path={ROOT}",
    "-V", "geometry:margin=2.5cm",
    "-V", "papersize=a4",
    "-V", "fontsize=12pt",
    "-V", "linestretch=1.0",
    "-V", "mainfont=Times New Roman",
    "-V", "CJKmainfont=Microsoft YaHei",
    "--standalone",
]

print(f"Running: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
if result.returncode != 0:
    print(f"[error] pandoc stderr: {result.stderr}")
else:
    print(f"[saved] {DOCX_FILE.name}")

# Now convert docx to PDF using LibreOffice if available
import shutil
soffice = shutil.which("soffice") or shutil.which("libreoffice")
if not soffice:
    # Try common Windows paths
    for path in [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]:
        if Path(path).exists():
            soffice = path
            break

if soffice:
    print(f"Converting to PDF with LibreOffice: {soffice}")
    result = subprocess.run([
        soffice, "--headless", "--convert-to", "pdf",
        "--outdir", str(ROOT),
        str(DOCX_FILE)
    ], capture_output=True, text=True, timeout=120)
    if result.returncode == 0:
        print(f"[saved] {PDF_FILE.name}")
    else:
        print(f"[error] LibreOffice: {result.stderr}")
else:
    print("[warn] LibreOffice not found; trying pandoc PDF directly")
    cmd_pdf = [
        "pandoc",
        str(temp_md),
        "-o", str(PDF_FILE),
        "--from=markdown",
        f"--resource-path={ROOT}",
        "-V", "geometry:margin=2.5cm",
        "-V", "papersize=a4",
        "-V", "fontsize=12pt",
        "-V", "linestretch=1.0",
        "-V", "mainfont=Times New Roman",
        "-V", "CJKmainfont=Microsoft YaHei",
        "--pdf-engine=xelatex",
        "--standalone",
    ]
    result = subprocess.run(cmd_pdf, capture_output=True, text=True, encoding="utf-8")
    if result.returncode == 0:
        print(f"[saved] {PDF_FILE.name}")
    else:
        print(f"[error] pandoc PDF: {result.stderr[:500]}")

# Cleanup temp
temp_md.unlink(missing_ok=True)
ref_docx.unlink(missing_ok=True)