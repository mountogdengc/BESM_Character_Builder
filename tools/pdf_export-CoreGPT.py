"""
PDF Export functionality for BESM Character Generator
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable

def export_character_to_pdf(character_data, output_path=None):
    """
    Export character data to a PDF file
    
    Args:
        character_data (dict): The character data dictionary
        output_path (str, optional): Path to save the PDF. If None, saves to desktop with character name
    
    Returns:
        str: Path to the saved PDF file
    """
    # If no output path provided, create one on desktop
    if not output_path:
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        char_name = character_data.get("name", "Character").replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(desktop, f"{char_name}_{timestamp}.pdf")
    
    # Create the document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        spaceAfter=6,
        spaceBefore=12,
        textColor=colors.darkblue
    ))
    styles.add(ParagraphStyle(
        name='Subheader',
        parent=styles['Heading3'],
        spaceBefore=6,
        textColor=colors.darkblue
    ))
    styles.add(ParagraphStyle(
        name='Normal_Indent',
        parent=styles['Normal'],
        leftIndent=20
    ))
    
    # Story (content elements)
    story = []
    
    # Title
    char_name = character_data.get("name", "Unnamed Character")
    story.append(Paragraph(f"BESM Character Sheet: {char_name}", styles['Title']))
    story.append(Spacer(1, 0.1*inch))
    
    # Basic Info
    story.append(Paragraph("Character Information", styles['SectionHeader']))
    
    basic_info = [
        ["Name:", character_data.get("name", "")],
        ["Player:", character_data.get("player", "")],
        ["Campaign:", character_data.get("campaign", "")],
        ["Character Points:", str(character_data.get("totalPoints", 0))],
        ["Character Points Spent:", str(character_data.get("pointsSpent", 0))],
        ["Character Points Remaining:", str(character_data.get("totalPoints", 0) - character_data.get("pointsSpent", 0))]
    ]
    
    # Add description if available
    description = character_data.get("description", "")
    if description:
        basic_info.append(["Description:", description])
    
    # Create table for basic info
    basic_table = Table(basic_info, colWidths=[2.5*inch, 4*inch])
    basic_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(basic_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Horizontal line
    story.append(HRFlowable(width="100%", thickness=1, color=colors.darkblue))
    
    # Stats
    story.append(Paragraph("Stats", styles['SectionHeader']))
    
    stats = character_data.get("stats", {})
    body = stats.get("Body", 0)
    mind = stats.get("Mind", 0)
    soul = stats.get("Soul", 0)
    
    # Calculate derived values
    cv = (body + mind + soul) // 3
    acv = cv  # Attack Combat Value
    dcv = cv  # Defense Combat Value
    hp = body * 10  # Health Points
    ep = mind * 10  # Energy Points
    sv = body * 2   # Shock Value
    dm = (body + soul) // 2  # Damage Multiplier
    sp = soul * 10  # Sanity Points
    sop = mind * 10  # Society Points
    
    # Create stats table with fully spelled out derived values
    stats_data = [
        ["Stat", "Value", "Derived Values"],
        ["Body", str(body), f"Health Points: {hp}, Shock Value: {sv}"],
        ["Mind", str(mind), f"Energy Points: {ep}, Society Points: {sop}"],
        ["Soul", str(soul), f"Sanity Points: {sp}"]
    ]
    
    # Add combat values
    stats_data.append(["Combat Values", "", f"Combat Value: {cv}, Attack CV: {acv}, Defense CV: {dcv}, Damage Multiplier: {dm}"])
    
    stats_table = Table(stats_data, colWidths=[2*inch, 1.5*inch, 3.5*inch])
    stats_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Horizontal line
    story.append(HRFlowable(width="100%", thickness=1, color=colors.darkblue))
    
    # Attributes
    story.append(Paragraph("Attributes", styles['SectionHeader']))
    
    attributes = character_data.get("attributes", [])
    if attributes:
        attr_data = [["Name", "Level", "Cost", "Description"]]
        
        for attr in attributes:
            attr_data.append([
                attr.get("name", ""),
                str(attr.get("level", 0)),
                str(attr.get("cost", 0)),
                attr.get("user_description", attr.get("description", ""))[:100] + "..." if len(attr.get("user_description", attr.get("description", ""))) > 100 else attr.get("user_description", attr.get("description", ""))
            ])
        
        attr_table = Table(attr_data, colWidths=[2*inch, 0.75*inch, 0.75*inch, 3.5*inch])
        attr_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(attr_table)
    else:
        story.append(Paragraph("No attributes selected.", styles['Normal']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Horizontal line
    story.append(HRFlowable(width="100%", thickness=1, color=colors.darkblue))
    
    # Defects
    story.append(Paragraph("Defects", styles['SectionHeader']))
    
    defects = character_data.get("defects", [])
    if defects:
        defect_data = [["Name", "Rank", "Value", "Description"]]
        
        for defect in defects:
            defect_data.append([
                defect.get("name", ""),
                str(defect.get("rank", 0)),
                str(defect.get("cost", 0)),
                defect.get("description", "")[:100] + "..." if len(defect.get("description", "")) > 100 else defect.get("description", "")
            ])
        
        defect_table = Table(defect_data, colWidths=[2*inch, 0.75*inch, 0.75*inch, 3.5*inch])
        defect_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(defect_table)
    else:
        story.append(Paragraph("No defects selected.", styles['Normal']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Horizontal line
    story.append(HRFlowable(width="100%", thickness=1, color=colors.darkblue))
    
    # Skills
    story.append(Paragraph("Skills", styles['SectionHeader']))
    
    skills = character_data.get("skills", [])
    if skills:
        skill_data = [["Name", "Level", "Relevant Stat", "Description"]]
        
        for skill in skills:
            skill_data.append([
                skill.get("name", ""),
                str(skill.get("level", 0)),
                skill.get("relevant_stat", ""),
                skill.get("description", "")[:100] + "..." if len(skill.get("description", "")) > 100 else skill.get("description", "")
            ])
        
        skill_table = Table(skill_data, colWidths=[2*inch, 0.75*inch, 1.25*inch, 3*inch])
        skill_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(skill_table)
    else:
        story.append(Paragraph("No skills selected.", styles['Normal']))
    
    # Add special sections if they exist
    special_sections = [
        ("companions", "Companions"),
        ("items", "Items"),
        ("minions", "Minions"),
        ("alternate_forms", "Alternate Forms"),
        ("metamorphosis", "Metamorphosis")
    ]
    
    for section_key, section_title in special_sections:
        if character_data.get(section_key, []):
            # Add page break for each special section
            story.append(PageBreak())
            story.append(Paragraph(section_title, styles['SectionHeader']))
            
            items = character_data.get(section_key, [])
            for item in items:
                story.append(Paragraph(item.get("name", "Unnamed"), styles['Subheader']))
                
                # Create a list of item details
                details = []
                
                # Add common fields
                if "level" in item:
                    details.append(["Level", str(item.get("level", 0))])
                if "cost" in item:
                    details.append(["Cost", str(item.get("cost", 0)) + " CP"])
                if "total_cp" in item:
                    details.append(["Total CP", str(item.get("total_cp", 0))])
                if "description" in item:
                    details.append(["Description", item.get("description", "")])
                
                # Add section-specific fields
                if section_key == "companions":
                    # Add companion stats
                    if "stats" in item:
                        stats = item.get("stats", {})
                        details.append(["Body", str(stats.get("Body", 0))])
                        details.append(["Mind", str(stats.get("Mind", 0))])
                        details.append(["Soul", str(stats.get("Soul", 0))])
                
                elif section_key == "minions":
                    # Add minion count
                    if "count" in item:
                        details.append(["Count", str(item.get("count", 0))])
                
                # Create table for item details
                if details:
                    detail_table = Table(details, colWidths=[2.5*inch, 4.5*inch])
                    detail_table.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(detail_table)
                
                # Add attributes and defects if they exist
                if "attributes" in item and item["attributes"]:
                    story.append(Paragraph("Attributes:", styles['Subheader']))
                    attr_data = [["Name", "Level", "Cost"]]
                    for attr in item["attributes"]:
                        attr_data.append([
                            attr.get("name", ""),
                            str(attr.get("level", 0)),
                            str(attr.get("cost", 0))
                        ])
                    attr_table = Table(attr_data, colWidths=[3.5*inch, 1.5*inch, 2*inch])
                    attr_table.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(attr_table)
                
                if "defects" in item and item["defects"]:
                    story.append(Paragraph("Defects:", styles['Subheader']))
                    defect_data = [["Name", "Rank", "Value"]]
                    for defect in item["defects"]:
                        defect_data.append([
                            defect.get("name", ""),
                            str(defect.get("rank", 0)),
                            str(defect.get("cost", 0))
                        ])
                    defect_table = Table(defect_data, colWidths=[3.5*inch, 1.5*inch, 2*inch])
                    defect_table.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    story.append(defect_table)
                
                story.append(Spacer(1, 0.2*inch))
                story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
                story.append(Spacer(1, 0.2*inch))
    
    # Add final page with CP calculations
    story.append(PageBreak())
    story.append(Paragraph("Character Point Calculations", styles['Title']))
    story.append(Spacer(1, 0.2*inch))
    
    # Create detailed CP breakdown
    story.append(Paragraph("Character Point Breakdown", styles['SectionHeader']))
    story.append(Spacer(1, 0.1*inch))
    
    # Stats breakdown
    stats = character_data.get("stats", {})
    
    # Ensure stats is a dictionary
    if not isinstance(stats, dict):
        stats = {"Body": 1, "Mind": 1, "Soul": 1}
    
    # Calculate total CP from stats
    stat_cp = 0
    for stat_value in stats.values():
        if isinstance(stat_value, (int, float)):
            stat_cp += stat_value * 2
    
    stats_breakdown = [
        ["Stat", "Value", "Cost per Point", "Total CP"]
    ]
    
    for stat_name, stat_value in stats.items():
        if isinstance(stat_value, (int, float)):
            stats_breakdown.append([stat_name, str(stat_value), "2", str(stat_value * 2)])
    
    stats_breakdown.append(["Stats Subtotal", "", "", str(stat_cp)])
    
    stats_table = Table(stats_breakdown, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch])
    stats_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Attributes breakdown - detailed invoice style
    attributes = character_data.get("attributes", [])
    
    # Ensure attributes is a list
    if not isinstance(attributes, list):
        attributes = []
        
    attr_cp = 0
    if attributes:
        story.append(Paragraph("Attributes", styles['Subheader']))
        attr_breakdown = [
            ["Attribute", "Level", "Cost per Level", "Modifiers", "Total CP"]
        ]
        
        for attr in attributes:
            # Skip if attr is not a dictionary
            if not isinstance(attr, dict):
                continue
                
            name = attr.get("name", "")
            level = attr.get("level", 0)
            cost = attr.get("cost", 0)
            
            # Skip if level or cost is not a number
            if not isinstance(level, (int, float)) or not isinstance(cost, (int, float)):
                continue
                
            # Calculate base cost per level
            base_cost = cost / level if level > 0 else 0
            modifiers = ""
            
            # Check for enhancements/limiters
            enhancements = attr.get("enhancements", [])
            limiters = attr.get("limiters", [])
            
            # Ensure enhancements and limiters are lists
            if not isinstance(enhancements, list):
                enhancements = []
            if not isinstance(limiters, list):
                limiters = []
            
            if enhancements or limiters:
                mod_texts = []
                for enh in enhancements:
                    if isinstance(enh, dict):
                        mod_texts.append(f"+{enh.get('value', 0)} {enh.get('name', '')}")
                for lim in limiters:
                    if isinstance(lim, dict):
                        mod_texts.append(f"-{lim.get('value', 0)} {lim.get('name', '')}")
                modifiers = ", ".join(mod_texts)
            
            attr_breakdown.append([name, str(level), str(int(base_cost)), modifiers, str(cost)])
            attr_cp += cost
        
        attr_breakdown.append(["Attributes Subtotal", "", "", "", str(attr_cp)])
        
        attr_table = Table(attr_breakdown, colWidths=[2*inch, 0.75*inch, 1*inch, 2*inch, 1.25*inch])
        attr_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(attr_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Defects breakdown - detailed invoice style
    defects = character_data.get("defects", [])
    
    # Ensure defects is a list
    if not isinstance(defects, list):
        defects = []
        
    defect_cp = 0
    if defects:
        story.append(Paragraph("Defects", styles['Subheader']))
        defect_breakdown = [
            ["Defect", "Rank", "Value per Rank", "Total CP"]
        ]
        
        for defect in defects:
            # Skip if defect is not a dictionary
            if not isinstance(defect, dict):
                continue
                
            name = defect.get("name", "")
            rank = defect.get("rank", 0)
            cost = defect.get("cost", 0)
            
            # Skip if rank or cost is not a number
            if not isinstance(rank, (int, float)) or not isinstance(cost, (int, float)):
                continue
                
            value_per_rank = cost / rank if rank > 0 else 0
            
            defect_breakdown.append([name, str(rank), str(int(value_per_rank)), str(cost)])
            defect_cp += cost
        
        defect_breakdown.append(["Defects Subtotal", "", "", str(defect_cp)])
        
        defect_table = Table(defect_breakdown, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        defect_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(defect_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Skills breakdown if any
    skills = character_data.get("skills", [])
    
    # Ensure skills is a list
    if not isinstance(skills, list):
        skills = []
        
    skill_cp = 0
    if skills:
        story.append(Paragraph("Skills", styles['Subheader']))
        skill_breakdown = [
            ["Skill", "Level", "Cost per Level", "Total CP"]
        ]
        
        for skill in skills:
            # Skip if skill is not a dictionary
            if not isinstance(skill, dict):
                continue
                
            name = skill.get("name", "")
            level = skill.get("level", 0)
            cost = skill.get("cost", 0)
            
            # Skip if level or cost is not a number
            if not isinstance(level, (int, float)) or not isinstance(cost, (int, float)):
                continue
                
            cost_per_level = cost / level if level > 0 else 0
            
            skill_breakdown.append([name, str(level), str(int(cost_per_level)), str(cost)])
            skill_cp += cost
        
        skill_breakdown.append(["Skills Subtotal", "", "", str(skill_cp)])
        
        skill_table = Table(skill_breakdown, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        skill_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(skill_table)
        story.append(Spacer(1, 0.2*inch))
    
    # Total CP summary
    total_cp = stat_cp + attr_cp + defect_cp + skill_cp
    
    story.append(Paragraph("Character Points Summary", styles['Subheader']))
    summary = [
        ["Category", "Character Points"],
        ["Stats", str(stat_cp)],
        ["Attributes", str(attr_cp)],
        ["Defects", str(defect_cp)],
    ]
    
    if skill_cp > 0:
        summary.append(["Skills", str(skill_cp)])
    
    # Add starting CP and remaining CP if available
    starting_cp = character_data.get("totalPoints", total_cp)
    summary.append(["Total CP Spent", str(total_cp)])
    summary.append(["Starting CP", str(starting_cp)])
    summary.append(["Remaining CP", str(starting_cp - total_cp)])
    
    summary_table = Table(summary, colWidths=[4*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    
    # CP breakdown is now complete
    
    # Build the PDF
    doc.build(story)
    
    return output_path
