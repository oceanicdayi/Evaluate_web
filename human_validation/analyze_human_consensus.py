import pandas as pd
import numpy as np

consensus = pd.read_csv("human_validation/private_run/consensus_artifacts.csv", dtype=str, encoding="utf-8-sig")
key = pd.read_csv("human_validation/private_run/artifact_key.csv", dtype=str, encoding="utf-8-sig")
# key has private_id (e.g. GEO_S022, HW2_S022, FINAL_S022) and student_code (e.g. S022)
merged = consensus.merge(key[["artifact_id","private_id","stage","group","automated_media","automated_layout"]], on="artifact_id", validate="one_to_one")
# Extract student code (e.g. S020) from private_id (e.g. HW2_S020, FINAL_S022, GEO_S019)
merged["student_code"] = merged["private_id"].str.replace(r"^(HW2_|FINAL_|GEO_)", "", regex=True)
merged["media_score"] = pd.to_numeric(merged["media_score"], errors="coerce")
merged["layout_score"] = pd.to_numeric(merged["layout_score"], errors="coerce")

valid = merged[merged["media_score"] > 0].copy()

print("=== Human consensus: Seismology_first (first assignment) ===")
hw2 = valid[valid["stage"]=="Seismology_first"]
prior_hw2 = hw2[hw2["group"]=="prior"]
new_hw2 = hw2[hw2["group"]=="new"]
pm = prior_hw2["media_score"].mean()
pl = prior_hw2["layout_score"].mean()
nm = new_hw2["media_score"].mean()
nl = new_hw2["layout_score"].mean()
print(f"Prior group (n={len(prior_hw2)}): media={pm:.2f}, layout={pl:.2f}")
print(f"New group (n={len(new_hw2)}): media={nm:.2f}, layout={nl:.2f}")
print()

print("=== Human consensus: Seismology_final (final report) ===")
final = valid[valid["stage"]=="Seismology_final"]
prior_final = final[final["group"]=="prior"]
new_final = final[final["group"]=="new"]
pfm = prior_final["media_score"].mean()
pfl = prior_final["layout_score"].mean()
nfm = new_final["media_score"].mean()
nfl = new_final["layout_score"].mean()
print(f"Prior group (n={len(prior_final)}): media={pfm:.2f}, layout={pfl:.2f}")
print(f"New group (n={len(new_final)}): media={nfm:.2f}, layout={nfl:.2f}")
print()

# Students with both HW2 and Final - match by student_code
hw2_codes = set(hw2["student_code"])
final_codes = set(final["student_code"])
both_codes = hw2_codes & final_codes
print(f"=== Students with both HW2 and Final: {len(both_codes)} ===")
both_hw2 = hw2[hw2["student_code"].isin(both_codes)].sort_values("student_code")
both_final = final[final["student_code"].isin(both_codes)].sort_values("student_code")
combined = both_hw2[["student_code","group","media_score","layout_score"]].rename(columns={"media_score":"media_hw2","layout_score":"layout_hw2"}).merge(
    both_final[["student_code","media_score","layout_score"]].rename(columns={"media_score":"media_final","layout_score":"layout_final"}),
    on="student_code", validate="one_to_one"
)
combined["media_delta"] = combined["media_final"] - combined["media_hw2"]
combined["layout_delta"] = combined["layout_final"] - combined["layout_hw2"]
print(combined[["student_code","group","media_hw2","media_final","media_delta","layout_hw2","layout_final","layout_delta"]].to_string(index=False))
print()

prior_both = combined[combined["group"]=="prior"]
new_both = combined[combined["group"]=="new"]
pbm = prior_both["media_hw2"].mean()
pbf = prior_both["media_final"].mean()
pbd = prior_both["media_delta"].mean()
pbl = prior_both["layout_hw2"].mean()
pblf = prior_both["layout_final"].mean()
pbld = prior_both["layout_delta"].mean()
nbm = new_both["media_hw2"].mean()
nbf = new_both["media_final"].mean()
nbd = new_both["media_delta"].mean()
nbl = new_both["layout_hw2"].mean()
nblf = new_both["layout_final"].mean()
nbld = new_both["layout_delta"].mean()
print(f"Prior (n={len(prior_both)}): media {pbm:.2f} -> {pbf:.2f} (d={pbd:+.2f}), layout {pbl:.2f} -> {pblf:.2f} (d={pbld:+.2f})")
print(f"New (n={len(new_both)}): media {nbm:.2f} -> {nbf:.2f} (d={nbd:+.2f}), layout {nbl:.2f} -> {nblf:.2f} (d={nbld:+.2f})")
print()

# Cross-semester: Geophysics_final + Seismology_final - match by student_code
print("=== Cross-semester (Geophysics_final -> Seismology_final, prior students only) ===")
geo = valid[valid["stage"]=="Geophysics_final"]
seis_final = valid[valid["stage"]=="Seismology_final"]
geo_codes = set(geo["student_code"])
seis_final_codes = set(seis_final["student_code"])
cross_codes = geo_codes & seis_final_codes
print(f"Students with both semesters final: {len(cross_codes)}")
cross_geo = geo[geo["student_code"].isin(cross_codes)].sort_values("student_code")
cross_seis = seis_final[seis_final["student_code"].isin(cross_codes)].sort_values("student_code")
cross = cross_geo[["student_code","media_score","layout_score"]].rename(columns={"media_score":"media_geo","layout_score":"layout_geo"}).merge(
    cross_seis[["student_code","media_score","layout_score"]].rename(columns={"media_score":"media_seis","layout_score":"layout_seis"}),
    on="student_code", validate="one_to_one"
)
cross["media_delta"] = cross["media_seis"] - cross["media_geo"]
cross["layout_delta"] = cross["layout_seis"] - cross["layout_geo"]
print(cross[["student_code","media_geo","media_seis","media_delta","layout_geo","layout_seis","layout_delta"]].to_string(index=False))
cm = cross["media_geo"].mean()
cs = cross["media_seis"].mean()
cd = cross["media_delta"].mean()
cl = cross["layout_geo"].mean()
cls = cross["layout_seis"].mean()
cld = cross["layout_delta"].mean()
print(f"Mean: media {cm:.2f} -> {cs:.2f} (d={cd:+.2f}), layout {cl:.2f} -> {cls:.2f} (d={cld:+.2f})")