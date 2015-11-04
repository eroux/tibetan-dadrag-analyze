#!/usr/bin/env python3

import re
from icu import RuleBasedCollator


#dd_reg = re.compile('(?P<syl>[\u0F40-\u0FBC]+(?P<final>(?P<rorl>ལ|ར)|ན))(?P<dd>ད?)(?P<second>་(?P<dds>ཏོ|ཅེ་ན|ཅིང|ཅིག|ཅེའོ|ཅེས|ཏམ|ཀྱང|ཏུ|(?(rorl)པ(?:འི|འོ|ར|ས|འམ|འང)?))|་(?P<ndds>(?P=final)\u0F7C|(?P=final)མ|ཤིག|ཤེས|ཤེ་ན|ཤེའོ|ཤིང|ཞེ་ན|ཞིང|ཞིག|ཞེའོ|ཞེས|ཡང|དུ|(?(rorl)བ(?:འི|ར|ས|འོ|འམ|འང)?)))?(?:[^\u0F40-\u0FBC]|$)')
#verbs_reg = re.compile('(?:(?:[^\u0F40-\u0FBC]|\A)(?P<neg>མི?་))?(?P<syl>[\u0F40-\u0FBC]+(?P<final>[\u0F40-\u0FBC]))་(?P<second>(?P<noun>འདི|རྣམས)|(?P<past>ན|ཏེ|སྟེ|དེ|ཅིང|ཞིང|ཤིང|པ་དང|བ་དང|བ་ལས|པ་ལས|པས|བས|(?P=final)\u0F7C)|(?P<cig>ཅིག|ཞིག|ཤིག)|(?P<fut>(?:དུ|ཏུ)་(?:མི་རུང|རུང|ཡོད|མེད|གྲགས))|(?P<pres>ནས))(?:[^\u0F40-\u0FBC]|$)')

verbs_reg = re.compile('(?:(?:[^\u0F40-\u0FBC]|\A)(?P<neg>མི?་))?(?P<syl>[\u0F40-\u0FBC]+(?P<final>[\u0F40-\u0FBC]))་(?P<second>(?P<noun>འདི|རྣམས)|(?P<past>ན|ཏེ|སྟེ|དེ|ཅིང|ཞིང|ཤིང|པ་དང|བ་དང|བ་ལས|པ་ལས|པས|བས|(?P=final)\u0F7C)|(?P<cig>ཅིག|ཞིག|ཤིག)|(?P<fut>(?:དུ|ཏུ)་(?:མི་རུང|རུང|ཡོད|མེད|གྲགས))|(?P<past_pres>ནས))(?=[^\u0F40-\u0FBC]|\Z)')

def add_occurence(stats, syl, type, second_part, id, prefix):
    if not syl in stats["verbs"]:
        stats["verbs"][syl] = {
            "noun": {"total": 0}, 
            "past": {"total": 0}, 
            "fut_pres": {"total": 0}, 
            "pres": {"total": 0}, 
            "imp": {"total": 0},
            "fut": {"total": 0},
            "past_pres": {"total": 0}
        }
    substats = stats["verbs"][syl][type]
    substats["total"] = substats["total"] + 1
    complete_form = prefix + syl + second_part
    if not complete_form in substats:
        substats[complete_form] = []
    substats[complete_form].append(id)

def analyze_verbs(stats, line, id):
    for m in re.finditer(verbs_reg, line):
        #print(m.groups())
        syl = m.group('syl')
        second = '་'+m.group('second')
        prefix = ''
        prefix = m.group('neg')
        if not m.group('neg'):
            prefix = ''
        if m.group('past'):
            if prefix == 'མི་':
                add_occurence(stats, syl, "fut_pres", second, id, prefix)
            elif prefix == 'མ་':
                add_occurence(stats, syl, "past", second, id, prefix)
        elif m.group('noun'):
            add_occurence(stats, syl, "noun", second, id, prefix)
        elif m.group('fut'):
            add_occurence(stats, syl, "fut", second, id, prefix)
        elif m.group('past_pres'):
            add_occurence(stats, syl, "past_pres", second, id, prefix)
        elif m.group('cig'):
            if prefix == '':
                add_occurence(stats, syl, "imp", second, id, prefix)
            elif prefix == 'མ་':
                add_occurence(stats, syl, "pres", second, id, prefix)

# collation
RULES=''
with open ("tibetan-collation/rules.txt", "r") as rulesfile:
    RULES=rulesfile.read()
COLLATOR = RuleBasedCollator('[normalization on]\n'+RULES)

def get_forms_str(syl_stats):
    res = ''
    for formtype in ["past", "past_pres", "pres", "fut_pres", "fut", "imp", "noun"]:
        for form in syl_stats[formtype]:
            if form == 'total':
                continue
            ids = syl_stats[formtype][form]
            res += form+' ('+str(len(ids))+'), '
    return res

def print_stats_csv(stats):
    sortedkeys = sorted(stats["verbs"].keys(), key=COLLATOR.getSortKey)
    print('syllable,past,past or present,present,future or present,future,imperative,noun,forms')
    for syl in sortedkeys:
        syl_stats = stats["verbs"][syl]
        if syl_stats["fut"]["total"] + syl_stats["past"]["total"] + syl_stats["fut_pres"]["total"] + syl_stats["pres"]["total"] == 0 and syl_stats["noun"]["total"] > 0 :
            continue
        print(syl+','+
            str(syl_stats["past"]["total"])+','+
            str(syl_stats["past_pres"]["total"])+','+
            str(syl_stats["pres"]["total"])+','+
            str(syl_stats["fut_pres"]["total"])+','+
            str(syl_stats["fut"]["total"])+','+
            str(syl_stats["imp"]["total"])+','+
            str(syl_stats["noun"]["total"])+',"'+get_forms_str(syl_stats)+'"')

with open('corpus2.txt', 'r') as f:
    stats = {"verbs": {}, "ids": {}}
    for line in f.readlines():
        id = line.split(' -')[0]
        analyze_verbs(stats, line, id)
    print_stats_csv(stats)

#line="མ་གྱུར་ཅིང མི་གྱུར་ཅིང མ་གྱུར་ཅིག གྱུར་ཅིག གྱུར་འདི མི་གྱུར་ནས གྱུར་དུ་མི་རུང"
#stats = {"verbs": {}, "ids": {}}
#analyze_verbs(stats, line, 1)
#print_stats_csv(stats)
