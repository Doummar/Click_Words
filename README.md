# Click Words

Click Words is a clean, interactive word-clicking exercise note type and add-on for Anki.
Works on Anki Desktop, AnkiWeb, AnkiMobile (iOS), and AnkiDroid (Android).

## User Flow
1. Read the Instruction (e.g. "Click on all adjectives").
2. Read the Passage.
3. Click target words directly within the text.
4. Click Check to see instant visual evaluation (correct, incorrect, missed).
5. Flip to the back to inspect the official answer key, explanation, and your attempt score.

## Note Type Fields
- **Instruction** (required): Task prompt shown on the card.
- **Passage** (required): Full reading text containing target words.
- **TargetWords** (required): Target words separated by `|` (pipe). Example: `dead|dead|stingy|heartless`. Duplicates and attached punctuation are supported; matching runs in passage order.
- **ExerciseType** (optional): Metadata category label (e.g. "Adjective Forms").
- **Explanation** (optional): Grammar or contextual notes displayed on the back of the card.
- **Front Audio** (optional): Anki `[sound:...]` replay button on front.
- **Back Audio** (optional): Anki `[sound:...]` replay button on back.
- **Source** (optional): Reference text or citation.
- **Extra** (optional): Additional supplementary notes.

## Mobile and AnkiWeb Support
The interactive engine is embedded directly inside the card template (HTML, CSS, JavaScript). The cards run on mobile devices (AnkiMobile, AnkiDroid) and AnkiWeb even without the desktop add-on installed.

## Add-on Features (Desktop)
- Automatically creates and configures the "Click Words" note type on first profile open.
- Safe template updates: card templates are never overwritten during regular review or settings save.
- **Restore Templates**: Available in **Tools > Click Words** to restore Front, Back, and Styling templates directly from the add-on package.

## License
MIT License. Copyright (c) 2026 Adel Aitah.
