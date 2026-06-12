# Product Requirements

## Event Background Selection

### Goal
Banner generation should automatically use the background configured for the selected event.

### Requirements
- Each event in `events.json` may define a `background` path.
- Generator scripts must resolve the configured background relative to the project root.
- Existing generation behavior must continue when a configured background is unavailable by falling back to `bg.png`.
- Event-specific backgrounds are stored in `bg/` using event-code filenames where available.

### Acceptance Criteria
- Selecting an event with `background: "bg/MOMD.png"` generates with `bg/MOMD.png`.
- Events without a dedicated background can still generate with `bg.png`.
- Invalid event codes still raise the existing validation error.
