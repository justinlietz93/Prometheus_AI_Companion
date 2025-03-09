# Prometheus UI Enhancement Plan

This document outlines the specific UI improvements needed, based on the requested enhancements. Each task is broken down into actionable steps.

## 1. Fix QPixmap Error in Search Widget

- [x] Identify the search widget QPixmap error in prompt_generator_qt.py
- [x] Update search widget to use a proper QLabel or icon instead of QPixmap
- [x] Test search widget functionality

## 2. Implement 10 Levels of Urgency

- [ ] Update constants.py to define 10 urgency levels
- [ ] Modify the urgency slider to support 10 levels (min=1, max=10)
- [ ] Update the urgency display formatting to show "/10"
- [ ] Test slider functionality with all levels

## 3. Fix Selector Window to Show All Text and Tags

- [ ] Adjust layout of prompt list items to prevent text truncation
- [ ] Add tooltips to show full text on hover
- [ ] Ensure tags are properly visible and not overlapping
- [ ] Test with various screen sizes

## 4. Replace Bottom Description with Brief Description Above Selection

- [ ] Remove description text area from bottom of left panel
- [ ] Add a brief description label above the prompt list
- [ ] Update handleItemSelection method to update the brief description
- [ ] Test description update when selecting different prompts

## 5. Add Info Icon for Metadata Display

- [ ] Add info icon to PromptListItem class
- [ ] Connect icon to metadata dialog display
- [ ] Update styling to match modern IDE look
- [ ] Test metadata display functionality

## 6. Move Generate Prompts Button Next to Copy to Clipboard

- [ ] Rearrange button layout to place both buttons side by side
- [ ] Apply consistent styling to both buttons
- [ ] Test button placement and functionality

## 7. Make Editor Window Editable

- [ ] Update output text area to be editable instead of read-only
- [ ] Update placeholder text to indicate editability
- [ ] Test editing functionality

## 8. Clean Up Generated Prompt Output

- [ ] Remove metadata and headers from generated prompts
- [ ] Ensure only the clean prompt text is included in output
- [ ] Test prompt generation with different selections

## 9. Update Search Icon to Modern Style

- [ ] Replace the current search icon with a more modern one from Qt standard icons
- [ ] Position icon properly within the search input
- [ ] Test search functionality with new icon

## 10. Overall Modern IDE-Like UI Improvements

- [ ] Adjust padding and margins for better spacing
- [ ] Improve color contrast for better readability
- [ ] Add hover effects for interactive elements
- [ ] Ensure consistent styling across all components
- [ ] Test UI appearance with different themes 