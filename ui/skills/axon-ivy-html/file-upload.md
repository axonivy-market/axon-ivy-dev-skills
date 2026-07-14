# File Upload

Rules and best practices for `p:fileUpload` in Axon Ivy HTML Dialogs.

## Preferred Pattern: Advanced Mode with Drag & Drop

Always use **advanced mode** (default) with drag-and-drop support instead of `mode="simple"`.

### Key Rules

- Set `style="display: none;"` on `p:fileUpload` — use a custom drop zone for the visual area.
- Always define a `widgetVar` for programmatic control.
- Use `dropZone` attribute pointing to the ID of a `p:outputPanel` that serves as the visual drop area.
- Set `auto="true"` to upload immediately after file selection.
- Use `dragDropSupport="true"` to enable drag-and-drop.
- Use `listener` attribute pointing to `#{logic.upload}` — handled by a `HtmlDialogMethodStart` in the process.
- Use `rendered` to hide the upload component once a file is uploaded; show a preview instead.
- Provide `invalidSizeMessage` and `invalidFileMessage` for user-friendly validation feedback.
- Always set `accept` attribute in addition to `allowTypes` for native file picker filtering.

### Drop Zone Layout

The drop zone panel should contain:

1. An upload icon (e.g., `si si-file-code-upload-1`)
2. A descriptive label ("Drag and drop file here")
3. A `p:link` that triggers `PF('widgetVar').show()` as a fallback for manual file selection
4. A file preview section (shown after upload) with file name and optional metadata
5. A delete/remove button to clear the uploaded file

### Template

```html
<h:panelGroup id="file-upload-panel" layout="block"
  styleClass="#{empty data.inputFile ? 'col-12' : 'col-12 p-fluid'}">

  <!-- Hidden fileUpload - shown only when no file is uploaded -->
  <p:fileUpload id="file-upload" style="display: none;"
    widgetVar="fileUpload"
    rendered="#{empty data.inputFile}"
    listener="#{logic.upload}"
    dragDropSupport="true" auto="true"
    update="@form"
    allowTypes="/(\.|\/)(pdf)$/i"
    accept=".pdf"
    sizeLimit="5242880"
    invalidSizeMessage="#{ivy.cms.co('/Path/To/InvalidSizeMessage')}"
    invalidFileMessage="#{ivy.cms.co('/Path/To/InvalidFileMessage')}"
    dropZone="file-upload-drop-zone" />

  <!-- Visual Drop Zone -->
  <p:outputPanel id="file-upload-drop-zone"
    styleClass="flex flex-column align-items-center justify-content-center border-1 border-dashed border-round p-5 cursor-pointer">

    <!-- Empty state: drag & drop prompt -->
    <h:panelGroup rendered="#{empty data.inputFile}"
      styleClass="flex flex-column align-items-center gap-2">
      <i class="si si-file-code-upload-1 text-4xl text-secondary" />
      <p:outputLabel value="#{ivy.cms.co('/Path/To/DragAndDropLabel')}" styleClass="text-secondary" />
      <p:link value="#{ivy.cms.co('/Path/To/BrowseLabel')}"
        onclick="PF('fileUpload').show();return false" />
    </h:panelGroup>

    <!-- Uploaded state: file preview -->
    <h:panelGroup rendered="#{not empty data.inputFile}"
      styleClass="flex align-items-center gap-2">
      <i class="si si-file-pdf text-2xl" />
      <h:outputText value="#{data.inputFile.name}" styleClass="font-semibold" />
    </h:panelGroup>
  </p:outputPanel>

  <!-- Remove button (shown after upload) -->
  <h:panelGroup styleClass="flex justify-content-end mt-2"
    rendered="#{not empty data.inputFile}">
    <p:commandButton id="remove-file-btn"
      icon="si si-bin-1" styleClass="ui-button-outlined ui-button-danger"
      ariaLabel="#{ivy.cms.co('/Labels/Remove')}"
      actionListener="#{logic.removeFile}"
      process="@this" update="file-upload-panel" />
  </h:panelGroup>
</h:panelGroup>
```

### Image Upload Variant

For image uploads, add a `p:graphicImage` preview instead of a text-based file name display:

```html
<!-- In the uploaded state section -->
<p:graphicImage id="preview-image"
  rendered="#{not empty data.imageLocation}"
  styleClass="preview-image" library="ivy-cms"
  name="#{data.imageLocation}"
  alt="#{data.altText}" />
```

### Common File Type Patterns

| File Type | `allowTypes` | `accept` |
|-----------|-------------|----------|
| PDF | `/(\.\|\/)(pdf)$/i` | `.pdf` |
| Images | `/(\.\|\/)(png\|jpg\|jpeg\|svg)$/i` | `.png,.jpg,.jpeg,.svg` |
| Documents | `/(\.\|\/)(pdf\|doc\|docx)$/i` | `.pdf,.doc,.docx` |

## Anti-Patterns

- **Do NOT** use `mode="simple"` — it lacks drag-and-drop, auto-upload, and drop zone support.
- **Do NOT** use a separate upload button with `mode="simple"` — use `auto="true"` instead.
- **Do NOT** bind `value` directly with `mode="simple"` — use `listener` for server-side handling.
- **Do NOT** forget `update` on the `p:fileUpload` to refresh the panel after upload.
- **Do NOT** use `java.nio.file.Files.write(Path, byte[])` in IvyScript — it resolves to the wrong overload (`Iterable<CharSequence>`). Use `java.io.FileOutputStream` instead.
- **Do NOT** create a managed bean for file upload — use `#{logic.*}` with `HtmlDialogMethodStart` in the dialog process instead.

## Process Logic Checklist

After creating or updating the XHTML file upload, **always verify the dialog data class and process** have the required fields and methods.

### Required Steps

1. **Verify the data class** — the dialog data class (`.d.json`) must have these fields:
   - A `java.io.File` field for the uploaded file (e.g., `inputFile`)
   - An `Object` field for temporary event storage (e.g., `uploadedFile`)

   If the fields are missing, add them:
   ```json
   {
     "fields": [
       {
         "name": "inputFile",
         "type": "java.io.File",
         "comment": "Uploaded file"
       },
       {
         "name": "uploadedFile",
         "type": "Object",
         "comment": "Temporary PrimeFaces uploaded file reference"
       }
     ]
   }
   ```

2. **Verify the upload method in the process** — the dialog process (`.p.json`) must have a `HtmlDialogMethodStart` for `upload` that accepts `FileUploadEvent`, maps it to the data field, and connects to a Script step that saves the file:

   **HtmlDialogMethodStart:**
   ```json
   {
     "id": "f_upload",
     "type": "HtmlDialogMethodStart",
     "name": "upload(FileUploadEvent)",
     "config": {
       "signature": "upload",
       "input": {
         "params": [
           { "name": "event", "type": "org.primefaces.event.FileUploadEvent", "desc": "" }
         ],
         "map": {
           "out.uploadedFile": "param.event"
         }
       },
       "guid": "UNIQUE_GUID"
     }
   }
   ```

   **Script (Save uploaded file):**
   ```json
   {
     "type": "Script",
     "name": "Save uploaded file",
     "config": {
       "output": {
         "code": [
           "import org.primefaces.event.FileUploadEvent;",
           "",
           "FileUploadEvent event = in.uploadedFile as FileUploadEvent;",
           "if (event != null && event.getFile() != null) {",
           "  java.io.File tempFile = java.io.File.createTempFile(\"upload_\", \".pdf\");",
           "  java.io.FileOutputStream fos = new java.io.FileOutputStream(tempFile);",
           "  fos.write(event.getFile().getContent());",
           "  fos.close();",
           "  in.inputFile = tempFile;",
           "}",
           "in.uploadedFile = null;"
         ]
       }
     }
   }
   ```

   **CRITICAL — Writing bytes in IvyScript**: Do NOT use `java.nio.file.Files.write(tempFile.toPath(), bytes)` — IvyScript resolves it to the `Iterable<CharSequence>` overload, causing `ClassCastException: Byte cannot be cast to CharSequence`. Always use `java.io.FileOutputStream` instead.

   - The `listener` attribute in XHTML must be `#{logic.upload}` — no parentheses, no arguments.
   - The `HtmlDialogMethodStart` receives the `FileUploadEvent` automatically from PrimeFaces.
   - The `input.map` maps `param.event` to `out.uploadedFile` so the Script step can access it via `in.uploadedFile`.

3. **Verify the removeFile method in the process** — if the XHTML has a remove/delete button, the process must have a `HtmlDialogMethodStart` for `removeFile` connected to a Script step:

   **HtmlDialogMethodStart:**
   ```json
   {
     "type": "HtmlDialogMethodStart",
     "name": "removeFile()",
     "config": {
       "signature": "removeFile",
       "guid": "UNIQUE_GUID"
     }
   }
   ```

   **Script (Clear uploaded file):**
   ```json
   {
     "type": "Script",
     "name": "Clear uploaded file",
     "config": {
       "output": {
         "code": [
           "if (in.inputFile != null && in.inputFile.exists()) {",
           "  in.inputFile.delete();",
           "}",
           "in.inputFile = null;"
         ]
       }
     }
   }
   ```

   - The remove button in XHTML must use `actionListener="#{logic.removeFile}"`.

4. **Verify rendered-state bindings** — the XHTML must use `#{data.inputFile}` (not a bean reference) for all rendering conditions:
   - `rendered="#{empty data.inputFile}"` — show upload zone
   - `rendered="#{not empty data.inputFile}"` — show file preview and remove button
   - `disabled="#{empty data.inputFile}"` — disable submit when no file uploaded

5. **Verify process flow connections** — each method flow must end with `HtmlDialogEnd` (NOT `HtmlDialogExit`):
   - `HtmlDialogMethodStart (upload)` → `Script (save)` → `HtmlDialogEnd`
   - `HtmlDialogMethodStart (removeFile)` → `Script (clear)` → `HtmlDialogEnd`

   **CRITICAL**: `HtmlDialogExit` exits the dialog and returns to the calling process. Only use it for navigation events like submit. For methods that should keep the dialog open (upload, removeFile, validate), always use `HtmlDialogEnd`.
