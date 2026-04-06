# =============================================================================
# extraction.py — PDF text extraction functions
# =============================================================================
# Two extraction approaches for DSA PDFs:
#   1. Docling     → PDF to markdown (batch conversion)
#   2. VLM parsing → Page image extraction via Qwen2.5-VL
#
# Model loading and Qwen interfaces live in models.py
#
# Location: E:\Data\gsoto\analytical\extraction.py
# Usage:    from extraction import batch_docling_to_md
# =============================================================================


# --- Docling imports ---
try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
except ImportError:
    DocumentConverter = None


# =============================================================================
# DOCLING — DSA PDF to Markdown conversion
# =============================================================================

def create_docling_converter(do_ocr=False):
    """Create a Docling DocumentConverter instance."""
    if DocumentConverter is None:
        raise ImportError("Docling not installed. Run: pip install docling")

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = do_ocr

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    return converter


def is_narrative(item):
    """Filter for narrative text items from Docling output."""
    import re

    if item.label not in ('text', 'list_item'):
        return False
    if not hasattr(item, 'text'):
        return False
    t = item.text.strip()
    if len(t) < 50:
        return False
    if re.match(r'^\d+/', t):
        return False
    if t.startswith('Source'):
        return False
    if t.startswith('_'):
        return False
    return True


def extract_narrative_docling(pdf_path, converter=None, do_ocr=False):
    """
    Extract narrative paragraphs from a DSA PDF using Docling.
    Returns list of paragraph strings.
    """
    if converter is None:
        converter = create_docling_converter(do_ocr=do_ocr)

    result = converter.convert(str(pdf_path))

    paragraphs = []
    for item, _ in result.document.iterate_items():
        if is_narrative(item):
            paragraphs.append(item.text.strip())

    return paragraphs


def batch_docling_to_md(input_dir, output_dir, do_ocr=False):
    """
    Batch convert all DSA PDFs to markdown using Docling.
    Removes table lines (|...) from output.
    Skips files that already exist in output_dir.
    """
    from pathlib import Path

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    converter = create_docling_converter(do_ocr=do_ocr)

    pdfs = sorted(input_dir.rglob("*.pdf"))
    print(f"Found {len(pdfs)} PDFs\n")

    for i, pdf_path in enumerate(pdfs):
        name = pdf_path.stem
        out_file = output_dir / f"{name}.md"

        if out_file.exists():
            print(f"[{i+1}/{len(pdfs)}] SKIP (exists): {name}")
            continue

        try:
            print(f"[{i+1}/{len(pdfs)}] Processing: {name}...", end=" ", flush=True)
            result = converter.convert(str(pdf_path))
            md = result.document.export_to_markdown()

            # Remove table lines
            clean_lines = []
            for line in md.split('\n'):
                if line.strip().startswith('|'):
                    continue
                clean_lines.append(line)
            clean_md = '\n'.join(clean_lines)

            out_file.write_text(clean_md, encoding='utf-8')
            print(f"OK ({len(clean_md):,} chars)")

        except Exception as e:
            print(f"ERROR: {e}")

    print(f"\nDone! Output: {output_dir}")


# =============================================================================
# VLM UTILITIES — parsing and bucket validation for page-image extraction
# =============================================================================

VALID_BUCKETS = [
    'summary_abstract', 'background_introduction', 'macroeconomic_assumptions',
    'country_classification', 'coverage', 'external_debt_sustainability',
    'public_debt_sustainability', 'stress_tests_scenarios', 'realism_tools',
    'market_access', 'debt_management', 'monetary_financial_sector',
    'debt_relief_hipc_mdri', 'authorities_views', 'conclusions', 'boilerplate',
]

VLM_PROMPT = """Look at this page from an IMF Debt Sustainability Analysis document.

Your task: extract ALL narrative text from this page.

Narrative text = paragraphs with complete sentences containing policy analysis, economic assessment, descriptions, or recommendations.

DO NOT extract:
- Tables or rows of numbers
- Figure/chart content
- Table titles, figure labels, or column headers
- Footnotes
- Page numbers, headers, footers
- "Approved By" or "Prepared By" blocks

For each paragraph, classify it into ONE bucket:
- summary_abstract: executive summary, abstract, italic introductory text
- background_introduction: background, introduction, debt evolution, debt composition, recent developments
- macroeconomic_assumptions: baseline assumptions, macroeconomic forecast, growth projections, outlook
- country_classification: country classification, composite indicator, CPIA
- coverage: public debt coverage, scope of debt covered
- external_debt_sustainability: external debt analysis, external PPG debt, external indicators
- public_debt_sustainability: public/domestic debt analysis, fiscal sustainability, domestic indicators
- stress_tests_scenarios: stress tests, alternative scenarios, bound tests, sensitivity analysis
- realism_tools: realism of projections, realism tools
- market_access: market financing, gross financing needs, sovereign bonds, eurobonds
- debt_management: debt management strategy, borrowing strategy, concessional borrowing
- monetary_financial_sector: monetary policy, financial sector, banking
- debt_relief_hipc_mdri: HIPC, MDRI, debt relief, completion point
- authorities_views: authorities' views, authorities' response
- conclusions: conclusions, risk rating, overall assessment, staff assessment
- boilerplate: standard disclaimers, generic methodology text

Return ONLY valid JSON in this exact format:
{"blocks": [{"section": "SECTION TITLE FROM THE PAGE", "bucket": "bucket_name", "text": "The complete paragraph text exactly as it appears."}]}

If this page has NO narrative text (only tables/figures), return: {"blocks": []}

CRITICAL:
- Copy every paragraph COMPLETELY — every word, every sentence
- Do NOT summarize, shorten, or paraphrase
- If a paragraph continues from a previous page (starts mid-sentence), extract it
- Bullet points belong with the paragraph that introduces them"""

VLM_FALLBACK_PROMPT = """Extract all narrative paragraphs from this page. Skip tables and figures.
Return JSON: {"blocks": [{"section": "section title", "bucket": "background_introduction", "text": "full paragraph text"}]}
If no narrative text, return: {"blocks": []}"""


def pdf_to_images(pdf_path, dpi=100):
    """Convert every page of a PDF to a PIL Image."""
    import fitz, io
    from PIL import Image

    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap(dpi=dpi)
        images.append(Image.open(io.BytesIO(pix.tobytes("png"))))
    doc.close()
    return images


def parse_vlm_json(raw_text):
    """
    Parse JSON from VLM response. Handles markdown wrappers.
    Returns dict with 'blocks' key, or None.
    """
    import re, json

    text = raw_text.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    text = text.strip()

    # Attempt 1: direct parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and "blocks" in parsed:
            return parsed
        if isinstance(parsed, list):
            return {"blocks": parsed}
        if isinstance(parsed, dict) and "sections" in parsed:
            blocks = []
            for s in parsed["sections"]:
                for p in s.get("paragraphs", []):
                    blocks.append({
                        "section": s.get("section_title", ""),
                        "bucket": s.get("bucket", "boilerplate"),
                        "text": p.get("text", "")
                    })
            return {"blocks": blocks}
        return {"blocks": []}
    except json.JSONDecodeError:
        pass

    # Attempt 2: find JSON in text
    match = re.search(r'\{[\s\S]*"blocks"\s*:\s*\[', text)
    if match:
        start = match.start()
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i+1])
                    except json.JSONDecodeError:
                        break

    # Attempt 3: fix trailing commas
    fixed = re.sub(r',\s*([\]\}])', r'\1', text)
    try:
        parsed = json.loads(fixed)
        if isinstance(parsed, dict) and "blocks" in parsed:
            return parsed
    except json.JSONDecodeError:
        pass

    return None


def validate_bucket(bucket_str):
    """Map any bucket string to a valid bucket name."""
    if not bucket_str:
        return 'boilerplate'
    if bucket_str in VALID_BUCKETS:
        return bucket_str

    b = bucket_str.lower().strip().replace(" ", "_").replace("-", "_")
    if b in VALID_BUCKETS:
        return b

    rules = [
        ('abstract', 'summary_abstract'), ('summary', 'summary_abstract'),
        ('background', 'background_introduction'), ('introduction', 'background_introduction'),
        ('evolution', 'background_introduction'), ('composition', 'background_introduction'),
        ('recent_dev', 'background_introduction'),
        ('macroeconomic', 'macroeconomic_assumptions'), ('assumption', 'macroeconomic_assumptions'),
        ('forecast', 'macroeconomic_assumptions'), ('outlook', 'macroeconomic_assumptions'),
        ('classif', 'country_classification'), ('cpia', 'country_classification'),
        ('composite', 'country_classification'),
        ('coverage', 'coverage'),
        ('external', 'external_debt_sustainability'),
        ('public_debt', 'public_debt_sustainability'), ('fiscal', 'public_debt_sustainability'),
        ('domestic', 'public_debt_sustainability'),
        ('stress', 'stress_tests_scenarios'), ('scenario', 'stress_tests_scenarios'),
        ('bound', 'stress_tests_scenarios'), ('sensitiv', 'stress_tests_scenarios'),
        ('threshold', 'stress_tests_scenarios'),
        ('realism', 'realism_tools'),
        ('market', 'market_access'), ('financing_need', 'market_access'),
        ('debt_manage', 'debt_management'), ('borrowing', 'debt_management'),
        ('concessional', 'debt_management'),
        ('monetary', 'monetary_financial_sector'), ('financial_sector', 'monetary_financial_sector'),
        ('banking', 'monetary_financial_sector'),
        ('hipc', 'debt_relief_hipc_mdri'), ('mdri', 'debt_relief_hipc_mdri'),
        ('debt_relief', 'debt_relief_hipc_mdri'), ('completion_point', 'debt_relief_hipc_mdri'),
        ('authorit', 'authorities_views'),
        ('conclusion', 'conclusions'), ('risk_rating', 'conclusions'),
        ('staff_assess', 'conclusions'), ('overall', 'conclusions'),
    ]
    for pattern, valid in rules:
        if pattern in b:
            return valid
    return 'boilerplate'