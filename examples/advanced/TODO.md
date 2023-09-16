- [ ] seperate "spawn velocity" into a seperate (optional) component
- [x] try dynamically spawned entities with save & load
- [ ] fix issues with multiple entites having the same name ??
- [ ] fix issues with system ordering
    - [x] add sets for proxy-replacements
- [x] annoying camera movement : camera should be saveable as well
        => we need to be able to only save the camera position (and name)
- [ ] only spawn "new level" stuff when transitioning from menu to game ?
        - [ ] put more thoughts into this 

- [ ] rework how save-loading is triggered
        - [ ] no hardcoded keypresses
        - [ ] ability to choose what save to load ?
        - [ ] take a look at bevy_moonshine_save
        - [ ] move to system pipelines

- [ ] split Blueprints into a seperate crate: perhaps bevy_gltf_blueprints
        - [ ] how to deal with states that are not defined as part of the plugin/crate ?
        - [ ] same issue for the assets

- [ ] support multiple main scenes in the blender plugin ?
- [ ] study possibilities of expanding the bevy & blender tooling side to define UIS
        - likely using the blender data only as a placeholder/ directly replace in Python

- system ordering ? 
        load level => inject components => spawn blueprint entities/rehydrate => (loading) => replace proxies 
        OR 
        load level => inject components => (loading)  => spawn blueprint entities/rehydrate => replace proxies 

- perhaps it does make more sense to save ALL entities and not just the dynamic ones? mostly as we have the blueprints anyway, which should cut down on needed data ?


- different approaches for dealing with saving/loading
    in particular the problem of entites that are defined as part of the level but can be despawned (items that get picked up etc)

    Bevy side
    * var 1 : spawn all entities completely, despawn those saveables that are not actually present in the save data but that have been spawned
            * problems: needs correct ordering of systems otherwise the diffing above will not work
            * pros: minimal save files, only bevy boilerplate
            * cons: requires spawning potentially huge gltf files just to "peek" inside of them to know if they are saveable


    * var 2 : save both saveables & unsaveables but only save the absolute minimal data for unsaveables
            * problems: how to combine different filters into a single save file ?
            * pros: easier diffing, more homogeneous handling
            * cons: a lot bigger save file with mostly useless data

    Blender side

    * var 3 => CHOSEN OPTION : mark INSTANCES in advance as static/dynamic (ie saveable or not), thus this data would be present in the world/level and not inside the gltf data
            * problems: would require adding custom properties to each instance in Blender (COULD be automated by 'peeking' inside the collection)
            * pros: simpler, and this might be more "editor-like" where you would mark each item as static or not
            * cons: potentially a lot of manual work / error prone