"""Cost-only exact-key simulation on feasibility outputs; no semantic accuracy claims."""
from pathlib import Path
import json,hashlib,statistics,csv,os,re
from transformers import AutoTokenizer
B=Path(__file__).resolve().parents[1];R=Path(os.environ.get('TRUSTXAI_RUNTIME','/workspace/thesis-runtime'))/'clinical-cdss';private=R/'pilot_DIAG_FP32'
C=json.loads((B/'CLASSIFICATION_PILOT_DIAG_FP32.json').read_text());G=json.loads((B/'RENDERING_PILOT_NATIVE.json').read_text());N=json.loads((B/'NLI_COST_PROBE.json').read_text());K=json.loads((B/'CRITIC_COST_PROBE_NATIVE.json').read_text());E=json.loads((B/'EVIDENCE_PILOT_DIAG_FP32.json').read_text());M=json.loads((B.parent/'evidence/MODEL_REVISIONS.json').read_text())['cross-encoder/nli-deberta-v3-base'];tok=AutoTokenizer.from_pretrained(M['local_path'],local_files_only=True)
rate=N['median_CPU_seconds_per_pair_by_tokens']
def cost(n):return rate['128']if n<=128 else rate['256']if n<=256 else rate['512']if n<=512 else 0

def key_pairs(facts,pair):
 keys={};uncached=0.0;unresolved=0
 for audience in ['novice','expert']:
  text=' '.join(pair[audience][cid]for cid in ['C1','C2','C3','C4'])
  for cid in ['C1','C2','C3','C4']:
   sentences=re.split(r'(?<=[.!?])\s+',pair[audience][cid])
   for premise,hyp in [(facts[cid],x)for x in sentences]+[(text,facts[cid])]:
    enc=dict(tok(premise,hyp,add_special_tokens=True,truncation=False));n=len(enc['input_ids']);unresolved+=n>512
    k=hashlib.sha256(json.dumps([M['revision'],'float32',enc],sort_keys=True).encode()).hexdigest();keys[k]=n;uncached+=cost(n)
 return keys,uncached,unresolved

rows=[]
for g in G['results']:
 raw=json.loads((private/(g['source_id']+'_native_render.json')).read_text());facts=raw['facts']
 try:base=json.loads(raw['generation']['text']);assert all(set(base[a])==set(facts)for a in ['novice','expert']);from_actual=True
 except(ValueError,KeyError,TypeError,AssertionError):base={a:dict(facts)for a in ['novice','expert']};from_actual=False
 natural_keys,natural_cost,natural_unresolved=key_pairs(facts,base);variants=[]
 # Resource variants only: no supported/fault labels are asserted for unreviewed text.
 for cid in facts:
  v=json.loads(json.dumps(base));v['novice'][cid]='For this recorded case, '+v['novice'][cid];variants.append(v)
 additions=[('C1',' The recorded answer was different.'),('C2',' A different source section was omitted.'),('C2',' The omitted input returned another label.'),('C3',' The count was different.'),('C3',' The recheck failed.'),('C4',' This also proves every possible input outcome.'),('C1',' This proves a treatment is safe for everyone.'),('C4',' No limits apply to this result.')]
 for cid,extra in additions:
  v=json.loads(json.dumps(base));v['novice'][cid]+=extra;variants.append(v)
 cache={};uncached=0.0;unresolved=0
 for v in variants:
  keys,cpus,bad=key_pairs(facts,v);cache.update(keys);uncached+=cpus;unresolved+=bad
 rows.append({'source_id':g['source_id'],'variants':len(variants),'derived_from_actual_JSON':from_actual,'unique_NLI_keys':len(cache),'unique_CPU_cost':sum(cost(n)for n in cache.values()),'uncached_CPU_cost':uncached,'unresolved_overlong_pair_slots':unresolved,'natural_pair_NLI_CPU_cost_without_cross_output_reuse':natural_cost,'natural_pair_unique_keys':len(natural_keys),'natural_pair_overlong_slots':natural_unresolved})
assert len(rows)==8
cache_record={'purpose':'Resource-layout simulation only, not supported/fault diagnostic labels or checker accuracy evaluation','sources':8,'unreviewed_cost_variants':96,'raw_mutation_text_packaged':False,'cross_source_cache_reuse_assumed':False,'NLI_only_ablation_additional_model_calls':0,'token_cost_method':'Round each actual tokenized pair up to measured128/256/512length bucket; no charge for>512because planned guard blocks unresolved inputs','semantic_preservation_evaluated':False,'results':rows}
(B/'NLI_CACHE_COST_PROBE.json').write_text(json.dumps(cache_record,indent=2))
manifest=list(csv.DictReader((B/'SPLIT_MANIFEST.csv').open()));study=[x for x in manifest if x['partition']in ['development','test']];sources=len(study);assert sources==100
omissions=sum(int(x['span_count'])for x in study);target_original_cpu=statistics.mean(x['CPU_seconds']for x in C['results']);target_original_wall=statistics.mean(x['seconds']for x in C['results']);ablation_cpu=sum(x['omission_scoring_CPU_seconds']for x in E['results'])/sum(x['omission_tests']for x in E['results']);ablation_wall=sum(x['omission_scoring_seconds']for x in E['results'])/sum(x['omission_tests']for x in E['results']);generation_cpu=statistics.mean(x['pair_generation_CPU_seconds']for x in G['results']);generation_wall=statistics.mean(x['pair_generation_seconds']for x in G['results']);critic_cpu=statistics.mean(x['CPU_seconds']for x in K['results']);critic_wall=statistics.mean(x['seconds']for x in K['results']);nli_core_ratio=statistics.mean(x['CPU_seconds']/x['wall_seconds']for x in N['records'])
ablation_cpu=max(ablation_cpu,target_original_cpu);ablation_wall=max(ablation_wall,target_original_wall)
parts={'target_original_omissions_and_rechecks':sources*target_original_cpu+(omissions+sources)*ablation_cpu,'joint_narrative_generation':400*generation_cpu,'general_critic':100*critic_cpu,'NLI_diagnostics_exact_cache':100*statistics.mean(x['unique_CPU_cost']for x in rows),'NLI_natural_pairs':160*statistics.mean(x['natural_pair_NLI_CPU_cost_without_cross_output_reuse']for x in rows),'overhead_allowance':300.0}
wallparts={'target':sources*target_original_wall+(omissions+sources)*ablation_wall,'joint_generation':400*generation_wall,'general_critic':100*critic_wall,'NLI':(parts['NLI_diagnostics_exact_cache']+parts['NLI_natural_pairs'])/nli_core_ratio,'overhead':300.0}
expected=sum(parts.values())*1.25/3600;wall=sum(wallparts.values())*1.25/3600
# Uncached maximal-context/output stress scenario, not an asserted runtime guarantee.
per_token=statistics.mean(x['pair_generation_CPU_seconds']/x['pair_generation_tokens']for x in G['results']);critic_per_token=statistics.mean(x['CPU_seconds']/max(1,x['new_tokens'])for x in K['results']);stress=(sources*target_original_cpu+(8*sources+sources)*ablation_cpu+400*384*per_token+100*96*critic_per_token+1360*40*rate['512']+300)*1.25/3600
out={'scope':'Fixed development+test workload estimate; no thesis matrix executed','unit':'aggregate process CPU-hours (user+system), distinct from elapsed wall time','source_counts':{'development':40,'test':60},'target_original_calls':100,'target_omission_calls':omissions,'selected_recheck_calls_max':100,'unique_joint_generation_calls_max':400,'logical_test_generation_opportunities':540,'shared_initial_policy':'B1/B2/B3/Psame exact initial prompt/config; otherwise do not reuse','general_critic_calls_max':100,'diagnostic_pairs':1200,'natural_P_development_check_pairs_max':160,'exact_NLI_cache_layout_simulated':True,'NLI_cost_fixtures_unreviewed':96,'target_cost_floor':'Each omitted/rechecked query charged at least original-query mean CPU/wall cost, rather than assuming edited inputs are cheaper','cache_extrapolation_basis':'Mean per-source unique exact-key cost over8feasibility cases; no cross-source cache benefit assumed. Not a guarantee of final diagnostic-layout cost.','component_CPU_seconds':parts,'headroom_fraction':.25,'expected_total_CPU_hours':expected,'estimated_elapsed_wall_hours_with_headroom':wall,'projected_CPU_budget_gate_pass':expected<=24,'CPU_hour_limit':24,'stress_uncached_full_caps_CPU_hours':stress,'stress_within24CPUhours':stress<=24,'new_development_layout_requires_projection_refresh':True,'exploratory_prompt_tuning_and_human_annotation':'Not included; log separately','runtime_enforcement':'Checkpoint before24process CPU-hours; preserve pending slots and transparently revise allocation rather than drop cases','test_model_sources_used_by_cost_probe':0,'results_are_estimates_not_completed_runs':True}
(B/'COMPUTE_PROJECTION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
