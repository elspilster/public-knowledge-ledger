# Initial PKL Knowledge Corpus

This is a small pilot corpus for exercising PKL's claim, evidence, provenance, independence, challenge, and assessment model.

It is intentionally a **fixture and review dataset**, not a declaration that PKL has independently established these claims. Each entry should be converted into ledger events by the ingestion/assessment layer as that work matures.

## Pilot claims

### K001 — Earth is approximately spherical

**Claim:** Earth is approximately spherical, more precisely an oblate spheroid.

**Evidence candidates:**
- NASA Earth facts and Earth-observing material.
- NOAA geodesy material describing Earth's shape and geoid.
- Direct geodetic observations such as measurements of Earth's curvature/shape.

**Test purpose:** Strong convergence from physically distinct measurement methods.

**Provenance note:** News or educational pages derived from the same NASA/NOAA material should not automatically count as independent evidence.

### K002 — Water freezes at approximately 0°C at standard atmospheric pressure

**Claim:** Pure water's freezing point is approximately 0°C at standard atmospheric pressure.

**Evidence candidates:**
- NIST thermophysical data.
- IAPWS reference material.
- Independent laboratory measurement.

**Test purpose:** Straightforward, highly reproducible claim.

### K003 — Earth orbits the Sun

**Claim:** Earth follows an orbit around the Sun.

**Evidence candidates:**
- NASA Solar System dynamics material.
- Independent astronomical observations and orbital calculations.

**Test purpose:** Convergence between observational astronomy and dynamical modelling.

### K004 — DNA carries hereditary information

**Claim:** DNA is the principal hereditary material in cellular life, with important biological exceptions and qualifications depending on the organism/context.

**Evidence candidates:**
- Primary molecular-biology research.
- Established experimental evidence on DNA replication and inheritance.
- Modern reference material that traces claims back to primary literature.

**Test purpose:** Tests a claim that needs careful wording rather than an over-broad absolute.

### K005 — Jupiter is a planet in the Solar System

**Claim:** Jupiter is a planet in the Solar System.

**Evidence candidates:**
- NASA Solar System exploration data.
- Independent astronomical observations.

**Test purpose:** Simple observational claim suitable for a baseline case.

### K006 — Penicillin has antibacterial activity

**Claim:** Penicillin-class antibiotics can inhibit or kill susceptible bacteria through interference with bacterial cell-wall synthesis.

**Evidence candidates:**
- Original antibiotic research.
- Modern pharmacology/microbiology references.
- Controlled laboratory observations.

**Test purpose:** Tests a scientific claim with mechanism, replication, and scope conditions.

### K007 — Lightning is an electrical discharge

**Claim:** Lightning is a large-scale electrical discharge in the atmosphere.

**Evidence candidates:**
- NOAA atmospheric electricity material.
- Laboratory/field observations and physical models of lightning.

**Test purpose:** Tests convergence between observation and physical explanation.

### K008 — Increased atmospheric CO2 contributes to warming

**Claim:** Increasing atmospheric carbon dioxide contributes to warming of Earth's climate system through its radiative properties.

**Evidence candidates:**
- IPCC assessment literature.
- Direct atmospheric/radiative measurements.
- Independent climate modelling and observational studies.

**Test purpose:** A real-world claim with extensive evidence, modelling, uncertainty, and potential for derivative reporting. The corpus should preserve uncertainty rather than reduce it to a slogan.

### K009 — Mixed-evidence case

**Claim:** A deliberately selected contemporary claim with credible evidence on multiple sides.

**Evidence candidates:** To be selected during the M2/M7 pilot from at least two genuinely distinct evidence families.

**Test purpose:** Ensure PKL does not merely produce sensible results for settled textbook facts.

**Initial status:** `uncertain` until a concrete claim and evidence set are selected.

### K010 — Provenance-collision case

**Claim:** A claim reported by several outlets where most or all reports can be traced to one original source.

**Evidence candidates:**
- One primary source.
- Three or more derivative reports that explicitly cite or reproduce it.
- One genuinely independent source if available.

**Test purpose:** Exercise provenance-aware independence. Repetition must not masquerade as independent corroboration.

## Corpus rules

1. Prefer primary or authoritative sources where possible.
2. Record the actual source identity and provenance relationship rather than relying on publication count.
3. Preserve supporting and contradicting evidence.
4. Do not infer truth from source prestige alone.
5. Keep claim wording narrow enough that the evidence can actually address it.
6. When evidence is incomplete or contested, represent that state explicitly.
7. This corpus is a testbed for PKL and is expected to change as external reviewers identify weaknesses.

## Next step

M2 should provide a reproducible path from these fixture records to ledger events and an explainable claim assessment. M7 should replace/augment the fixture candidates with fully cited real-world evidence packages and adversarial review.