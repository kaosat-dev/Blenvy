use bevy::prelude::*;

use crate::GameState;

#[derive(Component, Reflect, Default, Debug)]
#[reflect(Component)]
/// Demo marker component
pub struct Player;

fn player_move_demo(
    keycode: Res<Input<KeyCode>>,
    mut players: Query<&mut Transform, With<Player>>,
) {
    let speed = 0.2;
    if let Ok(mut player) = players.get_single_mut() {
        if keycode.pressed(KeyCode::Left) {
            player.translation.x += speed;
        }
        if keycode.pressed(KeyCode::Right) {
            player.translation.x -= speed;
        }

        if keycode.pressed(KeyCode::Up) {
            player.translation.z += speed;
        }
        if keycode.pressed(KeyCode::Down) {
            player.translation.z -= speed;
        }
    }
}

pub struct PlayerPlugin;
impl Plugin for PlayerPlugin {
    fn build(&self, app: &mut App) {
        app.register_type::<Player>().add_systems(
            Update,
            (player_move_demo,).run_if(in_state(GameState::InGame)),
        );
    }
}
