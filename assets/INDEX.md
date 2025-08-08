# /assets/INDEX.md

## Purpose and Overview
The `assets/` directory holds static resources used by the project. It also serves as the default location for local presets storage (JSON) used by the application to persist Brand Bibles, Email signatures, and Blog styles.

## Files
- `banner.png`: Project banner used in the root `README.md`.
- `presets.json` (created on first run): Local key-value store managed by `utils/presets.py`.

## Usage
- Presets are automatically created/read by `utils/presets.py`. You do not need to manually create `presets.json`—it will be created on first write.
- To change where presets are stored, set environment variable `PRESETS_PATH` to an absolute or relative file path.

Example structure (subject to change):

```json
{
  "brand_bibles": {
    "Acme_Default": { "xml_raw": "<brand>...</brand>" }
  },
  "email_sigs": {
    "Standard": { "content": "Best,\nAcme Team" }
  },
  "blog_styles": {
    "HouseStyleA": { "content": "{\"title_case\": true}" }
  }
}
```

## Dependencies / Prerequisites
- None at build time. At runtime, `utils/presets.py` will read/write `assets/presets.json` unless `PRESETS_PATH` is set.
