use bevy::{
    pbr::{ExtendedMaterial, MaterialExtension},
    prelude::*,
    render::render_resource::*,
};
use std::ops::Range;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct UnitTest;

#[derive(Component, Reflect, Default, Debug, Deref, DerefMut)]
#[reflect(Component)]
pub struct TupleTestF32(pub f32);

#[derive(Component, Reflect, Default, Debug, Deref, DerefMut)]
#[reflect(Component)]
struct TupleTestU64(u64);

#[derive(Component, Reflect, Default, Debug, Deref, DerefMut)]
#[reflect(Component)]
pub struct TupleTestStr(String);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TupleTest2(f32, u64, String);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TupleTestBool(bool);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TupleVec2(Vec2);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TupleVec3(Vec3);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TupleVec(Vec<String>);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TupleVecF32F32(Vec<(f32, f32)>);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TupleTestColor(Color);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct BasicTest {
    a: f32,
    b: u64,
    c: String,
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub enum EnumTest {
    Metal,
    Wood,
    Rock,
    Cloth,
    Squishy,
    #[default]
    None,
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct NestingTestLevel2 {
    text: String,
    enable: bool,
    enum_inner: EnumTest,
    color: TupleTestColor,
    toggle: TupleTestBool,
    basic: BasicTest,
    pub nested: NestingTestLevel3,
    colors_list: VecOfColors,
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct NestingTestLevel3 {
    vec: TupleVec3,
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct NestedTupleStuff(f32, u64, NestingTestLevel2);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub enum EnumComplex {
    Float(f32),
    Wood(String),
    Vec(BasicTest),
    SomeThing,
    StructLike {
        a: f32,
        b: u32,
        c: String,
    },
    #[default]
    None,
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct VecOfVec3s2(Vec<TupleVec3>);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct VecOfColors(Vec<Color>);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct AAAAddedCOMPONENT;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct AComponentWithAnExtremlyExageratedOrMaybeNotButCouldBeNameOrWut;

/* fn toto(){
   let bla:core::ops::Range<f32> = Range { start: 0.1, end: 5.0};
} */

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct VecOfF32s(Vec<f32>);

// test for extended materials
#[derive(Asset, AsBindGroup, Reflect, Debug, Clone)]
struct MyExtension {
    // We need to ensure that the bindings of the base material and the extension do not conflict,
    // so we start from binding slot 100, leaving slots 0-99 for the base material.
    #[uniform(100)]
    quantize_steps: u32,
}

impl MaterialExtension for MyExtension {
    fn fragment_shader() -> ShaderRef {
        "shaders/extended_material.wgsl".into()
    }

    fn deferred_fragment_shader() -> ShaderRef {
        "shaders/extended_material.wgsl".into()
    }
}

pub struct ComponentsTestPlugin;
impl Plugin for ComponentsTestPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<BasicTest>()
            .register_type::<UnitTest>()
            .register_type::<TupleTestF32>()
            .register_type::<TupleTestU64>()
            .register_type::<TupleTestStr>()
            .register_type::<TupleTestBool>()
            .register_type::<TupleTest2>()
            .register_type::<TupleVec2>()
            .register_type::<TupleVec3>()
            .register_type::<EnumTest>()
            .register_type::<TupleTestColor>()
            .register_type::<TupleVec>()
            .register_type::<Vec<String>>()
            .register_type::<NestingTestLevel2>()
            .register_type::<NestingTestLevel3>()
            .register_type::<NestedTupleStuff>()
            .register_type::<EnumComplex>()
            .register_type::<VecOfVec3s2>()
            .register_type::<TupleVecF32F32>()
            .register_type::<(f32, f32)>()
            .register_type::<Vec<(f32, f32)>>()
            .register_type::<Vec<TupleVec3>>()
            .register_type::<Vec<Color>>()
            .register_type::<VecOfColors>()
            .register_type::<Range<f32>>()
            .register_type::<VecOfF32s>()
            .register_type::<Vec<f32>>()
            // .register_type::<AAAAddedCOMPONENT>()
            .register_type::<AComponentWithAnExtremlyExageratedOrMaybeNotButCouldBeNameOrWut>()
            .add_plugins(MaterialPlugin::<
                ExtendedMaterial<StandardMaterial, MyExtension>,
            >::default());
    }
}
