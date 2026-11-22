# -*- coding: utf-8 -*-
"""The workspace's audit.yaml: every check of the suite (intake, offer, later review and read), with its status,
evidence and date. Each skill brings its own catalogue (checks.yaml: id, area, priority, label, why, how, fix,
when); the results of all skills live side by side in one file.

    a = Audit(P, Path(<skill>/scripts/checks.yaml))
    a.set("page_price", "ok", "205 000 GNF, lu par fetch")
    a.save()
    a.items(ws)          # [(check, result)] for the checks that apply to this workspace
    a.todo(ws)           # what is not ok, by priority then status
"""
from pathlib import Path

from ws import WsError, load_yaml, dump_yaml, today

STATUSES = ("ok", "warn", "fail", "todo", "na")
ICON = {"ok": "✅", "warn": "🟡", "fail": "🔴", "todo": "⬜", "na": "➖"}
STATUS_FR = {"ok": "bon", "warn": "à revoir", "fail": "à corriger", "todo": "à vérifier", "na": "sans objet"}
RANK = {"fail": 0, "warn": 1, "todo": 2}


def load_catalogue(path):
    data = load_yaml(Path(path), {}) or {}
    return data.get("areas") or {}, {c["id"]: c for c in data.get("checks") or []}


def applies(check, ws):
    cond = check.get("when") or {}
    if "channel" in cond and cond["channel"] not in (ws.get("channels") or []):
        return False
    # what is sold (kinds.py): `kind: webinar` or `kind: [product, digital]`; absent = every kind
    if "kind" in cond:
        kinds = cond["kind"] if isinstance(cond["kind"], list) else [cond["kind"]]
        if (ws.get("kind") or "product") not in kinds:
            return False
    # where the ads lead (1.6): `destination: quiz`; absent = every destination
    if "destination" in cond and str(ws.get("destination") or "page") != cond["destination"]:
        return False
    if "stage" in cond and ws.get("stage") != cond["stage"]:
        return False
    if cond.get("payment") == "cod":
        pays = {m.get("payment") for m in ws.get("markets") or [] if isinstance(m, dict)}
        if not pays & {"cod", "both"}:
            return False
    return True


class Audit:
    def __init__(self, P, catalogue_file):
        self.P = P
        self.path = P["root"] / "audit.yaml"
        self.areas, self.cat = load_catalogue(catalogue_file)
        data = load_yaml(self.path, {}) or {}
        if not isinstance(data, dict) or not isinstance(data.get("checks", {}), dict):
            raise WsError("audit.yaml n'a pas la bonne forme ; restaure audit.yaml.bak ou supprime-le (il se reconstruit)")
        data.setdefault("checks", {})
        for cid, r in list(data["checks"].items()):  # a hand-edited entry never crashes a run
            if not isinstance(r, dict):
                data["checks"][cid] = {"status": "todo", "evidence": str(r or ""), "date": "", "by": "manuel"}
            elif r.get("status") not in STATUSES:
                r["status"] = "todo"
        self.data = data

    def check(self, cid):
        if cid not in self.cat:
            raise WsError(f"contrôle inconnu « {cid} » ; la liste : la commande check <dossier>")
        return self.cat[cid]

    def applies(self, cid, ws):
        return applies(self.check(cid), ws)

    def set(self, cid, status, evidence, by="auto"):
        """A verdict given by hand (by: manuel) wins: an automatic run only records what it read next to it."""
        self.check(cid)
        if status not in STATUSES:
            raise WsError(f"statut « {status} » inconnu ({', '.join(STATUSES)})")
        old = self.data["checks"].get(cid)
        evidence = str(evidence or "").strip()
        if by == "auto" and isinstance(old, dict) and old.get("by") == "manuel":
            old["auto"] = {"status": status, "evidence": evidence, "date": today()}
            return
        self.data["checks"][cid] = {"status": status, "evidence": evidence, "date": today(), "by": by}

    def get(self, cid):
        return self.data["checks"].get(cid)

    def save(self):
        self.data["updated"] = today()
        dump_yaml(self.path, self.data)

    def items(self, ws):
        return [(c, self.data["checks"].get(c["id"], {"status": "todo", "evidence": ""}))
                for c in self.cat.values() if applies(c, ws)]

    def todo(self, ws):
        return sorted([(c, r) for c, r in self.items(ws) if r["status"] in RANK],
                      key=lambda cr: (cr[0].get("priority", 2), RANK[cr[1]["status"]]))

    def counts(self, ws):
        items = self.items(ws)
        return {s: sum(1 for _, r in items if r["status"] == s) for s in STATUSES}

    def render_list(self, ws):
        """Markdown: the checks by area, each with its icon and evidence."""
        L = []
        items = self.items(ws)
        for area, label in self.areas.items():
            sub = [(c, r) for c, r in items if c["area"] == area]
            if not sub:
                continue
            L += [f"### {label}", ""]
            for c, r in sub:
                L.append(f"- {ICON[r['status']]} **{c['label']}**" + (f" — {r['evidence']}" if r.get("evidence") else ""))
            L.append("")
        return L

    def render_todo(self, ws):
        todo = self.todo(ws)
        if not todo:
            return []
        L = ["## À faire, dans cet ordre", ""]
        for i, (c, r) in enumerate(todo, 1):
            L.append(f"{i}. {ICON[r['status']]} **{c['label']}.** {c['fix']} *Pourquoi : {c['why']}*")
        return L + [""]
