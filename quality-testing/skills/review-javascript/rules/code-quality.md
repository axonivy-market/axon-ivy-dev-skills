# Code Quality Rules — Q1–Q4

**Q1. DRY — Extract Shared Helpers and Decompose**
*Scan for:* same DOM operations repeated in 2+ functions; if/else branches repeating the same work categories; functions >50 lines mixing multiple concerns.
*Why:* Duplicated code leads to partial fixes. Extract each concern into a helper; public methods become short orchestrators.

**Decomposition pattern:**

| Concern | Symptom | Extract to |
| --- | --- | --- |
| DOM class + ARIA + label | `addClass`/`removeClass` if/else, `.show()`/`.hide()` | `_applyVisualState(flag)` |
| Persistence | `$.cookie` / `remoteCommand` / `$.post` | `_persistState(flag)` |
| Deferred layout | `setTimeout` + layout recalculation | `_scheduleLayoutUpdate()` |

```javascript
// Bad: duplicated in init() and toggle()
init: function() {
  if (stateExists) { $('.label').show(); $('.btn').attr('aria-expanded', 'true'); }
},
toggle: function() {
  this._isExpanded = !this._isExpanded;
  if (this._isExpanded) { $('.label').show(); $('.btn').attr('aria-expanded', 'true'); }
  else { $('.label').hide(); $('.btn').attr('aria-expanded', 'false'); }
  setTimeout(function() { Portal.updateBreadcrumb(); }, 250);
}

// Good: shared helper + orchestrator
_applyVisualState: function(expanded) {
  $(SEL_WRAPPER).toggleClass('layout-static', expanded);
  $(SEL_LABEL).toggle(expanded);
  $(SEL_BTN).attr('aria-expanded', String(expanded));
},
toggle: function() {
  this._isExpanded = !this._isExpanded;
  this._applyVisualState(this._isExpanded);
  this._persistState(this._isExpanded);
  this._scheduleLayoutUpdate();
}
```

---

**Q2. Cache Repeated jQuery Selectors**
*Scan for:* same `$(selector)` called 3+ times without caching.
*Why:* Each call traverses the DOM. Cache in a variable or named constant.

---

**Q3. No Magic Values — Name Constants**
*Scan for:* unnamed literals in logic (timeouts, pixel fallbacks, class names as identifiers); same literal in 2+ places.
*Why:* Magic values are fragile. Extract to named constants.

```javascript
// Bad                                    // Good
setTimeout(fn, 250);                      var FREYA_TRANSITION_MS = 250;
                                          setTimeout(fn, FREYA_TRANSITION_MS);
```

---

**Q4. Consistent API — Don't Mix jQuery and Native DOM**
*Scan for:* `document.querySelector` in one function and `$(selector)` in another for the same element.
*Why:* Mixing styles hurts readability. Use jQuery everywhere. Exception: native APIs that require a DOM element (e.g., `MutationObserver.observe()`). Use `$(selector)[0]` and comment why.

```javascript
// Bad
ensureCollapsed: function() { document.querySelector('.wrapper').classList.remove('active'); },
toggle: function() { $('.wrapper').addClass('active'); }

// Good
ensureCollapsed: function() { $(SEL_WRAPPER).removeClass('active'); },
observeAndBlockHover: function() {
  var wrapper = $(SEL_WRAPPER)[0]; // native required by MutationObserver
  this._observer = new MutationObserver(function() { /* classList OK here */ });
  this._observer.observe(wrapper, { attributes: true, attributeFilter: ['class'] });
}
```
