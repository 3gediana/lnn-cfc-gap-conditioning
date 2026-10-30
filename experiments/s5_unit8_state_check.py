import json
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(PROJECT, "experiments", "s5_unit8_state_out.json"),
                   encoding="utf-8"))
for p in d['projects']:
    if '4a1c4c0a' in p['project']:
        print('classification:', p['classification'])
        print('active:', p['active'])
        print('terminal_action:', p.get('terminal_action'))
        print('ready_stage_ids:', p.get('ready_stage_ids'))
