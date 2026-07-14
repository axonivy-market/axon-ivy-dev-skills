# Ivy Component Syntax

Rules and best practices for using Axon Ivy-specific syntax in HTML Dialogs.

## HTML Component Usage

To use Axon Ivy HTML components, you must declare the Ivy component namespace in the `<html>` tag:

```xml
xmlns:ic="http://ivyteam.ch/jsf/component"
```

For example, if you have an HTML component named ProjectDetails located in `src_hd/hr/talent/acquisition/component`, you can use it in your HTML dialog as follows:

```xml
<ic:hr.talent.acquisition.component.ProjectDetails />
```
