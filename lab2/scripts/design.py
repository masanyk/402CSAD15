"""
Лабораторна №2 (АПКС): генерація параметрів плати з GUID.

GUID отримується детерміновано з повного імені студента як UUID версії 5
(RFC 4122: SHA-1 хеш від імені в просторі імен NAMESPACE_DNS).
Кожна група GUID -> квадратний компонент U1..U5:
  сторона (мм) = кількість символів групи, кількість пінів = кількість символів,
  символ i-го піна = i-й символ групи.
З'єднання: піни з однаковим символом з'єднуються в одне коло (net) N_<символ>.
Піни, символ яких не зустрічається більше ніде, — вільні; їх виводимо на роз'єм J1
біля однієї меншої сторони плати.
"""
import json
import uuid
from collections import OrderedDict

FULL_NAME = "Процак Максим Степанович"
GUID = str(uuid.uuid5(uuid.NAMESPACE_DNS, FULL_NAME))


def components():
    comps = []
    for i, group in enumerate(GUID.split("-"), start=1):
        comps.append({
            "ref": f"U{i}",
            "group": group,
            "size_mm": len(group),
            "pins": [{"num": n, "char": c} for n, c in enumerate(group, start=1)],
        })
    return comps


def nets():
    """Повертає (nets, free_pins).

    nets: OrderedDict net_name -> list of (ref, pin_num, char)
    free_pins: list of (ref, pin_num, char) — символ, що є лише в одному піні.
    """
    comps = components()
    by_char = OrderedDict()
    for c in comps:
        for p in c["pins"]:
            by_char.setdefault(p["char"], []).append((c["ref"], p["num"], p["char"]))
    result, free = OrderedDict(), []
    for ch in sorted(by_char):
        members = by_char[ch]
        if len(members) > 1:
            result[f"N_{ch}"] = members
        else:
            free.append(members[0])
    return result, free


def connector_pins():
    """J1: по одному піну на кожен вільний пін, коло FREE_<символ>."""
    _, free = nets()
    return [{"num": i, "net": f"FREE_{ch}", "to": (ref, num, ch)}
            for i, (ref, num, ch) in enumerate(free, start=1)]


def pin_net(ref, num):
    all_nets, _ = nets()
    for name, members in all_nets.items():
        for r, n, _c in members:
            if r == ref and n == num:
                return name
    for j in connector_pins():
        if j["to"][0] == ref and j["to"][1] == num:
            return j["net"]
    raise KeyError((ref, num))


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print("ПІБ :", FULL_NAME)
    print("GUID:", GUID)
    for c in components():
        print(f"{c['ref']}: {c['group']:<14} {c['size_mm']} мм x {c['size_mm']} мм, {len(c['pins'])} пінів")
    n, free = nets()
    print("\nКола (net):")
    for name, members in n.items():
        print(f"  {name:<6}", ", ".join(f"{r}.{p}" for r, p, _ in members))
    print("\nВільні піни -> J1:")
    for j in connector_pins():
        print(f"  J1.{j['num']}  {j['net']:<7} <- {j['to'][0]}.{j['to'][1]} ('{j['to'][2]}')")
    out = {"name": FULL_NAME, "guid": GUID, "components": components(),
           "nets": {k: [list(m) for m in v] for k, v in n.items()},
           "connector": connector_pins()}
    with open(sys.argv[1] if len(sys.argv) > 1 else "netlist.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
