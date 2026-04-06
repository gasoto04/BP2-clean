# =============================================================================
# bp2_topics.py — Keyword dictionaries and topic groupings
# =============================================================================
# MENTION_TOPICS:        46 topics with keyword lists for regex search
# COUNTRY_TOPIC_GROUPS:  Maps topics to visualization/analysis groups
#
# Location: E:\Data\gsoto\analytical\bp2_topics.py
# Usage:    from bp2_topics import MENTION_TOPICS, COUNTRY_TOPIC_GROUPS
# =============================================================================


# =============================================================================
# MENTION_TOPICS — Keyword dictionary (46 topics, hierarchical buckets)
# =============================================================================

MENTION_TOPICS = {

    # ============================================================
    # BUCKET: External Shocks
    # ============================================================

    'global_regional_shocks': {
        'description': 'Global & Regional Shocks',
        'keywords': [
            # Global crises
            'world wide recession', 'global economic crisis', 'global crisis',
            'world recession', 'worldwide recession', 'international crisis',
            'global financial crisis', 'deep international recession',
            'international downturn', 'international recession',
            'ongoing global downturn', 'deterioration of external environment',
            'weakening of international economic activity',
            'turbulence in international markets',
            'external conditions deteriorated markedly',
            'unfavorable developments in the international economic environment',
            'recession in the world economy', 'international monetary crisis',
            'worsening international environment', 'difficult external environment',
            'downside risks in the international environment',
            'further deterioration in the international environment',
            'uncertain external environment', 'slowdown in international economy',
            'fragile global outlook', 'international financial turmoil',
            'sharply deteriorating external conditions',
            # Regional / contagion
            'regional crisis', 'crisis in the region',
            'spillovers from the global crisis', 'systemic crisis',
            'crisis in emerging economies', 'regional financial crisis',
            'vulnerable to external shocks', 'crisis spillover',
            'regional economic situation turned adverse',
            'contagion from the crisis in neighboring',
            'contagion', 'fears of contagion', 'spillovers',
            'exogenous events', 'adverse exogenous events',
            'external vulnerability',
            # Commodity / terms of trade
            'oil price shock', 'commodity price decline',
            'commodity price shock', 'terms of trade',
            'exchange rate depreciation',
            # Financial tightening
            'global interest rates', 'monetary policy normalization',
            'taper tantrum',
            # Generic
            'external shock', 'external shocks', 'negative shock',
        ],
    },

    'health_shocks': {
        'description': 'Health Shocks',
        'keywords': [
            'epidemic', 'pandemic', 'virus', 'infection',
            'flu', 'relapsing fever', 'typhoid fever', 'leishmaniasis',
            'dengue', 'mumps', 'meningitis', 'poliomyelitis', 'measles',
            'zika', 'encephalitis', 'sars', 'mers', 'nipah', 'vcjd',
            'hiv', 'hiv/aids', 'typhus', 'hepatitis',
            'h1n1', 'h5n1', 'ebola', 'rotavirus', 'lyme',
            'chikungunya', 'dysentery', 'smallpox',
            'yellow fever', 'cholera', 'malaria',
            'coronavirus', 'covid 19', 'plague',
        ],
    },

    'climate_shocks': {
        'description': 'Climate & Natural Disaster Shocks',
        'keywords': [
            'flood', 'drought', 'rainfall', 'torrential rains',
            'natural calamities', 'natural disaster', 'calamity',
            'earthquake', 'hurricane', 'typhoon', 'cyclone', 'tsunami',
            'adverse weather conditions', 'power shortage',
        ],
    },

    # ============================================================
    # BUCKET: Domestic Conditions
    # ============================================================

    'domestic_economic_conditions': {
        'description': 'Domestic Economic Conditions',
        'keywords': [
            'severe economic crisis', 'very difficult economic circumstances',
            'severe recession', 'severe crisis', 'economic crisis',
            'steep recession', 'strong recessionary headwinds',
            'sharp slowdown', 'sharp declines in output',
            'significant loss of output', 'economic collapse',
            'deeper recession', 'deepening recession',
            'painful recession', 'prolonged recession',
            'lengthening recession', 'severity of the recession',
            'economic recession',
            'sharp contraction of economic activity',
            'strong contraction of economic activity',
            'large contraction of economic activity',
            'deep recession', 'large economic slowdown',
            'profond recession', 'contraction in output',
            'severe contraction', 'deep contraction', 'profond contraction',
            'large decline in income per capita',
            'deep economic downturn', 'severe economic downturn',
            'slowdown in the economic activity', 'slowdown in economic growth',
            'slowdown of the economy', 'slowdown of output',
            'economic decline', 'activity remains weak',
            'the economy slowed down', 'declining trend in economic activity',
            'decline in economic activity', 'slowing down of business activity',
            'slow down', 'low rates of economic growth',
            'low rate of economic growth',
            'economic activity on a downward trend',
            'depressed level of economic activity',
            'the economic situation worsen',
            'slowing the pace of economic recovery',
            'weakening of economic fundamental',
            'recession', 'contraction of output', 'sluggish recovery',
            'contraction of economic activity', 'economic downturn',
            'output is estimated to have contracted',
            'slow economic activity',
        ],
    },

    # ============================================================
    # BUCKET: Domestic Debt (standalone)
    # ============================================================

    'domestic_debt': {
        'description': 'Domestic Debt',
        'keywords': [
            'domestic debt', 'domestic public debt',
            'domestic and external debt',
            'domestic obligations', 'domestic liability', 'domestic liabilities',
            'domestic borrowing', 'domestic financing',
            'domestic market', 'domestic markets',
            'domestic interest', 'domestic currency',
            #'domestic arrears',
            'domestic bond', 'domestic bonds', 'domestic securities',
            'treasury bill', 'treasury bills', 't-bill', 't-bills',
            'monetary financing',
            'local currency bonds', 'local currency borrowing',
        ],
    },

    # ============================================================
    # BUCKET: Market Access
    # ============================================================

    'market_access': {
        'description': 'Market Access',
        'keywords': [
            'international financial markets',
            'international capital markets',
            'market access',
            'regional market',
            'market financing',
            'market creditworthiness',
            'eurobond issuance',
            'sovereign bond issuance',
            'international bond issuance',
            # Variantes eurobond - verificar con diagnose_keyword_hits
            # 'eurobond placement', 'eurobond offering',
            # 'issued a eurobond', 'placed a eurobond',
            # Variantes sovereign bond
            # 'sovereign bond placement', 'sovereign bond offering',
            # 'issued a sovereign bond', 'placed a sovereign bond',
            # Redundantes - capturados por keywords existentes
            # 'international markets',  # ambiguo, puede referir a commodities/comercio
            # 'eurobond',  # ambiguo, vive en otro bucket
            # 'sovereign bond',  # ambiguo, vive en otro bucket
            # 'international bond',  # ambiguo
            # 'tapped international markets',  # subcadena de 'international markets'
            # 'tap international markets',  # subcadena de 'international markets'
            # 'accessed market access', 'gained market access',  # subcadena de 'market access'
            # 'maintained market access', 'kept market access',  # subcadena de 'market access'
            # 'access market access', 'gain market access',  # subcadena de 'market access'
            # 'maintain market access', 'keep market access',  # subcadena de 'market access'
        ],
    },

    # ============================================================
    # BUCKET: Remittances
    # ============================================================

    'remittances': {
        'description': 'Remittances',
        'keywords': ['remittances', 'remittance'],
    },

    # ============================================================
    # BUCKET: DSA Tools
    # ============================================================

    'realism_tools': {
        'description': 'Realism Tools',
        'keywords': [
            'realism tools', 'realism tool', 'projected growth path',
            'realism of planned fiscal adjustment',
            'fiscal adjustment growth relationship',
            'public investment growth relationship',
            'fiscal adjustment assumption',
        ],
    },

    # ============================================================
    # BUCKET: Debt-Investment Nexus
    # ============================================================

    'debt_investment_nexus': {
        'description': 'Debt-Investment Nexus',
        'keywords': [
            'economic diversification', 'public investment efficiency',
            'private participation', 'growth dividend',
            'frontloading public investment',
            'resource project',
        ],
    },

    # ============================================================
    # BUCKET: Domestic Political & Social Factors
    # ============================================================

    'political_social': {
        'description': 'Political and Social Factors',
        'keywords': [
            # Political instability / crisis
            'political turmoil', 'political crisis', 'political uncertainty',
            'political instability', 'political risk', 'unstable political',
            'unstable political environment', 'poor governance', 'weak governance',
            'governance issues', 'disturbed political conditions',
            'unsettled political situation', 'political tensions',
            'internal security situation', 'political atmosphere',
            # Transitions / elections
            'political transition', 'political transition spillovers',
            'political turn over', 'political pressures',
            'change of administration', 'military coup', 'coup d etat',
            'annulment of the election', 'parliamentary upheavals',
            'lack of an approved government',
            'risks linked to the electoral calendar',
            'uncertainty surrounding the outcome of the presidential election',
            'uncertainty regarding the political transition',
            'domestic political developments',
            'facilitate an orderly transition to a new administration',
            'uncertainty about the continuity of policies',
            'uncertainty regarding future policies',
            'uncertain national election',
            # Policy uncertainty
            'policies risks', 'policy related uncertainty',
            'uncertain policies', 'uncertainty about policy',
            # Geopolitical
            'geopolitical events', 'geopolitical risk',
            'geopolitical tensions', 'geopolitical turmoil',
            'complex geopolitical situation',
            'adverse geopolitical events', 'adverse geopolitical',
            'unexpected political events', 'political contagion',
            'election related uncertainty', 'election related uncertainties',
            # Social unrest
            'social risk', 'social strain', 'social turmoil',
            'social disruption', 'social tension', 'social protest',
            'social unrest', 'deteriorating social climate',
            'social climate as deteriorate',
            'railroad transport strike', 'blockade', 'walkouts',
            # Other
            'revolution', 'euro exit', 'exit of the eurozone',
            'critical political juncture',
        ],
    },

    # ============================================================
    # BUCKET: Conflict & Violence
    # ============================================================

    'conflict_violence': {
        'description': 'Conflict & Violence',
        'keywords': [
            # Armed conflict
            'civil conflict', 'civil war', 'armed conflict',
            'armed internal conflict', 'armed domestic conflict',
            'ensuing conflict', 'ongoing conflict', 'violent conflict',
            'atlantic conflict', 'internal conflict',
            'regional conflict', 'conflicts in the region',
            'conflict zone', 'conflict regions',
            # Coups / military
            'military coup', 'military take over', 'coup d etat',
            # Security crises
            'war damage', 'insurgency crisis', 'security crisis',
            'escalated attacks', 'breakdown of cease fire',
            'ethnic rivalries',
            # Terrorism
            'terrorist attacks', 'terrorism', 'guerilla offensive',
            'continuing external aggression',
        ],
    },

    # ============================================================
    # BUCKET: Debt Distress
    # ============================================================

    'arrears': {
        'description': 'Arrears',
        'keywords': [
            'arrears', 'clearance of arrears', 'external arrears',
            'domestic arrears', 'payment arrears',
            'rescheduling of arrears', 'arrears in the payment',
        ],
    },

    'debt_restructuring': {
        'description': 'Debt Restructuring',
        'keywords': [
            # Core restructuring
            'debt restructuring', 'debt rescheduling',
            'rescheduling agreement', 'restructuring agreement',
            'restructuring agreements',
            'debt relief', 'debt service flow relief',
            'debt restructuring program', 'restructuring of debt',
            'restructuring of its external debt',
            'rescheduling of external debt', 'rescheduling of the debt',
            # Techniques
            'haircut', 'refinancing envelope', 'restructuring envelope',
            'debt reprofiling', 'debt swap',
            'debt service reduction', 'suspension of payments',
            # Creditor participation (per LC1)
            'private sector participation', 'paris club',
            'committee of bondholders', 'bondholders committee',
            'creditors committee',
        ],
    },

    # ============================================================
    # BUCKET: SOEs & Contingent Liabilities
    # ============================================================

    'soes': {
        'description': 'State-Owned Enterprises',
        'keywords': [
            'soe', 'soes', "soe's",
            'state owned enterprise', 'state-owned enterprise',
            'public enterprise',
            #'soe contingent', 'soe debt', 'soe guaranteed',
            #'soe health check tool',
        ],
    },

    'contingent_liabilities': {
        'description': 'Contingent Liabilities',
        'keywords': [
            'contingent liabilities', 'contingent liability',
            'ppp', 'public private partnership', 'ppp law',
            'disputed claims',
            'soe contingent',
        ],
    },

    # ============================================================
    # BUCKET: Data Quality & Transparency
    # ============================================================

    'data_quality': {
        'description': 'Data Quality & Transparency',
        'keywords': [
            'off the book', 'capacity constraints',
            'data coverage', 'statistical coverage',
            'debt data', 'data quality',
            'hidden debt', 'debt surprises',
            'lack of data', 'stock flow',
            'not reporting', 'data availability',
        ],
    },

    'debt_transparency': {
        'description': 'Debt Transparency & Disclosure',
        'keywords': [
            'transparency', 'audit', 'disclosure',
            'data availability',
            'off the book',
            'confidentiality clauses', 'confidentiality clause',
            'confidentiality', 'non disclosure',
        ],
    },

    # ============================================================
    # BUCKET: Debt Characteristics
    # ============================================================

    'liquidity_issues': {
        'description': 'Liquidity Issues',
        'keywords': [
            'liquidity risk', 'rollover risk', 'maturity risk',
            'currency risk', 'refinancing issues', 'refinancing constraints',
            'liquidity shortening', 'liquidity crunch',
            'interest rate risk', 'refinancing risk',
        ],
    },

    'solvency_issues': {
        'description': 'Solvency Issues',
        'keywords': ['solvency', 'unsustainable'],
    },

    'non_concessional_borrowing': {
        'description': 'Non-Concessional Borrowing',
        'keywords': [
            'non concessional borrowing', 'non concessional debt',
            'concessional terms', 'concessionality',
            'ncb ceiling', 'semi concessional',
        ],
    },

    'creditor_composition': {
        'description': 'Creditor Composition',
        'keywords': [
            'creditor composition', 'multilateral creditors',
            'bilateral creditors', 'domestic banks', 'pension funds',
            'official creditors', 'domestic debt',
            'external debt composition',
        ],
    },

    # ============================================================
    # BUCKET: DSA Tools
    # ============================================================

    'market_financing_tool': {
        'description': 'Market Financing Tool (post-2018)',
        'keywords': [
            'market financing tool', 'market financing module',
            'market access module', 'market financing scenario',
            'tailored market financing', 'market module',
        ],
    },

    'probability_approach': {
        'description': 'Probability Approach',
        'keywords': [
            'probability approach', 'signal approach', 'stochastic',
        ],
    },

    # ============================================================
    # BUCKET: Creditors — Multilateral
    # ============================================================

    'world_bank': {
        'description': 'World Bank / IDA / IBRD',
        'keywords': ['world bank', 'ida', 'ibrd',
                     'international development association'],
    },

    'afdb': {
        'description': 'African Development Bank',
        'keywords': ['african development bank', 'african development fund',
                     'afdb', 'afdf'],
    },

    'adb': {
        'description': 'Asian Development Bank',
        'keywords': ['asian development bank', 'asian development fund'],
    },

    'idb': {
        'description': 'Inter-American Development Bank',
        'keywords': ['inter american development bank', 'iadb', 'idb'],
    },

    'isdb': {
        'description': 'Islamic Development Bank',
        'keywords': ['islamic development bank', 'isdb'],
    },

    'ifi_multilateral': {
        'description': 'International Financial Institutions',
        'keywords': [
            # UN / other global
            'international fund for agricultural development', 'ifad',
            #'bank for international settlements', 'bis',
            # European
            'european bank for reconstruction', 'ebrd',
            'european investment bank', 'eib',
            #'european financial stability', 'efsm',
            #'european stability mechanism', 'esm',
            'council of europe development bank', 'ceb',
            #'eurosystem',
            # Regional MDBs
            #'african development bank', 'afdb',
            #'asian development bank', 'adb',
            #'inter american development bank', 'iadb', 'idb',
            'asian infrastructure investment bank', 'aiib',
            'caribbean development bank',
            #'west african development bank', 'boad',
            'new development bank', 'ndb',
            # Other multilateral
            #'islamic development bank', 'isdb',
            #'caf', 'development bank of latin america',
            #'opec fund', 'ofid',
            #'arab monetary fund', 'amf',
            #'arab bank for economic development', 'badea',
            'black sea trade and development bank', 'bstdb',
            #'chiang mai initiative', 'cmim',
            #'brics contingent reserve',
        ],
    },

    # ============================================================
    # BUCKET: Creditors — Bilateral Traditional (Paris Club)
    # ============================================================

    'paris_club': {
        'description': 'Paris Club',
        'keywords': ['paris club'],
    },

    'japan': {
        'description': 'Japan',
        'keywords': ['japan', 'japanese', 'jica', 'jbic'],
    },

    'france': {
        'description': 'France',
        'keywords': ['france', 'french', 'afd',
                     'agence francaise'],
    },

    'germany': {
        'description': 'Germany',
        'keywords': ['germany', 'german', 'kfw'],
    },

    'united_states': {
        'description': 'United States',
        'keywords': ['united states', 'usaid'],
    },

    'united_kingdom': {
        'description': 'United Kingdom',
        'keywords': ['united kingdom', 'dfid'],
    },

    'australia': {
        'description': 'Australia',
        'keywords': ['australia', 'australian'],
    },

    'austria': {
        'description': 'Austria',
        'keywords': ['austria', 'austrian'],
    },

    'belgium': {
        'description': 'Belgium',
        'keywords': ['belgium', 'belgian'],
    },

    'canada': {
        'description': 'Canada',
        'keywords': ['canada', 'canadian', 'cida'],
    },

    'denmark': {
        'description': 'Denmark',
        'keywords': ['denmark', 'danish', 'danida'],
    },

    'finland': {
        'description': 'Finland',
        'keywords': ['finland', 'finnish'],
    },

    'ireland': {
        'description': 'Ireland',
        'keywords': ['ireland', 'irish'],
    },

    'israel': {
        'description': 'Israel',
        'keywords': ['israel', 'israeli'],
    },

    'italy': {
        'description': 'Italy',
        'keywords': ['italy', 'italian'],
    },

    'netherlands': {
        'description': 'Netherlands',
        'keywords': ['netherlands', 'dutch'],
    },

    'norway': {
        'description': 'Norway',
        'keywords': ['norway', 'norwegian', 'norad'],
    },

    'south_korea': {
        'description': 'South Korea',
        'keywords': ['south korea', 'korean', 'koica', 'korea exim'],
    },

    'spain': {
        'description': 'Spain',
        'keywords': ['spain', 'spanish', 'aecid'],
    },

    'sweden': {
        'description': 'Sweden',
        'keywords': ['sweden', 'swedish', 'sida'],
    },

    'switzerland': {
        'description': 'Switzerland',
        'keywords': ['switzerland', 'swiss'],
    },

    'russia': {
        'description': 'Russia',
        'keywords': ['russia', 'russian'],
    },

    'brazil': {
        'description': 'Brazil',
        'keywords': ['brazil', 'brazilian', 'bndes'],
    },

    # ============================================================
    # BUCKET: Creditors — Ad Hoc Participants
    # ============================================================

    'china': {
        'description': 'China',
        'keywords': ['china', 'chinese', 'china exim', 'cdb'],
    },

    'india': {
        'description': 'India',
        'keywords': ['india', 'indian', 'india exim'],
    },

    'gulf_states': {
        'description': 'Gulf States',
        'keywords': [
            'saudi arabia', 'saudi fund', 'saudi',
            'kuwait fund', 'kuwait',
            'abu dhabi fund', 'adfd', 'united arab emirates',
            'qatar',
        ],
    },

    'turkey': {
        'description': 'Turkey',
        'keywords': ['turkey', 'turkish', 'tika', 'turkiye'],
    },

    'argentina': {
        'description': 'Argentina',
        'keywords': ['argentina', 'argentine'],
    },

    'hungary': {
        'description': 'Hungary',
        'keywords': ['hungary', 'hungarian'],
    },

    'czech_republic': {
        'description': 'Czech Republic',
        'keywords': ['czech republic', 'czech'],
    },

    'mexico': {
        'description': 'Mexico',
        'keywords': ['mexico', 'mexican'],
    },

    'morocco': {
        'description': 'Morocco',
        'keywords': ['morocco', 'moroccan'],
    },

    'new_zealand': {
        'description': 'New Zealand',
        'keywords': ['new zealand'],
    },

    'portugal': {
        'description': 'Portugal',
        'keywords': ['portugal', 'portuguese'],
    },

    'south_africa': {
        'description': 'South Africa',
        'keywords': ['south africa', 'south african'],
    },

    'trinidad_and_tobago': {
        'description': 'Trinidad and Tobago',
        'keywords': ['trinidad and tobago', 'trinidad'],
    },

    # ============================================================
    # BUCKET: Non-Paris Club (generic concept only)
    # ============================================================

    'non_paris_club': {
        'description': 'Non-Paris Club (generic)',
        'keywords': [
            'non paris club',
            'non-paris club',
        ],
    },
    # ============================================================
    # BUCKET: Creditors — Market / Private
    # ============================================================

    'bondholders': {
        'description': 'Bondholders & Bond Markets',
        'keywords': [
            'bondholder',  'bond issuance',
            'sukuk', 'eurobond', 'international bond', 'sovereign bond'
            #'eurobond issuance', 'sovereign bond issuance', 'international bond issuance',
        ],
    },

    'private_creditors': {
        'description': 'Private / Commercial Creditors',
        'keywords': [
            'private creditor', 'commercial creditor', 'commercial bank',
            'commercial debt', 'bank loan', 'syndicated loan',
            'private sector participation',
        ],
    }
}


# =============================================================================
# COUNTRY_TOPIC_GROUPS — Maps topics to visualization groups
# =============================================================================

COUNTRY_TOPIC_GROUPS = {

    # --- Shocks & Conditions ---
    'External Shocks': [
        ('global_regional_shocks', 'Global & Regional Shocks'),
        ('health_shocks',          'Health Shocks'),
        ('climate_shocks',         'Climate & Natural Disasters'),
    ],
    'Domestic Conditions': [
        ('domestic_economic_conditions', 'Domestic Economic Conditions'),
        ('political_social',             'Political & Social Factors'),
        ('conflict_violence',            'Conflict & Violence'),
    ],

    # --- Debt Topics ---
    'Domestic Debt': [
        ('domestic_debt', 'Domestic Debt'),
    ],
    'Debt Distress': [
        ('arrears',            'Arrears'),
        ('debt_restructuring', 'Debt Restructuring'),
    ],
    'Debt Characteristics': [
        ('liquidity_issues',            'Liquidity Issues'),
        ('solvency_issues',             'Solvency Issues'),
        ('non_concessional_borrowing',  'Non-Concessional Borrowing'),
        ('creditor_composition',        'Creditor Composition'),
    ],

    # --- Institutional ---
    'SOEs': [
        ('soes', 'State-Owned Enterprises'),
    ],
    'Contingent Liabilities': [
        ('contingent_liabilities', 'Contingent Liabilities'),
    ],
    'Data Quality': [
        ('data_quality', 'Data Quality'),
    ],
    'Debt Transparency': [
        ('debt_transparency', 'Debt Transparency'),
    ],

    # --- Market & Financing ---
    'Market Access': [
        ('market_access', 'Market Access'),
        ('remittances',   'Remittances'),
    ],
    'Debt-Investment Nexus': [
        ('debt_investment_nexus', 'Debt-Investment Nexus'),
    ],

    # --- DSA Tools ---
    'DSA Tools': [
        ('realism_tools',          'Realism Tools'),
        ('market_financing_tool',  'Market Financing Tool'),
        ('probability_approach',   'Probability Approach'),
    ],

    # --- Creditor Composition ---
    'Creditors: Multilateral': [
        ('world_bank',       'World Bank'),
        ('afdb',             'AfDB'),
        ('adb',              'ADB'),
        ('idb',              'IDB'),
        ('isdb',             'IsDB'),
        ('ifi_multilateral', 'IFIs (broad)'),
    ],
    'Creditors: Paris Club': [
        ('paris_club',      'Paris Club (generic)'),
        ('japan',           'Japan'),
        ('france',          'France'),
        ('germany',         'Germany'),
        ('united_states',   'United States'),
        ('united_kingdom',  'United Kingdom'),
        ('australia',       'Australia'),
        ('austria',         'Austria'),
        ('belgium',         'Belgium'),
        ('canada',          'Canada'),
        ('denmark',         'Denmark'),
        ('finland',         'Finland'),
        ('ireland',         'Ireland'),
        ('israel',          'Israel'),
        ('italy',           'Italy'),
        ('netherlands',     'Netherlands'),
        ('norway',          'Norway'),
        ('south_korea',     'South Korea'),
        ('spain',           'Spain'),
        ('sweden',          'Sweden'),
        ('switzerland',     'Switzerland'),
        ('russia',          'Russia'),
        ('brazil',          'Brazil'),
    ],
    'Creditors: China': [
        ('china', 'China'),
    ],
    'Creditors: Ad Hoc Participants': [
        ('india',              'India'),
        ('gulf_states',        'Gulf States'),
        ('turkey',             'Turkey'),
        ('argentina',          'Argentina'),
        ('hungary',            'Hungary'),
        ('czech_republic',     'Czech Republic'),
        ('mexico',             'Mexico'),
        ('morocco',            'Morocco'),
        ('new_zealand',        'New Zealand'),
        ('portugal',           'Portugal'),
        ('south_africa',       'South Africa'),
        ('trinidad_and_tobago','Trinidad and Tobago'),
    ],
    'Creditors: Non-Traditional Bilateral': [
        ('non_paris_club',     'Non-Paris Club (generic)'),
        ('china',              'China'),
        ('russia',             'Russia'),
        ('brazil',             'Brazil'),
        ('india',              'India'),
        ('gulf_states',        'Gulf States'),
        ('turkey',             'Turkey'),
        ('argentina',          'Argentina'),
        ('hungary',            'Hungary'),
        ('czech_republic',     'Czech Republic'),
        ('mexico',             'Mexico'),
        ('morocco',            'Morocco'),
        ('new_zealand',        'New Zealand'),
        ('portugal',           'Portugal'),
        ('south_africa',       'South Africa'),
        ('trinidad_and_tobago','Trinidad and Tobago'),
    ],
    'Creditors: Market / Private': [
        ('bondholders',       'Bondholders'),
        ('private_creditors', 'Private Creditors'),
        ('rating_agencies',   'Rating Agencies'),
    ],
}