import sys
import random
from client import EvasionClient, GameState, Wall, Velocity, MAX_WIDTH, MAX_HEIGHT, Point

# -------------------------------------------------------------------------------
# INSTRUCTIONS 
# -------------------------------------------------------------------------------

"""
TODO list for your team if you wish to use this client:
1. Change self.team_name in the Client class to your team name
2. Implement the calculate_hunter_move function in your client 
3. Implement the calculate_prey_move function in your client
"""

# -------------------------------------------------------------------------------
# YOUR CLIENT
# -------------------------------------------------------------------------------

class MyClient(EvasionClient):
    def __init__(self, port=4000):
        self.team_name = "VGA2"
        super().__init__(self.team_name, port)
        self.built_walls = []

    def calculate_hunter_move(self, game: GameState) -> str:
        # Check if we can build a wall
        if (
            game.hunter_last_wall_time is None
            or game.ticker - game.hunter_last_wall_time >= self.config.next_wall_time
        ):
            #remove all walls that are not the closest to the prey from top and bottom
            walls_to_keep_top = []
            #find the closest wall to the prey from top
            current_least_pos_top = MAX_HEIGHT
            for wall in self.built_walls:
                if wall.y1 < game.prey_position.y and game.prey_position.y - wall.y1 < current_least_pos_top:
                    current_least_pos_top = game.prey_position.y - wall.y1
                    walls_to_keep_top = [wall]
            #find the closest wall to the prey from bottom
            walls_to_keep_bottom = []
            current_least_pos_bottom = MAX_HEIGHT
            for wall in self.built_walls:
                if wall.y1 > game.prey_position.y and wall.y1 - game.prey_position.y < current_least_pos_bottom:
                    current_least_pos_bottom = wall.y1 - game.prey_position.y
                    walls_to_keep_bottom = [wall]
            walls_to_keep = walls_to_keep_top + walls_to_keep_bottom
            walls_to_remove = [wall for wall in self.built_walls if wall not in walls_to_keep]

            # Get hunter's previous position (before moving)
            hunter_prev_pos = game.hunter_position

            # The wall must touch the hunter's previous position
            wall_y = hunter_prev_pos.y

            # Define the wall from x1 to x2, ensuring x1 < x2
            x1 = 0
            x2 = MAX_WIDTH - 1

            # Ensure x1 < x2
            if x1 > x2:
                x1, x2 = x2, x1

            wall = Wall(x1=x1, y1=wall_y, x2=x2, y2=wall_y)

            # Calculate hunter's new position after moving
            new_hunter_x = game.hunter_position.x + game.hunter_velocity.x
            new_hunter_y = game.hunter_position.y + game.hunter_velocity.y

            #prey is up and hunter is going down dont do anything
            if game.prey_position.y < new_hunter_y and new_hunter_y > hunter_prev_pos.y:
                if len(game.walls) > 2:
                    self.built_walls = walls_to_keep
                    return self.move_only_remove_walls(walls_to_remove)
                else:
                    return self.move_no_op()
            
            #is prey is below but hunter is going up dont do anything
            if game.prey_position.y > new_hunter_y and new_hunter_y < hunter_prev_pos.y:
                if len(game.walls) > 2:
                    self.built_walls = walls_to_keep
                    return self.move_only_remove_walls(walls_to_remove)
                else:
                    return self.move_no_op()

            # Check if the wall would touch the hunter's new position
            if new_hunter_y == wall_y:
                # Wall would touch hunter's new position
                if len(game.walls) > 2:
                    self.built_walls = walls_to_keep
                    return self.move_only_remove_walls(walls_to_remove)
                else:
                    return self.move_no_op()

            # Check if the wall would touch the prey's position
            if game.prey_position.y == wall_y:
                # Wall would touch prey's position
                if len(game.walls) > 2:
                    self.built_walls = walls_to_keep
                    return self.move_only_remove_walls(walls_to_remove)
                else:
                    return self.move_no_op()

            # Build the wall
            
            if len(game.walls) < self.config.max_walls:
                self.built_walls.append(wall)
                return self.move_create_wall(wall)
            else:
                #remove walls from built walls that are not the closest to the prey
                self.built_walls = walls_to_keep
                self.built_walls.append(wall)
                return self.move_remove_walls_and_create(walls_to_remove, wall)              
        else:
            # Cannot build wall yet
            walls_to_keep_top = []
            #find the closest wall to the prey from top
            current_least_pos_top = MAX_HEIGHT
            for wall in self.built_walls:
                if wall.y1 < game.prey_position.y and game.prey_position.y - wall.y1 < current_least_pos_top:
                    current_least_pos_top = game.prey_position.y - wall.y1
                    walls_to_keep_top = [wall]
            #find the closest wall to the prey from bottom
            walls_to_keep_bottom = []
            current_least_pos_bottom = MAX_HEIGHT
            for wall in self.built_walls:
                if wall.y1 > game.prey_position.y and wall.y1 - game.prey_position.y < current_least_pos_bottom:
                    current_least_pos_bottom = wall.y1 - game.prey_position.y
                    walls_to_keep_bottom = [wall]
            walls_to_keep = walls_to_keep_top + walls_to_keep_bottom
            walls_to_remove = [wall for wall in self.built_walls if wall not in walls_to_keep]
            
            if len(game.walls) > 2:
                self.built_walls = walls_to_keep
                return self.move_only_remove_walls(walls_to_remove)
            else:
                return self.move_no_op()

    def calculate_prey_move(self, game: GameState) -> str:
        dx = game.hunter_position.x - game.prey_position.x
        dy = game.hunter_position.y - game.prey_position.y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # If hunter is close, move away
        if distance < 20:
            # Determine direction away from hunter
            vx = -1 if dx > 0 else (1 if dx < 0 else random.choice([-1, 1]))
            vy = -1 if dy > 0 else (1 if dy < 0 else random.choice([-1, 1]))

            # Check for walls in the new direction
            new_x = game.prey_position.x + vx
            new_y = game.prey_position.y + vy
            collision = False
            for wall in game.walls:
                if wall.x1 <= new_x <= wall.x2 and wall.y1 <= new_y <= wall.y2:
                    collision = True
                    break
            if collision:
                # Choose an alternative direction
                vx = random.choice([-1, 0, 1])
                vy = random.choice([-1, 0, 1])

            # Create new velocity
            velocity = Velocity(vx, vy)
            return self.move_change_velocity(velocity)
        else:
            # Occasionally change direction randomly
            if random.random() < 0.1:
                vx = random.randint(-1, 1)
                vy = random.randint(-1, 1)
                velocity = Velocity(vx, vy)
                return self.move_change_velocity(velocity)
            else:
                return self.move_no_op()

# -------------------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) == 1: port = 4000
    else: port = int(sys.argv[1])
    client = MyClient(port)
    client.run()