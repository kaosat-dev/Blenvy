Basics
- [ ] add panel
- [ ] add a "create blueprint" button
    - [ ] when clicked: 
        - create collection (popup for name input ?)
        - add an empty inside collection and name it <COLLECTION_NAME>_components
        - add a **AutoExport** Boolean property to collection 

- [ ] add an "edit blueprint" section
    - [ ] only filled when there is ONE selection, and that selection is a collection
    - [ ] add a dropdown of possible components 
        - for now this list will be HARDCODED until we find a good way to extract data from Bevy's typeregistry
        - [ ] prefill with
            - unit struct
            - vec3
            -  
    - [ ] add a checkbox for enabling disabling a component (enabled by default)
    - [ ] add a button for copying a component
    - [ ] add a button for pasting a component