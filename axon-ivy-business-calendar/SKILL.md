---
name: axon-ivy-business-calendar
description: Read holidays, free days, and working-day information from the Axon Ivy Business Calendar. Use whenever Java code needs to determine working days, public holidays, vacation calendars, or capacity planning based on a configured business calendar.
---

# Axon Ivy Business Calendar

Use this skill when Java code in `src/` needs to consume the **Business Calendar** configured in the Axon Ivy engine (Designer → Business Calendar settings). Typical use cases: capacity / resource planning, holiday-aware date arithmetic, working-day counts, "next working day" lookups.

## When to use

- Counting working days for a given week / month / period
- Displaying configured holidays in a UI
- Computing deadlines that must skip non-working days
- Reading the calendar associated with a team / org-unit / user

## When NOT to use

- For plain ISO calendar week / weekday math (Mon–Fri without holidays) — use `java.time` directly.
- For per-user vacation tracking — that's application data, not the engine's business calendar.

---

## 1. Accessing the calendar configuration

Always go through `IApplication.current()`. The older `Ivy.wf().getApplication()` is **deprecated** since 9.4 and will be removed.

```java
import ch.ivyteam.ivy.application.IApplication;
import ch.ivyteam.ivy.calendar.IBusinessCalendarConfiguration;

IApplication app = IApplication.current();

// Find a specific calendar by name
IBusinessCalendarConfiguration config =
    app.getBusinessCalendarSettings().findBusinessCalendarConfiguration("MyCalendar");

// Or list all configured calendars (e.g. to populate a dropdown)
List<IBusinessCalendarConfiguration> all =
    app.getBusinessCalendarSettings().getAllBusinessCalendarConfigurationsAsList();
```

If `findBusinessCalendarConfiguration(name)` returns `null`, the calendar does not exist in the application — handle this gracefully (fall back to a default like 5 working days).

---

## 2. Free-day model classes

The free-day model uses **concrete classes without an `I-` prefix**. Don't search for `IFreeDate` — it doesn't exist.

| Class | Type of free day | Key methods |
|---|---|---|
| `FreeDate` | One-off date (specific year, e.g. company event) | `getDate()`, `getName()` |
| `FreeDayOfYear` | Annual recurring holiday (e.g. New Year, Christmas) | `getDay()`, `getMonth()`, `getName()` |
| `FreeEasterRelativeDay` | Easter-relative holiday (e.g. Good Friday = −2, Easter Monday = +1) | `getDaysSinceEaster()`, `getName()` |

> ⚠️ The Easter-relative offset method is `getDaysSinceEaster()` — **not** `getOffset()`. The latter does not exist and will fail to compile.

---

## 3. `FreeDate.getDate()` returns Ivy's Date — not `java.util.Date`

`FreeDate.getDate()` returns `ch.ivyteam.ivy.scripting.objects.Date`, **not** `java.util.Date`. This Ivy type has no `getTime()` method. Convert to `LocalDate` via field accessors:

```java
import ch.ivyteam.ivy.scripting.objects.Date;
import java.time.LocalDate;

private static LocalDate toLocalDate(Date date) {
    if (date == null) return null;
    return LocalDate.of(date.getYear(), date.getMonth(), date.getDay());
}
```

Calling `.getTime()` on this type is a common mistake — the IDE may not flag it because the Ivy class shadows the `java.util.Date` import.

---

## 4. Calendar inheritance — traverse the parent chain

Calendars can inherit from a parent calendar (e.g. `Bavaria` extends `Germany`). Free days defined on the parent must also be considered. Always walk the parent chain via `getParentCalendar()`:

```java
private static String findHolidayName(IBusinessCalendarConfiguration config, LocalDate date) {
    IBusinessCalendarConfiguration current = config;
    while (current != null) {
        // One-off dates (year-specific)
        for (FreeDate fd : current.getFreeDates()) {
            LocalDate d = toLocalDate(fd.getDate());
            if (d != null && d.equals(date)) {
                return fd.getName();
            }
        }
        // Annual recurring holidays
        for (FreeDayOfYear fd : current.getFreeDaysOfYear()) {
            if (fd.getDay() == date.getDayOfMonth() && fd.getMonth() == date.getMonthValue()) {
                return fd.getName();
            }
        }
        current = current.getParentCalendar();
    }
    return null;
}
```

`getParentCalendar()` returns `null` once the root is reached — that's the loop's exit condition.

---

## 5. Easter-relative holidays — compute Easter locally

The API exposes `getDaysSinceEaster()` per holiday but does **not** provide a method to compute Easter for a given year. Implement Gauss's algorithm locally:

```java
private static LocalDate calculateEaster(int year) {
    int a = year % 19, b = year / 100, c = year % 100;
    int d = b / 4, e = b % 4, f = (b + 8) / 25;
    int g = (b - f + 1) / 3, h = (19 * a + b - d - g + 15) % 30;
    int i = c / 4, k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7;
    int m = (a + 11 * h + 22 * l) / 451;
    int month = (h + l - 7 * m + 114) / 31;
    int day = ((h + l - 7 * m + 114) % 31) + 1;
    return LocalDate.of(year, month, day);
}

private static String findEasterRelativeHolidayName(
        IBusinessCalendarConfiguration config, LocalDate date, int year) {
    LocalDate easter = calculateEaster(year);
    IBusinessCalendarConfiguration current = config;
    while (current != null) {
        for (FreeEasterRelativeDay fd : current.getFreeEasterRelativeDays()) {
            if (easter.plusDays(fd.getDaysSinceEaster()).equals(date)) {
                return fd.getName();
            }
        }
        current = current.getParentCalendar();
    }
    return null;
}
```

---

## 6. Recommended pattern — count working days for an ISO week

Load the calendar configuration once, iterate Mon–Fri, and check each day against all three free-day kinds (one-off, annual, easter-relative). Return both the count and the names of the holidays found, so the UI can show a tooltip.

```java
public class WorkingDayResult {
    private final int workingDays;
    private final List<String> holidays;

    public WorkingDayResult(int workingDays, List<String> holidays) {
        this.workingDays = workingDays;
        this.holidays = holidays;
    }
    public int getWorkingDays() { return workingDays; }
    public List<String> getHolidays() { return holidays; }
}

public static WorkingDayResult countWorkingDays(String calendarName, int year, int isoWeek) {
    IBusinessCalendarConfiguration config = IApplication.current()
        .getBusinessCalendarSettings()
        .findBusinessCalendarConfiguration(calendarName);

    if (config == null) {
        return new WorkingDayResult(5, List.of()); // sensible default
    }

    LocalDate monday = LocalDate.now()
        .with(WeekFields.ISO.weekBasedYear(), year)
        .with(WeekFields.ISO.weekOfWeekBasedYear(), isoWeek)
        .with(DayOfWeek.MONDAY);

    List<String> holidays = new ArrayList<>();
    for (int i = 0; i < 5; i++) {
        LocalDate day = monday.plusDays(i);
        String name = findHolidayName(config, day);
        if (name == null) {
            name = findEasterRelativeHolidayName(config, day, year);
        }
        if (name != null) {
            holidays.add(name);
        }
    }
    return new WorkingDayResult(5 - holidays.size(), holidays);
}
```

---

## 7. Combining calendar holidays with explicit overrides

In capacity / resource-planning apps you often have both:
- **Calendar holidays** (deterministic, from the engine config)
- **Per-week overrides** (e.g. `WeekConfig.workingDays`, set manually for half-day Fridays or vacation weeks)

Recommended priority order:

```
WeekConfig.workingDays != null   → use it as explicit override (ignores calendar)
WeekConfig.workingDays == null   → fall through to calendar count
No WeekConfig at all             → fall through to calendar / default 5
```

Make `WeekConfig.workingDays` **nullable** (`Integer`, not `int`) so a vacation-only override does not accidentally clobber the calendar's holiday count.

---

## Common Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| `getApplication()` flagged as deprecated | `Ivy.wf().getApplication()` | Use `IApplication.current()` |
| `getOffset()` not found on `FreeEasterRelativeDay` | Method doesn't exist | Use `getDaysSinceEaster()` |
| `getTime()` not found on `FreeDate.getDate()` result | Returned type is `ch.ivyteam.ivy.scripting.objects.Date`, not `java.util.Date` | Convert via `getYear()/getMonth()/getDay()` to `LocalDate` |
| Bavarian holidays missing although parent calendar has them | Did not traverse parent chain | Loop `current = current.getParentCalendar()` |
| Easter-relative holidays never matched | Tried to read Easter from the API | Compute Easter locally (Gauss algorithm) |
| `findBusinessCalendarConfiguration(name)` returns `null` in tests | Calendar name typo or not configured in the app | Provide a default fallback (e.g. 5 working days) |
