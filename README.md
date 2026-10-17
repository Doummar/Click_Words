# Click Words

**Click Words** is an interactive Anki add-on for practicing word recognition in context. Read a passage, click the words that match the instruction, and check your answers instantly.

It is designed for grammar practice, language learning, and reading exercises.

## How It Works

1. Read the instruction, such as *"Click on all adjectives."*
2. Read the passage.
3. Click the words that match the instruction.
4. Select **Check** to see correct, incorrect, and missed answers.
5. Flip the card to review the answer key, explanation, and your score.

## Note Type Fields

| Field | Description |
|---|---|
| **Instruction** | The task or question shown on the card. |
| **Passage** | The text containing the words to identify. |
| **TargetWords** | Correct answers separated by `\|` (pipe). For example: `dead\|stingy\|heartless`. Repeated words and punctuation are supported. |
| **ExerciseType** | Optional category, such as `Adjective Forms`. |
| **Explanation** | Optional explanation or grammar notes shown on the back. |
| **Front Audio** | Optional audio replay button on the front. |
| **Back Audio** | Optional audio replay button on the back. |
| **Source** | Optional source or reference. |
| **Extra** | Optional supplementary information. |

## Platform Support

The interactive exercise is built into the card templates using HTML, CSS, and JavaScript. This allows the cards to run without the desktop add-on being installed on the reviewing device, provided the platform supports the required template functionality.

- Anki Desktop
- AnkiWeb
- AnkiMobile (iOS)
- AnkiDroid (Android)

## Desktop Add-on Features

- Automatically creates and configures the **Click Words** note type when a profile is opened for the first time.
- Keeps existing card templates intact during normal reviews and settings saves.
- Provides **Restore Templates** under **Tools → Click Words** to restore the default Front, Back, and Styling templates from the add-on package.

## License

MIT License. Copyright (c) 2026
