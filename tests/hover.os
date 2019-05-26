#Workshop Script that makes players hover as soon as they press the F key.

def on_player_hover():
	if isButtonHeld(player, "Interact") == True:
		while True == True:
			applyImpulse(player, Vector(0, 1, 0), 1, "To World", "Cancel Contrary Motion")