"""
Flask Web App – CFG ↔ PDA Converter
Run:  python app.py
Open: http://127.0.0.1:5000
"""

from flask import Flask, render_template, request, jsonify
from itertools import product as cart_product

app = Flask(__name__, template_folder="templates")


# ── Data Structures ──────────────────────────────────────────────

class CFG:
    def __init__(self, variables, terminals, productions, start):
        self.variables = variables
        self.terminals = terminals
        self.productions = productions  # dict: var → list of bodies (each body = list of symbols)
        self.start = start

    def to_dict(self):
        prods = {}
        for var, bodies in self.productions.items():
            prods[var] = [" ".join(b) if b else "ε" for b in bodies]
        return {
            "variables": sorted(self.variables),
            "terminals": sorted(self.terminals),
            "start": self.start,
            "productions": prods,
        }


class PDA:
    def __init__(self, states, input_alphabet, stack_alphabet,
                 transitions, start_state, start_stack, accept_states=None):
        self.states = states
        self.input_alphabet = input_alphabet
        self.stack_alphabet = stack_alphabet
        self.transitions = transitions  # list of (state, input_or_ε, stack_pop, next_state, push_list)
        self.start_state = start_state
        self.start_stack = start_stack
        self.accept_states = accept_states or set()

    def to_dict(self):
        trans = []
        for (s, a, X, s2, push) in self.transitions:
            trans.append({
                "state": s,
                "input": a if a else "ε",
                "pop": X,
                "next_state": s2,
                "push": "".join(push) if push else "ε",
            })
        return {
            "states": sorted(self.states),
            "input_alphabet": sorted(self.input_alphabet),
            "stack_alphabet": sorted(self.stack_alphabet),
            "start_state": self.start_state,
            "start_stack": self.start_stack,
            "accept_states": sorted(self.accept_states),
            "transitions": trans,
        }


# ── CFG → PDA ────────────────────────────────────────────────────

def cfg_to_pda(cfg: CFG) -> PDA:
    states = {"q_start", "q_loop", "q_accept"}
    start_stack = "Z0"
    stack_alphabet = set(cfg.variables) | set(cfg.terminals) | {start_stack}
    transitions = []

    transitions.append(("q_start", "", start_stack, "q_loop", [cfg.start, start_stack]))

    for var, bodies in cfg.productions.items():
        for body in bodies:
            push_symbols = list(body) if body else []
            transitions.append(("q_loop", "", var, "q_loop", push_symbols))

    for term in cfg.terminals:
        transitions.append(("q_loop", term, term, "q_loop", []))

    transitions.append(("q_loop", "", start_stack, "q_accept", []))

    return PDA(states=states, input_alphabet=set(cfg.terminals),
               stack_alphabet=stack_alphabet, transitions=transitions,
               start_state="q_start", start_stack=start_stack,
               accept_states={"q_accept"})


# ── PDA → CFG ────────────────────────────────────────────────────

def pda_to_cfg(pda: PDA) -> CFG:
    states_list = sorted(pda.states)

    def var_name(p, A, q):
        return f"[{p},{A},{q}]"

    productions = {}
    variables = {"S"}
    productions["S"] = []

    for q in states_list:
        v = var_name(pda.start_state, pda.start_stack, q)
        variables.add(v)
        productions["S"].append([v])

    for (p, a, A, r, push_list) in pda.transitions:
        k = len(push_list)
        if k == 0:
            v = var_name(p, A, r)
            variables.add(v)
            body = [a] if a else []
            productions.setdefault(v, [])
            productions[v].append(body)
        else:
            for combo in cart_product(states_list, repeat=k):
                q_list = list(combo)
                head = var_name(p, A, q_list[-1])
                variables.add(head)
                body = []
                if a:
                    body.append(a)
                prev_state = r
                for i in range(k):
                    triple = var_name(prev_state, push_list[i], q_list[i])
                    variables.add(triple)
                    body.append(triple)
                    prev_state = q_list[i]
                productions.setdefault(head, [])
                productions[head].append(body)

    return CFG(variables=variables, terminals=set(pda.input_alphabet),
               productions=productions, start="S")


# ── Parsing helpers ──────────────────────────────────────────────

def parse_symbols(text):
    """Split body text into individual symbols (handles multi-char like Z0, A1)."""
    symbols, i = [], 0
    text = text.strip()
    while i < len(text):
        if text[i] == ' ':
            i += 1
            continue
        sym = text[i]
        i += 1
        while i < len(text) and (text[i].isdigit() or text[i] == "'"):
            sym += text[i]
            i += 1
        symbols.append(sym)
    return symbols


# ── Routes ───────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convert/cfg-to-pda", methods=["POST"])
def convert_cfg_to_pda():
    try:
        data = request.json
        variables = set(v.strip() for v in data["variables"].split(",") if v.strip())
        terminals = set(t.strip() for t in data["terminals"].split(",") if t.strip())
        start = data["start"].strip()

        productions = {}
        for rule in data["productions"]:
            lhs = rule["lhs"].strip()
            for alt in rule["rhs"].split("|"):
                alt = alt.strip()
                if alt in ("ε", "epsilon", "e", "E", "''", '""'):
                    body = []
                else:
                    body = parse_symbols(alt)
                productions.setdefault(lhs, []).append(body)

        cfg = CFG(variables, terminals, productions, start)
        pda = cfg_to_pda(cfg)
        return jsonify({"success": True, "result": pda.to_dict()})
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)})


@app.route("/convert/pda-to-cfg", methods=["POST"])
def convert_pda_to_cfg():
    try:
        data = request.json
        states = set(s.strip() for s in data["states"].split(",") if s.strip())
        input_alpha = set(a.strip() for a in data["input_alphabet"].split(",") if a.strip())
        stack_alpha = set(a.strip() for a in data["stack_alphabet"].split(",") if a.strip())
        start_state = data["start_state"].strip()
        start_stack = data["start_stack"].strip()
        accept_raw = data.get("accept_states", "").strip()
        accept_states = set(a.strip() for a in accept_raw.split(",") if a.strip()) if accept_raw else set()

        transitions = []
        for t in data["transitions"]:
            s = t["state"].strip()
            a = t["input"].strip()
            if a in ("ε", "e", "E", "epsilon"):
                a = ""
            X = t["pop"].strip()
            s2 = t["next_state"].strip()
            push_str = t["push"].strip()
            if push_str in ("ε", "e", "E", "epsilon"):
                push_list = []
            else:
                push_list = parse_symbols(push_str)
            transitions.append((s, a, X, s2, push_list))

        pda = PDA(states, input_alpha, stack_alpha, transitions,
                  start_state, start_stack, accept_states)
        cfg = pda_to_cfg(pda)
        return jsonify({"success": True, "result": cfg.to_dict()})
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
