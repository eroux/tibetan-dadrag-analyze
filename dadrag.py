#!/usr/bin/env python3

import re

# global result, object with the following structure:
#    - da_drag
#    - ids
#
# da_drag is an object with the following structure:
#    keys are syllables where da drag or sandhi appear
#    values are:
#       - expl (explicit)
#       - expl_w_sandhi (explicit with wrong sandhi)
#       - expl_c_sandhi (explicit with correct sandhi)
#       - sandhi (implicit with no sandhi)
#       - no_sandhi (syllable appears with sandhi as if it had no da drag
#
# each value is an object with the following structure:
#    keys are the different forms of sandhi plus "total"
#    values are:
#       - for total, an integer with the total num
#       - for other values, an array containing a tuple with first the occurence,
#            the id of the occurence

#dd_reg = re.compile('(?P<syl>[\u0F40-\u0FBC]+(?P<final>[ལར(?P<n>ན)]))(?P<dd>ད?)(?P<second>་(?P<dds>ཏོ|ཅེ་ན|ཅིང|ཅིག|ཅེའོ|ཅེས|ཏམ|ཀྱང|ཏུ|པོ?(?:འི|འོ|ར|ས|འམ|འང)?)|་(?P<ndds>(?P=final)\u0F7C|(?P=final)མ|ཞེ་ན|ཞིང|ཞིག|ཞེའོ|ཞེས|ཡང|དུ|བོ?(?:འི|ར|ས|འོ|འམ|འང)?))?(?:[^\u0F40-\u0FBC]|$)')

dd_reg = re.compile('(?P<syl>[\u0F40-\u0FBC]+(?P<final>(?P<rorl>ལ|ར)|ན))(?P<dd>ད?)(?P<second>་(?P<dds>ཏོ|ཅེ་ན|ཅིང|ཅིག|ཅེའོ|ཅེས|ཏམ|ཀྱང|ཏུ|(?(rorl)པོ?(?:འི|འོ|ར|ས|འམ|འང)?))|་(?P<ndds>(?P=final)\u0F7C|(?P=final)མ|ཞེ་ན|ཞིང|ཞིག|ཞེའོ|ཞེས|ཡང|དུ|(?(rorl)བོ?(?:འི|ར|ས|འོ|འམ|འང)?)))?(?:[^\u0F40-\u0FBC]|$)')
#dd_reg = re.compile('(?P<syl>[\u0F40-\u0FBC]+(?P<final>(?P<rorl>ལ|ར)|ན))(?P<dd>ད?)(?P<second>་(?P<dds>ཏོ|ཅེ་ན|ཅིང|ཅིག|ཅེའོ|ཅེས|ཏམ|ཀྱང|ཏུ)|་(?P<ndds>(?P=final)\u0F7C|(?P=final)མ|ཞེ་ན|ཞིང|ཞིག|ཞེའོ|ཞེས|ཡང|དུ|(?(rorl)བོ?(?:འི|ར|ས|འོ|འམ|འང)?)))?(?:[^\u0F40-\u0FBC]|$)')

def add_occurence(stats, syl, type, second_part, id):
    if not syl in stats["da_drag"]:
        stats["da_drag"][syl] = {
            "expl_no_sandhi": {"total": 0}, 
            "expl_w_sandhi": {"total": 0}, 
            "expl_c_sandhi": {"total": 0}, 
            "sandhi": {"total": 0}, 
            "w_sandhi": {"total": 0},
            "no_sandhi": {"total": 0}
        }
    substats = stats["da_drag"][syl][type]
    substats["total"] = substats["total"] + 1
    complete_form = syl + second_part
    if not complete_form in substats:
        substats[complete_form] = []
    substats[complete_form].append(id)

def analyze_dd(stats, line, id):
    for m in re.finditer(dd_reg, line):
        #print(m.groups())
        syl = m.group('syl')
        second = m.group('second')
        if second == '་': # not sure why this happens sometimes
            second = None
        if m.group('dd'):
            if second:
                if m.group('dds'):
                    add_occurence(stats, syl, "expl_c_sandhi", 'ད'+second, id)
                else:
                    add_occurence(stats, syl, "expl_w_sandhi", 'ད'+second, id)
            else:
                add_occurence(stats, syl, "expl_no_sandhi", 'ད', id)
        else:
            if second:
                if m.group('dds'):
                    add_occurence(stats, syl, "sandhi", second, id)
                else:
                    add_occurence(stats, syl, "w_sandhi", second, id)
            else:
                add_occurence(stats, syl, "no_sandhi", 'ད', id)

def print_stats_csv(stats):
    print('syllable,explicit da drag with correct sandhi,explicit da drag with incorrect sandhi,explicit da drag with no sandhi,no explicit da drag with da drag sandhi,no explicit da drag with non-dadrag sandhi,no explicit da drag with no sandhi')
    for syl, syl_stats in stats["da_drag"].items():
        if syl_stats["expl_c_sandhi"]["total"] + syl_stats["expl_w_sandhi"]["total"] + syl_stats["expl_no_sandhi"]["total"] + syl_stats["sandhi"]["total"] + syl_stats["w_sandhi"]["total"] == 0 :
            continue
        print(syl+','+
            str(syl_stats["expl_c_sandhi"]["total"])+','+
            str(syl_stats["expl_w_sandhi"]["total"])+','+
            str(syl_stats["expl_no_sandhi"]["total"])+','+
            str(syl_stats["sandhi"]["total"])+','+
            str(syl_stats["w_sandhi"]["total"])+','+
            str(syl_stats["no_sandhi"]["total"]))

with open('corpus.txt', 'r') as f:
    stats = {"da_drag": {}, "ids": {}}
    for line in f.readlines():
        id = line.split(' - ')[0]
        analyze_dd(stats, line, id)
    print_stats_csv(stats)

#line=" test བནད པན པན་དུ པན་ཏུ པནད་ པནད། པནད་པ པནད་བ པནད་པོ པནད་པོའི པནད་ནོ པནད་ན པནད་ལོ པལད་ལོ པལད་བ"
#stats = {"da_drag": {}, "ids": {}}
#analyze_dd(stats, line, 1)
#print_stats_csv(stats)

# exceptions: རྒྱལ་ལོ་ ཐོར་ཏོ