import arcade

class BarbershopGame(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "Arcade Barbershop Game")
        arcade.set_background_color(arcade.color.BLACK)
        
    def setup(self):
        self.time_limit = 30  # Seconds
        self.precision_meter = 50  # Initial precision state

    def on_draw(self):
        arcade.start_render()
        self.draw_background()
        self.draw_ui()
        self.draw_gameplay_scenario()

    def draw_background(self):
        arcade.draw_lrwh_rectangle_textured(0, 0, 800, 600, arcade.load_texture("barbershop_blur.png"))

    def draw_ui(self):
        # Time limit
        arcade.draw_text(f"Time Limit: {self.time_limit}s", 20, 560, arcade.color.RED_DEVIL, 20)

        # Precision Meter
        arcade.draw_text(f"Precision: {self.precision_meter}/100", 720, 20, arcade.color.WHITE, 14, align="right", anchor_x="right")

        # Central Text
        arcade.draw_text("PERFECT FADE!", 400, 300, arcade.color.ELECTRIC_BLUE, 40, align="center", anchor_x="center", anchor_y="center")

    def draw_gameplay_scenario(self):
        # Player's hand with a gold clipper
        arcade.draw_texture_rectangle(400, 300, 50, 100, arcade.load_texture("hand_with_clipper.png"))

        # Sparks and combo-hit effects
        arcade.draw_text("Combo!