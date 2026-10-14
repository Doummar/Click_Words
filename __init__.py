"""
Click Words — Anki Add-on & Note Type
Author: Adel Aitah
License: MIT
Goal: Maintainable, simple, minimal, functional.
Works on Anki Desktop, AnkiWeb, AnkiMobile, AnkiDroid.
"""

import os
import re
from aqt import mw, gui_hooks
from aqt.qt import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QGroupBox,
    QAction,
    QTextBrowser,
    Qt,
    QFont,
)

from aqt.utils import tooltip

NOTE_TYPE_NAME = "Click Words"
VERSION = "1.2.17"

DEFAULT_CONFIG = {
    "word_style": "plain",
    "font_family": "",
    "font_size": 18,
    "card_vertical": "top",
    "card_horizontal": "center",
    "controls_pos": "top-right",
    "show_counter": True,
    "show_check_button": True,
    "show_attempt_summary": True
}

FIELDS = [
    "Instruction",
    "Passage",
    "TargetWords",
    "ExerciseType",
    "Explanation",
    "Front Audio",
    "Back Audio",
    "Source",
    "Extra"
]

def get_system_font_families():
    """Get sorted list of system font family names (Qt5 and Qt6 compatible)."""
    try:
        from aqt.qt import QFontDatabase
        try:
            families = QFontDatabase.families()
        except TypeError:
            families = QFontDatabase().families()
        clean_families = [f for f in families if not f.startswith("@")]
        return sorted(clean_families)
    except Exception:
        return []

def get_template_file(filename: str) -> str:
    """Read a template file from the add-on templates/ folder."""
    addon_dir = os.path.dirname(__file__)
    tmpl_path = os.path.join(addon_dir, "templates", filename)
    if os.path.exists(tmpl_path):
        with open(tmpl_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def ensure_note_type(force_restore: bool = False) -> bool:
    """
    Ensure the 'Click Words' note type exists with exact required fields and templates.
    Card templates are STABLE: templates are only updated on first install,
    version bump, or when the user explicitly clicks 'Restore Templates'.
    """
    if not mw or not mw.col:
        return False

    models = mw.col.models
    model = models.by_name(NOTE_TYPE_NAME)

    qfmt = get_template_file("front.html")
    afmt = get_template_file("back.html")
    css = get_template_file("styling.css")

    if not qfmt or not afmt or not css:
        return False

    if not model:
        # Create new model
        model = models.new(NOTE_TYPE_NAME)
        for field_name in FIELDS:
            fld = models.new_field(field_name)
            models.add_field(model, fld)

        template = models.new_template("Card 1")
        template["qfmt"] = qfmt
        template["afmt"] = afmt
        model["css"] = css
        models.add_template(model, template)
        model["cw_version"] = VERSION

        models.add(model)
        models.save(model)
        return True
    else:
        changed = False

        # Ensure all required fields exist
        existing_fields = [f["name"] for f in model["flds"]]
        for field_name in FIELDS:
            if field_name not in existing_fields:
                fld = models.new_field(field_name)
                models.add_field(model, fld)
                changed = True

        # Check version bump or user forced restore
        current_version = model.get("cw_version", "")
        if force_restore or current_version != VERSION:
            for tmpl in model.get("tmpls", []):
                tmpl["qfmt"] = qfmt
                tmpl["afmt"] = afmt
            model["css"] = css
            model["cw_version"] = VERSION
            changed = True

        if changed:
            models.save(model)
            return True

    return False

# ==============================================================================
# card_will_show Hook: Single Path for User Options & Isolation
# ==============================================================================
def on_card_will_show(text: str, card, kind: str) -> str:
    """
    Apply layout, options, and progress counter visibility to Click Words cards only.
    Non-Click Words cards are untouched (zero pollution).
    """
    # 1. Isolation check
    try:
        if hasattr(card, "note_type"):
            model = card.note_type()
        elif hasattr(card, "model"):
            model = card.model()
        else:
            model = None
        is_cw = (model and model.get("name") == NOTE_TYPE_NAME) or ('class="click-words"' in text)
    except Exception:
        is_cw = 'class="click-words"' in text

    if not is_cw:
        return text

    config = mw.addonManager.getConfig(__name__) or DEFAULT_CONFIG

    # 2. Progress Counter visibility: if show_counter is False, remove counter element
    show_counter = config.get("show_counter", True)
    if not show_counter:
        text = re.sub(r'<div[^>]*id="(?:cw|gct)-counter"[^>]*>.*?</div>', '', text, flags=re.DOTALL)

    # 3. Check button visibility: if show_check_button is False, remove Check button
    show_check = config.get("show_check_button", True)
    if not show_check:
        text = re.sub(r'<button[^>]*id="cw-btn-check"[^>]*>.*?</button>', '', text, flags=re.DOTALL)

    # 4. Attempt summary visibility on back: if show_attempt_summary is False, remove attempt box
    show_attempt_summary = config.get("show_attempt_summary", True)
    if not show_attempt_summary:
        text = re.sub(r'<div[^>]*id="cw-attempt-box"[^>]*>.*?</div>', '', text, flags=re.DOTALL)

    # 5. Apply options via data attributes on root .click-words
    word_style = config.get("word_style", "plain")
    controls_pos = config.get("controls_pos", "top-right")
    card_v = config.get("card_vertical", "top")
    card_h = config.get("card_horizontal", "center")
    font_family = str(config.get("font_family", "")).strip()
    font_size = config.get("font_size", 18)

    attrs = [
        f'data-word-style="{word_style}"',
        f'data-controls-pos="{controls_pos}"',
        f'data-align-v="{card_v}"',
        f'data-align-h="{card_h}"'
    ]

    inline_styles = []
    if font_family:
        inline_styles.append(f'--cw-font-family: "{font_family}", sans-serif; font-family: "{font_family}", sans-serif;')
    if font_size and font_size != 18:
        inline_styles.append(f'--cw-font-size: {font_size}px; font-size: {font_size}px;')

    if inline_styles:
        attrs.append(f'style="{" ".join(inline_styles)}"')

    attr_str = " ".join(attrs)

    # Inject into the root .click-words div cleanly (handles any attribute order)
    pattern = r'<div\s+([^>]*\bclass="[^"]*\bclick-words\b[^"]*"[^>]*)>'
    def replacer(m):
        existing = m.group(1)
        cleaned = re.sub(r'\s*data-(?:word-style|controls-pos|align-v|align-h)="[^"]*"', '', existing)
        return f'<div {attr_str} {cleaned.strip()}>'

    text = re.sub(pattern, replacer, text, count=1)
    return text

gui_hooks.card_will_show.append(on_card_will_show)

# ==============================================================================
# Guide Dialog
# ==============================================================================
class ClickWordsGuide(QDialog):
    """Simple plain-language Guide dialog for Click Words."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Click Words — Guide")
        self.setMinimumWidth(520)
        self.setMinimumHeight(440)
        layout = QVBoxLayout(self)

        guide_text = (
            "<h3>Click Words Guide</h3>"
            "<p><b>What it does:</b><br>"
            "Click Words turns any text passage into an interactive exercise where you click words "
            "directly in the passage to test your grammar, vocabulary, or comprehension.</p>"

            "<p><b>Card Fields:</b></p>"
            "<ul>"
            "<li><b>Instruction:</b> What the learner should find (e.g. <i>Find all past tense verbs</i>).</li>"
            "<li><b>Passage:</b> The full text containing words to click.</li>"
            "<li><b>TargetWords:</b> Correct words separated by a pipe <code>|</code> "
            "(e.g. <code>went | ate | slept</code>). Exact matches, case-sensitive, handles duplicates and multi-word phrases.</li>"
            "<li><b>ExerciseType:</b> Optional category label (e.g. <i>Grammar</i>, <i>Vocabulary</i>).</li>"
            "<li><b>Explanation:</b> Feedback and notes shown on the back side.</li>"
            "<li><b>Front Audio / Back Audio:</b> Optional sound clips.</li>"
            "<li><b>Extra / Source:</b> Optional context or citation notes.</li>"
            "</ul>"

            "<p><b>How to Review:</b></p>"
            "<ol>"
            "<li>Click words in the passage to select them.</li>"
            "<li>Click <b>Check</b> to see feedback on the front, or press <b>Show Answer</b> to flip.</li>"
            "<li>Back side highlights correct picks (solid green), incorrect picks (solid red), and missed words (dashed green), with a quiet summary line.</li>"
            "</ol>"

            "<p><b>Settings Overview:</b><br>"
            "Customize word style, font, size, alignment, progress counter, and whether to show the Check button.</p>"

            "<p><b>Mobile &amp; Web Compatibility:</b><br>"
            "Cards work fully on AnkiMobile (iOS), AnkiDroid (Android), and AnkiWeb. No add-on is required on mobile devices.</p>"
        )

        browser = QTextBrowser()
        browser.setHtml(guide_text)
        browser.setOpenExternalLinks(True)
        layout.addWidget(browser)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

# ==============================================================================
# Preferences Dialog
# ==============================================================================
class ClickWordsPreferences(QDialog):
    """Preferences Dialog for Click Words."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Click Words — Preferences")
        self.setMinimumWidth(440)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel(f"<b>Click Words</b> <span style='color: #64748b;'>v{VERSION}</span>")
        title.setStyleSheet("font-size: 14px; margin-bottom: 2px;")
        layout.addWidget(title)

        # General Group
        gen_group = QGroupBox("General Options")
        grid = QGridLayout(gen_group)

        # 1. Word style
        grid.addWidget(QLabel("Word style:"), 0, 0)
        self.style_combo = QComboBox()
        self.style_combo.addItem("Plain (bold on select)", "plain")
        self.style_combo.addItem("Outline", "outline")
        self.style_combo.addItem("Pills", "pills")
        grid.addWidget(self.style_combo, 0, 1)

        # 2. Font family (compact dropdown with System Default option)
        grid.addWidget(QLabel("Font family:"), 1, 0)
        self.font_combo = QComboBox()
        self.font_combo.setMaxVisibleItems(10)
        self.font_combo.addItem("System Default", "")
        try:
            font_role = Qt.ItemDataRole.FontRole
        except AttributeError:
            font_role = getattr(Qt, "FontRole", 6)
        for fam in get_system_font_families():
            self.font_combo.addItem(fam, fam)
            idx = self.font_combo.count() - 1
            try:
                self.font_combo.setItemData(idx, QFont(fam), font_role)
            except Exception:
                pass
        grid.addWidget(self.font_combo, 1, 1)

        # 3. Font size
        grid.addWidget(QLabel("Font size:"), 2, 0)
        self.size_spin = QSpinBox()
        self.size_spin.setRange(12, 32)
        self.size_spin.setValue(18)
        grid.addWidget(self.size_spin, 2, 1)

        # 4. Vertical alignment
        grid.addWidget(QLabel("Vertical:"), 3, 0)
        self.v_combo = QComboBox()
        self.v_combo.addItem("Top (default)", "top")
        self.v_combo.addItem("Center", "center")
        self.v_combo.addItem("Bottom", "bottom")
        grid.addWidget(self.v_combo, 3, 1)

        # 5. Horizontal alignment
        grid.addWidget(QLabel("Horizontal:"), 4, 0)
        self.h_combo = QComboBox()
        self.h_combo.addItem("Center (default)", "center")
        self.h_combo.addItem("Left", "left")
        self.h_combo.addItem("Right", "right")
        grid.addWidget(self.h_combo, 4, 1)

        # 6. Controls position (Audio corner)
        grid.addWidget(QLabel("Controls position:"), 5, 0)
        self.controls_combo = QComboBox()
        self.controls_combo.addItem("Top Right (default)", "top-right")
        self.controls_combo.addItem("Top Left", "top-left")
        self.controls_combo.addItem("Bottom Right", "bottom-right")
        self.controls_combo.addItem("Bottom Left", "bottom-left")
        grid.addWidget(self.controls_combo, 5, 1)

        # 7. Progress counter checkbox
        self.counter_cb = QCheckBox("Show progress counter (0/N found)")
        grid.addWidget(self.counter_cb, 6, 0, 1, 2)

        # 8. Check button checkbox
        self.check_btn_cb = QCheckBox("Show Check button")
        grid.addWidget(self.check_btn_cb, 7, 0, 1, 2)

        # 9. Attempt summary checkbox
        self.attempt_summary_cb = QCheckBox("Show attempt summary on back")
        grid.addWidget(self.attempt_summary_cb, 8, 0, 1, 2)

        layout.addWidget(gen_group)
        layout.addSpacing(10)

        # Bottom Button Row (Native Anki-like order: Restore Defaults | Restore Templates | Help | Save | Close)
        btn_layout = QHBoxLayout()

        restore_defs_btn = QPushButton("Restore Defaults")
        restore_defs_btn.clicked.connect(self.on_restore_defaults)
        btn_layout.addWidget(restore_defs_btn)

        restore_tmpl_btn = QPushButton("Restore Templates")
        restore_tmpl_btn.setToolTip("Force rewrite Front, Back, and CSS templates from disk into note type.")
        restore_tmpl_btn.clicked.connect(self.on_restore_templates)
        btn_layout.addWidget(restore_tmpl_btn)

        btn_layout.addStretch()

        help_btn = QPushButton("Help")
        help_btn.clicked.connect(self.on_help)
        btn_layout.addWidget(help_btn)

        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(save_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        # Load values
        self.load_from_config()

    def load_from_config(self, cfg=None):
        if cfg is None:
            cfg = mw.addonManager.getConfig(__name__) or DEFAULT_CONFIG

        # Style
        idx = self.style_combo.findData(cfg.get("word_style", "plain"))
        if idx >= 0:
            self.style_combo.setCurrentIndex(idx)

        # Font family
        font_fam = str(cfg.get("font_family", "")).strip()
        idx = self.font_combo.findData(font_fam)
        if idx >= 0:
            self.font_combo.setCurrentIndex(idx)
        else:
            idx = self.font_combo.findText(font_fam)
            if idx >= 0:
                self.font_combo.setCurrentIndex(idx)
            else:
                self.font_combo.setCurrentIndex(0)

        # Size
        self.size_spin.setValue(int(cfg.get("font_size", 18)))

        # Align V
        idx = self.v_combo.findData(cfg.get("card_vertical", "top"))
        if idx >= 0:
            self.v_combo.setCurrentIndex(idx)

        # Align H
        idx = self.h_combo.findData(cfg.get("card_horizontal", "center"))
        if idx >= 0:
            self.h_combo.setCurrentIndex(idx)

        # Controls Pos
        idx = self.controls_combo.findData(cfg.get("controls_pos", "top-right"))
        if idx >= 0:
            self.controls_combo.setCurrentIndex(idx)

        # Counter
        self.counter_cb.setChecked(bool(cfg.get("show_counter", True)))

        # Check Button
        self.check_btn_cb.setChecked(bool(cfg.get("show_check_button", True)))

        # Attempt Summary
        self.attempt_summary_cb.setChecked(bool(cfg.get("show_attempt_summary", True)))

    def on_restore_defaults(self):
        self.load_from_config(DEFAULT_CONFIG)
        tooltip("Default settings restored (click Save to apply).")

    def on_restore_templates(self):
        updated = ensure_note_type(force_restore=True)
        if mw.reviewer and mw.reviewer.card:
            try:
                mw.reset()
            except Exception:
                pass
        if updated:
            tooltip("Click Words templates restored from disk.")
        else:
            tooltip("Click Words templates already up-to-date.")

    def on_help(self):
        guide = ClickWordsGuide(self)
        guide.exec()

    def on_save(self):
        font_fam = self.font_combo.currentData()
        if font_fam is None:
            font_fam = ""

        new_config = {
            "word_style": self.style_combo.currentData(),
            "font_family": font_fam,
            "font_size": self.size_spin.value(),
            "card_vertical": self.v_combo.currentData(),
            "card_horizontal": self.h_combo.currentData(),
            "controls_pos": self.controls_combo.currentData(),
            "show_counter": self.counter_cb.isChecked(),
            "show_check_button": self.check_btn_cb.isChecked(),
            "show_attempt_summary": self.attempt_summary_cb.isChecked()
        }

        mw.addonManager.writeConfig(__name__, new_config)

        # If a Click Words card is currently being reviewed, refresh it immediately
        if mw.reviewer and mw.reviewer.card:
            try:
                style_val = new_config.get("word_style", "plain")
                # Immediately update active webview DOM attribute for live preview
                if hasattr(mw, "web") and mw.web:
                    mw.web.eval(f"var el = document.querySelector('.click-words'); if (el) el.setAttribute('data-word-style', '{style_val}');")
            except Exception:
                pass
            try:
                mw.reviewer.show()
            except Exception:
                pass
            try:
                mw.reset()
            except Exception:
                pass

        tooltip("Click Words preferences saved.")
        self.accept()

def on_profile_did_open():
    """Hook called automatically when user opens their Anki profile."""
    ensure_note_type(force_restore=False)

gui_hooks.profile_did_open.append(on_profile_did_open)

def open_preferences():
    dlg = ClickWordsPreferences(mw)
    dlg.exec()

# Register Tools Menu Action
action = QAction("Click Words", mw)
action.triggered.connect(open_preferences)
mw.form.menuTools.addAction(action)

# Register Add-on Config Action
mw.addonManager.setConfigAction(__name__, open_preferences)
