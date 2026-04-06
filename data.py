# =============================================================================
# data.py — Core dataframes for the BP analysis pipeline
# =============================================================================
# Builds the foundational dataframes from Country_Characteristics.xlsx,
# document inventories (DSA/AIV/Programs), and arrangement mappings.
#
# Key outputs:
#   df_base      → 68 countries with cleaned characteristics
#   df_inventory → df_base + document counts (n_dsa, n_aiv, n_programs)
#   df_ts        → Country-year panel (2005–2025) with characteristics
#   df_dsa       → Document-level DSA records with country characteristics
#   df_aiv       → Document-level AIV records with country characteristics
#   df_programs  → Document-level Program records with country characteristics
#
# Location: E:\Data\gsoto\analytical\data.py
# Usage:    from data import build_base, build_inventory, build_timeseries
# =============================================================================

import re
import pandas as pd
import numpy as np
from pathlib import Path


# =============================================================================
# ARRANGEMENT YEAR MAP
# =============================================================================

def build_arrangement_year_map(excel_path):
    """Parse arrangement-range Excel and return {year: [arrangement_numbers]} dict."""
    df = pd.read_excel(excel_path, sheet_name='years')

    def parse_numbers(text):
        if pd.isna(text):
            return set()
        text = re.sub(r'(including|excluding)\s*', '', str(text), flags=re.IGNORECASE)
        numbers = set()
        for part in text.split(','):
            part = part.strip().rstrip(',')
            if not part:
                continue
            m = re.match(r'(\d+)\s*-\s*(\d+)', part)
            if m:
                numbers.update(range(int(m.group(1)), int(m.group(2)) + 1))
            elif re.match(r'\d+', part.strip()):
                numbers.add(int(re.match(r'(\d+)', part).group(1)))
        return numbers

    year_to_arr = {}
    for _, row in df.iterrows():
        year = int(row['year'])
        nums = parse_numbers(row['arrangement-range'])
        nums |= parse_numbers(row['including'])
        nums -= parse_numbers(row['excluding'])
        year_to_arr[year] = sorted(nums)
    return year_to_arr


# =============================================================================
# df_base — Country characteristics (68 countries)
# =============================================================================

def build_base(country_char_path):
    """
    Load Country_Characteristics.xlsx and return cleaned df_base.
    68 PRGT-eligible countries with binary categoricals and cleaned columns.
    """
    df_countries = pd.read_excel(country_char_path)
    df_base = df_countries[[
        'ifs', 'country', 'country-dsa', 'region', 'cex', 'fcs', 'rst', 'sds', 'hipc',
        'hipc-completion', 'frontier-market', 'exposure-china',
        'dssi-eligible-participant', 'dssi-eligible-nonparticipant',
        'nb-program(05:24)', 'dr(post-hipc)',
        'domestic-debt-exposure(05:23)', 'liquidity-risk-evolution(05:24)'
    ]].copy()

    df_base.columns = [
        'ifs', 'country_name', 'country_name_dsa', 'region', 'cex', 'fcs', 'rst', 'sds', 'hipc',
        'hipc_completion_date', 'frontier_market', 'exposure_china',
        'dssi_eligible_participant', 'dssi_eligible_nonparticipant',
        'nb_programs', 'dr_post_hipc',
        'domestic_debt_exposure', 'liquidity_risk_evolution'
    ]

    # Clean binary categoricals
    cat_cols = [
        'cex', 'fcs', 'rst', 'sds', 'hipc', 'frontier_market',
        'exposure_china', 'dssi_eligible_participant', 'dssi_eligible_nonparticipant',
        'dr_post_hipc'
    ]
    for col in cat_cols:
        df_base[col] = df_base[col].replace('na', np.nan).fillna(0).astype(int)
    df_base['hipc'] = df_base['hipc'].replace(2, 1)

    # Clean HIPC completion date
    df_base['hipc_completion_date'] = (
        df_base['hipc_completion_date']
        .astype(str)
        .str.replace('*', '', regex=False)
        .replace('na', np.nan)
        .replace('nan', np.nan)
        .str.strip()
    )
    df_base['hipc_completion_date'] = pd.to_numeric(df_base['hipc_completion_date'], errors='coerce')

    # nb_programs: numeric
    df_base['nb_programs'] = df_base['nb_programs'].fillna(0).astype(int)

    # Clean NA values
    df_base['domestic_debt_exposure'] = df_base['domestic_debt_exposure'].replace('na', np.nan)
    df_base['liquidity_risk_evolution'] = df_base['liquidity_risk_evolution'].replace('na', np.nan)

    # DSA folder name: use country-dsa if available, else country
    df_base['country_name_dsa'] = df_base['country_name_dsa'].fillna(df_base['country_name'])

    return df_base


# =============================================================================
# DOCUMENT REGISTRIES — scan input folders
# =============================================================================

def build_dsa_registry(input_dir_dsa):
    """
    Scan DSA PDF folders and build records + registry.
    Returns (dsa_records_list, dsa_registry_dict).

    dsa_registry: {(country_folder_name, year): [filenames]}
    """
    import fitz

    input_dir = Path(input_dir_dsa)
    records = []
    registry = {}

    for country_folder in sorted(input_dir.iterdir()):
        if not country_folder.is_dir():
            continue
        folder_name = country_folder.name
        for f in sorted(country_folder.iterdir()):
            if not f.is_file() or f.suffix.lower() != '.pdf':
                continue
            filename = f.name
            year_match = re.search(r'(20\d{2}|19\d{2})', filename)
            year = int(year_match.group(1)) if year_match else None
            month = None
            parts = f.stem.split('_')
            if len(parts) >= 3:
                month = parts[-1]
            try:
                doc = fitz.open(f)
                n_pages = len(doc)
                doc.close()
            except:
                n_pages = None

            records.append({
                'doc_type': 'DSA',
                'country': folder_name,
                'filename': filename,
                'year': year,
                'month': month,
                'n_pages': n_pages,
                'filepath': str(f),
            })
            key = (folder_name, year)
            registry.setdefault(key, []).append(filename)

    return records, registry


def build_aiv_registry(input_dir_aiv, valid_ifs_codes):
    """
    Scan AIV markdown folders and build records + registry.
    Returns (aiv_records_list, aiv_registry_dict).

    aiv_registry: {(ifs_code_str, year): [filenames]}
    """
    input_dir = Path(input_dir_aiv)
    records = []
    registry = {}

    for f in sorted(input_dir.rglob('*')):
        if not f.is_file():
            continue
        parts = f.stem.split('_')
        ifs_code = parts[0]
        year = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else None
        if ifs_code not in valid_ifs_codes or year is None or year < 2005:
            continue
        records.append({
            'doc_type': 'AIV',
            'ifs': int(ifs_code),
            'filename': f.name,
            'year': year,
            'filepath': str(f),
        })
        key = (ifs_code, year)
        registry.setdefault(key, []).append(f.name)

    return records, registry


def build_prog_registry(input_dir_programs, valid_ifs_codes, meta_path,
                        meta_sheet='Final_Final'):
    """
    Scan Program folders and build records + registry.
    Uses clean_meta_complete.xlsx for year/month instead of arrangement-year mapping.
    """
    input_dir = Path(input_dir_programs)
    
    # Load metadata: File_Name -> year, month
    meta = pd.read_excel(meta_path, sheet_name=meta_sheet,
                         usecols=['File_Name', 'Final_Document_Date'])
    meta['Final_Document_Date'] = pd.to_datetime(meta['Final_Document_Date'], format='mixed')
    meta['year'] = meta['Final_Document_Date'].dt.year
    meta['month'] = meta['Final_Document_Date'].dt.month
    meta_map = meta.set_index('File_Name')[['year', 'month']].to_dict('index')

    records = []
    registry = {}
    skipped = []

    for f in sorted(input_dir.iterdir()):
        if not f.is_file():
            continue
        parts = f.stem.split('_')
        ifs_code = parts[0]
        arr_num = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else None
        review = parts[2] if len(parts) >= 3 else None

        if ifs_code not in valid_ifs_codes:
            continue

        meta_info = meta_map.get(f.stem, {})
        year = meta_info.get('year')
        month = meta_info.get('month')

        if year is None or year < 2005:
            skipped.append(f.name)
            continue

        records.append({
            'doc_type': 'Program',
            'ifs': int(ifs_code),
            'filename': f.name,
            'arrangement_number': arr_num,
            'review': review,
            'year': int(year),
            'month': int(month) if pd.notna(month) else None,
            'filepath': str(f),
        })
        key = (ifs_code, int(year))
        registry.setdefault(key, []).append(f.name)

    if skipped:
        print(f"⚠ Programs skipped (no metadata date): {len(skipped)}")

    return records, registry
    """
    Scan Program folders and build records + registry.
    Returns (prog_records_list, prog_registry_dict).

    prog_registry: {(ifs_code_str, year): [filenames]}
    """
    input_dir = Path(input_dir_programs)
    arr_to_year = {arr: yr for yr, arrs in year_to_arr.items() for arr in arrs}
    records = []
    registry = {}

    for f in sorted(input_dir.iterdir()):
        if not f.is_file():
            continue
        parts = f.stem.split('_')
        ifs_code = parts[0]
        arr_num = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else None
        review = parts[2] if len(parts) >= 3 else None
        year = arr_to_year.get(arr_num) if arr_num else None
        if ifs_code not in valid_ifs_codes or year is None or year < 2005:
            continue
        records.append({
            'doc_type': 'Program',
            'ifs': int(ifs_code),
            'filename': f.name,
            'arrangement_number': arr_num,
            'review': review,
            'year': year,
            'filepath': str(f),
        })
        key = (ifs_code, year)
        registry.setdefault(key, []).append(f.name)

    return records, registry


# =============================================================================
# df_inventory — Country-level document counts
# =============================================================================

def build_inventory(df_base, dsa_registry, aiv_registry, prog_registry):
    """
    Build df_inventory: df_base + n_dsa, n_aiv, n_programs per country.
    """
    df_inventory = df_base.copy()

    # DSA counts (registry keyed by folder name)
    dsa_counts = {}
    for (country, year), files in dsa_registry.items():
        dsa_counts[country] = dsa_counts.get(country, 0) + len(files)
    df_inventory['n_dsa'] = df_inventory['country_name_dsa'].map(dsa_counts).fillna(0).astype(int)

    # AIV counts (registry keyed by ifs string)
    aiv_counts = {}
    for (ifs, year), files in aiv_registry.items():
        aiv_counts[ifs] = aiv_counts.get(ifs, 0) + len(files)
    df_inventory['n_aiv'] = df_inventory['ifs'].astype(str).map(aiv_counts).fillna(0).astype(int)

    # Program counts (registry keyed by ifs string)
    prog_counts = {}
    for (ifs, year), files in prog_registry.items():
        prog_counts[ifs] = prog_counts.get(ifs, 0) + len(files)
    df_inventory['n_programs'] = df_inventory['ifs'].astype(str).map(prog_counts).fillna(0).astype(int)

    return df_inventory


# =============================================================================
# df_ts — Country-year time series panel
# =============================================================================

def build_timeseries(df_base, df_inventory, dsa_registry, aiv_registry, prog_registry,
                     year_range=range(2005, 2026)):
    """
    Build df_ts: country × year panel with document counts and characteristics.
    """
    # DSA year counts (keyed by folder name)
    df_dsa_yr = pd.DataFrame([
        {'country_name_dsa': k[0], 'year': k[1], 'n_dsa': len(v)}
        for k, v in dsa_registry.items()
    ])

    # AIV year counts
    df_aiv_yr = pd.DataFrame([
        {'ifs': k[0], 'year': k[1], 'n_aiv': len(v)}
        for k, v in aiv_registry.items()
    ])

    # Program year counts
    df_prog_yr = pd.DataFrame([
        {'ifs': k[0], 'year': k[1], 'n_programs': len(v)}
        for k, v in prog_registry.items()
    ])

    # Base: all country × year combinations
    years = list(year_range)
    df_base_ts = df_base[['country_name', 'country_name_dsa', 'ifs']].copy()
    df_base_ts = df_base_ts.assign(key=1).merge(
        pd.DataFrame({'year': years, 'key': 1}), on='key'
    ).drop(columns='key')
    df_base_ts['ifs'] = df_base_ts['ifs'].astype(str)

    # Merge counts
    df_ts = df_base_ts.merge(df_dsa_yr, on=['country_name_dsa', 'year'], how='left')
    df_ts = df_ts.merge(df_aiv_yr, on=['ifs', 'year'], how='left')
    df_ts = df_ts.merge(df_prog_yr, on=['ifs', 'year'], how='left')
    df_ts[['n_dsa', 'n_aiv', 'n_programs']] = (
        df_ts[['n_dsa', 'n_aiv', 'n_programs']].fillna(0).astype(int)
    )

    # Add country characteristics
    df_ts['ifs'] = df_ts['ifs'].astype(int)
    char_cols = [c for c in df_inventory.columns
                 if c not in ['n_dsa', 'n_aiv', 'n_programs', 'country_name']]
    df_ts = df_ts.merge(df_inventory[char_cols], on='ifs', how='left')

    return df_ts


# =============================================================================
# DOCUMENT-LEVEL DATAFRAMES with country characteristics
# =============================================================================

def build_doc_dataframes(dsa_records, aiv_records, prog_records, df_inventory):
    """
    Build document-level DataFrames (df_dsa, df_aiv, df_programs)
    merged with country characteristics from df_inventory.

    Returns (df_dsa, df_aiv, df_programs).
    """
    merge_cols = [
        'ifs', 'country_name', 'country_name_dsa', 'region', 'cex', 'fcs', 'sds', 'rst',
        'hipc', 'frontier_market', 'exposure_china'
    ]

    # DSA: merge by folder name (country_name_dsa)
    df_dsa = pd.DataFrame(dsa_records)
    if len(df_dsa) > 0:
        df_dsa = df_dsa.merge(
            df_inventory[merge_cols],
            left_on='country', right_on='country_name_dsa', how='left'
        )

    # AIV: merge by ifs
    df_aiv = pd.DataFrame(aiv_records)
    if len(df_aiv) > 0:
        df_aiv = df_aiv.merge(df_inventory[merge_cols], on='ifs', how='left')

    # Programs: merge by ifs
    df_programs = pd.DataFrame(prog_records)
    if len(df_programs) > 0:
        df_programs = df_programs.merge(df_inventory[merge_cols], on='ifs', how='left')

    # Summary
    print(f"{'='*60}")
    print("DOCUMENT SUMMARY")
    print(f"{'='*60}")
    for name, df in [('DSA', df_dsa), ('AIV', df_aiv), ('Programs', df_programs)]:
        matched = df['country_name'].notna().sum() if len(df) > 0 else 0
        total = len(df)
        yrs = (f"{df['year'].min():.0f}-{df['year'].max():.0f}"
               if len(df) > 0 and df['year'].notna().any() else 'N/A')
        print(f"  {name}: {total} docs | Matched: {matched} | Years: {yrs}")

    return df_dsa, df_aiv, df_programs


# =============================================================================
# CONVENIENCE: build everything at once
# =============================================================================

def build_all(country_char_path, arrangement_path,
              input_dir_dsa, input_dir_aiv, input_dir_programs):
    """
    Build all core dataframes in one call.

    Returns dict with keys:
        df_base, df_inventory, df_ts,
        df_dsa, df_aiv, df_programs,
        dsa_registry, aiv_registry, prog_registry, year_to_arr
    """
    # Step 1: base characteristics
    df_base = build_base(country_char_path)
    valid_codes = set(df_base['ifs'].astype(str).values)

    # Step 2: arrangement map
    year_to_arr = build_arrangement_year_map(arrangement_path)

    # Step 3: scan document folders
    dsa_records, dsa_registry = build_dsa_registry(input_dir_dsa)
    aiv_records, aiv_registry = build_aiv_registry(input_dir_aiv, valid_codes)
    META_PATH = Path("U:/dil/input/clean_meta_complete.xlsx")
    prog_records, prog_registry = build_prog_registry(input_dir_programs, valid_codes, META_PATH)

    print(f"DSA: {len(dsa_records)} docs | AIV: {len(aiv_records)} docs | "
          f"Programs: {len(prog_records)} docs")

    # Step 4: inventory (country-level counts)
    df_inventory = build_inventory(df_base, dsa_registry, aiv_registry, prog_registry)

    # Step 5: time series panel
    df_ts = build_timeseries(df_base, df_inventory, dsa_registry, aiv_registry, prog_registry)

    # Step 6: document-level with characteristics
    df_dsa, df_aiv, df_programs = build_doc_dataframes(
        dsa_records, aiv_records, prog_records, df_inventory
    )

    return {
        'df_base': df_base,
        'df_inventory': df_inventory,
        'df_ts': df_ts,
        'df_dsa': df_dsa,
        'df_aiv': df_aiv,
        'df_programs': df_programs,
        'dsa_registry': dsa_registry,
        'aiv_registry': aiv_registry,
        'prog_registry': prog_registry,
        'year_to_arr': year_to_arr,
    }