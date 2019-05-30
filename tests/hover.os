#Workshop Script that makes players hover as soon as they press the F key.

@event("player", "all", "all")
@trigger(isButtonHeld(player, "Interact"))
def hover():
	while True == True:
		applyImpulse(player, vector(0, 1, 0), 5, "To World", "Cancel Contrary Motion")
		wait(0.015)