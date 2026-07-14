# Client-Side Storage Rules — A1–A2

**Audit/compliance rules — non-negotiable.**

---

**A1. No Client-Side Cookie Writes**
*Scan for:* `$.cookie('name', 'value', ...)`, `$.removeCookie(...)`, `document.cookie = '...'`.
*Why:* Cookies must be set/removed server-side via `Set-Cookie` headers. Client-side writes bypass audit trails.

```javascript
// VIOLATION
$.cookie('freya_menu_static', 'freya_menu_static', { path: '/' });
$.removeCookie('freya_menu_static', { path: '/' });

// FIX: delegate to server via remoteCommand or AJAX
saveSidebarState([{ name: 'state', value: 'expanded' }]);
```

---

**A2. No Client-Side localStorage/sessionStorage Writes**
*Scan for:* `.setItem(...)`, `.removeItem(...)`, `.clear()`, or direct assignment. Reading (`.getItem()`) is acceptable.
*Why:* Persistent state must be server-managed for audit logging and retention policies.

```javascript
// VIOLATION
localStorage.setItem('sidebar_expanded', 'true');

// FIX: read from server-set data attribute
var state = $('.js-layout-wrapper').data('sidebarState');
```

---

## Exception Process

If unavoidable (e.g., third-party theme cookie):

1. Add `// AUDIT-EXCEPTION: <reason>` at the call site
2. Document key name, purpose, and lifetime
3. Get security/compliance reviewer approval

Without this, any client-side storage write is **Critical (Audit)**.
