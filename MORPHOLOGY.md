# TCF French Morphology Trainer

This page complements Anki. Anki remains the only vocabulary source of truth.

## Import from Anki

Export your deck from Anki as `.apkg`, `.csv`, or `.tsv`, then run:

```powershell
python .\scripts\import_anki_deck.py "D:\path\your-deck.apkg"
```

The script writes:

```text
data/morphology.json
```

Open:

```text
morphology.html
```

or on GitHub Pages:

```text
https://littlechicken2.github.io/study-dashboard/morphology.html
```

## Required Anki fields

- `French`
- `Chinese`
- `Gender`
- `PartOfSpeech`
- `Lemma`
- `Plural`
- `Theme`
- `Level`
- `FixedPhrases`
- `ConjugationGroup`
- `PastParticiple`
- `Notes`

## Optional conjugation fields

For full verb training, add present-tense fields such as:

- `PresentJe`
- `PresentTu`
- `PresentIl`
- `PresentNous`
- `PresentVous`
- `PresentIls`

Alternatively, add a `Conjugations` field containing JSON:

```json
{
  "present": {
    "je": "vais",
    "tu": "vas",
    "il": "va",
    "nous": "allons",
    "vous": "allez",
    "ils": "vont"
  }
}
```

## Principle

Do not edit `data/morphology.json` by hand. Update the Anki deck, export again,
and re-run the importer.
