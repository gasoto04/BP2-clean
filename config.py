# =============================================================================
# config.py — Shared imports and paths for all BP modules
# =============================================================================
# All BP notebooks import from here for shared dependencies and paths.
# Topic-specific: MENTION_TOPICS and COUNTRY_TOPIC_GROUPS live in bp2_topics.py
# Output dirs:    Each BP/notebook defines its own.
#
# Location: E:\Data\gsoto\analytical\config.py
# Usage:    sys.path.insert(0, r'E:\Data\gsoto\analytical')
#           from config import *

# All BP notebooks import from here for shared dependencies and paths.
# Topic-specific: MENTION_TOPICS and COUNTRY_TOPIC_GROUPS live in bp2_topics.py
# Output dirs:    Each BP/notebook defines its own.
#
# Location: E:\Data\gsoto\analytical\bp2_config.py
# Usage:    sys.path.insert(0, r'E:\Data\gsoto\analytical')
#           from bp2_config import *
#
# Implicit dependencies (need install, no explicit import):
#   pip install openpyxl          # Required by pd.read_excel
#   pip install sentencepiece     # Required by transformers tokenizers
# =============================================================================

# --- Standard library ---
import os
import sys
import re
import json
import time
import io
import gc
from pathlib import Path
from datetime import datetime
from collections import Counter
from typing import List, Dict, Tuple, Optional

# --- Data ---
import pandas as pd
import numpy as np
from tqdm import tqdm

# --- PDF extraction ---
import fitz  # PyMuPDF
from PIL import Image

# --- ML / NLP ---
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import AutoModelForVision2Seq, AutoProcessor
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity

# --- NLTK ---
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')

# --- Visualization ---
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import FancyArrowPatch
import textwrap
try:
    import seaborn as sns
except ImportError:
    pass  # Optional: enhanced plotting

# --- Statistics ---
from scipy import stats  # trimmed mean, etc.
 

# --- Qwen VL utilities ---
#try:
#    from qwen_vl_utils import process_vision_info
#except ImportError:
#    pass  # Only needed for vision-language tasks

# --- Docling (AIV/Program markdown conversion) ---
#try:
#    from docling.document_converter import DocumentConverter, PdfFormatOption
#    from docling.datamodel.base_models import InputFormat
#    from docling.datamodel.pipeline_options import PdfPipelineOptions
#except ImportError:
#    pass  # Only needed for AIV/Program extraction


# =============================================================================
# HuggingFace Cache
# =============================================================================
os.environ['HF_HOME']            = 'E:/Data/gsoto/hf_cache'
os.environ['HF_HUB_CACHE']      = 'E:/Data/gsoto/hf_cache'
os.environ['TRANSFORMERS_CACHE'] = 'E:/Data/gsoto/hf_cache'


# =============================================================================
# Shared Paths
# =============================================================================

# --- Inputs (shared across all BPs) ---
INPUT_DIR_DSA_PDF    = Path("U:/dil/input/dsa/pdf")
INPUT_DIR_DSA_MD     = Path("U:/dil/input/dsa/md")
INPUT_DIR_DSA_TXT    = Path("U:/dil/input/dsa/txt")
INPUT_DIR_AIV        = Path("U:/dil/input/aiv")
INPUT_DIR_PROGRAMS   = Path("U:/dil/input/programs")

# --- Main characteristics ---
COUNTRY_CHAR_PATH    = Path("U:/dil/main-characteristics/country-characteristics.xlsx")
ARRANGEMENT_NUMBERS  = Path("U:/dil/main-characteristics/country-years-range.xlsx")

# --- Code / analytical modules ---
ANALYTICAL_DIR       = Path("E:/Data/gsoto/analytical")