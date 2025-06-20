from tools.widgets import LabeledRowWithHelp
from PyQt5.QtWidgets import (
    QWidget, QLabel, QSpinBox, QFormLayout
)

def init_stats_tab(self):
    tab = QWidget()
    main_content_layout = QFormLayout()
    self.stat_spinners = {}

    stats_help = {
        "Body": "Physical strength, stamina, and toughness.",
        "Mind": "Intellect, memory, logic, and reasoning.",
        "Soul": "Willpower, intuition, and force of personality.",
    }

    for stat in ["Body", "Mind", "Soul"]:
        spin = QSpinBox()
        spin.setMinimum(0)
        spin.setMaximum(99)
        spin.setValue(self.character_data["stats"][stat])
        
        # Connect to update_stat method which will handle derived values
        spin.valueChanged.connect(lambda value, stat_name=stat: self.update_stat(stat_name, value))
        
        self.stat_spinners[stat] = spin
        row_widget = LabeledRowWithHelp(stat, spin, stats_help[stat])
        main_content_layout.addRow(row_widget)

    # Derived stat labels
    self.cv_label = QLabel("")
    self.acv_label = QLabel("")
    self.dcv_label = QLabel("")
    self.hp_label = QLabel("")
    self.ep_label = QLabel("")
    self.dm_label = QLabel("")
    self.sv_label = QLabel("")
    self.sp_label = QLabel("")
    self.scv_label = QLabel("")
    self.sop_label = QLabel("")

    self.stat_rows = {}

    def add_stat_row(label, widget, help_text):
        row_widget = LabeledRowWithHelp(label, widget, help_text)
        main_content_layout.addRow(row_widget)
        self.stat_rows[label] = row_widget

    add_stat_row("Combat Value (CV)", self.cv_label, "Your overall combat proficiency. It represents how skilled and balanced you are in physical and mental combat.")
    add_stat_row("Attack CV (ACV)", self.acv_label, "Your accuracy in combat.")
    add_stat_row("Defense CV (DCV)", self.dcv_label, "Your ability to avoid or deflect attacks.")
    add_stat_row("Health Points (HP)", self.hp_label, "Health Points measure the amount of physical damage your character’s body can sustain.")
    add_stat_row("Energy Points (EP)", self.ep_label, "Characters possess a personal reserve of energy that may be burned when carrying out difficult tasks.")
    add_stat_row("Damage Multiplier", self.dm_label, "Increases the damage you deal when you successfully hit.")
    add_stat_row("Shock Value", self.sv_label, "The damage threshold before the character risks being stunned, knocked out, or suffering a serious injury.")
    add_stat_row("Sanity Points", self.sp_label, "Sanity Points represent a character’s relationship with reality and conscious understanding of the greater world.")
    add_stat_row("Social Combat Value", self.scv_label, "The talent that a character has for witty societal engagements.")
    add_stat_row("Society Points", self.sop_label, "Once a character’s Society Points drop to zero in social combat, they have been defeated in the war of words and suffer an outcome appropriate to the situation.")
    tab.setLayout(main_content_layout)
    self.tabs.addTab(tab, "Stats")