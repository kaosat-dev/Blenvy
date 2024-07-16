
# Basic xpbd physics example/demo

Same as the basic example but using [xpbd](https://github.com/Jondolf/bevy_xpbd) instead of Rapier [rapier](https://github.com/dimforge/bevy_rapier)

## Running this example

```
cargo run --features bevy/dynamic_linking
```

### Additional notes

* You usually define either the Components directly or use ```Proxy components``` that get replaced in Bevy systems with the actual Components that you want (usually when for some reason, ie external crates with unregistered components etc) you cannot use the components directly.
* this example contains code for future features, not finished yet ! please disregard anything related to saving & loading
