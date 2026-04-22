"""
Static Test Bank — 240 MCQs hand-curated by Claude Opus 4.7, scaled to match
the 8-domain curriculum (30 questions per domain, 10 each of impulse / deep /
axiom). Used in place of runtime LLM-generated questions so the question
author is a different model family than the agents under test, eliminating
the last self-preference bias in MCQ evaluation.

Structure per domain (30 qs):
  - 10 IMPULSE — quick factual recall (specific named results, constants, laws)
  - 10 DEEP    — multi-step analytical reasoning, mechanism, justification
  - 10 AXIOM   — claim about a universal principle + reasoned true/false verdict

Options are shuffled per-run by the evaluator using the run's rng, so the
canonical "correct" letter here does not bias the actual exam.
"""


STATIC_QUESTIONS: list[dict] = [

    # =======================================================================
    # DOMAIN 1 — Advanced Mathematics & Mathematical Logic (30 questions)
    # =======================================================================

    # ----- Math: IMPULSE -----
    {
        "type": "impulse",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "According to the Riemann Hypothesis, the non-trivial zeros of ζ(s) lie on which line?",
        "options": {
            "A": "Re(s) = 1",
            "B": "Re(s) = 1/2",
            "C": "Re(s) = 0",
            "D": "Im(s) = 0",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Gödel's first incompleteness theorem shows that any consistent recursively axiomatizable theory capable of encoding arithmetic has which property?",
        "options": {
            "A": "It is decidable but incomplete",
            "B": "It proves its own consistency",
            "C": "There exists a true arithmetical sentence it cannot prove",
            "D": "It is categorical",
        },
        "correct": "C",
    },
    {
        "type": "impulse",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "The cardinality of the continuum |ℝ| is equal to:",
        "options": {
            "A": "ℵ₀",
            "B": "2^{ℵ₀}",
            "C": "ℵ₁ (provably, without assumptions)",
            "D": "ℵ_ω",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Euler's identity e^{iπ} + 1 = 0 relates which five fundamental constants?",
        "options": {
            "A": "0, 1, e, π, i",
            "B": "0, 1, e, π, φ",
            "C": "0, 1, √2, π, i",
            "D": "0, e, π, i, γ",
        },
        "correct": "A",
    },
    {
        "type": "impulse",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Fermat's Last Theorem — the claim that x^n + y^n = z^n has no positive integer solutions for n > 2 — was proved in 1995 by:",
        "options": {
            "A": "Grigori Perelman",
            "B": "Andrew Wiles (with Richard Taylor completing the modular-lifting step)",
            "C": "Terence Tao",
            "D": "Pierre de Fermat himself",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "The fundamental group π₁(S¹) of the unit circle is isomorphic to:",
        "options": {
            "A": "The trivial group",
            "B": "ℤ/2ℤ",
            "C": "ℤ (the additive group of integers)",
            "D": "ℝ",
        },
        "correct": "C",
    },
    {
        "type": "impulse",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "In ZFC, the axiom of choice is equivalent to which of the following well-known principles?",
        "options": {
            "A": "The principle of mathematical induction",
            "B": "Zorn's lemma (and the well-ordering theorem)",
            "C": "The axiom of regularity",
            "D": "The continuum hypothesis",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "A number is 'transcendental' if it is:",
        "options": {
            "A": "Irrational",
            "B": "Not a root of any non-zero polynomial with rational coefficients",
            "C": "Not expressible in decimal form",
            "D": "Greater than every algebraic number",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "The Euclidean algorithm for gcd(a, b) with a > b > 0 runs in how many division steps in the worst case?",
        "options": {
            "A": "O(√b)",
            "B": "O(log_φ b), where φ is the golden ratio (Lamé's theorem)",
            "C": "O(b)",
            "D": "O(b log b)",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "The fundamental theorem of arithmetic asserts that every integer greater than 1:",
        "options": {
            "A": "Has at most three prime factors",
            "B": "Can be uniquely factored into primes, up to ordering",
            "C": "Is either prime or a perfect square",
            "D": "Is expressible as a sum of two squares",
        },
        "correct": "B",
    },

    # ----- Math: DEEP -----
    {
        "type": "deep",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Suppose f: ℝ → ℝ is continuous and satisfies f(f(x)) = x for all x. Which conclusion is forced?",
        "options": {
            "A": "f must be the identity",
            "B": "f is either the identity or strictly decreasing with a unique fixed point",
            "C": "f must be differentiable everywhere",
            "D": "f must be bounded",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "The (downward) Löwenheim-Skolem theorem implies that first-order theory of the reals:",
        "options": {
            "A": "Is categorical",
            "B": "Admits countable models despite ℝ being uncountable (the Skolem paradox)",
            "C": "Cannot express addition",
            "D": "Is inconsistent",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Why does Cantor's diagonal argument prove that |ℝ| > |ℕ|?",
        "options": {
            "A": "It shows ℝ contains more elements than any finite set",
            "B": "Assuming a surjection ℕ → [0,1] exists, diagonalizing constructs a real not in its image, contradicting surjectivity",
            "C": "It constructs an explicit bijection between ℝ and ℘(ℕ)",
            "D": "It relies on the axiom of choice",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Why does the Banach-Tarski paradox decompose the unit ball into finitely many pieces and reassemble two identical copies?",
        "options": {
            "A": "The pieces are measurable and the construction avoids any non-constructive choices",
            "B": "The construction relies on the axiom of choice to produce non-measurable pieces, so 'volume' is not preserved piecewise",
            "C": "It depends on the continuum hypothesis being false",
            "D": "It works only in dimension 2",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Compactness theorem (first-order logic): if every finite subset of a set Σ of sentences has a model, then Σ has a model. A typical consequence is:",
        "options": {
            "A": "Any statement provable in ZFC is provable in PA",
            "B": "Existence of non-standard models of arithmetic containing infinite integers",
            "C": "Every consistent theory is complete",
            "D": "Every complete theory is decidable",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "On a complete metric space, why do Cauchy sequences always converge?",
        "options": {
            "A": "By definition — completeness means every Cauchy sequence has a limit in the space",
            "B": "Because metric spaces are always closed",
            "C": "Because the diameter of the tail shrinks to zero",
            "D": "Because continuous functions preserve Cauchyness",
        },
        "correct": "A",
    },
    {
        "type": "deep",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Why does Zorn's lemma imply that every vector space has a basis?",
        "options": {
            "A": "The set of linearly independent subsets, ordered by inclusion, is a chain-complete poset; Zorn yields a maximal element, which spans",
            "B": "The dimension is always finite",
            "C": "Every vector space is isomorphic to ℝⁿ for some n",
            "D": "Linear independence implies spanning by a duality argument",
        },
        "correct": "A",
    },
    {
        "type": "deep",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "A sequence of continuous functions converging pointwise to a function f need not converge uniformly. What structure does uniform convergence preserve that pointwise does not?",
        "options": {
            "A": "The limit is measurable",
            "B": "The limit f is continuous, and limits of integrals commute with the limit function",
            "C": "Pointwise convergence implies uniform convergence on compact sets",
            "D": "Uniform convergence makes the functions differentiable",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "The Cantor middle-thirds set is uncountable and has Lebesgue measure zero. Why is this not contradictory?",
        "options": {
            "A": "It is, and standard measure theory rejects the construction",
            "B": "Uncountability and positive Lebesgue measure are independent — a set can have cardinality 2^{ℵ₀} while covering no positive length (e.g. via a geometric series of removed intervals summing to 1)",
            "C": "The Cantor set is actually countable",
            "D": "Measure zero means finite",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Quadratic reciprocity states that for distinct odd primes p, q, the Legendre symbols (p/q) and (q/p) are related by:",
        "options": {
            "A": "(p/q) = (q/p) always",
            "B": "(p/q)(q/p) = (-1)^{((p-1)/2)((q-1)/2)}",
            "C": "(p/q) = -(q/p) always",
            "D": "The symbols are independent of p, q",
        },
        "correct": "B",
    },

    # ----- Math: AXIOM -----
    {
        "type": "axiom",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Evaluate: 'Every bounded sequence in ℝⁿ has a convergent subsequence.'",
        "options": {
            "A": "True — this is the Bolzano-Weierstrass theorem, valid in every finite-dimensional real vector space",
            "B": "True only for monotone sequences",
            "C": "False — oscillating sequences provide counterexamples",
            "D": "True only in ℝ¹",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Evaluate: 'Every infinite set has a proper subset of the same cardinality.'",
        "options": {
            "A": "True — this is the Dedekind-infinite characterization, equivalent (under ZF + countable choice) to the standard notion",
            "B": "False — ℕ has no proper subset of the same size",
            "C": "True only for countable sets",
            "D": "False in every ZF model",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Evaluate: 'Every non-constant polynomial with complex coefficients has a root in ℂ.'",
        "options": {
            "A": "True — this is the Fundamental Theorem of Algebra; ℂ is algebraically closed",
            "B": "True only for polynomials of degree ≤ 4",
            "C": "False — degree 5 polynomials can have no roots",
            "D": "True only for polynomials with real coefficients",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Evaluate: 'For any metric d and points x, y, z: d(x, z) ≤ d(x, y) + d(y, z).'",
        "options": {
            "A": "True — this is the triangle inequality, part of the definition of a metric",
            "B": "True only in Euclidean space",
            "C": "False — it fails in Lᵖ spaces for p < 1, which are still metrics",
            "D": "True only if d is translation-invariant",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Evaluate: 'A continuous real-valued function on [a, b] attaining values f(a) and f(b) attains every value in between.'",
        "options": {
            "A": "True — this is the Intermediate Value Theorem, consequence of connectedness of [a,b] and continuity",
            "B": "True only if f is monotonic",
            "C": "False — f might skip values at isolated points",
            "D": "True only if f is differentiable",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Evaluate: 'Every field has an algebraic closure, unique up to isomorphism.'",
        "options": {
            "A": "True — existence uses Zorn's lemma; uniqueness uses field isomorphism extension",
            "B": "False — only ℝ has an algebraic closure (ℂ)",
            "C": "True, but the closure need not be unique",
            "D": "False in any infinite field",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Evaluate: 'A countable union of countable sets is countable.'",
        "options": {
            "A": "True — under countable choice, we can list the listings and diagonalize",
            "B": "False — the union could have cardinality 2^{ℵ₀}",
            "C": "True only for finite unions",
            "D": "True without any choice principle",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Evaluate: 'In a Hausdorff space, limits of convergent sequences are unique.'",
        "options": {
            "A": "True — disjoint open neighborhoods separating hypothetical distinct limits would exclude one from the tail",
            "B": "False — sequences can have multiple limits in any topology",
            "C": "True only if the space is metrizable",
            "D": "True only for compact spaces",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Evaluate: 'A consistent recursively axiomatizable theory strong enough to encode PA cannot prove its own consistency.'",
        "options": {
            "A": "True — Gödel's second incompleteness theorem",
            "B": "False — PA proves Con(PA)",
            "C": "True only for classical logic",
            "D": "True only for theories with infinitely many axioms",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Advanced Mathematics & Mathematical Logic",
        "question": "Evaluate: 'Every compact subset of a Hausdorff space is closed.'",
        "options": {
            "A": "True — in Hausdorff spaces, points outside a compact set admit neighborhoods disjoint from it, so the complement is open",
            "B": "False — compactness is independent of closedness",
            "C": "True only in metric spaces",
            "D": "True only if the space is also connected",
        },
        "correct": "A",
    },

    # =======================================================================
    # DOMAIN 2 — Theoretical Physics (30 questions)
    # =======================================================================

    # ----- Physics: IMPULSE -----
    {
        "type": "impulse",
        "topic": "Theoretical Physics",
        "question": "Planck's constant h to three significant figures (SI units):",
        "options": {
            "A": "6.626 × 10⁻³⁴ J·s",
            "B": "6.022 × 10²³ mol⁻¹",
            "C": "9.109 × 10⁻³¹ kg",
            "D": "1.381 × 10⁻²³ J/K",
        },
        "correct": "A",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Physics",
        "question": "The fine-structure constant α is approximately:",
        "options": {
            "A": "1/137.036",
            "B": "1/42",
            "C": "1/299792458",
            "D": "1/10⁶",
        },
        "correct": "A",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Physics",
        "question": "Einstein's field equations of general relativity relate the Einstein tensor Gμν to the stress-energy tensor Tμν via:",
        "options": {
            "A": "Gμν = Tμν",
            "B": "Gμν + Λgμν = 8πG/c⁴ · Tμν",
            "C": "Gμν = -4πG · Tμν",
            "D": "Gμν = G · Tμν (no geometric coupling)",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Physics",
        "question": "The Pauli exclusion principle applies to particles of which statistics?",
        "options": {
            "A": "Bosons only",
            "B": "Fermions (half-integer spin) — no two fermions may occupy the same quantum state",
            "C": "Both bosons and fermions equally",
            "D": "Only massless particles",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Physics",
        "question": "The Heisenberg uncertainty relation for position and momentum is:",
        "options": {
            "A": "Δx · Δp ≥ ℏ/2",
            "B": "Δx · Δp = ℏ",
            "C": "Δx · Δp ≤ ℏ",
            "D": "Δx + Δp ≥ ℏ",
        },
        "correct": "A",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Physics",
        "question": "Which gauge group describes the Standard Model of particle physics (ignoring gravity)?",
        "options": {
            "A": "SU(2) × U(1)",
            "B": "SU(3)_C × SU(2)_L × U(1)_Y",
            "C": "SO(10)",
            "D": "U(1) × U(1) × U(1)",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Physics",
        "question": "The Schwarzschild radius r_s of a mass M is:",
        "options": {
            "A": "r_s = GM/c²",
            "B": "r_s = 2GM/c²",
            "C": "r_s = GM/c",
            "D": "r_s = Mc²/G",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Physics",
        "question": "The Dirac equation describes:",
        "options": {
            "A": "Non-relativistic spin-0 particles",
            "B": "Relativistic spin-1/2 particles, predicting antimatter",
            "C": "Classical electromagnetic waves",
            "D": "Gravitational radiation",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Physics",
        "question": "The Higgs mechanism gives mass to which Standard Model particles?",
        "options": {
            "A": "Only the Higgs boson itself",
            "B": "W⁺, W⁻, Z⁰ bosons, and (via Yukawa couplings) the charged fermions",
            "C": "Only the photon",
            "D": "Only quarks, not leptons",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Physics",
        "question": "The de Broglie wavelength of a particle with momentum p is:",
        "options": {
            "A": "λ = h/p",
            "B": "λ = p/h",
            "C": "λ = hc/p",
            "D": "λ = ℏ²/p",
        },
        "correct": "A",
    },

    # ----- Physics: DEEP -----
    {
        "type": "deep",
        "topic": "Theoretical Physics",
        "question": "A free neutron decays (τ ≈ 880 s) but bound neutrons in stable nuclei generally do not. Why?",
        "options": {
            "A": "Strong force suppresses weak vertices in nuclei",
            "B": "The would-be final bound state has higher mass-energy than the initial bound neutron state, so β⁻ decay is kinematically forbidden",
            "C": "Pauli exclusion prevents the emitted electron from existing",
            "D": "Bound neutrons are protons in disguise",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Physics",
        "question": "The near-isotropy of the CMB (~1 part in 10⁵) motivates the inflationary epoch because:",
        "options": {
            "A": "Isotropy is expected without inflation — no problem exists",
            "B": "Causally disconnected regions of the last-scattering surface could not have thermalized to a common temperature without a prior epoch of exponential expansion",
            "C": "It implies the universe rotates coherently",
            "D": "It violates Lorentz invariance cosmologically",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Physics",
        "question": "Noether's theorem links symmetries to conservation laws. Which pairing is correct?",
        "options": {
            "A": "Time-translation symmetry ↔ conservation of charge",
            "B": "Spatial translation ↔ conservation of energy",
            "C": "Time translation ↔ conservation of energy; spatial translation ↔ momentum; rotational ↔ angular momentum",
            "D": "Gauge symmetry ↔ conservation of mass",
        },
        "correct": "C",
    },
    {
        "type": "deep",
        "topic": "Theoretical Physics",
        "question": "Why does the EPR / Bell-inequality analysis exclude local hidden-variable theories of quantum mechanics?",
        "options": {
            "A": "Because quantum measurements are classically correlated",
            "B": "Because experimental correlations violate the Bell inequalities, which any local realist theory must satisfy — observed violations rule out locality-plus-realism",
            "C": "Because hidden variables cannot exist in principle",
            "D": "Because entangled states require non-locality in every interpretation",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Physics",
        "question": "Why is the CPT theorem considered a foundational constraint on any local relativistic QFT?",
        "options": {
            "A": "It is an empirical regularity with no theoretical basis",
            "B": "Any Lorentz-invariant local QFT with a Hermitian Hamiltonian must be invariant under combined charge conjugation, parity, and time reversal",
            "C": "It follows from gauge invariance alone",
            "D": "It is assumed rather than derived",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Physics",
        "question": "Black hole entropy is proportional to horizon area, not volume. Why is this surprising classically?",
        "options": {
            "A": "Classical thermodynamic entropy scales extensively with volume, but the Bekenstein-Hawking formula S = A/(4G) depends only on area — hinting at holography",
            "B": "Because black holes have no entropy classically",
            "C": "Because area is a surface quantity with no thermodynamic meaning",
            "D": "Because volume is ill-defined inside the horizon",
        },
        "correct": "A",
    },
    {
        "type": "deep",
        "topic": "Theoretical Physics",
        "question": "Why does spontaneous symmetry breaking produce massless Goldstone bosons (in absence of gauge symmetry)?",
        "options": {
            "A": "By the Goldstone theorem: each broken continuous global symmetry generator corresponds to a massless mode parametrizing the flat direction in the vacuum manifold",
            "B": "Because broken symmetries always produce massless particles by definition",
            "C": "Because the vacuum must be degenerate and vacua have zero energy",
            "D": "Because symmetry breaking implies asymptotic freedom",
        },
        "correct": "A",
    },
    {
        "type": "deep",
        "topic": "Theoretical Physics",
        "question": "In thermodynamics, why is the statistical (Boltzmann) entropy S = k_B ln Ω extensive despite counting microstates?",
        "options": {
            "A": "Because logarithm of a product (multiplicative microstates for independent subsystems) equals a sum, making S additive for independent subsystems",
            "B": "Because microstates count additively",
            "C": "Because Boltzmann's constant is dimensionless",
            "D": "It is not actually extensive",
        },
        "correct": "A",
    },
    {
        "type": "deep",
        "topic": "Theoretical Physics",
        "question": "Renormalization in QFT is sometimes presented as ad hoc, yet yields precise predictions (e.g. g-2 of the electron). What principled view resolves this?",
        "options": {
            "A": "Renormalization is a trick with no physical meaning",
            "B": "Wilsonian renormalization treats QFTs as effective theories valid below a cutoff; physical predictions are the running couplings and relevant operators, independent of the UV completion",
            "C": "Renormalization is only needed in strongly coupled theories",
            "D": "Renormalization violates unitarity and is therefore wrong",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Physics",
        "question": "Why does a thermodynamically reversible Carnot engine operating between temperatures T_h and T_c achieve maximum efficiency η = 1 - T_c/T_h?",
        "options": {
            "A": "Because real engines are more efficient than ideal ones",
            "B": "Any cycle more efficient than Carnot would allow a process transferring heat from cold to hot with no work — violating the Clausius form of the second law",
            "C": "Because entropy is conserved in every cycle",
            "D": "Because T_c = 0 makes any engine 100% efficient",
        },
        "correct": "B",
    },

    # ----- Physics: AXIOM -----
    {
        "type": "axiom",
        "topic": "Theoretical Physics",
        "question": "Evaluate: 'Energy is conserved in every physical process.'",
        "options": {
            "A": "True universally and without qualification",
            "B": "True in systems with time-translation symmetry (Noether); no globally conserved energy exists in a generic GR spacetime lacking a timelike Killing vector",
            "C": "False in all contexts",
            "D": "True only in quantum mechanics",
        },
        "correct": "B",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Physics",
        "question": "Evaluate: 'The total electric charge of an isolated system is conserved.'",
        "options": {
            "A": "True — consequence of U(1) gauge symmetry; charge conservation holds locally and globally in the Standard Model",
            "B": "False — radioactive decay creates charge",
            "C": "True only in classical electromagnetism",
            "D": "True only in vacuum",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Physics",
        "question": "Evaluate: 'The entropy of an isolated system never decreases.'",
        "options": {
            "A": "True — the second law of thermodynamics; statistical basis in phase-space volume growth under time evolution",
            "B": "False — fluctuations routinely decrease entropy permanently",
            "C": "True only for ideal gases",
            "D": "False in quantum mechanics",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Physics",
        "question": "Evaluate: 'The speed of light c is the same in all inertial reference frames.'",
        "options": {
            "A": "True — second postulate of special relativity; confirmed to extreme precision in Michelson-Morley-type experiments",
            "B": "False — c depends on the observer's velocity",
            "C": "True only in vacuum; c varies with source motion in media",
            "D": "True only for massless photons in the classical limit",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Physics",
        "question": "Evaluate: 'Quantum measurement outcomes are perfectly predictable given the full wave function.'",
        "options": {
            "A": "True — given ψ, all outcomes are determined",
            "B": "False — measurement outcomes on a non-eigenstate of the measured observable are intrinsically probabilistic (Born rule); ψ determines probabilities, not outcomes",
            "C": "True only for eigenstates",
            "D": "False only in the Copenhagen interpretation",
        },
        "correct": "B",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Physics",
        "question": "Evaluate: 'Information cannot propagate faster than the speed of light.'",
        "options": {
            "A": "True — required by special relativity; even entanglement does not transmit classical information superluminally (no-signaling theorem)",
            "B": "False — entangled particles send information instantly",
            "C": "True only classically",
            "D": "False for photons in a medium with n < 1",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Physics",
        "question": "Evaluate: 'In any physical system, observable operators correspond to Hermitian operators.'",
        "options": {
            "A": "True in standard quantum mechanics — Hermiticity ensures real eigenvalues (observable values) and a complete orthonormal basis of eigenstates",
            "B": "False — non-Hermitian operators are also observables",
            "C": "True only in finite-dimensional systems",
            "D": "True only for bounded operators",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Physics",
        "question": "Evaluate: 'The gravitational and inertial masses of any object are equal.'",
        "options": {
            "A": "True (equivalence principle) — cornerstone of general relativity; tested to ~10⁻¹³ precision",
            "B": "False — they differ by the Higgs coupling",
            "C": "True only for atomic matter, not dark matter",
            "D": "True only in weak gravitational fields",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Physics",
        "question": "Evaluate: 'No physical process can cool a system to exactly absolute zero (T = 0 K) in a finite number of steps.'",
        "options": {
            "A": "True — third law of thermodynamics (Nernst unattainability principle)",
            "B": "False — lasers routinely reach T = 0",
            "C": "True only for classical systems",
            "D": "False — absolute zero is routinely achieved",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Physics",
        "question": "Evaluate: 'Quantum information cannot be perfectly copied from an unknown state.'",
        "options": {
            "A": "True — the no-cloning theorem, following from linearity of quantum evolution: a universal cloner would violate superposition",
            "B": "False — classical copying extends to quantum states",
            "C": "True only for pure states",
            "D": "True only in non-interacting systems",
        },
        "correct": "A",
    },

    # =======================================================================
    # DOMAIN 3 — Formal Methods & Programming Language Theory (30 questions)
    # =======================================================================

    # ----- Formal methods: IMPULSE -----
    {
        "type": "impulse",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "In the untyped λ-calculus, β-reduction performs:",
        "options": {
            "A": "Renaming of bound variables (α-conversion)",
            "B": "Application of a function abstraction to an argument via substitution",
            "C": "Extensional equivalence of terms (η)",
            "D": "Normalization to weak head normal form",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Hindley-Milner type inference has which worst-case complexity?",
        "options": {
            "A": "Linear",
            "B": "DEXPTIME-complete in principle (pathological nesting); near-linear in practice",
            "C": "Undecidable",
            "D": "NP-complete",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "The Curry-Howard correspondence identifies proofs with programs. A proof of A → B corresponds to:",
        "options": {
            "A": "A pair ⟨A, B⟩",
            "B": "A function of type A → B",
            "C": "A disjunction",
            "D": "A contradiction",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "In System F (polymorphic lambda calculus), the type ∀α. α → α has exactly how many closed normal inhabitants (up to β-equality)?",
        "options": {
            "A": "Zero",
            "B": "One (the polymorphic identity function)",
            "C": "Infinitely many",
            "D": "Exactly 42",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "A 'sound' static type system guarantees well-typed programs do not get stuck. This property is typically proved via:",
        "options": {
            "A": "Progress + preservation",
            "B": "Termination + confluence",
            "C": "Church-Rosser + strong normalization",
            "D": "Denotational adequacy alone",
        },
        "correct": "A",
    },
    {
        "type": "impulse",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "The Hoare triple {P} C {Q} means:",
        "options": {
            "A": "P, C, and Q are all true",
            "B": "If P holds before executing C and C terminates, then Q holds afterwards (partial correctness)",
            "C": "C implements both P and Q",
            "D": "C terminates for all inputs",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Linear types (à la Girard / Wadler) enforce which discipline on values?",
        "options": {
            "A": "Values may be shared freely",
            "B": "Each linear value must be used exactly once",
            "C": "Values must be primitive",
            "D": "Values are reference-counted at runtime",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "The Y combinator's purpose is:",
        "options": {
            "A": "Type inference",
            "B": "Enabling recursion in untyped λ-calculus without explicit recursive bindings, via Y f = f (Y f)",
            "C": "Pattern matching",
            "D": "Encoding pairs",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "The key property a small-step operational semantics relation → should have for a well-defined deterministic language is:",
        "options": {
            "A": "Totality (every term steps)",
            "B": "Determinism: if t → t' and t → t'', then t' = t''",
            "C": "Symmetry",
            "D": "Reflexivity",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "In dependently typed systems (e.g. Coq, Agda), the type Vec A n represents:",
        "options": {
            "A": "An array of any length",
            "B": "A vector of elements of type A whose length n is part of the type",
            "C": "A heap-allocated list",
            "D": "A lazy stream",
        },
        "correct": "B",
    },

    # ----- Formal methods: DEEP -----
    {
        "type": "deep",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "A static type system is called 'sound' when well-typed programs satisfy which combined property?",
        "options": {
            "A": "Every well-typed program terminates on every input",
            "B": "Progress (a well-typed term is a value or steps) AND preservation (stepping preserves typability) — jointly, well-typed programs do not get stuck",
            "C": "Type inference is polynomial",
            "D": "Every syntactic program type-checks",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Why does adding general recursion (e.g. fix) to the simply-typed λ-calculus destroy strong normalization?",
        "options": {
            "A": "It doesn't — STLC + fix is still SN",
            "B": "fix has type (τ → τ) → τ, so fix (λx. x) loops; the type system can no longer bound reduction length",
            "C": "Adding fix introduces α-conversion failures",
            "D": "fix makes the system inconsistent with Curry-Howard",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "The principal type (for a term in Hindley-Milner) is the most general type. Why is it important for type inference?",
        "options": {
            "A": "It lets the compiler pick arbitrary types",
            "B": "Principal types make HM inference unique (up to substitution) and let inference be local and compositional",
            "C": "It enables dependent types",
            "D": "It guarantees termination",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Why is subject reduction (type preservation under evaluation) often proved by structural induction on the typing derivation rather than on the term?",
        "options": {
            "A": "Because terms have no structure",
            "B": "Typing derivations carry the typing environment and applicable rule, enabling cases that depend on HOW the term is typed — not just its shape",
            "C": "Because preservation is trivial on terms",
            "D": "Because induction on terms fails decidably",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Why does higher-order unification (pattern-matching in λ-calculus with variables for functions) become undecidable, unlike first-order unification?",
        "options": {
            "A": "It remains decidable, same as first-order",
            "B": "Higher-order unification can encode Post correspondence / Hilbert's 10th-problem-like equations; the semantic problem of equating two λ-terms modulo β is undecidable in general",
            "C": "Higher-order unification is decidable only in finite types",
            "D": "It is only undecidable in polymorphic calculi",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Why do effect systems (e.g. algebraic effects, monadic IO) separate 'what' from 'how'?",
        "options": {
            "A": "They don't — effects are always hidden",
            "B": "Effects appear in types as side-effect commitments; handlers / monad implementations determine execution, so the same effectful code can run in multiple semantic interpretations",
            "C": "Effects are purely syntactic",
            "D": "Because effects make code impure at runtime",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "What does Rice's theorem imply for static analysis?",
        "options": {
            "A": "All semantic program properties are decidable",
            "B": "Every non-trivial semantic property of recursively enumerable languages is undecidable, so sound static analyses for non-trivial properties must be approximate (over-approximating failure or under-approximating success)",
            "C": "Static analysis can decide halting but not correctness",
            "D": "Rice's theorem is specific to Turing machines and irrelevant to languages",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Why does separation logic (Reynolds, O'Hearn) scale Hoare-style reasoning to heap-mutating code?",
        "options": {
            "A": "It doesn't; Hoare logic suffices",
            "B": "The separating conjunction P * Q asserts heap disjointness, enabling local reasoning via the frame rule: verify effect on a small footprint, freely add disjoint context",
            "C": "It bans heap mutation entirely",
            "D": "It models the heap as a single global variable",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "In type theory, why is universe polymorphism (Type_i : Type_{i+1}) preferred over a single impredicative universe?",
        "options": {
            "A": "Impredicative Type: Type leads to Girard's paradox, breaking logical consistency",
            "B": "It makes type checking slower but safer syntactically",
            "C": "It is required by the halting problem",
            "D": "It enables garbage collection",
        },
        "correct": "A",
    },
    {
        "type": "deep",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Why is termination in dependently typed theorem provers (Coq, Agda) typically checked via a 'structural recursion' check on a decreasing argument?",
        "options": {
            "A": "To prevent stack overflow at runtime",
            "B": "Because general recursion would admit fix (λx. x) : ⊥, making the logic inconsistent (any proposition provable)",
            "C": "Because the compiler cannot handle infinite loops",
            "D": "Because total functions are easier to compile",
        },
        "correct": "B",
    },

    # ----- Formal methods: AXIOM -----
    {
        "type": "axiom",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Evaluate: 'Any consistent recursively axiomatizable theory strong enough for PA cannot prove its own consistency.'",
        "options": {
            "A": "False — PA proves Con(PA) trivially",
            "B": "True — Gödel's second incompleteness theorem, applying to any sufficiently expressive consistent recursively axiomatizable system",
            "C": "True only in classical logic",
            "D": "True only for finitely axiomatized systems",
        },
        "correct": "B",
    },
    {
        "type": "axiom",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Evaluate: 'Every non-trivial semantic property of programs in a Turing-complete language is undecidable.'",
        "options": {
            "A": "True — Rice's theorem",
            "B": "False — termination is decidable",
            "C": "True only for deterministic programs",
            "D": "False — only halting is undecidable",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Evaluate: 'The simply-typed λ-calculus is strongly normalizing — every typable term reduces to a unique normal form in finitely many steps.'",
        "options": {
            "A": "True — STLC is strongly normalizing (Tait's proof via reducibility candidates)",
            "B": "False — STLC is Turing-complete",
            "C": "True only for closed terms",
            "D": "False — it has infinite reduction sequences",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Evaluate: 'Under Curry-Howard, logical consistency of a type theory corresponds to non-inhabitance of the empty type (⊥, also known as Void or False).'",
        "options": {
            "A": "True — inhabiting ⊥ gives a proof of False, so the logic is inconsistent",
            "B": "False — ⊥ is inhabited in every consistent theory",
            "C": "True only in classical logic",
            "D": "False — inhabiting ⊥ is always possible by diverging",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Evaluate: 'The Church-Rosser (confluence) property guarantees λ-terms have unique normal forms when they exist.'",
        "options": {
            "A": "True — confluence ensures different reduction orders converge, so at most one normal form exists",
            "B": "False — normal forms may differ by reduction strategy",
            "C": "True only in the typed calculus",
            "D": "False — confluence is about strong normalization, not uniqueness",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Evaluate: 'Two program fragments are contextually equivalent iff they are observationally indistinguishable in every program context.'",
        "options": {
            "A": "True — this is the standard Morris-style contextual equivalence, the coarsest compositional equivalence respecting observations",
            "B": "False — equivalence requires identical syntax",
            "C": "True only for pure functional languages",
            "D": "False — context cannot be quantified",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Evaluate: 'A recursive type μα.τ is sound to add to a type system as long as α appears positively in τ.'",
        "options": {
            "A": "True — positive (covariant) occurrence admits least fixed-point semantics and preserves type safety; unrestricted recursive types introduce cardinality-style issues",
            "B": "False — all recursive types are unsound",
            "C": "True only for finite types",
            "D": "False — positivity is irrelevant",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Evaluate: 'Parametric polymorphism (System F) implies 'theorems for free': the type of a polymorphic function constrains its behaviour.'",
        "options": {
            "A": "True — Reynolds' parametricity theorem: a value of ∀α. α → α must be the identity, forced by the type alone without inspecting source",
            "B": "False — types impose no behavioural constraint",
            "C": "True only for monomorphic types",
            "D": "True only in impure languages",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Evaluate: 'In Hoare logic, if {P} C {Q} holds and P' implies P, then {P'} C {Q} holds.'",
        "options": {
            "A": "True — this is the rule of consequence (precondition strengthening), routine in Hoare logic proofs",
            "B": "False — preconditions must match exactly",
            "C": "True only if Q is preserved",
            "D": "False — this violates preservation",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Formal Methods & Programming Language Theory",
        "question": "Evaluate: 'Every total recursive function can be expressed as a λ-term in the untyped λ-calculus.'",
        "options": {
            "A": "True — the untyped λ-calculus is Turing-complete; Church's thesis identifies total recursive with λ-definable (via encodings like Church numerals)",
            "B": "False — λ-calculus can only express boolean functions",
            "C": "True only for primitive recursive functions",
            "D": "False — λ-calculus is strictly weaker than Turing machines",
        },
        "correct": "A",
    },

    # =======================================================================
    # DOMAIN 4 — Theoretical Computer Science & Cryptography (30 questions)
    # =======================================================================

    # ----- TCS/Crypto: IMPULSE -----
    {
        "type": "impulse",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "The security of textbook RSA conjecturally rests on which hard problem?",
        "options": {
            "A": "Discrete logarithm in finite fields",
            "B": "Shortest vector in lattices",
            "C": "Integer factorization of large semiprimes",
            "D": "Graph isomorphism",
        },
        "correct": "C",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "The Harvey-van der Hoeven (2019) integer multiplication algorithm runs in:",
        "options": {
            "A": "O(n²)",
            "B": "O(n^1.585) Karatsuba",
            "C": "O(n log n · 2^{O(log* n)})",
            "D": "O(n log n)",
        },
        "correct": "D",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "The class NP is defined as:",
        "options": {
            "A": "Problems decidable in polynomial time by a deterministic Turing machine",
            "B": "Problems whose YES-instances have polynomial-length certificates verifiable in polynomial time",
            "C": "Problems requiring polynomial space",
            "D": "Problems solvable only by quantum computers",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "AES uses which block cipher structure?",
        "options": {
            "A": "Feistel network",
            "B": "Substitution-permutation network (SPN) with 10/12/14 rounds depending on key size",
            "C": "Stream cipher with OFB mode",
            "D": "Hash-based MAC",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "A cryptographic hash function H must satisfy which property to resist chosen-prefix collisions?",
        "options": {
            "A": "Preimage resistance",
            "B": "Collision resistance (it must be infeasible to find x ≠ y with H(x) = H(y))",
            "C": "Second-preimage resistance",
            "D": "Avalanche property only",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "The Cook-Levin theorem establishes that which problem is NP-complete?",
        "options": {
            "A": "Graph isomorphism",
            "B": "SAT (Boolean satisfiability)",
            "C": "Primality testing",
            "D": "Linear programming",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Shor's algorithm factors an integer n on a quantum computer in:",
        "options": {
            "A": "O(n^{1/3}) time",
            "B": "Polynomial time in log n",
            "C": "Sub-exponential time via the GNFS analog",
            "D": "Constant time",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "A perfect zero-knowledge proof system must be:",
        "options": {
            "A": "Complete, sound, and zero-knowledge (the verifier learns nothing beyond statement validity)",
            "B": "Only complete",
            "C": "Deterministic",
            "D": "Based on RSA",
        },
        "correct": "A",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "The class BPP (bounded-error probabilistic polynomial time) satisfies:",
        "options": {
            "A": "BPP = P (provably)",
            "B": "P ⊆ BPP ⊆ Σ₂ ∩ Π₂ (Sipser-Gács-Lautemann); widely conjectured BPP = P",
            "C": "BPP is undecidable",
            "D": "BPP ⊋ NP",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Which property of a pseudorandom generator G: {0,1}^n → {0,1}^{p(n)} must it satisfy?",
        "options": {
            "A": "It is a bijection",
            "B": "No polynomial-time distinguisher tells its output from uniform with non-negligible advantage",
            "C": "It is information-theoretically uniform",
            "D": "Its output is perfectly random",
        },
        "correct": "B",
    },

    # ----- TCS/Crypto: DEEP -----
    {
        "type": "deep",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "In Diffie-Hellman over a prime-order cyclic group, the eavesdropper observes g^a, g^b. Why can't they efficiently compute g^{ab}?",
        "options": {
            "A": "Because g^a · g^b = g^{a+b}, never g^{ab}",
            "B": "Because computing a from g^a (discrete log) is conjectured hard in well-chosen groups",
            "C": "Because a hash is applied, destroying algebraic structure",
            "D": "Because the group order is secret",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Why does Cook's theorem reduce every problem in NP to SAT?",
        "options": {
            "A": "It reduces to graph coloring, not SAT",
            "B": "A polynomial-time verifier is a polynomial-size Boolean circuit; encoding its successful execution as a SAT formula is polynomial and satisfiable iff a certificate exists",
            "C": "SAT is stronger than NP",
            "D": "Cook's theorem applies only to PSPACE",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Why is the time hierarchy theorem important?",
        "options": {
            "A": "It shows TIME(f(n)) = TIME(g(n)) for any f, g",
            "B": "If f grows sufficiently faster than g (f(n) log f(n) = o(g(n))), then TIME(g) strictly contains TIME(f), establishing a hierarchy and proving P ≠ EXP",
            "C": "It implies P = NP",
            "D": "It is a conjecture, not a theorem",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Why does the birthday paradox imply that collisions in an n-bit hash can be found in ~2^{n/2} queries?",
        "options": {
            "A": "Because hashes are linear",
            "B": "With q random outputs into 2^n buckets, expected collisions scale as q²/2^n; setting q ≈ 2^{n/2} yields a collision with constant probability",
            "C": "Because hash functions are bijective",
            "D": "Because 2^{n/2} is one-way",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "What does the PCP theorem imply for the hardness of approximation?",
        "options": {
            "A": "All NP problems admit PTAS",
            "B": "NP = PCP(log n, O(1)); consequently, approximating many NP-hard problems (e.g. MAX-3SAT beyond 7/8) is itself NP-hard",
            "C": "PCP implies P = NP",
            "D": "It applies only to decision problems, not optimization",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "IND-CPA (indistinguishability under chosen plaintext attack) is a standard security notion. Why does it require probabilistic (randomized) encryption?",
        "options": {
            "A": "It doesn't — deterministic encryption can be IND-CPA",
            "B": "A deterministic encryption trivially fails IND-CPA: encrypting two chosen plaintexts twice shows whether they are equal, giving the adversary non-negligible advantage",
            "C": "Because keys are deterministic",
            "D": "Because randomness avoids side channels",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Why does the existence of a one-way function imply that P ≠ NP?",
        "options": {
            "A": "It doesn't — existence is independent of P vs NP",
            "B": "If f is one-way, inverting f is in NP (via a witness) but not in P (by hardness of inversion), giving NP ⊋ P",
            "C": "Because all one-way functions are NP-complete",
            "D": "Because P = NP implies everything is one-way",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Lattice-based cryptography (e.g. Kyber, LWE-based schemes) derives security from:",
        "options": {
            "A": "Integer factorization",
            "B": "Worst-case to average-case reductions from problems like GapSVP or LWE, believed hard even against quantum adversaries",
            "C": "Discrete logarithm",
            "D": "Graph isomorphism",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Why does interactive proof theory yield IP = PSPACE (Shamir 1992)?",
        "options": {
            "A": "Because PSPACE = NP",
            "B": "A PSPACE-complete problem (e.g. TQBF) admits an interactive protocol via arithmetization and sumcheck, showing IP ⊇ PSPACE; the reverse is a standard simulation",
            "C": "Because interactive proofs can't go beyond P",
            "D": "By circular reasoning from IP ⊆ NEXP",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Why is the halting problem NOT in NP?",
        "options": {
            "A": "It is in NP with an infinite certificate",
            "B": "NP requires YES-instances to have polynomial-length verifiable certificates; halting has no such finite certificate for non-halting inputs, and the problem is undecidable, so it is outside the decidable complexity hierarchy entirely",
            "C": "It is in NP but unsolvable",
            "D": "It is NP-complete",
        },
        "correct": "B",
    },

    # ----- TCS/Crypto: AXIOM -----
    {
        "type": "axiom",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Evaluate: 'No algorithm can decide, for an arbitrary program and input, whether the program halts.'",
        "options": {
            "A": "True — Turing's halting theorem, a universal result for any Turing-complete model",
            "B": "False — modern static analyzers decide halting for all programs",
            "C": "True only for nondeterministic machines",
            "D": "True only conditional on P ≠ NP",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Evaluate: 'P ⊆ NP ⊆ PSPACE, and each inclusion is conjectured but not proven strict.'",
        "options": {
            "A": "True — standard complexity hierarchy; separation of any pair would be a field-transforming result",
            "B": "False — P = NP is proved",
            "C": "True, but PSPACE ⊆ P is proved",
            "D": "False — NP ⊈ PSPACE in some models",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Evaluate: 'The Church-Turing thesis asserts that every effectively calculable function is computable by a Turing machine.'",
        "options": {
            "A": "True — this is the standard formulation; not a theorem but a working thesis supported by equivalence of multiple models of computation",
            "B": "False — λ-calculus is strictly more powerful",
            "C": "True and provable from ZFC",
            "D": "False — hypercomputation is proven possible",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Evaluate: 'A cryptographic primitive secure against computationally unbounded adversaries is called information-theoretically (unconditionally) secure.'",
        "options": {
            "A": "True — e.g. the one-time pad with a truly random key as long as the plaintext",
            "B": "False — no such primitives exist",
            "C": "True only in quantum settings",
            "D": "False — information-theoretic security requires a quantum channel",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Evaluate: 'If P = NP, then efficient one-way functions do not exist.'",
        "options": {
            "A": "True — one-way functions require hardness that vanishes under P = NP; inversion would be in P",
            "B": "False — one-way functions are independent of P vs NP",
            "C": "True only for bijective OWFs",
            "D": "False — OWFs exist unconditionally",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Evaluate: 'Every context-free language is decidable.'",
        "options": {
            "A": "True — CFLs are decidable (e.g. CYK algorithm in O(n³)); context-free membership is a specific decidable problem",
            "B": "False — some CFLs are undecidable",
            "C": "True only for deterministic CFGs",
            "D": "False — membership in CFLs is undecidable",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Evaluate: 'Quantum computers offer at best a polynomial speedup over classical for all problems.'",
        "options": {
            "A": "True — BQP is no larger than PH for most problems",
            "B": "False — Shor's algorithm gives exponential speedup for factoring (on quantum) vs best known classical; Grover gives provable quadratic speedup for unstructured search",
            "C": "True — all quantum speedups are constant-factor",
            "D": "True only for search problems",
        },
        "correct": "B",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Evaluate: 'The one-time pad achieves perfect secrecy if and only if the key is truly random, as long as the plaintext, and used exactly once.'",
        "options": {
            "A": "True — Shannon's characterization of perfect secrecy; reusing the key leaks the XOR of plaintexts",
            "B": "False — OTP is computationally secure at best",
            "C": "True only for short messages",
            "D": "False — OTP requires a quantum channel",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Evaluate: 'Randomized reductions can establish NP-hardness just as well as deterministic ones.'",
        "options": {
            "A": "True — randomized polynomial-time reductions preserve NP-hardness; the only caveat is that the target problem's hardness is under randomized reductions, which is standardly accepted",
            "B": "False — only deterministic reductions count",
            "C": "True only if derandomization is possible",
            "D": "False — randomized reductions are undecidable",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Computer Science & Cryptography",
        "question": "Evaluate: 'A perfect zero-knowledge proof leaks NO information about the witness beyond the validity of the statement.'",
        "options": {
            "A": "True — by definition: the verifier's view in an honest execution is simulable without the witness, so no auxiliary information is extracted",
            "B": "False — ZK proofs always leak partial info",
            "C": "True only for NP-complete problems",
            "D": "False — no ZK proof systems exist",
        },
        "correct": "A",
    },

    # =======================================================================
    # DOMAIN 5 — Molecular Biology, Biochemistry & Advanced Neuroscience (30)
    # =======================================================================

    # ----- Biology: IMPULSE -----
    {
        "type": "impulse",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "In E. coli, the principal replicative polymerase is:",
        "options": {
            "A": "DNA polymerase I",
            "B": "DNA polymerase II",
            "C": "DNA polymerase III holoenzyme",
            "D": "DNA gyrase",
        },
        "correct": "C",
    },
    {
        "type": "impulse",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "The resting membrane potential of a typical mammalian neuron is approximately:",
        "options": {
            "A": "−70 mV",
            "B": "+40 mV",
            "C": "0 mV",
            "D": "−200 mV",
        },
        "correct": "A",
    },
    {
        "type": "impulse",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "The primary neurotransmitter at the neuromuscular junction in vertebrates is:",
        "options": {
            "A": "GABA",
            "B": "Acetylcholine",
            "C": "Dopamine",
            "D": "Glutamate",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "CRISPR-Cas9 gene editing relies on which component for sequence-specific DNA recognition?",
        "options": {
            "A": "Protospacer adjacent motif (PAM) alone",
            "B": "A guide RNA (gRNA/sgRNA) that base-pairs with the target DNA, with Cas9 cleaving where the gRNA directs",
            "C": "Restriction endonucleases",
            "D": "Zinc-finger domains",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "In eukaryotic cells, the site of oxidative phosphorylation (ATP synthesis coupled to electron transport) is:",
        "options": {
            "A": "Cytosol",
            "B": "Inner mitochondrial membrane (ETC) with ATP synthase spanning it",
            "C": "Nuclear envelope",
            "D": "Smooth ER",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "The genetic code is degenerate in which sense?",
        "options": {
            "A": "One codon codes for multiple amino acids",
            "B": "Multiple codons code for the same amino acid (except Met and Trp, which have single codons)",
            "C": "Codons are ignored during translation",
            "D": "The code is random",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Long-term potentiation (LTP) at hippocampal synapses is typically mediated by which receptor type?",
        "options": {
            "A": "AMPA receptors only",
            "B": "NMDA receptors, which sense coincident pre- and post-synaptic activity and admit Ca²⁺ to trigger downstream cascades",
            "C": "GABA_A receptors",
            "D": "Metabotropic 5-HT receptors",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "The Hodgkin-Huxley model describes the action potential using voltage-dependent conductances for which ions?",
        "options": {
            "A": "Ca²⁺ and Cl⁻",
            "B": "Na⁺ and K⁺ (plus a leak current)",
            "C": "Mg²⁺ only",
            "D": "H⁺ only",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "The p53 tumor suppressor protein is often called:",
        "options": {
            "A": "'The growth activator'",
            "B": "'The guardian of the genome' — triggers DNA repair, cell-cycle arrest, or apoptosis in response to stress",
            "C": "'The oncogene'",
            "D": "'A housekeeping gene'",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "The Krebs (citric acid / TCA) cycle per acetyl-CoA produces:",
        "options": {
            "A": "1 ATP, 1 NADH, 1 FADH₂",
            "B": "1 GTP/ATP, 3 NADH, 1 FADH₂, 2 CO₂",
            "C": "3 ATP, 0 NADH",
            "D": "1 O₂",
        },
        "correct": "B",
    },

    # ----- Biology: DEEP -----
    {
        "type": "deep",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Prions (e.g. PrP^Sc) challenge the simplest statement of the central dogma because they:",
        "options": {
            "A": "Reverse-transcribe RNA to DNA",
            "B": "Propagate heritable information via self-templated protein conformational change, without any nucleic acid",
            "C": "Encode DNA in lipids",
            "D": "Reverse-translate proteins to DNA",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Why is the lagging strand synthesized discontinuously via Okazaki fragments?",
        "options": {
            "A": "DNA polymerase can synthesize in both directions",
            "B": "DNA polymerase synthesizes only 5'→3'; the lagging strand runs 3'→5' relative to the fork, so it is assembled in short fragments that are later joined by ligase",
            "C": "To avoid mutations",
            "D": "By random diffusion",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Why can identical DNA produce different cell types in a multicellular organism?",
        "options": {
            "A": "Different cells have different DNA",
            "B": "Gene expression is regulated — different transcription-factor programs and epigenetic states (chromatin marks, DNA methylation) select different subsets of genes for transcription in each lineage",
            "C": "By random mutation",
            "D": "Because DNA is copied incorrectly in differentiation",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Why does an action potential propagate only in one direction along an axon?",
        "options": {
            "A": "Axons have physical valves",
            "B": "After firing, voltage-gated Na⁺ channels enter a refractory (inactivated) state, preventing re-firing in the just-depolarized region while the wave moves forward",
            "C": "The myelin only covers one side",
            "D": "It propagates both directions equally",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Why do most enzymes exhibit Michaelis-Menten kinetics at low substrate concentrations?",
        "options": {
            "A": "Because enzymes saturate immediately",
            "B": "Enzyme + substrate form a reversible ES complex; rate-limiting product release yields rate = Vmax · [S] / (Km + [S]), linear in [S] when [S] ≪ Km",
            "C": "Because substrate concentration does not affect rate",
            "D": "Because enzymes are catalytically unlimited",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Why does the chemiosmotic hypothesis (Mitchell) link electron transport to ATP synthesis?",
        "options": {
            "A": "ETC directly phosphorylates ADP",
            "B": "ETC pumps H⁺ across the inner membrane, generating a proton-motive force whose dissipation via ATP synthase drives ADP + Pᵢ → ATP",
            "C": "By thermal coupling",
            "D": "Via direct ATP–electron exchange",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Why does the Hodgkin-Huxley formulation reproduce the observed action-potential shape?",
        "options": {
            "A": "It fits arbitrary data without mechanism",
            "B": "It combines voltage-gated Na⁺ activation/inactivation and K⁺ delayed-rectifier kinetics with a capacitive membrane, yielding a rapid depolarization followed by repolarization and a refractory period",
            "C": "It treats neurons as passive resistors",
            "D": "By assuming sinusoidal currents",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Why is cancer often described as an 'evolutionary' disease within the body?",
        "options": {
            "A": "It is infectious",
            "B": "Somatic cells accumulate heritable mutations; in a tumor, clonal cell populations with higher replication or survival fitness outcompete others via within-body selection, giving cancer many properties of an evolutionary process",
            "C": "Cancer cells evolve back into healthy ones",
            "D": "Cancer mutates faster than possible",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Why can a single gene produce many protein variants in eukaryotes?",
        "options": {
            "A": "Genes duplicate during transcription",
            "B": "Alternative splicing, alternative promoter use, and post-translational modifications yield multiple mature mRNA and protein isoforms from one coding locus",
            "C": "By reverse transcription",
            "D": "By lateral gene transfer",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Why do most drugs exhibit sigmoidal dose-response curves rather than linear ones?",
        "options": {
            "A": "Linear pharmacology is rare in biology",
            "B": "Binding to receptors follows Hill-type saturation kinetics: at low doses, binding is near-linear; at high doses, receptors saturate, producing a sigmoid response",
            "C": "Dose is always ignored",
            "D": "Random biological noise",
        },
        "correct": "B",
    },

    # ----- Biology: AXIOM -----
    {
        "type": "axiom",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Evaluate: 'Natural selection always maximizes the fitness of individual organisms.'",
        "options": {
            "A": "True universally",
            "B": "False — selection acts at multiple levels (gene, individual, kin, group); kin selection, sexually antagonistic selection, intragenomic conflict, and meiotic drive can reduce individual-level fitness while increasing gene-level fitness",
            "C": "True only in haploid organisms",
            "D": "False — selection does not exist",
        },
        "correct": "B",
    },
    {
        "type": "axiom",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Evaluate: 'All known life on Earth uses the same genetic code (with minor variations in mitochondria and a few organisms).'",
        "options": {
            "A": "True — near-universality of the genetic code supports common descent; deviations are rare reassignments (e.g. mitochondrial UGA = Trp)",
            "B": "False — each phylum uses its own code",
            "C": "True only for prokaryotes",
            "D": "False — the code changes across species randomly",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Evaluate: 'All cells arise from pre-existing cells (omnis cellula e cellula).'",
        "options": {
            "A": "True — core tenet of cell theory; consistent with observed biology since Virchow 1855",
            "B": "False — spontaneous generation is routine",
            "C": "True only for eukaryotes",
            "D": "False — viruses violate this",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Evaluate: 'The central dogma is: DNA → RNA → protein, with information flow irreversible.'",
        "options": {
            "A": "True — Crick's original formulation",
            "B": "Partially true — information normally flows DNA → RNA → protein, but reverse transcription (retroviruses: RNA → DNA) is well-documented, complicating the strict 'one-way' reading",
            "C": "False — information flows from protein to DNA",
            "D": "True — retroviruses do not exist",
        },
        "correct": "B",
    },
    {
        "type": "axiom",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Evaluate: 'Every living organism uses ATP as its primary energy currency.'",
        "options": {
            "A": "True — ATP is the universal energy currency across all known life",
            "B": "False — some organisms use only NADH",
            "C": "True only for aerobic organisms",
            "D": "False — plants primarily use glucose as energy currency",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Evaluate: 'Allele frequencies in a large, randomly mating, infinite population remain constant across generations absent selection, mutation, migration, and drift.'",
        "options": {
            "A": "True — Hardy-Weinberg equilibrium, a null model for population genetics",
            "B": "False — drift always changes frequencies",
            "C": "True only for dominant alleles",
            "D": "False — mutation is unavoidable",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Evaluate: 'The resting potential of most neurons is dominated by K⁺ permeability because the cell is highly permeable to K⁺ at rest.'",
        "options": {
            "A": "True — the resting membrane is near E_K (≈ −90 mV) because K⁺ leak channels (e.g. two-pore channels) dominate the resting conductance",
            "B": "False — Na⁺ dominates at rest",
            "C": "True only for myelinated axons",
            "D": "False — there is no resting permeability",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Evaluate: 'Enzymes lower the activation energy of a reaction without changing the reaction's equilibrium constant.'",
        "options": {
            "A": "True — enzymes catalyze by stabilizing the transition state; they speed forward and reverse rates equally, leaving ΔG° unchanged",
            "B": "False — enzymes shift equilibria",
            "C": "True only for hydrolytic enzymes",
            "D": "False — activation energy is not relevant to biology",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Evaluate: 'Most functional genomic information in humans is encoded in the protein-coding ~1.5% of the genome.'",
        "options": {
            "A": "True — all function is in coding sequences",
            "B": "False — a large, still-debated fraction of regulatory, structural, and ncRNA function resides in non-coding sequence; ENCODE and follow-ups report extensive biochemical activity outside coding regions, though the fraction under purifying selection is contested",
            "C": "True — non-coding DNA is junk",
            "D": "False — proteins do not exist in most organisms",
        },
        "correct": "B",
    },
    {
        "type": "axiom",
        "topic": "Molecular Biology, Biochemistry & Advanced Neuroscience",
        "question": "Evaluate: 'DNA replication is semiconservative: each daughter duplex contains one parental and one newly synthesized strand.'",
        "options": {
            "A": "True — established by the Meselson-Stahl experiment (1958)",
            "B": "False — replication is conservative",
            "C": "True only in prokaryotes",
            "D": "False — replication is dispersive",
        },
        "correct": "A",
    },

    # =======================================================================
    # DOMAIN 6 — Analytic Philosophy & Formal Logic (30 questions)
    # =======================================================================

    # ----- Philosophy: IMPULSE -----
    {
        "type": "impulse",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Gettier cases are counterexamples to which classical analysis?",
        "options": {
            "A": "Utilitarianism",
            "B": "Knowledge as justified true belief",
            "C": "Mind-body identity theory",
            "D": "The correspondence theory of truth",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "In modal logic, the formula □(p → q) → (□p → □q) is known as:",
        "options": {
            "A": "Axiom T",
            "B": "Axiom K (distribution axiom); characteristic of all normal modal systems",
            "C": "Axiom 4",
            "D": "Axiom 5",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "The is-ought distinction (Hume's guillotine) claims that:",
        "options": {
            "A": "Descriptive statements entail normative ones",
            "B": "Normative 'ought' claims cannot be logically derived from purely descriptive 'is' claims",
            "C": "All 'ought' statements are false",
            "D": "All 'is' statements are normative",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "The axiom of extensionality in ZF says:",
        "options": {
            "A": "Every set has a complement",
            "B": "Two sets are equal iff they have the same elements (∀x∀y(∀z(z ∈ x ↔ z ∈ y) → x = y))",
            "C": "Sets are ordered",
            "D": "Only finite sets exist",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "The problem of induction, posed by Hume, concerns:",
        "options": {
            "A": "Inferring specific from general",
            "B": "Justifying the inference from observed regularities to unobserved cases (no observation of 'all F are G' follows deductively from 'all observed F are G')",
            "C": "Whether triangles exist",
            "D": "Mathematical induction only",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "In first-order logic, a 'valid' formula is one that is:",
        "options": {
            "A": "True in some model",
            "B": "True in every model (under every interpretation)",
            "C": "Syntactically well-formed",
            "D": "Provable in some axiom system only",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Russell's paradox concerns the set:",
        "options": {
            "A": "The empty set",
            "B": "{x : x ∉ x}; assuming its existence as a set in naive comprehension yields a contradiction",
            "C": "The set of all natural numbers",
            "D": "The powerset of ℝ",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "The Chinese Room argument (Searle) attacks:",
        "options": {
            "A": "The Church-Turing thesis",
            "B": "Strong AI — the claim that a program running on suitable hardware literally understands",
            "C": "Functionalism about emotions",
            "D": "Materialism about the brain",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "De Morgan's laws in propositional logic state:",
        "options": {
            "A": "¬(p ∧ q) ≡ ¬p ∨ ¬q  and  ¬(p ∨ q) ≡ ¬p ∧ ¬q",
            "B": "p → q ≡ ¬p ∨ q",
            "C": "p ∨ ¬p",
            "D": "p ∧ ¬p ≡ ⊥",
        },
        "correct": "A",
    },
    {
        "type": "impulse",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Kripke semantics for modal logic uses:",
        "options": {
            "A": "A single model",
            "B": "A frame ⟨W, R⟩ — worlds W with an accessibility relation R — plus a valuation of propositions in each world",
            "C": "Only classical truth tables",
            "D": "Only syntactic rules",
        },
        "correct": "B",
    },

    # ----- Philosophy: DEEP -----
    {
        "type": "deep",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Why does the liar sentence 'This sentence is false' generate a paradox in classical bivalent logic with an unrestricted truth predicate?",
        "options": {
            "A": "It is syntactically ill-formed",
            "B": "Each possible truth-value assignment (true / false) forces the opposite value via its own content, yielding a contradiction",
            "C": "It has no referent",
            "D": "It is only paradoxical intuitionistically",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Tarski's undefinability theorem shows that:",
        "options": {
            "A": "Truth in arithmetic is definable by an arithmetical formula",
            "B": "No arithmetical formula Tr(x) uniformly expresses 'x is the Gödel number of a true sentence' in the same language, on pain of formalized liar paradox",
            "C": "Truth is a semantic notion only",
            "D": "Arithmetic is decidable",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Why are S4 and S5 modal logics distinguished by the axiom 5 (◇p → □◇p)?",
        "options": {
            "A": "They differ only syntactically",
            "B": "S4 has reflexive + transitive accessibility; S5 further requires symmetry (making R an equivalence), which corresponds to axiom 5 — ensuring any accessible possibility is necessarily possible",
            "C": "Axiom 5 is equivalent to Axiom K",
            "D": "S5 rejects necessity altogether",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Why does Kripke (1980) argue that natural-kind terms are rigid designators?",
        "options": {
            "A": "Because natural kinds are abstract",
            "B": "Names and natural-kind terms pick out the same referent in every possible world where they refer at all — not via descriptive content — so claims like 'water is H₂O' are necessarily true despite being a posteriori",
            "C": "Because words are conventional",
            "D": "Because natural kinds change across worlds",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Why is the 'no miracles' argument offered for scientific realism?",
        "options": {
            "A": "It's a religious argument",
            "B": "It claims that the predictive and technological success of mature scientific theories would be a 'miracle' unless they at least approximately describe mind-independent reality",
            "C": "It denies empirical evidence",
            "D": "It is only applied to physics",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Why does the Ship of Theseus highlight a problem about identity over time?",
        "options": {
            "A": "Because ships are expensive",
            "B": "Replacing every plank raises the question whether numerical identity is preserved by gradual part replacement, exposing the tension between physical continuity and material constitution",
            "C": "Because planks have no identity",
            "D": "Because ships don't persist",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Why is the Duhem-Quine thesis a problem for strict falsificationism?",
        "options": {
            "A": "It supports falsificationism",
            "B": "It holds that hypotheses face experience only as webs — a failed prediction can always be accommodated by revising auxiliary assumptions rather than the target hypothesis, so no hypothesis is straightforwardly falsifiable",
            "C": "Duhem-Quine concerns only physics",
            "D": "It denies empirical content entirely",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Why is the Sorites paradox a problem for classical bivalent logic?",
        "options": {
            "A": "It isn't — classical logic handles it fine",
            "B": "With vague predicates (e.g. 'is a heap'), chain reasoning from clear cases using small increments leads to an evidently false conclusion while each step seems acceptable, challenging sharp cutoffs required by bivalence",
            "C": "It concerns only finite sets",
            "D": "It relies on axiom of choice",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Why does Gödel's second incompleteness theorem constrain Hilbert's programme?",
        "options": {
            "A": "It doesn't",
            "B": "Hilbert sought a finitary consistency proof for classical mathematics within a formal system; Gödel's result shows any sufficient formal system cannot prove its own consistency, so such a proof cannot live within the system being secured",
            "C": "It confirms Hilbert's programme",
            "D": "It applies only to type theory",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Why is the Stanford 'holdout' reading of Bayesian confirmation criticized for the problem of priors?",
        "options": {
            "A": "Priors are always uniform",
            "B": "Bayesian updating converges from many starting priors under regularity, but posterior verdicts depend on priors in the short run, and no non-question-begging way to fix objective priors has achieved consensus — leaving confirmation theory partially agent-relative",
            "C": "Priors are irrelevant to Bayesianism",
            "D": "Priors are uniquely determined by logic",
        },
        "correct": "B",
    },

    # ----- Philosophy: AXIOM -----
    {
        "type": "axiom",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Evaluate: 'If a proposition p is necessarily true, then p is true' — i.e. □p → p.",
        "options": {
            "A": "True — the T axiom, valid in any normal modal system modelling truth (T, S4, S5) and any frame with reflexive accessibility",
            "B": "False — necessity doesn't imply truth",
            "C": "True only in classical propositional logic",
            "D": "True only for empirical propositions",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Evaluate: 'A valid deductive argument with true premises has a true conclusion.'",
        "options": {
            "A": "True — the very definition of deductive validity in classical logic: in every model where premises are true, so is the conclusion",
            "B": "False — deduction can fail",
            "C": "True only for syllogisms",
            "D": "True only if the conclusion is tautologous",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Evaluate: 'In classical logic, p ∨ ¬p (law of excluded middle) holds universally.'",
        "options": {
            "A": "True in classical logic — intuitionistic and paraconsistent logics reject it, but these are non-classical alternatives",
            "B": "False — classical logic rejects LEM",
            "C": "True only for decidable propositions",
            "D": "False — all logics reject LEM",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Evaluate: 'Modus ponens (from p and p → q, infer q) is universally valid in classical logic.'",
        "options": {
            "A": "True — modus ponens is sound in classical propositional logic and a core inference rule in virtually every logic",
            "B": "False — it fails in modal contexts",
            "C": "True only in first-order logic",
            "D": "False — it is a substantive assumption",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Evaluate: 'In any complete bivalent logic, a sentence is either true or false.'",
        "options": {
            "A": "True by definition of bivalence; rejection yields multi-valued or intuitionistic logics",
            "B": "False — bivalence is always inconsistent",
            "C": "True only syntactically",
            "D": "False — truth is non-binary in classical logic",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Evaluate: 'Knowledge requires truth — one cannot know a falsehood.'",
        "options": {
            "A": "True — the factivity of knowledge is a near-universal premise in epistemology; if S knows that p, then p",
            "B": "False — we commonly 'know' false things",
            "C": "True only for a priori knowledge",
            "D": "False — factivity is controversial",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Evaluate: 'Every consistent first-order theory has a model (Gödel's completeness theorem).'",
        "options": {
            "A": "True — completeness theorem: consistency implies satisfiability in first-order logic",
            "B": "False — consistency implies only syntactic provability",
            "C": "True only for finite theories",
            "D": "False — Gödel refuted this",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Evaluate: 'A causal explanation must satisfy the counterfactual conditional: had the cause not occurred, the effect would not have occurred.'",
        "options": {
            "A": "True as a strict universal principle with no exceptions",
            "B": "False — counterfactual analyses of causation face counterexamples (pre-emption, overdetermination) that motivate alternative (e.g. interventionist, process) theories; counterfactual dependence is necessary for some accounts but contested as sufficient",
            "C": "True only in classical mechanics",
            "D": "False — causation has no counterfactual component",
        },
        "correct": "B",
    },
    {
        "type": "axiom",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Evaluate: 'In second-order logic with standard semantics, arithmetic is categorical: the second-order Peano axioms have a unique model up to isomorphism.'",
        "options": {
            "A": "True — Dedekind categoricity of second-order PA",
            "B": "False — PA is never categorical",
            "C": "True only in first-order logic",
            "D": "False — ω and ω+ω are both models",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Analytic Philosophy & Formal Logic",
        "question": "Evaluate: 'If a valid deductive argument has a false conclusion, at least one premise must be false.'",
        "options": {
            "A": "True — by contraposition of 'valid + true premises → true conclusion'; valid arguments preserve truth, so a false conclusion forces at least one false premise",
            "B": "False — validity does not constrain premises",
            "C": "True only in non-classical logics",
            "D": "False — counterexamples exist in first-order logic",
        },
        "correct": "A",
    },

    # =======================================================================
    # DOMAIN 7 — Quantitative Finance & Mathematical Economics (30 questions)
    # =======================================================================

    # ----- Finance: IMPULSE -----
    {
        "type": "impulse",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Under Black-Scholes, the underlying asset price follows which process?",
        "options": {
            "A": "Ornstein-Uhlenbeck",
            "B": "Geometric Brownian motion with constant drift and volatility",
            "C": "Compound Poisson jump",
            "D": "Fractional Brownian motion (H > 1/2)",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "The CAPM (Capital Asset Pricing Model) relates expected excess return to:",
        "options": {
            "A": "Only risk-free rate",
            "B": "E[R_i] − R_f = β_i · (E[R_m] − R_f), where β_i = Cov(R_i, R_m) / Var(R_m)",
            "C": "Only volatility",
            "D": "Duration alone",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "The Sharpe ratio of a portfolio is defined as:",
        "options": {
            "A": "(Expected return − risk-free rate) / standard deviation of return",
            "B": "Expected return / variance",
            "C": "Return / beta",
            "D": "Return × duration",
        },
        "correct": "A",
    },
    {
        "type": "impulse",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "The fundamental theorem of asset pricing (first) states:",
        "options": {
            "A": "Markets are always efficient",
            "B": "A market is arbitrage-free iff there exists an equivalent martingale (risk-neutral) measure",
            "C": "Every asset has the same return",
            "D": "Volatility is constant",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Put-call parity relates European call C and put P (same strike K, maturity T) on an underlying spot S via:",
        "options": {
            "A": "C + P = S + K",
            "B": "C − P = S − K · e^{−rT} (no dividends)",
            "C": "C · P = S · K",
            "D": "C = P always",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "The delta of a European call (Black-Scholes) with strike K, maturity T is:",
        "options": {
            "A": "1",
            "B": "N(d₁), where N is the standard normal CDF",
            "C": "K/S",
            "D": "r · T",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "The Modigliani-Miller theorem (Prop. I, no taxes, no bankruptcy) states:",
        "options": {
            "A": "Firms should use 100% debt",
            "B": "In a frictionless market, firm value is independent of capital structure (debt/equity mix)",
            "C": "Firms should use 0% debt",
            "D": "Dividends are irrelevant only in inflation",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "In the Markowitz mean-variance framework, the efficient frontier consists of portfolios that:",
        "options": {
            "A": "Minimize return for a given variance",
            "B": "Maximize expected return for each level of variance (and vice versa)",
            "C": "Have zero variance",
            "D": "Are fully invested in a single asset",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Duration of a bond (Macaulay) measures:",
        "options": {
            "A": "Time to maturity",
            "B": "Weighted-average time to cash-flow receipt, used as first-order sensitivity of price to yield",
            "C": "Coupon rate",
            "D": "Convexity",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "In a two-period binomial option pricing model with up-factor u, down-factor d, risk-free rate r, the risk-neutral probability of an up-move is:",
        "options": {
            "A": "(u + d) / 2",
            "B": "((1 + r) − d) / (u − d)",
            "C": "1/2",
            "D": "u / (u + d)",
        },
        "correct": "B",
    },

    # ----- Finance: DEEP -----
    {
        "type": "deep",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Why does the Black-Scholes price equal the discounted expected payoff under the risk-neutral measure ℚ rather than the physical measure ℙ?",
        "options": {
            "A": "Investors are empirically risk-neutral",
            "B": "Absence of arbitrage + existence of a self-financing replicating portfolio force the price to equal the discounted ℚ-expectation, where ℚ is the unique martingale measure equivalent to ℙ",
            "C": "The formula assumes zero volatility",
            "D": "Expected returns equal r_f under every measure",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Why is the Black-Scholes delta used for dynamic hedging?",
        "options": {
            "A": "Delta is unrelated to hedging",
            "B": "Maintaining a position of Δ = ∂C/∂S in the underlying cancels first-order P&L from small underlying moves; continuous delta rebalancing replicates the option under BS assumptions",
            "C": "Delta equals gamma",
            "D": "Delta hedging is only theoretical",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Why does volatility smile/skew on equity options contradict pure Black-Scholes?",
        "options": {
            "A": "Implied volatilities agree with BS exactly in practice",
            "B": "BS assumes constant volatility; observed implied vols vary with strike and maturity (smile/skew), reflecting fat tails, jumps, and risk-premia not captured by lognormal dynamics",
            "C": "Smile only exists in FX",
            "D": "Implied volatility is always flat",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Why is VaR (Value-at-Risk) at 99% quantile not a coherent risk measure in general?",
        "options": {
            "A": "It is coherent by Artzner et al.",
            "B": "VaR can fail subadditivity: the VaR of a combined portfolio can exceed the sum of its parts' VaRs (especially in heavy-tailed/non-elliptical distributions), violating coherence; CVaR (expected shortfall) is coherent",
            "C": "VaR is fully monotone",
            "D": "VaR is always convex",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Why does the Kelly criterion recommend betting f* = edge/odds of your bankroll for a favorable bet?",
        "options": {
            "A": "To minimize drawdown",
            "B": "Maximizing expected log-wealth — equivalent to asymptotic geometric growth rate — yields f* = (bp − q)/b for a bet with win-probability p, lose-probability q, odds b",
            "C": "To match the Sharpe ratio",
            "D": "Arbitrary choice",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Why does the efficient market hypothesis in its semi-strong form predict that technical analysis should not produce excess returns on average?",
        "options": {
            "A": "Technical analysis always works",
            "B": "If all public information is already reflected in prices, no public information (including past price history used by TA) can systematically yield risk-adjusted excess returns net of costs",
            "C": "Because markets ignore public news",
            "D": "Because TA is illegal",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Why does Arrow's impossibility theorem constrain collective preference aggregation?",
        "options": {
            "A": "It doesn't",
            "B": "No voting rule aggregating ≥3 alternatives from ≥2 voters' strict preferences can simultaneously satisfy non-dictatorship, unrestricted domain, Pareto, and independence of irrelevant alternatives",
            "C": "It applies only to binary choices",
            "D": "Majority rule satisfies all four criteria",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Why does Girsanov's theorem underpin risk-neutral pricing?",
        "options": {
            "A": "It's irrelevant to finance",
            "B": "Girsanov lets one change measure (from ℙ to ℚ) by a Radon-Nikodym derivative that shifts the drift of a Brownian motion; this turns the discounted asset into a ℚ-martingale, enabling risk-neutral valuation",
            "C": "Girsanov forbids measure change",
            "D": "Girsanov applies only to jump processes",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Why does the CAPM predict that idiosyncratic risk is unpriced?",
        "options": {
            "A": "All risk is priced",
            "B": "Under CAPM's assumptions, investors hold the market portfolio (diversifying away idiosyncratic risk); only systematic (β-exposure) risk cannot be diversified and therefore earns a risk premium",
            "C": "Idiosyncratic risk is always priced",
            "D": "Because CAPM ignores risk",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Why is Nash equilibrium (in pure strategies) not guaranteed to exist in all finite games?",
        "options": {
            "A": "It is guaranteed in pure strategies",
            "B": "Nash's theorem guarantees existence only in mixed strategies for finite games; some games (e.g. matching pennies) have no pure-strategy equilibrium but a unique mixed one",
            "C": "Pure equilibria are never unique",
            "D": "Mixed equilibria don't exist",
        },
        "correct": "B",
    },

    # ----- Finance: AXIOM -----
    {
        "type": "axiom",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Evaluate: 'In a frictionless arbitrage-free market, two self-financing portfolios with identical future cash flows in every state must have identical prices today.'",
        "options": {
            "A": "True — the law of one price, direct consequence of no-arbitrage",
            "B": "False — frictions always break this",
            "C": "True only for riskless bonds",
            "D": "True only under risk neutrality",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Evaluate: 'In a complete, arbitrage-free market, the risk-neutral measure is unique.'",
        "options": {
            "A": "True — second fundamental theorem of asset pricing: completeness is equivalent to uniqueness of the equivalent martingale measure",
            "B": "False — uniqueness requires risk-neutrality",
            "C": "True only in continuous time",
            "D": "False — multiple measures always exist",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Evaluate: 'Under rational expectations, agents' subjective beliefs equal the objective conditional probability given the available information set.'",
        "options": {
            "A": "True as an idealization — rational-expectations equilibrium imposes this consistency; empirical deviations (overconfidence, limited attention) motivate behavioral extensions",
            "B": "False — agents always have correct beliefs",
            "C": "True only in deterministic models",
            "D": "False — subjective beliefs are arbitrary",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Evaluate: 'If markets are complete and arbitrage-free, every contingent claim is replicable by a dynamic trading strategy.'",
        "options": {
            "A": "True — completeness is defined by replicability; pricing reduces to cost of replication",
            "B": "False — some claims are unreplicable by definition",
            "C": "True only for European options",
            "D": "False — replication is impossible in practice",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Evaluate: 'A risk-averse investor will always prefer a certain amount E[X] over a random payoff X with mean E[X].'",
        "options": {
            "A": "True — this is the definition of risk aversion; by Jensen, u(E[X]) ≥ E[u(X)] for concave utilities",
            "B": "False — risk-averse investors prefer risk",
            "C": "True only for log utility",
            "D": "False — risk is unrelated to utility",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Evaluate: 'Arbitrage opportunities cannot persist in liquid markets with rational traders.'",
        "options": {
            "A": "True as an equilibrium principle — competitive traders exploit arbitrage, eliminating it; real markets show small, costly arbitrages that vanish under scrutiny",
            "B": "False — arbitrages are eternal",
            "C": "True only in derivatives markets",
            "D": "False — arbitrage is undefined",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Evaluate: 'Expected utility maximization (von Neumann-Morgenstern) requires four axioms: completeness, transitivity, continuity, and independence.'",
        "options": {
            "A": "True — these four axioms on preferences over lotteries imply representation by a utility function in the expected-utility form (vNM theorem)",
            "B": "False — only transitivity is needed",
            "C": "True only for monetary payoffs",
            "D": "False — expected utility has no axiomatic basis",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Evaluate: 'In a Walrasian competitive equilibrium with complete markets, the allocation is Pareto efficient.'",
        "options": {
            "A": "True — first welfare theorem; assumes no externalities, no public goods, complete information",
            "B": "False — competitive equilibria are always inefficient",
            "C": "True only for two-agent economies",
            "D": "False — Pareto efficiency is undefined",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Evaluate: 'Every finite strategic game has a Nash equilibrium (possibly in mixed strategies).'",
        "options": {
            "A": "True — Nash's theorem, proved via Kakutani's fixed-point theorem on the best-response correspondence",
            "B": "False — existence is only conjectural",
            "C": "True only for zero-sum games",
            "D": "False — some games have no equilibrium",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Quantitative Finance & Mathematical Economics",
        "question": "Evaluate: 'In a Bayesian decision problem, the optimal action minimizes the expected posterior loss.'",
        "options": {
            "A": "True — by definition of Bayes-optimal decisions: choose action minimizing E[L(θ, a) | data]",
            "B": "False — frequentist optimality differs",
            "C": "True only for squared-error loss",
            "D": "False — posterior is irrelevant",
        },
        "correct": "A",
    },

    # =======================================================================
    # DOMAIN 8 — Theoretical Linguistics & Formal Semantics (30 questions)
    # =======================================================================

    # ----- Linguistics: IMPULSE -----
    {
        "type": "impulse",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "In Chomsky's hierarchy, context-free languages are exactly recognized by:",
        "options": {
            "A": "Deterministic finite automata",
            "B": "Nondeterministic pushdown automata",
            "C": "Linear bounded automata",
            "D": "Two-counter machines",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "In Montague semantics, the type ⟨e, t⟩ denotes:",
        "options": {
            "A": "An ordered pair (entity, truth value)",
            "B": "A characteristic function from entities to truth values (a one-place predicate's denotation)",
            "C": "A generalized quantifier over predicates",
            "D": "A modifier on truth values",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "A minimal pair in phonology consists of:",
        "options": {
            "A": "Two phonemes with identical features",
            "B": "Two lexical items differing in exactly one segment, distinguishing meaning (e.g. pat / bat) — evidence /p/ and /b/ are separate phonemes",
            "C": "Two words from different languages",
            "D": "Any two allophones",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "The distinction between 'competence' and 'performance' is due to:",
        "options": {
            "A": "de Saussure",
            "B": "Chomsky (1965), distinguishing the idealized tacit knowledge of a language from its real-time use",
            "C": "Sapir-Whorf",
            "D": "Grice",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Grice's four maxims (cooperative principle) are:",
        "options": {
            "A": "Truth, beauty, goodness, unity",
            "B": "Quality, quantity, relation, manner",
            "C": "Past, present, future, conditional",
            "D": "Syntax, semantics, pragmatics, phonology",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "The concept of 'phoneme' is defined by:",
        "options": {
            "A": "A physical sound",
            "B": "A unit of sound that distinguishes meaning in a language; contrastive with other phonemes in minimal pairs",
            "C": "A written letter",
            "D": "A morpheme",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "The pumping lemma for regular languages is used to:",
        "options": {
            "A": "Prove a language is regular",
            "B": "Prove certain languages are NOT regular, by showing no choice of pumping length admits the decomposition the lemma demands",
            "C": "Count the states of an automaton",
            "D": "Construct grammars",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "The English auxiliary 'do' in 'Do you like it?' is an instance of which phenomenon?",
        "options": {
            "A": "Passive voice",
            "B": "Do-support — insertion of auxiliary 'do' to carry tense/agreement in questions, negations, and emphasis when no other auxiliary is available",
            "C": "Reflexivization",
            "D": "Topicalization",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "The Saussurean sign is characterized by:",
        "options": {
            "A": "A direct referent",
            "B": "The arbitrary pairing of signifier (sound image) with signified (concept)",
            "C": "Iconic resemblance",
            "D": "Grammatical agreement",
        },
        "correct": "B",
    },
    {
        "type": "impulse",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "In formal semantics, the type for a generalized quantifier (like 'every student') is:",
        "options": {
            "A": "e",
            "B": "⟨⟨e, t⟩, t⟩ — function from properties to truth values",
            "C": "t",
            "D": "⟨e, e⟩",
        },
        "correct": "B",
    },

    # ----- Linguistics: DEEP -----
    {
        "type": "deep",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Why does Chomsky's argument from the poverty of the stimulus motivate a nativist account of language acquisition?",
        "options": {
            "A": "Children hear too much language",
            "B": "Children acquire complex grammatical knowledge (e.g. constraints on long-distance dependencies) that is not reliably present or disambiguated by their input, suggesting innate structural principles (Universal Grammar) constrain the hypothesis space",
            "C": "Because all children speak English",
            "D": "Because language cannot be learned",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Why does anaphora like 'Every student thinks he is smart' admit a bound-variable reading?",
        "options": {
            "A": "Because 'he' refers to a specific individual",
            "B": "When 'he' is in the scope of the quantifier 'every student' and is co-indexed with it, it functions as a bound variable — the reading is ∀x (student(x) → thinks(x, smart(x)))",
            "C": "Because English lacks quantifiers",
            "D": "Because pronouns are always referential",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Why do center-embedded sentences like 'The rat the cat the dog chased caught ate the cheese' become difficult to parse?",
        "options": {
            "A": "They are syntactically ungrammatical",
            "B": "Multiple open dependencies exceed working-memory capacity; parsers must hold unresolved NPs in a stack-like buffer, and humans reliably fail beyond ~2 levels, though grammar permits the construction",
            "C": "Because such sentences are semantically incoherent",
            "D": "Because English forbids nesting",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Why is 'John is easy to please' derived differently from 'John is eager to please'?",
        "options": {
            "A": "They have the same structure",
            "B": "'Easy' takes an infinitival clause whose object is coreferential with the matrix subject (tough-movement); 'eager' takes a subject-control structure where John is the PRO subject of 'please'",
            "C": "Both involve raising from object",
            "D": "Neither has a derivation",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Why is the compositionality principle (Frege) a cornerstone of formal semantics?",
        "options": {
            "A": "It is a pragmatic, not semantic, principle",
            "B": "It states the meaning of a complex expression is determined by its constituents' meanings and the syntactic rule combining them; this licenses recursive semantic interpretation and explains productivity of language",
            "C": "Compositionality is rejected in formal semantics",
            "D": "It applies only to context-free grammars",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Why is 'Colorless green ideas sleep furiously' grammatical but semantically ill-formed?",
        "options": {
            "A": "It is ungrammatical",
            "B": "Chomsky's example: syntactically the sentence satisfies English phrase-structure rules, but selectional restrictions on predicates (e.g. 'sleep' requires an animate subject) are violated, producing semantic anomaly without syntactic ill-formedness",
            "C": "Because it has no subject",
            "D": "Because colors cannot be colorless",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Why does Grice propose scalar implicatures (e.g. 'some students passed' often implying 'not all')?",
        "options": {
            "A": "'Some' logically excludes 'all'",
            "B": "Under the maxim of quantity, a cooperative speaker who asserted 'some' when they believed 'all' would be underinformative; so the hearer infers the speaker lacked evidence for 'all', generating the cancelable implicature",
            "C": "Because logic says so",
            "D": "Because 'all' is rarely true",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Why does long-distance wh-movement in English obey island constraints (Ross 1967)?",
        "options": {
            "A": "English forbids all wh-movement",
            "B": "Movement is blocked out of certain domains (complex NP islands, adjunct islands, wh-islands); current theories explain this via locality principles (phase impenetrability, Subjacency, relativized minimality) on the derivational mechanism",
            "C": "Because English lacks questions",
            "D": "Island constraints are language-universal but inexplicable",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Why is optimality theory (Prince & Smolensky) an alternative to rule-based phonology?",
        "options": {
            "A": "It isn't — OT is a rule system",
            "B": "OT replaces ordered rewrite rules with a ranked set of violable universal constraints; the 'optimal' surface form is the candidate minimally violating higher-ranked constraints, with typological variation reduced to constraint rerankings",
            "C": "OT and rule-based approaches are identical",
            "D": "OT handles syntax, not phonology",
        },
        "correct": "B",
    },
    {
        "type": "deep",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Why does Kripke's 'A Puzzle About Belief' threaten naïve substitution of co-referring terms in belief contexts?",
        "options": {
            "A": "Belief is irrelevant to reference",
            "B": "Pierre believes 'Londres est jolie' (in French) and 'London is not pretty' (in English) without knowing they co-refer; substituting co-referring terms in 'Pierre believes...' produces apparent contradiction, so belief contexts are not freely intersubstitutable",
            "C": "Because belief is trivial",
            "D": "Because 'London' and 'Londres' are not co-referring",
        },
        "correct": "B",
    },

    # ----- Linguistics: AXIOM -----
    {
        "type": "axiom",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Evaluate: 'All natural languages are fully intertranslatable without loss of meaning.'",
        "options": {
            "A": "True — meaning is language-independent",
            "B": "False — languages differ systematically in grammaticalized distinctions (evidentiality, aspect pairs, classifier systems, T/V honorifics) that cannot be rendered in a target language without paraphrase, explicit glossing, or omission",
            "C": "True only within the Indo-European family",
            "D": "True only for written languages",
        },
        "correct": "B",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Evaluate: 'Every natural language grammar is describable by a context-free grammar.'",
        "options": {
            "A": "True — CFGs capture all human syntax",
            "B": "False — phenomena like cross-serial dependencies in Swiss German (or reduplication) require at least mildly context-sensitive formalisms (e.g. TAG, CCG); strict CFGs are insufficient",
            "C": "True only for analytic languages",
            "D": "False — natural languages are regular",
        },
        "correct": "B",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Evaluate: 'The principle of compositionality states the meaning of a complex expression is a function of the meanings of its parts and the way they are syntactically combined.'",
        "options": {
            "A": "True — Frege's compositionality principle, foundational in formal semantics",
            "B": "False — compositionality is rejected",
            "C": "True only in logical languages",
            "D": "False — meaning is always holistic",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Evaluate: 'The relationship between signifier and signified in natural language is arbitrary (Saussure).'",
        "options": {
            "A": "True as a general principle — most signs are conventional; onomatopoeia and some iconicity (sound symbolism) are regularized exceptions but do not undermine the rule",
            "B": "False — signs are always iconic",
            "C": "True only in written language",
            "D": "False — signs have natural necessity",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Evaluate: 'All humans without severe cognitive impairment acquire their native language(s) without explicit instruction.'",
        "options": {
            "A": "True — first-language acquisition occurs robustly and quickly in a wide range of input conditions, provided basic exposure; explicit teaching is neither necessary nor typical",
            "B": "False — L1 requires explicit instruction",
            "C": "True only for phonology",
            "D": "False — only L2 acquisition is natural",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Evaluate: 'There exists a critical period for native-like phonological and grammatical acquisition of a first language.'",
        "options": {
            "A": "Broadly true — substantial evidence (e.g. late-signing deaf populations, Genie, second-language phonological attainment) shows declining success of native-level acquisition past early puberty, though the sharpness and nature of the 'period' is debated",
            "B": "False — acquisition is equally easy at all ages",
            "C": "True only for sign languages",
            "D": "False — there is no developmental effect",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Evaluate: 'Truth-conditional semantics assumes that to know the meaning of a declarative sentence is (in part) to know the conditions under which it would be true.'",
        "options": {
            "A": "True — core claim of Davidsonian / model-theoretic semantics; meaning-as-truth-conditions undergirds formal semantic theory",
            "B": "False — meaning is divorced from truth",
            "C": "True only for propositions",
            "D": "False — truth is undefinable",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Evaluate: 'Every language has mechanisms for recursion in the syntax (e.g. embedding of clauses within clauses without grammatical bound).'",
        "options": {
            "A": "True — long-standing Chomskyan view",
            "B": "Contested — Everett (2005) argued Pirahã lacks clausal recursion; the claim is empirically debated, so universality of syntactic recursion is a tentative rather than established axiom",
            "C": "True only in written languages",
            "D": "False — recursion is an artifact of translation",
        },
        "correct": "B",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Evaluate: 'In first-order logic with Montague grammar, quantifier scope ambiguity arises because multiple surface-compatible logical forms exist.'",
        "options": {
            "A": "True — 'Every boy loves some girl' admits both ∀x∃y and ∃y∀x readings; the grammar generates multiple LF derivations (e.g. via quantifier raising), producing distinct truth conditions",
            "B": "False — scope is always determined by surface order",
            "C": "True only in English",
            "D": "False — quantifier ambiguity doesn't exist",
        },
        "correct": "A",
    },
    {
        "type": "axiom",
        "topic": "Theoretical Linguistics & Formal Semantics",
        "question": "Evaluate: 'Information content of a message and its grammaticality are independent dimensions — grammatical sentences can be uninformative, and ungrammatical strings can be informative.'",
        "options": {
            "A": "True — grammaticality is a formal property of structure; informativeness concerns content and context. A grammatical tautology ('It is what it is') can be near-uninformative; a telegram ('Arrive tomorrow') can be highly informative despite being elliptical/ungrammatical",
            "B": "False — grammaticality entails information",
            "C": "True only in pragmatics, not syntax",
            "D": "False — ungrammatical strings carry zero information",
        },
        "correct": "A",
    },
]


# --- Structural invariants (enforced at import time) ---------------------

_EXPECTED_DOMAINS = {
    "Advanced Mathematics & Mathematical Logic",
    "Theoretical Physics",
    "Formal Methods & Programming Language Theory",
    "Theoretical Computer Science & Cryptography",
    "Molecular Biology, Biochemistry & Advanced Neuroscience",
    "Analytic Philosophy & Formal Logic",
    "Quantitative Finance & Mathematical Economics",
    "Theoretical Linguistics & Formal Semantics",
}

assert len(STATIC_QUESTIONS) == 240, f"expected 240 questions, got {len(STATIC_QUESTIONS)}"

_type_counts: dict[str, int] = {"impulse": 0, "deep": 0, "axiom": 0}
_domain_counts: dict[str, int] = {}
_per_domain_type: dict[str, dict[str, int]] = {}
for _q in STATIC_QUESTIONS:
    _type_counts[_q["type"]] = _type_counts.get(_q["type"], 0) + 1
    _domain_counts[_q["topic"]] = _domain_counts.get(_q["topic"], 0) + 1
    _per_domain_type.setdefault(_q["topic"], {}).setdefault(_q["type"], 0)
    _per_domain_type[_q["topic"]][_q["type"]] += 1

assert _type_counts == {"impulse": 80, "deep": 80, "axiom": 80}, \
    f"unbalanced top-level types: {_type_counts}"
assert set(_domain_counts.keys()) == _EXPECTED_DOMAINS, \
    f"domain set mismatch: {set(_domain_counts.keys()) ^ _EXPECTED_DOMAINS}"
for _d, _c in _domain_counts.items():
    assert _c == 30, f"domain {_d!r} has {_c} questions, expected 30"
for _d, _tc in _per_domain_type.items():
    assert _tc == {"impulse": 10, "deep": 10, "axiom": 10}, \
        f"domain {_d!r} has type breakdown {_tc}, expected 10/10/10"

for _q in STATIC_QUESTIONS:
    assert set(_q["options"].keys()) == {"A", "B", "C", "D"}, \
        f"bad options in: {_q['question'][:60]!r}"
    assert _q["correct"] in ("A", "B", "C", "D"), \
        f"bad correct letter in: {_q['question'][:60]!r}"
