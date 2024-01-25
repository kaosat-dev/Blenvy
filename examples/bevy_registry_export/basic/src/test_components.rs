use bevy::prelude::*;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct UnitTest;

#[derive(Component, Reflect, Default, Debug, Deref, DerefMut)]
#[reflect(Component)]
struct TuppleTestF32(f32);

#[derive(Component, Reflect, Default, Debug, Deref, DerefMut)]
#[reflect(Component)]
struct TuppleTestU64(u64);

#[derive(Component, Reflect, Default, Debug, Deref, DerefMut)]
#[reflect(Component)]
pub struct TuppleTestStr(String);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TuppleTest2(f32, u64, String);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TuppleTestBool(bool);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TuppleVec2(Vec2);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TuppleVec3(Vec3);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TuppleVec(Vec<String>);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TuppleVecF32F32(Vec<(f32, f32)>);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
struct TuppleTestColor(Color);

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
   enum_inner: EnumTest,
   color: TuppleTestColor,
   basic: BasicTest,
   pub nested: NestingTestLevel3
}



#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct NestingTestLevel3 {
    vec: TuppleVec3,
}


#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct NestedTuppleStuff(f32, u64, NestingTestLevel2);


#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub enum EnumComplex {
    Float(f32),
    Wood(String),
    Vec(BasicTest),
    #[default]
    None,
}

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct VecOfVec3s(Vec<TuppleVec3>);

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
pub struct VecOfColors(Vec<Color>);

pub struct ComponentsTestPlugin;
impl Plugin for ComponentsTestPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<BasicTest>()
            .register_type::<UnitTest>()
            .register_type::<TuppleTestF32>()
            .register_type::<TuppleTestU64>()
            .register_type::<TuppleTestStr>()
            .register_type::<TuppleTestBool>()
            .register_type::<TuppleTest2>()
            .register_type::<TuppleVec2>()
            .register_type::<TuppleVec3>()
            .register_type::<EnumTest>()
            .register_type::<TuppleTestColor>()
            .register_type::<TuppleVec>()
            .register_type::<Vec<String>>()
            
            .register_type::<NestingTestLevel2>()
            .register_type::<NestingTestLevel3>()
            .register_type::<NestedTuppleStuff>()
            .register_type::<EnumComplex>()

            .register_type::<VecOfVec3s>()
            .register_type::<TuppleVecF32F32>()

            .register_type::<(f32, f32)>()
            .register_type::<Vec<(f32, f32)>>()
            .register_type::<Vec<TuppleVec3>>()

            .register_type::<Vec<Color>>()
            .register_type::<VecOfColors>()
            ;
    }
}
