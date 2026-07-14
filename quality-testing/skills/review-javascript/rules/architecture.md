# Architecture Rules — AR1–AR2

**AR1. File Size — Split Large Files**
*Scan for:* `.js` file exceeding ~500 lines; a new namespace object pushing an existing file past this threshold.
*Why:* Large files are hard to navigate and review. One namespace object per file.

```javascript
// Bad: multiple namespace objects in one file
var Portal = { /* 160 lines */ };
var SidebarClickMode = { /* 90 lines */ };

// Good: portal.js → Portal only, sidebar.js → SidebarClickMode only
```

---

**AR2. Avoid Tight Coupling to External Theme Internals**
*Scan for:* direct manipulation of CSS classes owned by an external theme (e.g., Freya's `layout-static`); magic timeouts mirroring theme transition timing; MutationObservers on theme-managed classes.
*Why:* Theme upgrades silently break coupled code. Extract timing constants and document the dependency.

```javascript
// Bad
setTimeout(function() { Portal.updateBreadcrumb(); }, 250);

// Good
var FREYA_TRANSITION_MS = 250; // Freya menu animation duration
setTimeout(function() { Portal.updateBreadcrumb(); }, FREYA_TRANSITION_MS);
```
