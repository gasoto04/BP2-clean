# =============================================================================
# search.py — Keyword search engine for document corpora
# =============================================================================
# Core search functions for matching topic keywords against text documents.
# Works with TXT files (DSA whole-document), Markdown (AIV/Programs),
# and structured JSON (legacy DSA pipeline).
#
# Location: E:\Data\gsoto\analytical\search.py
# Usage:    from search import build_mentions_dsa_txt, build_mentions_aiv
# =============================================================================

import re
import pandas as pd
from pathlib import Path
from tqdm import tqdm


# =============================================================================
# CORE — normalize and count
# =============================================================================

def _normalize(text):
    """Lowercase + normalize hyphens/dashes to spaces."""
    return text.lower().replace('-', ' ').replace('\u2013', ' ').replace('\u2014', ' ')


def _count_keyword(text_norm, kw_norm):
    """Count keyword matches using word boundaries."""
    pattern = r'\b' + re.escape(kw_norm) + r'\b'
    return len(re.findall(pattern, text_norm))


# =============================================================================
# SEARCH: TXT files (whole-document, DSA)
# =============================================================================

def search_txt(filepath, topics, doc_meta=None):
    """
    Run keyword search on a TXT file.
    Reads entire file as one string — no block splitting.
    Returns dict with has_, count_ per topic.
    """
    filepath = Path(filepath)
    try:
        text = filepath.read_text(encoding='utf-8')
    except:
        text = filepath.read_text(encoding='latin-1')

    row = doc_meta.copy() if doc_meta else {}
    row['n_chars'] = len(text)
    row['word_count'] = len(text.split())


    text_norm = _normalize(text)

    for topic_name, topic_cfg in topics.items():
        keywords_norm = [_normalize(kw) for kw in topic_cfg['keywords']]
        hit_count = 0
        for kw in keywords_norm:
            hit_count += _count_keyword(text_norm, kw)
        row[f'has_{topic_name}'] = 1 if hit_count > 0 else 0
        row[f'count_{topic_name}'] = hit_count

    return row


def build_mentions_dsa_txt(txt_dir, df_dsa, topics):
    """
    Run keyword search on DSA TXT files.
    Uses df_dsa to get metadata (country, year, ifs, doc_type).

    TXT naming:  "Country_Country_Year_Month.txt"
    df_dsa naming: filename = "Country_Year_Month.pdf"
    Mapping: expected_txt_stem = country + "_" + dsa_stem
    """
    txt_dir = Path(txt_dir)

    # Build mapping: expected TXT stem → metadata from df_dsa
    meta_map = {}
    for _, r in df_dsa.iterrows():
        stem = r['filename'].replace('.pdf', '')
        expected_txt_stem = r['country'] + '_' + stem
        meta_map[expected_txt_stem] = {
            'filename': stem,
            'country': r['country'],
            'year': r['year'],
            'ifs': r.get('ifs', None),
            'doc_type': 'DSA',
        }

    # Find TXT files
    txt_files = sorted(txt_dir.glob('*.txt'))
    print(f"DSA (TXT): Found {len(txt_files)} TXT files, {len(meta_map)} entries in df_dsa")

    # Match and search
    rows = []
    skipped = []
    for tf in tqdm(txt_files, desc='DSA (TXT)'):
        if tf.stem not in meta_map:
            skipped.append(tf.name)
            continue

        meta = meta_map[tf.stem]

        try:
            result = search_txt(tf, topics, doc_meta=meta)
            rows.append(result)
        except Exception as e:
            print(f"\n⚠ Error: {tf.name} — {e}")
            continue

    df = pd.DataFrame(rows)

    # Report skipped
    if skipped:
        print(f"\n⚠ {len(skipped)} TXT files not matched to df_dsa:")
        for s in skipped[:10]:
            print(f"    {s}")
        if len(skipped) > 10:
            print(f"    ... and {len(skipped) - 10} more")

    # Summary
    _print_search_summary("DSA (TXT)", df, topics)

    return df


# =============================================================================
# SEARCH: Markdown files (AIV, Programs)
# =============================================================================

def search_markdown(filepath, topics, doc_meta=None):
    """
    Search one Markdown file for keyword mentions.
    Splits on double newlines to get paragraphs.
    doc_meta: dict with pre-computed metadata (filename, country, year, ifs, etc.)
    """
    filepath = Path(filepath)
    try:
        text = filepath.read_text(encoding='utf-8')
    except:
        try:
            text = filepath.read_text(encoding='latin-1', errors='ignore')
        except:
            print(f"⚠ Cannot read: {filepath}")
            row = doc_meta.copy() if doc_meta else {}
            row['n_paragraphs'] = 0
            row['n_chars'] = 0
            for topic_name in topics:
                row[f'has_{topic_name}'] = 0
                row[f'count_{topic_name}'] = 0
                row[f'paras_{topic_name}'] = 0
            return row

    raw_paras = re.split(r'\n{2,}', text)
    all_paras = [p.strip() for p in raw_paras if p.strip() and len(p.strip()) > 20]

    row = doc_meta.copy() if doc_meta else {}
    row['n_paragraphs'] = len(all_paras)
    row['n_chars'] = len(text)
    row['word_count'] = len(text.split())

    paras_norm = [_normalize(p) for p in all_paras]

    for topic_name, topic_cfg in topics.items():
        keywords_norm = [_normalize(kw) for kw in topic_cfg['keywords']]
        hit_count = 0
        para_count = 0
        for pn in paras_norm:
            para_has_hit = False
            for kw in keywords_norm:
                n = _count_keyword(pn, kw)
                hit_count += n
                if n > 0:
                    para_has_hit = True
            if para_has_hit:
                para_count += 1
        row[f'has_{topic_name}'] = 1 if hit_count > 0 else 0
        row[f'count_{topic_name}'] = hit_count
        row[f'paras_{topic_name}'] = para_count

    return row


def build_mentions_aiv(df_aiv, topics):
    """Run keyword search on AIV markdown files."""
    print(f"AIV: Searching {len(df_aiv)} files...")
    rows = []
    for _, doc_row in tqdm(df_aiv.iterrows(), total=len(df_aiv), desc='AIV'):
        meta = {
            'doc_type': 'AIV',
            'filename': doc_row['filename'],
            'country': doc_row.get('country_name', ''),
            'ifs': doc_row.get('ifs'),
            'year': doc_row.get('year'),
            'region': doc_row.get('region'),
        }
        rows.append(search_markdown(doc_row['filepath'], topics, meta))

    df = pd.DataFrame(rows)
    _print_search_summary("AIV", df, topics)
    return df


def build_mentions_programs(df_programs, topics):
    """Run keyword search on Program markdown files."""
    print(f"Programs: Searching {len(df_programs)} files...")
    rows = []
    for _, doc_row in tqdm(df_programs.iterrows(), total=len(df_programs), desc='Programs'):
        meta = {
            'doc_type': 'Program',
            'filename': doc_row['filename'],
            'country': doc_row.get('country_name', ''),
            'ifs': doc_row.get('ifs'),
            'year': doc_row.get('year'),
            'arrangement_number': doc_row.get('arrangement_number'),
            'review': doc_row.get('review'),
            'region': doc_row.get('region'),
        }
        rows.append(search_markdown(doc_row['filepath'], topics, meta))

    df = pd.DataFrame(rows)
    _print_search_summary("Programs", df, topics)
    return df


# =============================================================================
# SEARCH: JSON files (legacy DSA structured pipeline)
# =============================================================================

def search_document(doc, topics):
    """
    Search a structured DSA JSON document for keyword mentions.
    Returns dict with has_, count_, paras_ per topic.
    """
    filename = doc.get('filename', '')
    country = doc.get('country', '')
    year = doc.get('year')
    if year is None:
        ym = re.search(r'(20\d{2}|19\d{2})', filename)
        year = int(ym.group(1)) if ym else None

    all_paras = []
    for section in doc.get('sections', []):
        for para in section.get('paragraphs', []):
            text = para.get('text', '').strip()
            if text:
                all_paras.append(text)

    row = {
        'filename': filename,
        'country': country,
        'year': year,
        'n_paragraphs': len(all_paras),
    }

    paras_norm = [_normalize(p) for p in all_paras]

    for topic_name, topic_cfg in topics.items():
        keywords_norm = [_normalize(kw) for kw in topic_cfg['keywords']]
        hit_count = 0
        para_count = 0
        for pn in paras_norm:
            para_has_hit = False
            for kw in keywords_norm:
                n = _count_keyword(pn, kw)
                hit_count += n
                if n > 0:
                    para_has_hit = True
            if para_has_hit:
                para_count += 1
        row[f'has_{topic_name}'] = 1 if hit_count > 0 else 0
        row[f'count_{topic_name}'] = hit_count
        row[f'paras_{topic_name}'] = para_count

    return row


def build_mentions_json(json_dir, topics):
    """Run keyword search across all structured DSA JSONs."""
    import json as json_lib

    json_dir = Path(json_dir)
    json_files = sorted(json_dir.glob('*.json'))
    json_files = [f for f in json_files
                  if not f.stem.startswith('debug')
                  and f.stem != 'extraction_summary']

    print(f"DSA (JSON): Searching {len(json_files)} documents...")

    rows = []
    for jf in tqdm(json_files, desc='DSA (JSON)'):
        with open(jf, 'r', encoding='utf-8') as f:
            doc = json_lib.load(f)
        rows.append(search_document(doc, topics))

    df = pd.DataFrame(rows)
    _print_search_summary("DSA (JSON)", df, topics)
    return df


# =============================================================================
# COMBINE — merge all doc types into df_mentions_all
# =============================================================================

def combine_mentions(df_mentions_dsa, df_mentions_aiv, df_mentions_prog, df_inventory=None):
    """
    Concatenate DSA + AIV + Program mention DataFrames.
    Optionally merge country characteristics from df_inventory.
    """
    df_all = pd.concat([df_mentions_dsa, df_mentions_aiv, df_mentions_prog],
                       ignore_index=True)

    # Merge country characteristics if inventory provided
    if df_inventory is not None:
        char_cols = ['ifs', 'cex', 'fcs', 'sds', 'rst', 'hipc',
                     'frontier_market', 'exposure_china']
        for col in char_cols:
            if col != 'ifs' and col not in df_all.columns:
                mapping = df_inventory.set_index('ifs')[col]
                df_all[col] = df_all['ifs'].map(mapping)

    # Summary
    print(f"\n{'='*70}")
    print("COMBINED KEYWORD SEARCH RESULTS")
    print(f"{'='*70}")
    for dtype in ['DSA', 'AIV', 'Program']:
        sub = df_all[df_all['doc_type'] == dtype]
        print(f"  {dtype}: {len(sub)} docs")
    print(f"  Total: {len(df_all)} docs")

    return df_all


# =============================================================================
# DIAGNOSTICS — keyword hit analysis
# =============================================================================

def diagnose_keyword_hits(df_mentions_all, topic_key, topics, txt_dir,
                          n_sample=20, doc_type='DSA'):
    """
    For a topic, sample docs and show hit count per keyword.
    Helps identify which keywords cause noise from tables.
    """
    topic_cfg = topics[topic_key]
    txt_dir = Path(txt_dir)

    # Sample docs that have hits
    has_col = f'has_{topic_key}'
    hits = df_mentions_all[
        (df_mentions_all['doc_type'] == doc_type) &
        (df_mentions_all[has_col] == 1)
    ]
    sample = hits.sample(min(n_sample, len(hits)), random_state=42)

    # Count hits per keyword across sampled docs
    kw_totals = {kw: 0 for kw in topic_cfg['keywords']}
    kw_contexts = {kw: [] for kw in topic_cfg['keywords']}

    for _, row in sample.iterrows():
        fp = txt_dir / f"{row['country']}_{row['filename']}.txt"
        if not fp.exists():
            continue
        try:
            text = fp.read_text(encoding='utf-8')
        except:
            text = fp.read_text(encoding='latin-1')

        text_norm = _normalize(text)

        for kw in topic_cfg['keywords']:
            kw_norm = _normalize(kw)
            pattern = r'\b' + re.escape(kw_norm) + r'\b'
            matches = list(re.finditer(pattern, text_norm))
            kw_totals[kw] += len(matches)

            # Save first context per doc
            if matches and len(kw_contexts[kw]) < 5:
                m = matches[0]
                start = max(0, m.start() - 80)
                end = min(len(text_norm), m.end() + 80)
                ctx = text_norm[start:end].replace('\n', ' ')
                kw_contexts[kw].append((row['filename'], ctx))

    # Print results
    print(f"\n{'='*80}")
    print(f"TOPIC: {topic_cfg['description']} ({topic_key})")
    print(f"Sample: {len(sample)} docs")
    print(f"{'='*80}")
    print(f"\n{'Keyword':<45s} {'Hits':>6s}  {'Avg/doc':>7s}")
    print(f"{'-'*60}")

    for kw, count in sorted(kw_totals.items(), key=lambda x: -x[1]):
        if count == 0:
            continue
        avg = count / len(sample)
        flag = ' ⚠ TABLE NOISE?' if avg > 0.8 else ''
        print(f"  {kw:<43s} {count:>6d}  {avg:>7.1f}{flag}")

    # Zero-hit keywords
    zeros = [kw for kw, c in kw_totals.items() if c == 0]
    if zeros:
        print(f"\n  Zero hits: {', '.join(zeros)}")

    # Contexts for top keywords
    print(f"\n  --- Sample contexts (top keywords) ---")
    top_kws = sorted(kw_totals.items(), key=lambda x: -x[1])[:5]
    for kw, _ in top_kws:
        if not kw_contexts[kw]:
            continue
        print(f"\n  [{kw}]")
        for fname, ctx in kw_contexts[kw][:3]:
            print(f"    {fname}")
            print(f"    ...{ctx}...")


# =============================================================================
# INTERNAL — print summary
# =============================================================================

def _print_search_summary(label, df, topics):
    """Print keyword search summary for a document set."""
    if len(df) == 0:
        print(f"\n{label}: No results")
        return

    print(f"\n{'='*70}")
    print(f"{label} KEYWORD SEARCH — {len(df)} documents, {len(topics)} topics")
    print(f"{'='*70}")
    for topic_name, topic_cfg in topics.items():
        has_col = f'has_{topic_name}'
        count_col = f'count_{topic_name}'
        if has_col in df.columns:
            n_docs = df[has_col].sum()
            pct = n_docs / len(df) * 100
            total_hits = df[count_col].sum()
            print(f"  {topic_cfg['description']:45s} "
                  f"{n_docs:4d} docs ({pct:5.1f}%) | {total_hits:5d} hits")


# =============================================================================
# SEARCH: MD files (DSA — Docling-converted, cleaner than TXT)
# =============================================================================

def build_mentions_dsa_md(md_dir, df_dsa, topics):
    """
    Run keyword search on DSA Markdown files (Docling output).
    Reads entire file as one string — whole-document approach, same as TXT.

    MD structure: {md_dir}/{country_folder}/{filename}.md
    Uses country_name_dsa from df_dsa for folder name.
    """
    md_dir = Path(md_dir)

    rows = []
    skipped = []
    for _, r in tqdm(df_dsa.iterrows(), total=len(df_dsa), desc='DSA (MD)'):
        folder = r.get('country_name_dsa', r['country'])
        stem = r['filename'].replace('.pdf', '')
        md_path = md_dir / folder / f"{stem}.md"

        if not md_path.exists():
            skipped.append(str(md_path))
            continue

        meta = {
            'filename': stem,
            'country': r['country'],
            'year': r['year'],
            'ifs': r.get('ifs', None),
            'doc_type': 'DSA',
        }

        try:
            result = search_txt(md_path, topics, doc_meta=meta)
            rows.append(result)
        except Exception as e:
            print(f"\n⚠ Error: {md_path.name} — {e}")
            continue

    df = pd.DataFrame(rows)

    # Report skipped
    if skipped:
        print(f"\n⚠ {len(skipped)} MD files not found:")
        for s in skipped[:10]:
            print(f"    {s}")
        if len(skipped) > 10:
            print(f"    ... and {len(skipped) - 10} more")

    _print_search_summary("DSA (MD)", df, topics)

    return df