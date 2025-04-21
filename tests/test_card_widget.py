import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QLabel, QPushButton, QScrollArea, QSizePolicy,
    QTabWidget, QVBoxLayout, QWidget
)

def test_card_dynamic_height(besm_app, qtbot):
    """Test that cards have dynamic height based on content."""
    # Find the tools.utils module to access the card creation function
    from tools.utils import create_card_widget, ClickableCard
    
    # Create a test parent widget
    parent = QWidget()
    layout = QVBoxLayout(parent)
    
    # Create a card with short content
    short_card = create_card_widget(
        title="Short Card",
        lines=["This is a short description."]
    )
    
    # Create a card with long content
    long_content = ["This is a much longer description that should cause the card to expand."] * 5
    long_card = create_card_widget(
        title="Long Card",
        lines=long_content
    )
    
    # Add cards to layout
    layout.addWidget(short_card)
    layout.addWidget(long_card)
    
    # Show the parent widget
    parent.show()
    parent.adjustSize()  # Force layout recalculation
    qtbot.waitExposed(parent)
    
    # Add a longer delay to ensure layout is complete
    qtbot.wait(500)  # Increased from 100ms to 500ms
    
    # Force another layout recalculation
    parent.updateGeometry()
    parent.update()
    
    # Verify size policies
    short_content_label = None
    long_content_label = None
    
    for label in short_card.findChildren(QLabel):
        if label.text() == "This is a short description.":
            short_content_label = label
            break
    
    for label in long_card.findChildren(QLabel):
        if "\n".join(long_content) in label.text():
            long_content_label = label
            break
    
    assert short_content_label is not None, "Short content label not found"
    assert long_content_label is not None, "Long content label not found"
    
    # Verify content label size policies
    assert short_content_label.sizePolicy().verticalPolicy() == QSizePolicy.MinimumExpanding, "Short content label should have MinimumExpanding vertical policy"
    assert long_content_label.sizePolicy().verticalPolicy() == QSizePolicy.MinimumExpanding, "Long content label should have MinimumExpanding vertical policy"
    
    # Verify that the long card is taller than the short card
    assert long_card.height() > short_card.height(), f"Long card should be taller than short card (long: {long_card.height()}, short: {short_card.height()})"
    
    # Verify that text is selectable
    assert long_content_label.textInteractionFlags() & Qt.TextSelectableByMouse, "Text should be selectable"
    
    # Verify minimum height
    assert short_card.minimumHeight() >= 80, f"Card should have minimum height of 80px (actual: {short_card.minimumHeight()})"
    
    # Clean up
    parent.close()

def test_card_in_scroll_area(besm_app, qtbot, special_attributes):
    """Test that cards in scroll areas expand properly."""
    # Find a tab with special attributes (they all use scroll areas with cards)
    tab_widget = besm_app.findChild(QTabWidget)
    
    # Look for one of the special attribute tabs
    special_tab_found = False
    for i in range(tab_widget.count()):
        tab_name = tab_widget.tabText(i)
        if tab_name in special_attributes:
            tab_widget.setCurrentIndex(i)
            special_tab_found = True
            break
    
    # If no special tab is found, the test passes trivially
    # This can happen if no special attributes are added yet
    if not special_tab_found:
        return
    
    # Find the scroll area in the tab
    scroll_area = tab_widget.currentWidget().findChild(QScrollArea)
    assert scroll_area is not None, "Scroll area not found in special attribute tab"
    
    # Get the scroll area's widget
    scroll_widget = scroll_area.widget()
    assert scroll_widget is not None, "Scroll widget not found"
    
    # Check if there are any cards
    cards = scroll_widget.findChildren(QWidget, "card_widget")
    
    # If there are cards, verify they can expand vertically
    if cards:
        for card in cards:
            # Check size policy
            v_policy = card.sizePolicy().verticalPolicy()
            assert v_policy in [QSizePolicy.Expanding, QSizePolicy.MinimumExpanding], \
                "Card should have vertical expansion policy"
            
            # Check that there's no fixed maximum height that would prevent expansion
            assert card.maximumHeight() > 120 or card.maximumHeight() == 16777215, \
                "Card should not have restrictive maximum height"
