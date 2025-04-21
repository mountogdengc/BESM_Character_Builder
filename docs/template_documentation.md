# Template Documentation

This document provides detailed information on how to create and modify templates for the BESM 4e Character Generator.

## Template Types

The character generator supports three types of templates:

1. **Race Templates** - Define racial characteristics and traits
2. **Class Templates** - Define profession or role-based abilities
3. **Size Templates** - Define size-related attributes and modifiers

## Template Structure

All templates follow a similar JSON structure with some type-specific fields.

### Common Template Fields

| Field | Type | Description |
|-------|------|-------------|
| `key` | String | Unique identifier for the template (snake_case) |
| `attributes` | Array | List of attributes provided by the template |
| `defects` | Array | List of defects provided by the template |
| `stats` | Object | Stat modifiers (body_adj, mind_adj, soul_adj) |

### Race Template Structure

```json
{
  "race_name": "ANDROID BATTLE MAID",
  "key": "android_battle_maid",
  "baseSize": {
    "size_rank": 0,
    "size_name": "Medium",
    "options_source": "Race Template"
  },
  "stats": {
    "body_adj": 2,
    "mind_adj": 0,
    "soul_adj": 0
  },
  "attributes": [
    {
      "custom_name": "Armour",
      "key": "armour",
      "level": 3,
      "user_description": "AR 15",
      "enhancements": [],
      "limiters": [],
      "options": [],
      "user_input": null,
      "options_source": "Race Template",
      "valid": true
    }
  ],
  "defects": [
    {
      "custom_name": "Ism - Android",
      "key": "ism",
      "rank": 1,
      "user_description": null,
      "enhancements": [],
      "limiters": [],
      "options": [],
      "user_input": null,
      "options_source": "Race Template",
      "valid": true
    }
  ]
}
```

### Class Template Structure

```json
{
  "class_name": "ADVENTURER",
  "key": "adventurer",
  "baseSize": {
    "rank": 0,
    "name": "Medium",
    "options_source": "Class Template"
  },
  "stats": {
    "body_adj": 0,
    "mind_adj": 0,
    "soul_adj": 0
  },
  "attributes": [
    {
      "custom_name": "Combat Technique",
      "key": "combat_technique",
      "level": 1,
      "user_description": "(Select 1)",
      "enhancements": [],
      "limiters": [],
      "options": [],
      "user_input": null,
      "options_source": "Class Template",
      "valid": true
    }
  ],
  "defects": []
}
```

### Size Template Structure

```json
{
  "name": "Monumental",
  "key": "monumental",
  "rank": 10,
  "typicalHeight": "1-2 km",
  "typicalMass": "15 M - 125 M tonnes",
  "modifiers": {
    "liftingCapacity": "x 250 M",
    "strengthDamage": "+100",
    "armourEffect": "+100 AR",
    "rangedModifier": "-20",
    "speedRangeMultiplier": "x 1,000"
  },
  "attributes": [
    {
      "custom_name": "Superstrength",
      "key": "superstrength",
      "level": 20,
      "user_description": null,
      "enhancements": [],
      "limiters": [],
      "options": [],
      "user_input": null,
      "options_source": "Size Template",
      "valid": true
    }
  ],
  "defects": [
    {
      "custom_name": "Big, Heavy, and Obvious",
      "key": "unique_defect",
      "rank": 10,
      "user_description": null,
      "enhancements": [],
      "limiters": [],
      "options": [],
      "user_input": null,
      "options_source": "Size Template",
      "valid": true
    }
  ]
}
```

## Attribute and Defect Structure

### Attribute Fields

| Field | Type | Description |
|-------|------|-------------|
| `custom_name` | String | Display name for the attribute |
| `key` | String | Unique identifier matching attributes.json |
| `level` | Number | Power rating of the attribute (BESM 4e uses "level" for attributes) |
| `user_description` | String | Optional description or specification |
| `enhancements` | Array | List of enhancements applied to the attribute |
| `limiters` | Array | List of limiters applied to the attribute |
| `options` | Array | List of options for the attribute |
| `user_input` | String | User-provided input for the attribute |
| `options_source` | String | Source of the attribute (e.g., "Race Template") |
| `valid` | Boolean | Whether the attribute is valid |

### Defect Fields

| Field | Type | Description |
|-------|------|-------------|
| `custom_name` | String | Display name for the defect |
| `key` | String | Unique identifier matching defects.json |
| `rank` | Number | Power rating of the defect (BESM 4e uses "rank" for defects) |
| `user_description` | String | Optional description or specification |
| `enhancements` | Array | List of enhancements applied to the defect |
| `limiters` | Array | List of limiters applied to the defect |
| `options` | Array | List of options for the defect |
| `user_input` | String | User-provided input for the defect |
| `options_source` | String | Source of the defect (e.g., "Race Template") |
| `valid` | Boolean | Whether the defect is valid |

## Template Index

All templates must be listed in the `index.json` file in the templates directory:

```json
{
  "classes": [
    "adventurer",
    "artificer",
    "broker",
    "demon_hunter"
  ],
  "races": [
    "android_battle_maid",
    "archfiend",
    "asrai"
  ],
  "sizes": [
    "colossal",
    "diminutive",
    "enormous"
  ]
}
```

## Creating New Templates

1. Create a JSON file with the appropriate structure in the corresponding directory:
   - `data/templates/races/` for race templates
   - `data/templates/classes/` for class templates
   - `data/templates/sizes/` for size templates

2. Name the file using the template's key (e.g., `android_battle_maid.json`)

3. Add the template's key to the appropriate array in `index.json`

4. Ensure all attributes and defects reference valid keys from attributes.json and defects.json

## Best Practices

1. **Use Consistent Naming**: Keep naming conventions consistent
2. **Provide Clear Descriptions**: Make user_description fields clear and helpful
3. **Balance Templates**: Ensure templates are balanced and not overpowered
4. **Test Templates**: Verify templates work correctly in the application
5. **Follow BESM 4e Rules**: Adhere to the game's rules and terminology
6. **Use Appropriate Power Levels**: Match attribute levels and defect ranks to the intended power level

## Terminology Note

Remember that BESM 4e uses different terminology for attributes and defects:
- Attributes use "level" for their power rating
- Defects use "rank" for their power rating

The character generator maintains this terminology distinction.

## Examples

See the existing templates in the `data/templates/` directories for examples of well-structured templates.
