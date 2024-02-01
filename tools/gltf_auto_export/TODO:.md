TODO:
- every time the MAIN scene(s) get saved, all the objects are marked as changed BECAUSE THEY HAVE BEEN CHANGED !!
    - this leads to a complete re-export whenever we save again after that
    - we need a "pseudo global" marker settable to ignore any changes to objects when we want 