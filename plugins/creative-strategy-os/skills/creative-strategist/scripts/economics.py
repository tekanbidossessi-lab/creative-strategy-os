# -*- coding: utf-8 -*-
"""Unit economics shared by the suite (ws.py start page, cs-intake, later cs-read).

The question it answers: how much can one order cost in ads before this product loses money?
Cash on delivery aware: Meta counts orders placed (the Purchase event fires on the order form),
but money comes only from orders confirmed by phone and then delivered and paid.

Rates (economics in product.yaml):
  confirmation_rate  share of placed orders confirmed by phone            (1 when paid online)
  delivery_rate      share of confirmed orders delivered and paid          (1 when paid online)
  If the client only knows "35 % of orders are delivered", put confirmation_rate 1 and delivery_rate 0.35.
Costs, in the product's currency:
  unit_cost          one unit landed in stock (purchase + freight + customs)
  shipping_cost      one delivery attempt; paid on delivered orders unless shipping_on: confirmed
  return_cost        extra cost of a failed delivery (return trip), default 0
  cod_fee_rate       share of the cash kept by the delivery company, default 0
  call_cost          confirmation call per placed order, default 0
  target_profit      profit wanted per delivered order (optional) -> target cost per order
  ad_currency, fx_rate   the ad account's currency and how many product-currency units one unit of it costs

A webinar (kinds.py) sells a seat at a free live, and the programme during or after it: compute_live() says what one
sign-up may cost, from the programme's price (offers) and
  show_rate          share of sign-ups who come to the live (or watch the replay in time)
  sale_rate          share of those present who buy the programme
  refund_rate        share of sales refunded, default 0
  payment_fee_rate   share kept by the payment platform (card, mobile money), default 0
  cost_per_sale      what one sale costs besides the ads (a closer's commission, a call), default 0
  target_profit      profit wanted per sale (optional) -> target cost per sign-up
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numparse  # noqa: E402

DEFAULTS = {"shipping_on": "delivered", "return_cost": 0, "cod_fee_rate": 0, "call_cost": 0}
LABELS = {"unit_cost": "coût d'une unité", "shipping_cost": "coût de livraison", "return_cost": "coût d'un retour",
          "cod_fee_rate": "commission du livreur", "call_cost": "coût d'un appel de confirmation",
          "confirmation_rate": "taux de confirmation", "delivery_rate": "taux de livraison",
          "target_profit": "bénéfice visé", "fx_rate": "taux de change", "currency": "devise",
          "ad_currency": "devise du compte pub", "shipping_on": "livraison payée sur",
          "show_rate": "taux de présence au live", "sale_rate": "taux de vente parmi les présents",
          "refund_rate": "taux de remboursement", "payment_fee_rate": "commission de paiement",
          "cost_per_sale": "coût d'une vente hors pub"}


def labels(keys):
    return ", ".join(LABELS.get(k, k) for k in keys)


class EcoError(Exception):
    pass


def num(v, what, allow_empty=True):
    """A number typed by a person: 40000, "40 000", "5.000" (thousands), "0,5", "12 %" (see numparse.py)."""
    if v is None or (isinstance(v, str) and not v.strip()):
        if allow_empty:
            return None
        raise EcoError(f"{what} : valeur manquante")
    if isinstance(v, bool):
        raise EcoError(f"{what} : « {v} » n'est pas un nombre")
    x = numparse.parse(v)
    if x is None:
        raise EcoError(f"{what} : « {v} » n'est pas un nombre")
    return x


def rate(v, what, default, allow_zero=False):
    """0.8, "80", "80 %", "0,5 %" -> share between 0 and 1. A % sign always means percent."""
    x = num(v, what)
    if x is None:
        return default
    if numparse.has_percent(v) or 1 < x <= 100:
        x = x / 100
    if not (0 <= x <= 1) or (x == 0 and not allow_zero):
        raise EcoError(f"{what} : {v} doit être entre 0 et 1 (ou un pourcentage)")
    return x


def inputs(eco):
    eco = eco if isinstance(eco, dict) else {}
    out = {
        "unit_cost": num(eco.get("unit_cost"), "economics.unit_cost"),
        "shipping_cost": num(eco.get("shipping_cost"), "economics.shipping_cost") or 0.0,
        "return_cost": num(eco.get("return_cost"), "economics.return_cost") or 0.0,
        "cod_fee_rate": rate(eco.get("cod_fee_rate"), "economics.cod_fee_rate", 0.0, allow_zero=True),
        "call_cost": num(eco.get("call_cost"), "economics.call_cost") or 0.0,
        "confirmation_rate": rate(eco.get("confirmation_rate"), "economics.confirmation_rate", 1.0),
        "delivery_rate": rate(eco.get("delivery_rate"), "economics.delivery_rate", 1.0),
        "target_profit": num(eco.get("target_profit"), "economics.target_profit"),
        "shipping_on": eco.get("shipping_on") or "delivered",
        "currency": eco.get("currency") or "",
        "ad_currency": eco.get("ad_currency") or "",
        "fx_rate": num(eco.get("fx_rate"), "economics.fx_rate"),
        "assumed": list(eco.get("assumed") or []),
    }
    if out["fx_rate"] is not None and out["fx_rate"] <= 0:
        raise EcoError(f"economics.fx_rate : {eco.get('fx_rate')} doit être positif")
    if out["shipping_on"] not in ("delivered", "confirmed"):
        raise EcoError(f"economics.shipping_on : « {out['shipping_on']} » inconnu (delivered, confirmed)")
    return out


def compute(price, eco, qty=1):
    """Economics of one order of `qty` units sold at `price`. Returns a dict, or raises EcoError."""
    p = num(price, "prix", allow_empty=False)
    e = inputs(eco)
    if e["unit_cost"] is None:
        raise EcoError("economics.unit_cost : le coût d'une unité manque")
    q = int(qty or 1)
    conf, deliv = e["confirmation_rate"], e["delivery_rate"]
    d = conf * deliv
    revenue = d * p
    cogs = d * e["unit_cost"] * q
    ship = (conf if e["shipping_on"] == "confirmed" else d) * e["shipping_cost"]
    returns = conf * (1 - deliv) * e["return_cost"]
    fee = d * p * e["cod_fee_rate"]
    margin_placed = revenue - cogs - ship - returns - fee - e["call_cost"]
    r = {"price": p, "qty": q, "currency": e["currency"], "paid_share": d,
         "margin_delivered": margin_placed / d if d else 0.0,
         "breakeven_cpa": margin_placed,                   # ad cost per order placed, at break-even
         "breakeven_roas": (p / margin_placed) if margin_placed > 0 else None,
         "target_cpa": None, "kill_spend": None, "viable": margin_placed > 0}
    if e["target_profit"] is not None:
        r["target_cpa"] = margin_placed - e["target_profit"] * d
        r["target_unreachable"] = r["target_cpa"] <= 0   # the cut-off then falls back on break-even
    ref = r["target_cpa"] if (r["target_cpa"] or 0) > 0 else margin_placed
    r["kill_spend"] = 2 * ref if ref > 0 else None
    if e["ad_currency"] and e["fx_rate"]:
        fx = e["fx_rate"]
        r["ad"] = {"currency": e["ad_currency"], "breakeven_cpa": margin_placed / fx,
                   "target_cpa": (r["target_cpa"] / fx) if r["target_cpa"] is not None else None,
                   "kill_spend": (r["kill_spend"] / fx) if r["kill_spend"] else None}
    return r


def live_inputs(eco):
    eco = eco if isinstance(eco, dict) else {}
    out = {
        "show_rate": rate(eco.get("show_rate"), "economics.show_rate", None),
        "sale_rate": rate(eco.get("sale_rate"), "economics.sale_rate", None),
        "refund_rate": rate(eco.get("refund_rate"), "economics.refund_rate", 0.0, allow_zero=True),
        "payment_fee_rate": rate(eco.get("payment_fee_rate"), "economics.payment_fee_rate", 0.0, allow_zero=True),
        "cost_per_sale": num(eco.get("cost_per_sale"), "economics.cost_per_sale") or 0.0,
        "target_profit": num(eco.get("target_profit"), "economics.target_profit"),
        "currency": eco.get("currency") or "", "ad_currency": eco.get("ad_currency") or "",
        "fx_rate": num(eco.get("fx_rate"), "economics.fx_rate"), "assumed": list(eco.get("assumed") or []),
    }
    if out["fx_rate"] is not None and out["fx_rate"] <= 0:
        raise EcoError(f"economics.fx_rate : {eco.get('fx_rate')} doit être positif")
    return out


def compute_live(price, eco):
    """A webinar: what one sign-up may cost in ads, sold on the programme at `price`. Returns a dict, or raises."""
    p = num(price, "prix du programme", allow_empty=False)
    e = live_inputs(eco)
    missing = [k for k in ("show_rate", "sale_rate") if e[k] is None]
    if missing:
        raise EcoError("il manque " + labels(missing) + " (economics." + ", economics.".join(missing) + ")")
    buyers = e["show_rate"] * e["sale_rate"]                       # sales per sign-up
    net = p * (1 - e["refund_rate"]) * (1 - e["payment_fee_rate"]) - e["cost_per_sale"]
    cpl = buyers * net                                             # break-even ad cost per sign-up
    r = {"price": p, "currency": e["currency"], "buyers_per_signup": buyers, "net_per_sale": net,
         "signups_per_sale": (1 / buyers) if buyers else None,
         "breakeven_cpl": cpl, "breakeven_per_attendee": cpl / e["show_rate"], "breakeven_cps": net,
         "breakeven_roas": (p / net) if net > 0 else None,
         "target_cpl": None, "kill_spend": None, "viable": net > 0}
    if e["target_profit"] is not None:
        r["target_cpl"] = buyers * (net - e["target_profit"])
        r["target_unreachable"] = r["target_cpl"] <= 0
    ref = r["target_cpl"] if (r["target_cpl"] or 0) > 0 else cpl
    r["kill_spend"] = 2 * ref if ref > 0 else None
    if e["ad_currency"] and e["fx_rate"]:
        fx = e["fx_rate"]
        r["ad"] = {"currency": e["ad_currency"], "breakeven_cpl": cpl / fx,
                   "target_cpl": (r["target_cpl"] / fx) if r["target_cpl"] is not None else None,
                   "kill_spend": (r["kill_spend"] / fx) if r["kill_spend"] else None}
    return r


def offer_lines(product):
    """(label, price, qty, currency, market) for the main offer and each bundle of every market."""
    out = []
    for o in product.get("offers") or []:
        if not isinstance(o, dict) or o.get("price") in (None, ""):
            continue
        m = o.get("market", "")
        q0 = int(num(o.get("qty"), "offers.qty") or 1)   # a pack sold as the product: its units cost each
        out.append((f"{m} {'1 unité' if q0 == 1 else f'lot de {q0}'}".strip(), o["price"], q0, o.get("currency", ""), m))
        for b in o.get("bundles") or []:
            if isinstance(b, dict) and b.get("price") not in (None, ""):
                q = int(num(b.get("qty"), "bundles.qty") or 1)
                label = b.get("label") or f"lot de {q}"
                out.append((f"{m} {label}".strip(), b["price"], q, o.get("currency", ""), m))
    return out


def fmt(v, cur=""):
    if v is None or v == "":
        return "—"
    if not isinstance(v, (int, float)):
        x = numparse.parse(v)
        if x is None:
            return f"{v} {cur}".strip()
        v = x
    s = f"{v:,.0f}" if abs(v) >= 100 or float(v).is_integer() else f"{v:,.2f}"
    s = s.replace(",", " ").replace(".", ",").replace(" ", " ")
    return (s + (f" {cur}" if cur else "")).strip()


def dec(v, n=2):
    return "—" if v is None else f"{v:.{n}f}".replace(".", ",")


def one_line(product, kind=None):
    """The start page's sentence, or None when the costs are not known yet."""
    eco = product.get("economics") if isinstance(product.get("economics"), dict) else {}
    lines = offer_lines(product)
    if kind == "webinar" or (kind is None and eco.get("show_rate") not in (None, "")):
        if not lines or eco.get("show_rate") in (None, "") or eco.get("sale_rate") in (None, ""):
            return None
        try:
            r = compute_live(lines[0][1], eco)
        except EcoError as ex:
            return f"à calculer : {ex}"
        cur = eco.get("currency") or lines[0][3]
        e = live_inputs(eco)
        s = (f"{fmt(r['breakeven_cpl'], cur)} de pub au maximum par inscription (programme à {fmt(r['price'])}, "
             f"{e['show_rate']:.0%} de présents, {e['sale_rate']:.0%} d'acheteurs parmi eux)")
        if r.get("ad"):
            s += f", soit {fmt(r['ad']['breakeven_cpl'], r['ad']['currency'])}"
        if not r["viable"]:
            s = "aucune marge : chaque vente perd de l'argent avant même la pub"
        if e["assumed"]:
            s += " — hypothèses : " + labels(e["assumed"])
        return s
    if not lines or eco.get("unit_cost") in (None, ""):  # 0 is a real cost: a digital product has none per sale
        return None
    label, price, qty, cur, _ = lines[0]
    if eco.get("currency") and cur and eco["currency"] != cur:
        return f"à calculer : le prix est en {cur} et les coûts en {eco['currency']}"
    try:
        r = compute(price, eco, qty)
    except EcoError as ex:
        return f"à calculer : {ex}"
    cur = eco.get("currency") or cur
    s = (f"{fmt(r['breakeven_cpa'], cur)} de pub au maximum par commande passée "
         f"(prix {fmt(r['price'])}, {r['paid_share']:.0%} des commandes payées au final)")
    if r.get("ad"):
        s += f", soit {fmt(r['ad']['breakeven_cpa'], r['ad']['currency'])}"
    if not r["viable"]:
        s = f"aucune marge : chaque commande perd {fmt(-r['breakeven_cpa'], cur)} avant même la pub"
    if inputs(eco)["assumed"]:
        s += " — hypothèses : " + labels(inputs(eco)["assumed"])
    if kind == "digital":
        import kinds
        s = kinds.say({"kind": "digital"}, s)
    return s
