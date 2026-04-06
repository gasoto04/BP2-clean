# =============================================================================
# classification.py — DSA section classification and JSON cleanup
# =============================================================================
# Hybrid section classification (regex title rules + Qwen bucket fallback)
# and post-extraction JSON cleanup for structured DSA documents.
#
# Location: E:\Data\gsoto\analytical\classification.py
# Usage:    from classification import reclassify_all_jsons, cleanup_all_jsons
# =============================================================================


# =============================================================================
# TITLE RULES — regex patterns for section classification (~87% coverage)
# =============================================================================

TITLE_RULES = [
    # Authorities' views
    (r"authorit", 'authorities_views'),

    # Conclusions / Assessment / Results
    (r'^conclusions?$', 'conclusions'),
    (r'debt distress (classification|qualification)', 'conclusions'),
    (r'^staff assessment', 'conclusions'),
    (r'^assessment$', 'conclusions'),
    (r'main findings and conclusions', 'conclusions'),
    (r'^dsa results$', 'conclusions'),
    (r'debt sustainability (assessment|results)', 'conclusions'),
    (r'^results$', 'conclusions'),
    (r'calculation of.*(ci|composite)', 'conclusions'),

    # Risk rating / DCC / Vulnerabilities
    (r'risk rating', 'risk_rating'),
    (r'country classification', 'risk_rating'),
    (r'overall risk of (public )?debt distress', 'risk_rating'),
    (r'debt.carrying capacity', 'risk_rating'),
    (r'risks and vulnerabilities', 'risk_rating'),
    (r'granularity in the risk rating', 'risk_rating'),
    (r'country classification and determination', 'risk_rating'),

    # External debt DSA
    (r'external (debt |and public debt |public )?sustainab', 'external_debt'),
    (r'^external d(sa|ebt)$', 'external_debt'),
    (r'^external debt$', 'external_debt'),
    (r'^external public debt', 'external_debt'),
    (r'evaluation of external debt', 'external_debt'),
    (r'outlook for external', 'external_debt'),
    (r'external debt sustainability analysis', 'external_debt'),
    (r'external debt dsa', 'external_debt'),
    (r'public and external dsa', 'external_debt'),

    # Public debt DSA
    (r'public (sector )?(debt |dsa)sustainab', 'public_debt'),
    (r'^public (sector )?dsa$', 'public_debt'),
    (r'^public debt$', 'public_debt'),
    (r'^total public debt', 'public_debt'),
    (r'fiscal (debt )?sustainability', 'public_debt'),
    (r'domestic debt', 'public_debt'),
    (r'public debt sustainability analysis', 'public_debt'),
    (r'external and public (debt )?sustainability', 'public_debt'),
    (r'background on public sector debt', 'public_debt'),

    # Coverage / Composition / Debt structure
    (r'public (sector )?debt coverage', 'coverage'),
    (r'^(debt )?coverage', 'coverage'),
    (r'data (standards|adequacy)', 'coverage'),
    (r'structure of debt', 'coverage'),
    (r'evolution.*(composition|indicators)', 'coverage'),
    (r'debt management', 'coverage'),
    (r'^debt$', 'coverage'),
    (r'drivers of debt', 'coverage'),
    (r'private (external )?debt', 'coverage'),
    (r'assessment of data adequacy', 'coverage'),
    (r'debt coverage', 'coverage'),

    # Scenarios / Stress tests
    (r'alternative scenario', 'scenarios'),
    (r'bound test', 'scenarios'),
    (r'tailored test', 'scenarios'),
    (r'stress test', 'scenarios'),
    (r'sensitivity analysis', 'scenarios'),
    (r'^actual projections', 'scenarios'),
    (r'^projections$', 'scenarios'),
    (r'pv of debt', 'scenarios'),
    (r'debt service.to.(export|revenue)', 'scenarios'),
    (r'other sustainability indicators', 'scenarios'),
    (r'market module', 'scenarios'),
    (r'realism tool', 'scenarios'),
    (r'(oil|adjustment|reactive|customized).*scenario', 'scenarios'),
    (r'no debt relief', 'scenarios'),
    (r'stronger policies', 'scenarios'),
    (r'sudden stop', 'scenarios'),
    (r'reform scenario', 'scenarios'),

    # Underlying assumptions / Macro
    (r'underlying.*(assumptions|dsa)', 'underlying_assumptions'),
    (r'(key )?(macroeconomic|macro)\s*(assumptions|forecast|projections|outlook)', 'underlying_assumptions'),
    (r'baseline (scenario|assumptions)', 'underlying_assumptions'),
    (r'^assumptions$', 'underlying_assumptions'),
    (r'^dsa assumptions$', 'underlying_assumptions'),
    (r'key assumptions', 'underlying_assumptions'),
    (r'macroeconomic and (policy |fiscal |financing )?assumptions', 'underlying_assumptions'),
    (r'background on macro(economic)? (forecasts|assumptions)', 'underlying_assumptions'),
    (r'macroeconomic outlook', 'underlying_assumptions'),
    (r'outlook and key assumptions', 'underlying_assumptions'),
    (r'macroeconomic framework', 'underlying_assumptions'),
    (r'financing (strategy|assumptions)', 'underlying_assumptions'),
    (r'macro.fiscal assumptions', 'underlying_assumptions'),
    (r'assumptions underlying', 'underlying_assumptions'),
    (r'methodology and (key )?assumptions', 'underlying_assumptions'),
    (r'baseline scenario', 'underlying_assumptions'),
    (r'macro forecasts', 'underlying_assumptions'),
    (r'context and macroeconomic', 'underlying_assumptions'),
    (r'borrowing plan and underlying', 'underlying_assumptions'),
    (r'realism of.*assumptions', 'underlying_assumptions'),
    (r'background and (key )?assumptions', 'underlying_assumptions'),
    (r'background and macroeconomic', 'underlying_assumptions'),

    # Background (catch-all, must come LAST)
    (r'^background', 'background'),
    (r'^introduction$', 'background'),
    (r'recent (debt |economic )?developments', 'background'),
    (r'^debt background', 'background'),
    (r'joint bank.fund', 'background'),
    (r'^baseline$', 'background'),
    (r'^debt sustainability( analysis)?$', 'background'),
    (r'request for.*(arrangement|disbursement)', 'background'),
    (r'debt developments', 'background'),
    (r'debt burden thresholds', 'background'),
    (r'^annex', 'background'),
    (r'staff report for', 'background'),
    (r'statistical issues', 'background'),
    (r'methodology$', 'background'),

    # Abstract
    (r'^abstract$', 'abstract'),
]


# =============================================================================
# BUCKET FALLBACK — Qwen bucket string → canonical bucket (~13% coverage)
# =============================================================================

BUCKET_FALLBACK = {
    # Direct matches
    'abstract': 'abstract', 'background': 'background',
    'underlying_assumptions': 'underlying_assumptions', 'coverage': 'coverage',
    'external_debt': 'external_debt', 'public_debt': 'public_debt',
    'scenarios': 'scenarios', 'risk_rating': 'risk_rating',
    'conclusions': 'conclusions', 'authorities_views': 'authorities_views',
    'conclusion': 'conclusions', 'authorities_view': 'authorities_views',

    # External debt variants
    'external_debt_sustainability': 'external_debt',
    'external_debt_sustainability_analysis': 'external_debt',
    'external_dsa': 'external_debt',

    # Public debt variants
    'public_debt_sustainability': 'public_debt',
    'public_debt_sustainability_analysis': 'public_debt',
    'public_dsa': 'public_debt',
    'public_sector_debt_sustainability': 'public_debt',
    'public_sector_debt_sustainability_analysis': 'public_debt',
    'total_public_debt_sustainability': 'public_debt',
    'fiscal_sustainability': 'public_debt',
    'fiscal_debt_sustainability': 'public_debt',

    # Scenarios variants
    'alternative_scenarios': 'scenarios', 'bound_tests': 'scenarios',
    'tailored_tests': 'scenarios', 'baseline_scenario': 'scenarios',
    'actual_projections': 'scenarios', 'projections': 'scenarios',
    'realism_tools': 'scenarios', 'market_module': 'scenarios',
    'market_access': 'scenarios',

    # Risk rating variants
    'risk_rating_and_vulnerabilities': 'risk_rating',
    'risk_rating_vulnerabilities': 'risk_rating',
    'vulnerabilities': 'risk_rating', 'risks_and_vulnerabilities': 'risk_rating',
    'risk_assessment': 'risk_rating', 'country_classification': 'risk_rating',
    'country_classification_and_determination_of_stress_test_scenarios': 'risk_rating',
    'debt_carrying_capacity': 'risk_rating',
    'overall_risk_of_public_debt_distress': 'risk_rating',
    'categorization': 'risk_rating',

    # Underlying assumptions variants
    'key_assumptions': 'underlying_assumptions',
    'macroeconomic_assumptions': 'underlying_assumptions',
    'macroeconomic_forecast': 'underlying_assumptions',
    'macroeconomic_projections': 'underlying_assumptions',
    'macroeconomic_framework': 'underlying_assumptions',
    'macroeconomic_outlook': 'underlying_assumptions',
    'outlook': 'underlying_assumptions',
    'outlook_and_key_assumptions': 'underlying_assumptions',
    'assumptions': 'underlying_assumptions',
    'dsa_assumptions': 'underlying_assumptions',

    # Background variants
    'introduction': 'background', 'recent_debt_developments': 'background',
    'debt_sustainability': 'background', 'debt_sustainability_analysis': 'background',
    'fiscal_policy': 'background', 'monetary_policy': 'background',
    'financial_sector': 'background', 'climate_change_risks': 'background',
    'climate_risks': 'background', 'hipc_initiative': 'background', 'mdri': 'background',

    # Conclusions variants
    'dsa_results': 'conclusions', 'debt_sustainability_results': 'conclusions',
    'debt_sustainability_assessment': 'conclusions', 'general_assessment': 'conclusions',
    'assessment': 'conclusions', 'results': 'conclusions',
    'policy_implications': 'conclusions', 'diagnosis': 'conclusions',

    # Coverage variants
    'debt_coverage': 'coverage', 'structure_of_debt': 'coverage',
    'evolution_and_composition_of_public_debt': 'coverage',
    'evolution_composition': 'coverage', 'debt_management': 'coverage',
    'private_debt': 'coverage', 'drivers_of_debt_dynamics': 'coverage',
}

CANONICAL_BUCKETS = {
    'abstract', 'background', 'underlying_assumptions', 'coverage',
    'external_debt', 'public_debt', 'scenarios', 'risk_rating',
    'conclusions', 'authorities_views', 'other'
}


# =============================================================================
# CLASSIFICATION FUNCTIONS
# =============================================================================

def classify_section(title_norm: str, qwen_bucket: str) -> tuple:
    """
    Hybrid classification: title rules first, Qwen bucket fallback.
    Returns (canonical_bucket, method) where method is 'title_rule' or 'bucket_fallback'.
    """
    import re

    for pattern, target in TITLE_RULES:
        if re.search(pattern, title_norm):
            return target, 'title_rule'

    fb = BUCKET_FALLBACK.get(qwen_bucket, 'other')
    return (fb if fb in CANONICAL_BUCKETS else 'other'), 'bucket_fallback'


def reclassify_all_jsons(json_dir):
    """
    Reclassify all JSONs using hybrid title + bucket rules.
    Updates each JSON in place with canonical_bucket and classification_method.
    """
    import json
    from pathlib import Path
    from tqdm import tqdm
    from collections import Counter

    json_files = sorted(Path(json_dir).glob("*.json"))
    stats = Counter()

    for jf in tqdm(json_files, desc="Reclassifying"):
        if jf.stem.startswith("debug") or jf.stem == "extraction_summary":
            continue

        with open(jf, 'r', encoding='utf-8') as f:
            doc = json.load(f)

        for section in doc.get("sections", []):
            title_raw = section.get("section_title", "")
            title_norm = title_raw.strip().lower()
            qwen_bucket = section.get("bucket", "other")

            canonical, method = classify_section(title_norm, qwen_bucket)
            section["canonical_bucket"] = canonical
            section["classification_method"] = method
            stats[method] += 1

        with open(jf, 'w', encoding='utf-8') as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)

    total = sum(stats.values())
    print(f"\n✓ Reclassification complete:")
    print(f"  Title rules: {stats['title_rule']} ({stats['title_rule']/total*100:.0f}%)")
    print(f"  Bucket fallback: {stats['bucket_fallback']} ({stats['bucket_fallback']/total*100:.0f}%)")
    print(f"  Total sections: {total}")


# =============================================================================
# JSON CLEANUP
# =============================================================================

def cleanup_json(doc: dict) -> dict:
    """
    Clean a single structured JSON document.
    Returns (cleaned_doc, rescued_titles_count, removed_garbage_count).
    """
    import re, json

    doc = json.loads(json.dumps(doc))  # Deep copy
    rescued_titles = 0
    removed_garbage = 0

    new_sections = []

    for section in doc["sections"]:
        cleaned_paras = []

        for para in section["paragraphs"]:
            text = para["text"].strip()

            # Rescue misclassified section titles
            if (len(text) < 120
                and not text.endswith('.')
                and not re.search(r'\b(is|are|was|were|has|have|will|would|should)\b', text.lower())
                and len(text.split()) < 15):

                if cleaned_paras:
                    section["paragraphs"] = cleaned_paras
                    new_sections.append(section)

                section = {
                    "section_title": text,
                    "bucket": section["bucket"],
                    "paragraphs": []
                }
                cleaned_paras = []
                rescued_titles += 1
                continue

            # Remove table garbage
            non_alpha = sum(1 for c in text if not c.isalpha() and not c.isspace())
            total = len(text)
            if total > 0 and non_alpha / total > 0.4 and len(text) < 200:
                removed_garbage += 1
                continue

            cleaned_paras.append(para)

        section["paragraphs"] = cleaned_paras
        new_sections.append(section)

    # Remove empty sections
    doc["sections"] = [s for s in new_sections if s["paragraphs"]]

    return doc, rescued_titles, removed_garbage


def cleanup_all_jsons(json_dir):
    """Run cleanup on all JSONs in a directory. Overwrites in place."""
    import json
    from pathlib import Path
    from tqdm import tqdm

    json_files = sorted(Path(json_dir).glob("*.json"))
    total_rescued = 0
    total_garbage = 0

    for jf in tqdm(json_files, desc="Cleaning"):
        if jf.stem.startswith("debug") or jf.stem == "extraction_summary":
            continue
        with open(jf, 'r', encoding='utf-8') as f:
            doc = json.load(f)

        doc, rescued, garbage = cleanup_json(doc)
        total_rescued += rescued
        total_garbage += garbage

        with open(jf, 'w', encoding='utf-8') as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Cleanup complete:")
    print(f"  Rescued titles: {total_rescued}")
    print(f"  Removed garbage: {total_garbage}")
    print(f"  Files processed: {len(json_files)}")