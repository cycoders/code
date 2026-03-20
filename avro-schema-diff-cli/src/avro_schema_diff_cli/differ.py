from typing import Dict, Any, List, Union, Optional

Change = Dict[str, Any]


def check_type_compatible(writer_t: Any, reader_t: Any) -> bool:
    """Check if writer type is resolvable to reader type per Avro rules. Recursive."""
    def to_union(t: Any) -> List[Any]:
        return t if isinstance(t, list) else [t]

    w_union = to_union(writer_t)
    r_union = to_union(reader_t)

    for wt in w_union:
        matching = False
        for rt in r_union:
            if _check_single(wt, rt):
                matching = True
                break
        if not matching:
            return False
    return True


def _check_single(wt: Any, rt: Any) -> bool:
    if isinstance(wt, dict) and isinstance(rt, dict):
        wtype = wt["type"]
        rtype = rt["type"]
        if wtype != rtype:
            return False
        if wtype in ("record", "error"):
            return check_record_compatible(wt, rt)
        if wtype == "enum":
            return set(wt.get("symbols", [])) <= set(rt.get("symbols", []))
        if wtype == "array":
            return check_type_compatible(wt.get("items", "null"), rt.get("items", "null"))
        if wtype == "map":
            return check_type_compatible(wt.get("values", "null"), rt.get("values", "null"))
        if wtype == "fixed":
            return wt.get("size", 0) == rt.get("size", 0)
        return False
    else:
        # Primitives promotion (writer -> reader)
        promo = {
            "null": ["null"],
            "boolean": ["boolean"],
            "int": ["int", "long", "float", "double"],
            "long": ["long", "float", "double"],
            "float": ["float", "double"],
            "double": ["double"],
            "bytes": ["bytes"],
            "string": ["string"],
        }
        return rt in promo.get(wt, [])


def check_record_compatible(writer: Dict[str, Any], reader: Dict[str, Any]) -> bool:
    wfields = {f["name"]: f for f in writer.get("fields", [])}
    rfields = {f["name"]: f for f in reader.get("fields", [])}
    for fname, wfield in wfields.items():
        if fname not in rfields:
            return False
        rfield = rfields[fname]
        if not check_type_compatible(wfield["type"], rfield["type"]):
            return False
    return True


def get_schema_diff(old: Dict[str, Any], new: Dict[str, Any], name: str = "schema") -> Change:
    """Structural diff + compat checks."""
    changes: Change = {
        "added": [],
        "removed": [],
        "modified": {},
        "backward_compatible": check_type_compatible(old, new),
        "forward_compatible": check_type_compatible(new, old),
    }

    otype = old.get("type")
    ntype = new.get("type")

    if otype != ntype:
        changes["modified"]["type"] = {"old": otype, "new": ntype}
        return changes

    if otype in ("record", "error"):
        ofields = {f["name"]: f for f in old.get("fields", [])}
        nfields = {f["name"]: f for f in new.get("fields", [])}
        all_names = set(ofields) | set(nfields)
        for fname in all_names:
            if fname not in ofields:
                changes["added"].append(fname)
            elif fname not in nfields:
                changes["removed"].append(fname)
            else:
                fdiff = _field_diff(ofields[fname], nfields[fname])
                if fdiff:
                    changes["modified"][fname] = fdiff
    elif otype == "enum":
        osyms = sorted(old.get("symbols", []))
        nsyms = sorted(new.get("symbols", []))
        changes["added"] = [s for s in nsyms if s not in osyms]
        changes["removed"] = [s for s in osyms if s not in nsyms]
    # array/map handled in compat

    return changes


def _field_diff(old_f: Dict[str, Any], new_f: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    diff = {}
    ot = old_f.get("type")
    nt = new_f.get("type")
    if ot != nt:
        diff["type"] = {"old": ot, "new": nt}
    od = old_f.get("default")
    nd = new_f.get("default")
    if od != nd:
        diff["default"] = {"old": od, "new": nd}
    return diff if diff else None
