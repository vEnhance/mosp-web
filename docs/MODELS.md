# About models

This is a rough summary of what the models of the Django are.

- A _Hunt_ object is a top-level object for each year.
  In-universe, it is referred to instead as a _Volume_.
- A _Round_ object represents a round of each hunt.
  In-universe, it is referred to instead as a _Chapter_.
- A _Puzzle_ object represents a puzzle in a round.
- A _Unlockable_ object is the most complicated kind of object.
  Here are some details:
  - Every puzzle has exactly one unlockable attached to it.
  - Every round has exactly one unlockable attached to it.
  - An unlockable may also be _story-only_, meaning it is neither a puzzle nor round.
  - Each unlockable has a _name_ associated to it, often a place.
  - Each unlockable is associated with exactly one hunt.
  - Each unlockable can have a _parent_ unlockable.
    - For a puzzle, this is the round it belongs to.
    - For a round, this can _also_ be a round it belongs to. Meaning nested
      rounds are possible.
    - A top-level round has no parent for its corresponding unlockable.
  - Unlockables can be unlocked based on certain criteria:
    - Unlocked with courage
    - Unlocked if a certain other unlockable is solved or completed
    - Unlocked if a certain date/time has passed.
    - AND of any nonempty subset of the above.
  - Unlockables may also have different visibility based on `force_visibility`.
    - If True, then always visible.
    - If False, then never visible unless solver types URL manually.
    - If null, then becomes visible at the same time it can be unlocked.
- Other models should be self-explanatory.
