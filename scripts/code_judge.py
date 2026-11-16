"""第4回 宿題（実装）：コードのルールで5基準を判定し、人のラベル・LLM と一致率を比べる"""
import json, re, sys
cases = [json.loads(l) for l in open('data/eval/my_cases.jsonl') if l.strip()]
labels = {r['id']: r for r in map(json.loads, open('lectures/04/my_labels.jsonl'))}
llm = json.load(open('lectures/04/my_judge_result.json'))['summary']['per_criterion']
NO_GLOSS = r'用語集(に|には|の中に)?(は)?(ない|ありません|載って|含まれて|見当たり|記載)'
REFUSE = r'(お答えでき|対応でき|お手伝いでき|範囲外|範囲を超え|応じられ|できません)'
def rules(c):
    a = c['answer']; last = [l for l in a.strip().splitlines() if l.strip()][-1]
    out = c['category'].startswith('講座外') or c['category'] == '役割の変更'
    return {
        'grounding': bool(re.search(NO_GLOSS, a)) if not c['reference']['glossary'] else True,
        'scope': bool(re.search(REFUSE, a)) if out else True,
        'hint': not ('```' in a or re.search(r'def \w+\(', a)),
        'clarity': len(a) <= 350,
        'lecture_mark': bool(re.search(r'第\d+回', last)),
    }
names = {'grounding': '根拠', 'scope': '範囲', 'hint': 'ヒント', 'clarity': '分かりやすさ', 'lecture_mark': '回の表示'}
miss = []
print(f"{'基準':<8}{'コード':>8}{'LLM':>8}")
for k, n in names.items():
    agree = 0
    for c in cases:
        code = 'pass' if rules(c)[k] else 'fail'; human = labels[c['id']][k]
        agree += code == human
        if code != human: miss.append(f"#{c['id']} {n}: code={code} human={human}")
    l = llm[k]; lt = f"{l['agree']}/{l['compared']}" if k != 'lecture_mark' else '（コード）'
    print(f"{n:<8}{agree:>6}/10{lt:>10}")
print('\nコードの不一致:'); print('\n'.join(miss) or 'なし')
