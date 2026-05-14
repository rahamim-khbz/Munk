# Section-Specific Selection Refinement — Design Document

**Date:** 2026-05-14  
**Project:** Munk Parallel Reader  
**Status:** Approved  

## 1. Overview & Objectives
This design details the logic refactoring required to introduce specialized defaults and granular option filtering based on specific loaded reader section capabilities. Munk's scholarly prefaces and endnotes are structured to automatically default to French on the left and English on the right while grayout-filtering unpopulated original source language choices. User exploratory configurations in standard multi-variant philosophical chapters are tracked persistently to ensure custom views are reliably restored upon exiting specialized sections.

## 2. Tracking Variables Architecture & Contextual Masking
* **State Caching:** Two top-level JavaScript tracking references are declared to persist active selections across standard reading contexts:
  ```javascript
  let previousStandardLeft = 'en';
  let previousStandardRight = 'makbili';
  ```
* **Contextual Masking:** Within section activation hooks (`navigateToChapter()`), layout UI panels are filtered dynamically. The entire Table of Contents column configuration section (`.toc-column-panel`) is assigned `display: none` when activating the global landing page (`'Contents'`), preventing interactive exposure in contextless state environments.

## 3. Dynamic Default Forcing & Grayscale Variant Filtering
* **Section Mapping:** Navigation lifecycle triggers check whether destination chapters qualify as restricted Munk segments:
  ```javascript
  const isMunkSection = title.startsWith('Introduction to Volume') || 
                        title === 'Note On The Title' || 
                        title.startsWith('Endnotes to Volume');
  ```
* **Grayscale Option Filtering:** For restricted Munk sections, non-Munk options (`'makbili'`, `'tibon'`, `'jrb'`) are instantly assigned `disabled = true` within both selector dropdown structures. Standard Maimonides chapters unconditionally clear option status flags to restore fully selectable availability.
* **Persistent Forcing Rules:**
  1. **Entering a Munk Section:** Caches current custom dropdown states into `previousStandardLeft`/`previousStandardRight` tracking variables, then enforces default layout alignment: Left Column = **Munk (French)** (`'fr'`), Right Column = **Munk (AI-English)** (`'en'`).
  2. **Returning to a Standard Section:** Overrides generic global fallback parameters to restore user custom layout variants directly from saved internal tracking cache variables.

## 4. Coordination & Verification
* **Real-time DOM Synchronization:** Layout logic transformations trigger `updateColumnSelectors()` immediately after state changes, enforcing CSS main container variant reveal rules and processing mutual exclusion grayout filtering for opposite column options.
* **Automated Unit Verification:** Automated build pipeline test checks confirm the presence of new tracking variables, dynamic default forcing instructions, section layout predicates, and TOC panel context masking styles.
