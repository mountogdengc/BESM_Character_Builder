import json

def convert_stats(stats):
    # Convert list-style stats to body/mind/soul format
    if isinstance(stats, dict):
        return {
            "body_adj": stats.get("body_adj", 0) or 0,
            "mind_adj": stats.get("mind_adj", 0) or 0,
            "soul_adj": stats.get("soul_adj", 0) or 0
        }

    elif isinstance(stats, list):
        converted = {"body_adj": 0, "mind_adj": 0, "soul_adj": 0}
        for stat in stats:
            stat_type = stat.get("stat", "").lower()
            if stat_type == "body":
                converted["body_adj"] = stat.get("value", 0) or 0
            elif stat_type == "mind":
                converted["mind_adj"] = stat.get("value", 0) or 0
            elif stat_type == "soul":
                converted["soul_adj"] = stat.get("value", 0) or 0
        return converted
    else:
        return {"body_adj": 0, "mind_adj": 0, "soul_adj": 0}

def normalize_entry(entry, is_attribute=True):
    # Rename old `name` to `key`
    key = entry.get("key") or entry.get("name") or "unknown_attribute"
    return {
        "custom_name": entry.get("custom_name", entry.get("name", key)),
        "key": key.lower().replace(" ", "_"),
        "level": entry.get("level", 1) if is_attribute else None,
        "rank": None if is_attribute else entry.get("rank", 1),
        "user_description": entry.get("user_description", None),
        "enhancements": entry.get("enhancements", []),
        "limiters": entry.get("limiters", []),
        "options": entry.get("options", []),
        "user_input": entry.get("user_input", None),
        "options_source": "Race Template"
    }

def normalize_race(race):
    normalized = {}
    normalized["race_name"] = race.get("race_name", race.get("name", "UNKNOWN RACE"))
    normalized["baseSize"] = {
        "size_rank": race.get("baseSize", {}).get("size_rank", race.get("baseSize", {}).get("rank", 0)),
        "size_name": race.get("baseSize", {}).get("size_name", race.get("baseSize", {}).get("name", "Medium")),
        "options_source": "Race Template"
    }
    normalized["stats"] = convert_stats(race.get("stats", []))
    normalized["attributes"] = [normalize_entry(attr, True) for attr in race.get("attributes", [])]
    normalized["defects"] = [normalize_entry(defect, False) for defect in race.get("defects", [])]
    return normalized

# --- Load file ---
with open("legacy_race.json", "r") as f:
    raw_data = json.load(f)

legacy_races = raw_data["raceTemplates"]["races"]
normalized_races = [normalize_race(race) for race in legacy_races]

# --- Save normalized result ---
with open("normalized_races.json", "w") as f:
    json.dump(normalized_races, f, indent=2)
