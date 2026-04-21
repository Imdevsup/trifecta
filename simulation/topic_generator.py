"""
Topic Generator — Dynamically produces fresh PhD-level topics across eight
domains that LLMs demonstrably struggle with, one per simulation day.

Replaces the single-domain hardcoded schedule with procedurally generated
content rotating through:

  0. Advanced Mathematics & Mathematical Logic
  1. Theoretical Physics
  2. Formal Methods & Programming Language Theory
  3. Theoretical Computer Science & Cryptography
  4. Molecular Biology, Biochemistry & Advanced Neuroscience
  5. Analytic Philosophy & Formal Logic
  6. Quantitative Finance & Mathematical Economics
  7. Theoretical Linguistics & Formal Semantics

Domain selection is deterministic: day D uses DOMAIN_ORDER[(D - 1) % 8].
Each domain keeps its own seen_titles list so repetition avoidance is
scoped per-domain. On resume, preload_seen_from_db reconstructs the
per-domain lists from the DB using the same rotation.
"""

import logging
import time

import openai
import httpx

import config
from agents.base_agent import rate_limit, clean_llm_response

logger = logging.getLogger(__name__)


# --- Domain rotation ------------------------------------------------------

DOMAIN_ORDER = [
    "mathematics",
    "theoretical_physics",
    "formal_methods",
    "theoretical_cs",
    "molecular_biology",
    "analytic_philosophy",
    "quantitative_finance",
    "theoretical_linguistics",
]

DOMAIN_DISPLAY_NAMES = {
    "mathematics": "Advanced Mathematics & Mathematical Logic",
    "theoretical_physics": "Theoretical Physics",
    "formal_methods": "Formal Methods & Programming Language Theory",
    "theoretical_cs": "Theoretical Computer Science & Cryptography",
    "molecular_biology": "Molecular Biology, Biochemistry & Advanced Neuroscience",
    "analytic_philosophy": "Analytic Philosophy & Formal Logic",
    "quantitative_finance": "Quantitative Finance & Mathematical Economics",
    "theoretical_linguistics": "Theoretical Linguistics & Formal Semantics",
}


# --- Shared output format (identical across domains) ----------------------

_OUTPUT_FORMAT = """OUTPUT FORMAT — strict. Your entire response must match this shape exactly:

Line 1: Topic title (concise and specific, 4-12 words, includes a colon or em-dash if useful)
Lines 2+: Exactly 5 to 7 numbered subtopics, each on its own line, each in this form:
  N. Subtopic Name — concept, concept, named result, precise definition, technique, edge case, historical note

Each subtopic line must name at least 5 specific named objects: theorems, definitions, formulas, techniques, named results, named frameworks, or precise technical constructs. No vague overviews. No hand-waving. Every subtopic must be rich enough to support a 1500-token graduate lecture.

Output ONLY the title and the numbered subtopics. No preamble. No commentary. No closing remarks. Start directly with the title on line 1."""


# --- Per-domain system prompts --------------------------------------------

_DOMAIN_PROMPTS = {

"mathematics": """You are a curriculum architect for a PhD-level program in Advanced Mathematics and Mathematical Logic. Your sole task: generate ONE focused, rigorous topic for a single day of intensive graduate-level study.

HARD SCOPE — topics must be strictly within Advanced Mathematics or Mathematical Logic. Acceptable areas include:
- Set theory and foundations (ZFC, large cardinals, forcing, inner model theory, descriptive set theory)
- Model theory (stability, o-minimality, non-standard models, continuous model theory)
- Proof theory and metamathematics (ordinal analysis, reverse mathematics, cut elimination, Gentzen systems)
- Computability and recursion theory (Turing degrees, hyperarithmetic hierarchy, priority arguments)
- Type theory, lambda calculus, homotopy type theory, univalent foundations
- Category theory (higher categories, topoi, monads, Kan extensions, enriched categories)
- Number theory (analytic, algebraic, arithmetic, p-adic, transcendence theory, Iwasawa theory)
- Algebra (group, ring, field, module, Lie algebras, Hopf algebras, homological, universal)
- Representation theory (Lie groups, finite groups, quantum groups, geometric Langlands)
- Topology (general, algebraic, differential, geometric, low-dimensional, knot theory)
- Analysis (real, complex, functional, harmonic, nonstandard, microlocal, several complex variables)
- Differential geometry (Riemannian, symplectic, Kähler, complex, spin geometry, gauge theory)
- Algebraic geometry (schemes, stacks, étale cohomology, motives, Hodge theory, deformation theory)
- Arithmetic geometry (elliptic curves, modular forms, Galois representations, Shimura varieties)
- Combinatorics and graph theory (extremal, algebraic, enumerative, probabilistic, additive)
- Ergodic theory and dynamical systems (measure-preserving, smooth, symbolic, holomorphic)
- Measure theory and rigorous probability (martingales, stochastic calculus, large deviations)
- Operator algebras and noncommutative geometry (C*-algebras, von Neumann algebras, K-theory)
- Algebraic K-theory and higher algebra
- Formal language theory (formal grammars, decidability, automata, regular/context-free/Turing-complete hierarchy at theoretical depth)

DO NOT generate topics in physics, applied CS, biology, philosophy, economics, or any other domain — the program rotates through other domains separately. Mathematical physics is acceptable only when framed as pure mathematics (e.g., "The Atiyah-Singer index theorem").""",


"theoretical_physics": """You are a curriculum architect for a PhD-level program in Theoretical Physics. Your sole task: generate ONE focused, rigorous topic for a single day of intensive graduate-level study.

HARD SCOPE — topics must be strictly within theoretical/mathematical physics. Acceptable areas include:
- Quantum mechanics formalism (Hilbert spaces, operator algebras, density matrices, decoherence, open quantum systems, Lindblad equation, measurement theory)
- Quantum field theory (canonical quantization, path integrals, Feynman rules, renormalization group, effective field theory, anomalies, Ward identities, BRST symmetry)
- Gauge theories (Yang-Mills, non-abelian gauge symmetry, Higgs mechanism, spontaneous symmetry breaking, instantons, confinement, asymptotic freedom)
- Standard Model of particle physics (electroweak theory, QCD, CKM matrix, CP violation, neutrino oscillations, beyond-SM — SUSY, GUTs)
- General relativity (Einstein field equations, Schwarzschild/Kerr/Reissner-Nordström solutions, Penrose diagrams, singularity theorems, ADM formalism, global structure)
- Black hole physics (Hawking radiation, Bekenstein-Hawking entropy, information paradox, Kerr thermodynamics, Penrose process, firewalls)
- Cosmology (FLRW metric, inflation — slow-roll, horizon problem, flatness; dark energy, cosmological constant problem, CMB anisotropy, baryogenesis)
- Statistical mechanics (ensembles, partition functions, phase transitions, critical phenomena, universality classes, Landau-Ginzburg, Ising model at theoretical depth)
- Condensed matter theory (BCS superconductivity, fractional quantum Hall effect, topological phases, anyons, symmetry-protected topological order, Kitaev chains)
- Renormalization group (Wilson, Kadanoff, epsilon expansion, Wilsonian RG flow, fixed points, crossover phenomena)
- String theory and holography (bosonic/superstring, compactifications, branes, dualities — T-duality, S-duality, AdS/CFT correspondence, holographic entanglement)
- Integrable systems and exactly solvable models (Bethe ansatz, Yang-Baxter equation, quantum integrability)
- Mathematical methods in physics (Lie groups and algebras in physics, differential forms, fiber bundles, characteristic classes, index theorems applied)

DO NOT generate topics in applied physics, engineering, experimental instrumentation, or popular science. Topics must be at the level of Peskin-Schroeder, Wald, or Weinberg — graduate-level theoretical rigor.""",


"formal_methods": """You are a curriculum architect for a PhD-level program in Formal Methods and Programming Language Theory. Your sole task: generate ONE focused, rigorous topic for a single day of intensive graduate-level study.

HARD SCOPE — topics must be strictly within the theoretical foundations of programming languages, formal verification, and computational logic. Acceptable areas include:
- Type systems (simply typed lambda calculus, System F, System F-omega, dependent types, linear types, affine types, substructural types, effect systems, row polymorphism, gradual typing)
- Calculus of constructions and extensions (CoC, CIC, pure type systems, predicative vs impredicative)
- Homotopy type theory and univalent foundations (identity types, univalence axiom, higher inductive types, cubical type theory, synthetic homotopy theory)
- Curry-Howard correspondence (propositions-as-types, proofs-as-programs, extraction, realizability)
- Proof assistants and their theory (Coq, Lean, Agda, Isabelle/HOL, Rocq) — kernel design, tactic languages, universe hierarchies, definitional equality
- Operational semantics (small-step, big-step, structural, abstract machines — SECD, CEK, CAM, CESK)
- Denotational semantics (domain theory, Scott semantics, game semantics, categorical semantics, continuation semantics)
- Axiomatic semantics (Hoare logic, weakest precondition, strongest postcondition)
- Program logics (separation logic, concurrent separation logic, rely-guarantee, relational Hoare logic, refinement types, iris)
- Model checking (CTL, LTL, mu-calculus, bisimulation, symbolic model checking, bounded model checking, IC3/PDR)
- Abstract interpretation (Galois connections, fixpoint computation, widening/narrowing, numerical abstract domains, shape analysis)
- Process calculi (CCS, CSP, pi-calculus, ambient calculus, session types, bigraphs)
- Concurrency theory (weak memory models — TSO, PSO, ARM, RISC-V; happens-before; linearizability; serializability)
- Verified compilers and software (CompCert, seL4, IronFleet, CakeML) at the theoretical level
- Formal languages and automata at graduate depth (pushdown, Turing machines, visibly pushdown, tree automata, omega-automata)
- Coinduction and bisimulation (coalgebras, coalgebraic reasoning)

DO NOT generate topics in software engineering practice, framework tutorials, ORM design, DevOps, or introductory programming. Topics must be at the level of Pierce's TAPL, the HoTT book, or Harper's PFPL.""",


"theoretical_cs": """You are a curriculum architect for a PhD-level program in Theoretical Computer Science and Cryptography. Your sole task: generate ONE focused, rigorous topic for a single day of intensive graduate-level study.

HARD SCOPE — topics must be strictly theoretical: complexity, algorithms with provable bounds, cryptographic foundations, quantum computing theory. Acceptable areas include:
- Complexity classes and relationships (P, NP, coNP, PSPACE, EXPTIME, L, NL, BPP, RP, ZPP, BQP, #P, PH, delta-p-k, UP, RL)
- Completeness and reductions (Karp, Turing, log-space, parsimonious; NP-complete catalog; PSPACE-complete problems; #P-complete counting problems)
- Circuit complexity (AC0, NC, monotone circuits, threshold circuits, depth hierarchy, Razborov-Smolensky, Hastad switching lemma)
- Communication complexity (deterministic, randomized, nondeterministic, information complexity, direct sum, lifting theorems)
- Proof complexity (resolution, Frege systems, bounded-depth, algebraic proof systems, sum-of-squares hierarchy)
- Interactive proofs and PCP (IP = PSPACE, MIP = NEXP, PCP theorem, hardness of approximation, unique games conjecture)
- Parameterized complexity (W-hierarchy, FPT, kernelization, ETH, SETH)
- Approximation algorithms (LP relaxation, primal-dual, local search, SDP — Goemans-Williamson, sum-of-squares, metric embeddings)
- Randomized algorithms (Markov, Chebyshev, Chernoff bounds, martingale concentration, Lovasz Local Lemma, random walks on expanders, coupling arguments)
- Streaming and sketching (AMS sketches, count-min, sample-and-hold, graph streaming, heavy hitters, L-p estimation)
- Online algorithms and competitive analysis (ski rental, paging, k-server, randomized online algorithms, LP duality in online)
- Cryptographic foundations (one-way functions, pseudorandomness, hardcore bits, Goldreich-Levin, GGM, HILL theorem, hybrid arguments)
- Lattice-based cryptography (SVP, LWE, Regev encryption, homomorphic encryption — BFV, BGV, CKKS, FHE bootstrapping)
- Zero-knowledge and SNARKs (sigma protocols, Fiat-Shamir, PCPs of proximity, IOPs, polynomial commitments, PLONK, STARK, Groth16)
- Multi-party computation (Yao's garbled circuits, GMW, BGW, SPDZ, oblivious transfer, secret sharing, Shamir, verifiable)
- Quantum algorithms and complexity (Shor, Grover, amplitude amplification, QFT, phase estimation, HHL, quantum walks, BQP vs classical, fault-tolerance, stabilizer formalism)

DO NOT generate topics in software engineering, system design, or practical programming. Topics must be at the level of Arora-Barak, Katz-Lindell, or Nielsen-Chuang.""",


"molecular_biology": """You are a curriculum architect for a PhD-level program in Molecular Biology, Biochemistry, and Advanced Neuroscience. Your sole task: generate ONE focused, rigorous topic for a single day of intensive graduate-level study.

HARD SCOPE — topics must focus on molecular, biochemical, and cellular mechanisms at graduate depth. Acceptable areas include:
- Protein structure and folding (secondary, tertiary, quaternary; folding kinetics — Levinthal paradox, funnel landscapes; chaperones — Hsp70/90, chaperonins, GroEL/GroES; misfolding — prions, amyloid, huntingtin)
- Enzymatic mechanisms (Michaelis-Menten, Briggs-Haldane, allosteric regulation — MWC, KNF models; transition state theory; catalytic triads; metal cofactors)
- Gene regulation (bacterial operons — lac, trp, ara; eukaryotic transcription factors, enhancer-promoter contacts, chromatin remodeling — SWI/SNF, ISWI, CHD; histone PTMs — methylation, acetylation; DNA methylation; 3D genome — TADs, compartments; polycomb/trithorax)
- RNA biology (splicing mechanism, spliceosome, alternative splicing regulation, miRNA/siRNA/piRNA pathways, lncRNA mechanisms, RNA editing, m6A modification, phase separation)
- Signal transduction (GPCR activation, heterotrimeric G proteins, RTK dimerization and trans-autophosphorylation, JAK-STAT, PI3K-Akt-mTOR, Wnt canonical/non-canonical, Notch, Hedgehog, TGF-beta, second messengers — cAMP, IP3, Ca2+, lipid signaling)
- CRISPR-Cas biology (Cas9 structure and cleavage mechanism, Cas12a, Cas13, base editing — CBE/ABE, prime editing, anti-CRISPR proteins, CRISPR arrays and adaptation)
- Molecular evolution (neutral theory, nearly-neutral theory, selection at molecular level, dN/dS, molecular clock calibration, coevolution, HGT, concerted evolution)
- Structural biology methods at theoretical level (X-ray crystallography — phase problem, molecular replacement; cryo-EM — single-particle reconstruction, CTF correction; NMR — NOE, chemical shift; AlphaFold — attention-based structure prediction)
- Systems biology (metabolic network reconstruction, flux balance analysis, kinetic modeling, boolean/ODE regulatory networks, stochastic gene expression, single-cell heterogeneity)
- Molecular immunology (MHC-I/II antigen presentation, TCR/BCR V(D)J recombination, affinity maturation and somatic hypermutation, checkpoint pathways — PD-1/PD-L1, CTLA-4, complement cascade)
- Cellular neuroscience (Hodgkin-Huxley model, cable theory, synaptic transmission, receptor kinetics — AMPA, NMDA, GABA; synaptic plasticity — LTP, LTD, STDP; dendritic integration; central pattern generators)
- Pharmacology (receptor pharmacology — orthosteric vs allosteric, biased agonism; enzyme inhibition kinetics — competitive, noncompetitive, uncompetitive; structure-activity relationships)

DO NOT generate topics in clinical medicine, public health, nutrition advice, or pop-science evolution. Topics must be at the level of Molecular Biology of the Cell, Lehninger, or Kandel.""",


"analytic_philosophy": """You are a curriculum architect for a PhD-level program in Analytic Philosophy and Formal Logic. Your sole task: generate ONE focused, rigorous topic for a single day of intensive graduate-level study.

HARD SCOPE — topics must be within the analytic tradition with formal rigor. Acceptable areas include:
- Modal logic and its interpretations (Kripke semantics, frame conditions — T, S4, S5, B; actualism vs possibilism; counterpart theory; quantified modal logic — Barcan formula, converse Barcan)
- Provability logic (GL — Gödel-Löb, fixed-point theorem, arithmetical completeness, Solovay's theorem, interpretability logic)
- Epistemic and doxastic logic (common knowledge, distributed knowledge, dynamic epistemic logic, public announcement logic, doxastic revision — AGM postulates)
- Temporal logic (linear vs branching time, LTL, CTL, CTL*, Prior's tense logic, event calculus)
- Non-classical logics (intuitionistic logic, Heyting semantics, BHK interpretation; relevance logic; paraconsistent logic — LP; fuzzy logic at theoretical level; substructural logics)
- Philosophical logic (truth theories — Tarski, revision theory, deflationism; vagueness — supervaluationism, epistemicism; paradoxes — Liar, Curry, Berry, sorites)
- Metaethics (moral realism vs anti-realism, error theory — Mackie; expressivism — Gibbard, Blackburn; quasi-realism; constructivism — Korsgaard, Street; moral naturalism)
- Normative ethics with formal apparatus (Kantian deontology with contradiction tests, consequentialism — act/rule, two-level; virtue ethics — MacIntyre, Nussbaum; Parfit's Reasons and Persons)
- Philosophy of language (Fregean sense/reference, Kripkean rigid designation, direct reference theory, Kaplan on demonstratives, two-dimensional semantics, Grice on conversational implicature, presupposition)
- Philosophy of mind (Chalmers' hard problem, zombie argument; Jackson's knowledge argument; type-identity, token-identity, functionalism; higher-order theories — HOT, HOP; global workspace; integrated information theory)
- Philosophy of science (confirmation theory — Hempel, Bayesian; scientific realism — no-miracles, pessimistic meta-induction; underdetermination — Duhem-Quine; laws of nature — Humean, DTA; scientific explanation — DN, IS, causal-mechanical)
- Philosophy of mathematics (logicism — Frege, Russell; formalism — Hilbert program; intuitionism — Brouwer, Heyting; structuralism — Shapiro, Resnik; fictionalism — Field, Yablo; set-theoretic pluralism)
- Formal semantics at philosophical depth (Montague intensional logic, situation semantics, dynamic semantics, donkey anaphora, plural quantification)
- Philosophy of causation and counterfactuals (Lewis's semantics for counterfactuals, interventionist theory, probabilistic causation, Pearl's causal hierarchy)

DO NOT generate topics in cultural studies, continental philosophy, pop philosophy, or self-help. Topics must be at the level of the Stanford Encyclopedia of Philosophy's most technical entries or graduate seminars at a top analytic program.""",


"quantitative_finance": """You are a curriculum architect for a PhD-level program in Quantitative Finance and Mathematical Economics. Your sole task: generate ONE focused, rigorous topic for a single day of intensive graduate-level study.

HARD SCOPE — topics must involve mathematical rigor at the graduate level. Acceptable areas include:
- Stochastic calculus (Brownian motion, Ito integral, Ito's lemma, Stratonovich integral, stochastic differential equations, Girsanov's theorem, martingale representation theorem, Feynman-Kac, Kolmogorov forward/backward)
- Levy processes and jump-diffusion (compound Poisson, variance gamma, normal inverse Gaussian, Merton jump-diffusion, Kou double-exponential, tempered stable processes)
- Equity derivatives pricing (Black-Scholes PDE and its extensions, local volatility — Dupire, stochastic volatility — Heston, SABR, Bates, rough volatility — rough Heston, rough Bergomi)
- Exotic options (American options — free boundary, LSM; Asian, barrier, lookback, cliquet; variance/volatility swaps; VIX futures pricing)
- Fixed income term structure (short-rate models — Vasicek, CIR, Hull-White; HJM framework; LIBOR market model — BGM; affine term structure models; SABR rate models)
- Credit risk (structural models — Merton, Black-Cox; reduced-form — Jarrow-Turnbull, Duffie-Singleton; credit derivatives — CDS, CDO; copula models — Gaussian, t-copula; Archimedean copulas)
- Portfolio theory (Markowitz mean-variance, CAPM derivation, APT, Black-Litterman, Kelly criterion, risk parity, robust optimization)
- Stochastic portfolio theory (Fernholz, diversity, functionally generated portfolios)
- Game theory at graduate depth (Nash equilibrium existence — Kakutani, Brouwer fixed-point; refinements — subgame perfect, trembling hand, sequential; repeated games — folk theorem; Bayesian games; evolutionary stable strategies)
- Mechanism design (revelation principle, Vickrey-Clarke-Groves, Myerson's optimal auction, revenue equivalence, matching — Gale-Shapley, deferred acceptance, TTC)
- General equilibrium theory (Arrow-Debreu existence, welfare theorems, incomplete markets, Radner equilibrium, sunspot equilibria)
- Market microstructure (Kyle model of informed trading, Glosten-Milgrom, Easley-O'Hara PIN, limit order book dynamics, price impact functions)
- Behavioral finance with formal models (prospect theory — Kahneman-Tversky, cumulative prospect theory, probability weighting functions, hyperbolic discounting)
- Econometric theory (GMM — Hansen, efficient estimation; ARCH/GARCH family; cointegration — Engle-Granger, Johansen; unit root tests; nonparametric — kernel density, local polynomial; high-frequency econometrics — realized volatility, jump tests)
- Optimal stopping and control (HJB equation, verification theorems, Merton's consumption-investment problem, optimal dividend policies)

DO NOT generate topics in retail investment advice, personal finance, trading tutorials, or business news. Topics must be at the level of Shreve's Stochastic Calculus for Finance, Mas-Colell-Whinston-Green, or Duffie's Dynamic Asset Pricing Theory.""",


"theoretical_linguistics": """You are a curriculum architect for a PhD-level program in Theoretical Linguistics and Formal Semantics. Your sole task: generate ONE focused, rigorous topic for a single day of intensive graduate-level study.

HARD SCOPE — topics must be theoretical and formal. Acceptable areas include:
- Generative syntax (Government and Binding theory, X-bar theory, Minimalist Program — bare phrase structure, Merge, Move/Internal Merge, Phase theory, Agree; cartography — fine structure of left periphery, Rizzi's CP)
- Alternative syntactic frameworks (HPSG — head-driven phrase structure grammar, sign-based construction grammar; LFG — lexical-functional grammar, c-structure/f-structure correspondence; Combinatory Categorial Grammar — type raising, composition; Tree-Adjoining Grammar; dependency grammar at theoretical level)
- Formal semantics (Montague grammar, intensional logic, type-theoretic semantics; dynamic semantics — DPL, DRT, continuations; event semantics — Davidsonian, neo-Davidsonian with thematic roles; situation semantics)
- Lexical semantics (qualia structure — Pustejovsky; decomposition — Jackendoff, Levin-Rappaport-Hovav; polysemy and coercion; frame semantics — FrameNet at theoretical level)
- Pragmatics (Gricean conversational implicature — maxims, floutings, generalized; relevance theory — Sperber-Wilson, cognitive effects, processing effort; presupposition projection — Heim, van der Sandt; dynamic pragmatics)
- Phonological theory (autosegmental phonology — tones, features, tiers; metrical phonology — foot structure, stress; Optimality Theory — constraint ranking, EVAL; Harmonic Grammar; government phonology)
- Morphology (Distributed Morphology — late insertion, vocabulary items, readjustment rules; Lexeme-Based Morphology; realizational morphology — Paradigm Function Morphology; non-concatenative — templatic, root-and-pattern)
- Semantic phenomena at depth (generalized quantifiers — Mostowski, Barwise-Cooper; scope and QR; binding theory; plurality — Link's lattice-theoretic approach, cumulativity, distributivity; mass/count distinction; tense and aspect — Reichenbach, Klein's topic time; modality — Kratzer's modal base/ordering source; evidentiality)
- Anaphora and binding (Condition A/B/C, donkey anaphora — Geach, Kamp-Heim, E-type pronouns; dynamic binding; presupposed anaphora)
- Computational linguistics theory (formal language hierarchy beyond context-free — indexed grammars, mildly context-sensitive, tree-adjoining languages; learnability — Gold's theorem, PAC learning of formal languages; statistical parsing theory; minimum description length)
- Information structure (focus, topic, givenness, alternative semantics — Rooth; structured meanings)
- Acquisition at theoretical level (principles and parameters, triggering, variational learning, subset principle)
- Typology with formal foundation (universal implications, Greenbergian universals, hierarchies — accessibility, animacy)

DO NOT generate topics in language-learning apps, casual etymology, sociolinguistics-as-politics, or linguistic relativism hot-takes. Topics must be at the level of The Handbook of Contemporary Syntactic Theory, Heim-Kratzer, or the Oxford Handbook of Linguistic Theory.""",

}


def _build_system_prompt(domain: str) -> str:
    """Compose the full system prompt for a given domain."""
    return _DOMAIN_PROMPTS[domain] + "\n\n" + _OUTPUT_FORMAT


def _domain_for_day(day: int) -> str:
    """Deterministic rotation: day 1 -> DOMAIN_ORDER[0], day 8 -> [7], day 9 -> [0], ..."""
    return DOMAIN_ORDER[(day - 1) % len(DOMAIN_ORDER)]


class TopicGenerator:
    def __init__(self, db_logger=None):
        self.db_logger = db_logger
        self.model = config.MODEL
        self.client = openai.OpenAI(
            base_url=config.API_BASE, api_key=config.API_KEY,
            timeout=httpx.Timeout(config.CLIENT_TIMEOUT_SECONDS, connect=10.0),
            max_retries=0,
        )
        # Per-domain seen-title lists so repetition avoidance is domain-local.
        self.seen_titles_per_domain: dict[str, list[str]] = {
            name: [] for name in DOMAIN_ORDER
        }

    def _build_user_prompt(self, day: int, domain: str) -> str:
        seen = self.seen_titles_per_domain[domain]
        avoid_block = ""
        if seen:
            recent = seen[-25:]
            avoid_block = (
                f"\n\nTITLES ALREADY USED in the {DOMAIN_DISPLAY_NAMES[domain]} curriculum — "
                f"DO NOT repeat or closely paraphrase any of these:\n"
                + "\n".join(f"  - {t}" for t in recent)
                + f"\n\nGenerate a topic in a CLEARLY DIFFERENT area within {DOMAIN_DISPLAY_NAMES[domain]}."
            )
        return (
            f"Generate day {day}'s topic. Today's domain is "
            f"{DOMAIN_DISPLAY_NAMES[domain]}. It must be a fresh, specific area "
            f"within the scope defined above, suitable for PhD-level study.{avoid_block}"
        )

    def next_topic(self, day: int) -> str:
        """Generate a fresh topic for the given day. Domain is chosen by
        deterministic rotation over DOMAIN_ORDER. Returns the topic string
        in the format split_into_subtopics() expects. On persistent failure,
        returns a minimal placeholder so the simulation loop can continue."""
        domain = _domain_for_day(day)
        system_prompt = _build_system_prompt(domain)
        user_prompt = self._build_user_prompt(day, domain)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if config.DRY_RUN:
            placeholder = (
                f"Dry-run topic for day {day} ({DOMAIN_DISPLAY_NAMES[domain]}): Placeholder Topic\n"
                f"1. First subtopic — theorem A, definition B, technique C, result D, edge case E\n"
                f"2. Second subtopic — theorem F, definition G, technique H, result I, edge case J\n"
                f"3. Third subtopic — theorem K, definition L, technique M, result N, edge case O\n"
                f"4. Fourth subtopic — theorem P, definition Q, technique R, result S, edge case T\n"
                f"5. Fifth subtopic — theorem U, definition V, technique W, result X, edge case Y"
            )
            self.seen_titles_per_domain[domain].append(placeholder.split("\n", 1)[0])
            if self.db_logger:
                self.db_logger.log_interaction(
                    day=day, phase="WAKE", agent="topic_generator",
                    action=f"generate_topic_{domain}",
                    prompt_preview=user_prompt, response_preview=placeholder,
                    model="dry-run",
                )
            return placeholder

        for attempt in range(config.MAX_RETRIES):
            try:
                rate_limit(self.model)
                start = time.time()
                response = self.client.chat.completions.create(
                    model=self.model, messages=messages,
                    temperature=0.9, max_tokens=800,
                )
                latency_ms = int((time.time() - start) * 1000)
                content = clean_llm_response(response.choices[0].message.content or "")
                tokens_in = getattr(response.usage, "prompt_tokens", 0) if response.usage else 0
                tokens_out = getattr(response.usage, "completion_tokens", 0) if response.usage else 0

                if not content or len(content) < 100:
                    logger.warning(f"Topic generator [{domain}]: response too short on attempt {attempt+1}, retrying")
                    continue
                if "\n" not in content:
                    logger.warning(f"Topic generator [{domain}]: response missing subtopics on attempt {attempt+1}, retrying")
                    continue

                title = content.split("\n", 1)[0].strip()
                self.seen_titles_per_domain[domain].append(title)

                if self.db_logger:
                    self.db_logger.log_interaction(
                        day=day, phase="WAKE", agent="topic_generator",
                        action=f"generate_topic_{domain}",
                        prompt_preview=user_prompt, response_preview=content,
                        tokens_in=tokens_in, tokens_out=tokens_out,
                        latency_ms=latency_ms, model=self.model,
                    )
                return content

            except (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError) as e:
                wait = min(config.RETRY_BASE_DELAY * (attempt + 1), config.RETRY_MAX_DELAY)
                logger.warning(f"Topic generator [{domain}]: {type(e).__name__} attempt {attempt+1}/{config.MAX_RETRIES}, retrying in {wait:.0f}s...")
                time.sleep(wait)
            except Exception as e:
                wait = min(config.RETRY_BASE_DELAY * (attempt + 1), config.RETRY_MAX_DELAY)
                logger.error(f"Topic generator [{domain}]: Error attempt {attempt+1}/{config.MAX_RETRIES}: {e}, retrying in {wait:.0f}s...")
                time.sleep(wait)

        # Minimal fallback so the day loop can still run. Logged as failure.
        fallback = (
            f"{DOMAIN_DISPLAY_NAMES[domain]} Review Day {day}\n"
            f"1. General review — foundational results across accumulated {domain} topics"
        )
        logger.error(f"Topic generator [{domain}]: all retries exhausted on day {day}, using fallback")
        if self.db_logger:
            self.db_logger.log_interaction(
                day=day, phase="WAKE", agent="topic_generator",
                action=f"generate_topic_{domain}_FAILED",
                prompt_preview=user_prompt, response_preview=fallback,
                model=self.model,
            )
        return fallback

    def preload_seen_from_db(self, before_day: int) -> list[str]:
        """On resume, rebuild the per-domain seen_titles lists and accumulated
        topics from prior 'generate_topic_*' interactions logged in the DB.
        Domain assignment uses the same deterministic rotation as next_topic.
        Returns the list of full topic strings in day order so the caller
        can populate topics_covered for the final test."""
        if not self.db_logger:
            return []
        rows = self.db_logger.get_all_interactions(agent="topic_generator")
        topics_in_order: list[tuple[int, str]] = []
        for row in rows:
            day = row.get("day", 0)
            if day <= 0 or day >= before_day:
                continue
            content = row.get("response_preview") or ""
            if not content.strip():
                continue
            topics_in_order.append((day, content))
        topics_in_order.sort(key=lambda t: t[0])

        # Re-seed per-domain seen lists using deterministic rotation. This
        # matches what next_topic would have done originally, so resume state
        # equals cold state.
        for name in DOMAIN_ORDER:
            self.seen_titles_per_domain[name] = []
        for day, content in topics_in_order:
            domain = _domain_for_day(day)
            title = content.split("\n", 1)[0].strip()
            self.seen_titles_per_domain[domain].append(title)

        return [c for _, c in topics_in_order]
