from db import sm_get_risorse, sm_get_opportunities, sm_match_score

risorse = sm_get_risorse()
opps = sm_get_opportunities()
print(f"Caricate {len(risorse)} risorse, {len(opps)} opportunity\n")

opp_test = opps[0]
print(f"Test su: {opp_test['titolo']} ({opp_test['main_tech_cluster']})\n")

risultati = sorted([sm_match_score(r, opp_test) for r in risorse], key=lambda x: -x["score"])
print("Top 5 candidati:")
for r in risultati[:5]:
    print(f"  {r['nome']:25} score={r['score']:3}  {r['motivazione']}")
