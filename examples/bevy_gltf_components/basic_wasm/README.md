
# Basic bevy_gltf_components wasm demo

## Setup

as per the bevy documentation:

```shell
rustup target add wasm32-unknown-unknown
cargo install wasm-bindgen-cli
```


## Building this example

navigate to the current folder , and then


```shell
cargo build --release --target wasm32-unknown-unknown --target-dir ./target
wasm-bindgen --out-name wasm_example \
  --out-dir ./target/wasm \
  --target web target/wasm32-unknown-unknown/release/bevy_gltf_components_basic_wasm_example.wasm

```

## Running this example

run a web server in the current folder, and navigate to the page, you should see the example in your browser

### Additional notes


## Information
- the Bevy/ Rust code is [here](./src/main.rs)
- the Blender file is [here](./assets/basic.blend)
- I added [bevy_editor_pls](https://github.com/jakobhellermann/bevy_editor_pls) as a dependency for convenience so you can inspect your level/components
