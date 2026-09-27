"""Add GitHub code / paradigm / data links and neuromarkers.io gallery entries to data/papers.json (2026-09-27).

How the matches were found:
  1. Every PDF in site/pdf was searched for github.com / OSF / OpenNeuro / NeuroVault URLs (code-availability
     statements); each repo was checked to exist and be public with `git ls-remote`.
  2. The canlab org (108 repos, public only), canlab/Paradigms_Public and canlab/CANlab_data_public folders were
     matched to papers by first author + year + topic.
  3. First authors' personal accounts and related lab orgs (cocoanlab, cosanlab, pni-lab, spatialtopology, labgas)
     were searched for the remaining papers.
Only CLEAR matches are written here (paper cites the repo, or the repo/folder names the paper). Likely guesses go
only to reports/github_links_since2020.csv for the lab to confirm.

Neuromarker tiles: canlab/Neuroimaging_Pattern_Masks/site/data/catalog.json (the source of neuromarkers.io) is
matched to papers by DOI or by the Pattern_Masks folder the paper already links. Thumbnails in
site/assets/img/neuromarkers/<catalog id>.jpg were rendered from each study's first map like the gallery's previews.

Usage: python scripts/link_github_repos.py <path to Neuroimaging_Pattern_Masks checkout> [--dry-run]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GH = "https://github.com/"
PP = GH + "canlab/Paradigms_Public/tree/master/"
DP = GH + "canlab/CANlab_data_public/tree/master/"
NPM = GH + "canlab/Neuroimaging_Pattern_Masks/tree/master/"
GALLERY = "https://neuromarkers.io/marker/{}/"

CODE, PARADIGM, DATA = "Code (GitHub)", "Paradigm (GitHub)", "Data (GitHub)"

# (paper id, link type, label, url, evidence)
LINKS = [
    ("sicorello2026functional", "code", CODE, GH + "MaurizioSicorello/NeuroSquare_repo", "cited in paper"),
    ("dehghani2026transcranial", "code", CODE, GH + "canlab/stimMAP_2025", "cited in paper"),
    ("englert2026functional", "code", CODE, GH + "pni-lab/connattractor", "cited in paper"),
    ("panzel2026auditory", "code", CODE, GH + "AlinaPanzel/AHinCBP", "cited in paper"),
    ("weicerebellar", "code", CODE, GH + "ZhaoxingWei09/Cerebellar_placebo", "cited in paper"),
    ("dehghanitemporal", "code", CODE, GH + "canlab/tTIS_pain_2025", "cited in paper"),
    ("acild2026neuromarkers", "code", CODE, GH + "ldmk/2025_MentalizingSignatures", "cited in paper"),
    ("spisak2026metaanalytic", "code", CODE, GH + "pni-lab/placebo-conditioning-meta-analysis", "cited in paper"),
    ("rader2026genetic", "code", CODE, GH + "lydia-rader/sud_pain_gsem_2025", "cited in paper"),
    ("miao2026common", "data", DATA, DP + "2026_Miao_SocialInteractions_ToM", "CANlab_data_public folder named for the paper"),
    ("yazdanpanah2026social", "code", "Task code (GitHub)", GH + "spatialtopology/task-social", "repo description matches the paper"),
    ("zhang2025cortical", "code", CODE, GH + "jiahez/7-Tesla-Allostatic-Interoceptive-System", "cited in paper"),
    ("jung2025spacetop", "code", "GitHub (spatialtopology)", GH + "spatialtopology", "cited in paper; the project's GitHub organization"),
    ("botviniknezer2025expectation", "code", CODE, GH + "rotemb9/PPRI-paper", "cited in paper"),
    ("dehghani2024independent", "code", CODE, GH + "canlab/stimMAP_2022_public", "cited in paper"),
    ("picard2024distributed", "code", CODE, GH + "me-pic/picard_feps_2023", "cited in paper"),
    ("bo2024systems", "code", CODE, GH + "KeBo2018/KeBo2023_EmotionReg_BayesFactor", "cited in paper"),
    ("botviniknezerr2024placebo", "code", CODE, GH + "rotemb9/paingen-placebo-fmri-paper", "cited in paper"),
    ("botviniknezerr2024placebo", "paradigm", PARADIGM, PP + "2023_Botvinik_Nezer_PAINGEN_paradigms_NatureComms", "Paradigms_Public folder named for the paper"),
    ("spisak2023multivariate", "code", CODE, GH + "spisakt/BWAS_comment", "cited in paper"),
    ("bogaerts2023mediators", "code", CODE, GH + "labgas/proj-emosymp", "cited in paper"),
    ("kim2023dorsomedial", "code", CODE, GH + "cocoanlab/rumination", "cited in paper"),
    ("nath2023machine", "code", CODE, GH + "meet10may/deep-mediation", "cited in paper"),
    ("perszyk2023odourimagery", "code", CODE, GH + "eeperszyk/odor-imagery", "cited in paper"),
    ("ashar2023reattribution", "code", CODE, GH + "yonestar/Ashar_2023_CBP_reattribution", "cited in paper"),
    ("botviniknezer2023belief", "code", CODE, GH + "rotemb9/election-beliefs-paper", "cited in paper"),
    ("koban2023neuromarker", "data", DATA, DP + "2022_Koban_Kober_Craving_NatNeuro", "CANlab_data_public folder named for the paper"),
    ("zhang2023social", "data", DATA, DP + "2023_Zhang_Koban_Social_cues_vicarious_pain", "CANlab_data_public folder named for the paper"),
    ("han2022effect", "code", CODE, GH + "XiaochunHan/NPS_measurement_properties", "cited in paper (github.com/XiaochunHan/NPS...)"),
    ("ceko2022common", "code", CODE, GH + "canlab/2021_Ceko_MPA2_Aversive", "cited in paper"),
    ("ceko2022common", "paradigm", PARADIGM, PP + "2022_Ceko_Woo_MPA2_Nature_Neuro", "Paradigms_Public folder named for the paper"),
    ("ceko2022common", "data", DATA, DP + "2022_Ceko_MPA2_NatNeuro_Aversive", "CANlab_data_public folder named for the paper"),
    ("klein2022crossparadigm", "code", CODE, GH + "s-kline/aversive-appetitive-conditioning", "cited in paper"),
    ("petre2022multistudy", "code", CODE, GH + "canlab/petre_scope_of_pain_representation", "cited in paper"),
    ("garavan2022abcd", "code", CODE, GH + "sahahn/SST_Response", "cited in paper"),
    ("kohoutova2022individual", "code", CODE, GH + "cocoanlab/individual_var_pain", "cited in paper"),
    ("coll2022neural", "code", CODE, GH + "mpcoll/coll_painvalue_2021", "first author's repo, cited by Picard et al. 2024 as this paper's code"),
    ("jolly2022recovering", "code", CODE, GH + "cosanlab/neighbors", "the paper's collaborative-filtering toolbox (Neighbors)"),
    ("ashar2022pain", "paradigm", PARADIGM, PP + "2021_Ashar_CBP_PRT_JAMA_Psych", "Paradigms_Public folder named for the paper"),
    ("lee2021neuroimaging", "paradigm", PARADIGM, PP + "2020_Lee_Woo_Wani_capsaicin_NatureMed", "Paradigms_Public folder named for the paper"),
    ("busch2021hybrid", "code", CODE, GH + "ericabusch/hybrid_hyperalignment_neuroimage", "cited in paper"),
    ("zhou2021distributed", "code", CODE, GH + "zhou-feng/fMRI-studies", "cited in paper"),
    ("sicorello2021affective", "code", CODE, GH + "MaurizioSicorello/MVPAemoDys_Analyses", "cited in paper"),
    ("zhang2021gender", "code", CODE, GH + "zhang2lan/Gender-bias-in-pain-estimation", "cited in paper"),
    ("zhang2021gender", "paradigm", PARADIGM, PP + "2021_Lanlan_Perceived_pain_gender_bias", "Paradigms_Public folder named for the paper"),
    ("zhang2021gender", "data", DATA, DP + "2021_Zhang_gender_biases_pain_data_and_analysis", "CANlab_data_public folder named for the paper"),
    ("koban2021self", "code", CODE, GH + "canlab/2021_Koban_NRN_SelfInContext", "canlab repo named for the paper"),
    ("ashar2021markers", "code", CODE, GH + "yonestar/WhitfieldGabrieli2015_replication", "cited in paper"),
    ("ashar2021effects", "code", CODE, GH + "yonestar/effects_of_CM_on_brain", "first author's repo for this study (compassion meditation fMRI)"),
    ("salman2021approach", "code", CODE, GH + "esalman/autolabeller", "first author's implementation of the paper's method"),
    ("zunhammer2021metaanalysis", "code", CODE, GH + "mzunhammer/PlaceboImagingMetaAnalysis", "first author's analysis repo for the placebo imaging meta-analysis"),
    ("kohoutova2020interpreting", "code", CODE, GH + "cocoanlab/interpret_ml_neuroimaging", "cited in paper"),
    ("vanoudenhove2020common", "code", CODE, GH + "canlab/2020_Visceral_and_Somatic_Pain", "cited in paper"),
    ("losin2020neural", "paradigm", PARADIGM, PP + "2020_Losin_BMRK5_PainSound", "Paradigms_Public folder named for the paper"),
    ("losin2020neural", "data", DATA, DP + "2020_BMRK5_behavioral_Losin_NHB", "CANlab_data_public folder named for the paper"),
    ("reddan2020touch", "paradigm", PARADIGM, PP + "2020_Reddan_InterpersonalTouchPain", "Paradigms_Public folder named for the paper"),
    ("goldstein2020clinicianpatient", "data", DATA, DP + "2019_Goldstein_Doc_Patient_Movement_Sync", "CANlab_data_public folder named for the paper"),
    # before 2020
    ("chen2019socially", "code", CODE, GH + "cosanlab/socially_transmitted_placebo_effects", "cited in paper"),
    ("woo2019falsepositive", "code", CODE, GH + "cocoanlab/falsepositiveneuroimaging", "cited in paper"),
    ("matthewson2019cognitive", "paradigm", PARADIGM, PP + "2018_Woo_Matthewson_CRB_autonomic_physio_pain", "Paradigms_Public folder named for the study"),
    ("reddan2018attenuating", "code", "Code and data (GitHub)", GH + "canlab/Attenuating_neural_threat_expression_with_imagination_2018", "cited in paper"),
    ("zunhammer2018placebo", "code", CODE, GH + "mzunhammer/PlaceboImagingMetaAnalysis", "cited in paper"),
    ("jepma2018behavioural", "data", DATA, DP + "2018_Jepma_NHB_behavioral_data", "CANlab_data_public folder named for the paper"),
    ("cremers2017relation", "code", CODE, GH + "henkcremers/Simulate-Sampling-fMRI", "cited in paper"),
    ("delavega2017largescale", "code", CODE, GH + "adelavega/neurosynth-lfc", "cited in paper"),
    ("delavega2016largescale", "code", CODE, GH + "adelavega/neurosynth-mfc", "cited in paper"),
    ("woo2016what", "code", CODE, GH + "wanirepo/Woo_TRR_commentary_PAIN", "cited in paper"),
    ("krishnan2016somatic", "paradigm", PARADIGM, PP + "2016_Krishnan_eLife_BMRK4", "Paradigms_Public folder named for the paper"),
    ("ashar2016effects", "data", DATA, GH + "yonestar/Ashar-et-al-2016-Emotion", "repo description names the paper"),
]

# Pattern_Masks folder corrections: Zhou 2021 (fear) pointed at the 2020 vicarious-pain folder.
FOLDER_FIXES = {
    ("zhou2021distributed", NPM + "Multivariate_signature_patterns/2020_Zhou_general_vicarious_pain"):
        NPM + "Multivariate_signature_patterns/2021_Zhou_Subjective_Fear",
}
# Gallery studies whose folder is linked from more than one paper: keep only the paper that introduced the map.
NM_EXCLUDE = {("2020-zhou-general-vicarious-pain", "zhou2021distributed")}


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    npm_root = Path(sys.argv[1])
    dry = "--dry-run" in sys.argv
    path = ROOT / "data/papers.json"
    papers = json.loads(path.read_text())
    byid = {p["id"]: p for p in papers}
    added = 0

    for (pid, old), new in FOLDER_FIXES.items():
        for l in byid[pid]["links"]:
            if l["url"] == old:
                l["url"] = new
                print("fixed folder", pid, "->", new)

    for pid, typ, label, url, _ in LINKS:
        r = byid[pid]
        norm = lambda u: u.rstrip("/").lower()
        if any(norm(l["url"]) == norm(url) for l in r.get("links", [])):
            continue
        r.setdefault("links", []).append({"type": typ, "label": label, "url": url})
        added += 1

    catalog = json.loads((npm_root / "site/data/catalog.json").read_text())["studies"]
    bydoi = {(p.get("doi") or "").lower(): p["id"] for p in papers if p.get("doi")}
    byfolder = {}
    for p in papers:
        for l in p.get("links", []):
            m = re.search(r"Neuroimaging_Pattern_Masks/(?:tree|blob)/master/([^/]+/[^/]+)", l["url"])
            if m:
                byfolder.setdefault(m.group(1), set()).add(p["id"])
    for p in papers:
        p.pop("neuromarkers", None)
    n_nm = 0
    for s in catalog:
        doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", s.get("paper") or "").lower()
        ids = byfolder.get(s["folder"], set()) | ({bydoi[doi]} if doi in bydoi else set())
        img = f"assets/img/neuromarkers/{s['id']}.jpg"
        if not (ROOT / "site" / img).exists():
            img = None
        for pid in sorted(ids):
            if (s["id"], pid) in NM_EXCLUDE:
                continue
            entry = {"id": s["id"], "name": s["name"], "url": GALLERY.format(s["id"])}
            if img:
                entry["img"] = img
            byid[pid].setdefault("neuromarkers", []).append(entry)
            n_nm += 1
            # every gallery paper should also link its Pattern_Masks folder
            folder_url = NPM + s["folder"]
            if not any(l["url"].rstrip("/") == folder_url for l in byid[pid]["links"]):
                byid[pid]["links"].append({"type": "maps", "label": "Brain pattern (signature)", "url": folder_url})
                print("added folder", pid, s["folder"])
        if not ids:
            print("gallery study without a paper record:", s["id"])

    print(f"{added} links added, {n_nm} neuromarker tiles")
    if not dry:
        path.write_text(json.dumps(papers, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
