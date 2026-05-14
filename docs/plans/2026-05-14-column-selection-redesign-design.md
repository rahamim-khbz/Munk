# Universal Column Selection Redesign — Design Document

**Date:** 2026-05-14  
**Project:** Munk Parallel Reader  
**Status:** Approved  

## 1. Overview & Objectives
The goal of this redesign is to deliver a premium, uncluttered scholarly reading interface by relocating column configuration controls into the Table of Contents sidebar drawer. Furthermore, the selection architecture is decoupled to allow seamless side-by-side display of any two distinct language translations from the full corpus repository, backed by a responsive layout that automatically injects visual section dividers on mobile devices and gracefully manages missing translation segments.

## 2. UI Layout & TOC Integration
* **Sidebar Relocation:** Column selector dropdowns are moved entirely out of the top of the main `.content` viewing container and integrated into the **Table of Contents Drawer** (`#toc-drawer`), immediately underneath the header controls.
* **Explicit Labeling:** Dropdowns are clearly labeled **Left Column** and **Right Column** to accurately reflect screen layout.
* **Simplified Universal Selectors:** Both dropdown elements expose identical options mapped to premium simplified display labels:
  1. `en`: **Munk (AI-English)**
  2. `fr`: **Munk (French)**
  3. `makbili`: **מקבילי**
  4. `tibon`: **אבן תיבון**
  5. `jrb`: **Judeo-Arabic**

## 3. Symmetrical DOM Structure & Pure CSS Visibility Engine
* **Symmetrical Markup:** For every segment parallel row, `render_row()` generates two identical structural wrappers: `<div class="left-cell">` and `<div class="right-cell">`. Inside both containers, all five translation variant strings are embedded inside standardized child spans (`.variant-en`, `.variant-fr`, `.variant-makbili`, `.variant-tibon`, `.variant-jrb`).
* **Pure CSS View Switching:** The main container tracking layer tracks layout state via custom data attributes (`data-left-col` and `data-right-col`). CSS display rules selectively reveal the matched variant span while hiding all inactive variants:
  ```css
  .left-cell .variant-span, .right-cell .variant-span { display: none; }
  .main-container[data-left-col="en"] .left-cell .variant-en { display: block; }
  .main-container[data-right-col="makbili"] .right-cell .variant-makbili { display: block; }
  ```
* **Decoupled Typography & Directionality:** Text alignment, flow direction (`direction: rtl` vs `ltr`), precise scholarly fonts, and line heights are tied directly to specific `.variant-*` target classes. This ensures structural text fidelity (e.g., RTL for Hebrew/Arabic, LTR for English/French) regardless of column destination.
* **Mobile Layout & Soft Line Divider:** On screen widths under `768px`, parallel rows shift to vertical single-column flex configurations. To provide clear visual distinction between stacked segment versions, a clean top border line divider is applied specifically onto `.right-cell` on mobile devices:
  ```css
  @media (max-width: 768px) {
      .parallel-row { display: flex; flex-direction: column; gap: 16px; padding: 20px 0; }
      .right-cell { border-top: 1px solid var(--border); padding-top: 12px; }
  }
  ```

## 4. JavaScript Control Logic
* **Mutual Exclusion Coordination:** Bound to selector `onchange` handlers, `updateColumnSelectors()` updates container layout data attributes and dynamically grays out (`disabled = true`) the currently active language choice inside the opposite dropdown selector. This prevents users from selecting duplicate text versions for both columns simultaneously.
* **Dynamic Navigation & Fallback Auto-Switching:** 
  * During chapter transitions via `navigateToChapter()`, script logic checks available translations for the requested section (e.g., standard chapters expose all five variants; prefaces and endnotes only provide English and French).
  * Options mapping to unavailable text variants are dynamically disabled within both dropdown elements.
  * **Auto-Switching:** If an active column selection becomes invalid/disabled in the newly selected section, fallback logic automatically reassigns that column's state to an available active translation (e.g., switching an invalid Hebrew column to Munk French) to ensure uninterrupted side-by-side reading.
