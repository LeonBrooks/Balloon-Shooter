from tkinter import *
from tkinter import ttk
from dataclasses import dataclass
from random import randint
from typing import ClassVar


class BalloonShooter:
    isRunning = True  # False when paused/game over
    gameOver = False  # used to trigger game over
    upKeyActive = False
    downKeyActive = False
    speed = 1
    tickDelay = 3
    balloonSwitchCountdown = 0
    balloonDirection = True  # True=up, False=down

    # init window
    window = Tk()
    window.title("Leon Brooks Balloon Game")
    window["bg"] = "black"

    balls = list()  # projectile tracking list
    shootCooldown = 0
    missedShots = 0

    # projectile being shot
    @dataclass
    class CannonBall:
        cannonBallFile: ClassVar[PhotoImage] = PhotoImage(file="Assets/CannonBall.png")
        canvas: ClassVar[Canvas]
        cannon: ClassVar[int]
        balloon: ClassVar[int]
        id: int

        def __init__(self):
            cannonX, cannonY = self.canvas.coords(self.cannon)
            self.id = self.canvas.create_image(cannonX + 15, cannonY + 9, image=self.cannonBallFile, anchor="e")

        def move(self):
            self.canvas.move(self.id, BalloonShooter.speed * 10, 0)

            coords = self.canvas.coords(self.id)
            balloonCords = self.canvas.coords(self.balloon)

            # hit detection: canvas origin is top left, cannon ball y-size = 14p, balloon head y-size = 68p
            if coords[0] > balloonCords[0] and balloonCords[1] + 68 + 7 >= coords[1] >= balloonCords[1] - 7:
                BalloonShooter.gameOver = True

            # delete projectile when outside of canvas
            if coords[0] > 1200:
                self.canvas.delete(self.id)
                BalloonShooter.balls.remove(self)
                BalloonShooter.missedShots += 1

    @classmethod
    def upKeyPressed(cls, event):
        cls.upKeyActive = True

    @classmethod
    def downKeyPressed(cls, event):
        cls.downKeyActive = True

    @classmethod
    def upKeyReleased(cls, event):
        cls.upKeyActive = False

    @classmethod
    def downKeyReleased(cls, event):
        cls.downKeyActive = False

    @classmethod
    def shoot(cls, canvas, cannon):
        if cls.shootCooldown <= 0:
            cls.balls.append(cls.CannonBall())
            cls.shootCooldown = int(250 / cls.tickDelay)

    @classmethod
    def pause(cls, event):
        cls.isRunning = not cls.isRunning

    # reinit variables/sprite positions and remove game over text/retry button
    @classmethod
    def restart(cls, canvas, cannon, balloon, text, bWindow, button):
        cls.missedShots = 0
        cls.balloonSwitchCountdown = 0
        cls.shootCooldown = 0

        canvas.coords(cannon, 140, 375)
        canvas.coords(balloon, 1140, 375)
        canvas.delete(text)
        canvas.delete(bWindow)
        button.destroy()

        cls.gameOver = False
        cls.isRunning = True

    @classmethod
    def run(cls):
        # init canvas
        canvas = Canvas(cls.window, width=1200, height=700, background="white")
        canvas.pack(expand=True)
        cls.CannonBall.canvas = canvas

        # init cannon/balloon
        cannonFile = PhotoImage(file="Assets/Cannon.png")
        cannon = canvas.create_image(140, 357, image=cannonFile, anchor="ne")
        cls.CannonBall.cannon = cannon
        balloonFile = PhotoImage(file="Assets/Balloon.png")
        balloon = canvas.create_image(1140, 375, image=balloonFile, anchor="nw")
        cls.CannonBall.balloon = balloon

        # bind keys
        cls.window.bind("<KeyPress-Up>", cls.upKeyPressed)
        cls.window.bind("<KeyPress-Down>", cls.downKeyPressed)
        cls.window.bind("<KeyRelease-Up>", cls.upKeyReleased)
        cls.window.bind("<KeyRelease-Down>", cls.downKeyReleased)
        cls.window.bind("<space>", lambda e: cls.shoot(canvas, cannon))
        cls.window.bind("<p>", cls.pause)

        def gameLoop():
            if not cls.isRunning:
                cls.window.after(cls.tickDelay, gameLoop)  # continue game loop but pause game logic
                return

            # random balloon direction switching
            if cls.balloonSwitchCountdown <= 0:
                cls.balloonDirection = not cls.balloonDirection
                cls.balloonSwitchCountdown = randint(40, 150)
            cls.balloonSwitchCountdown -= 1

            # move balloon, if the balloon hits an edge -> switch direction
            if cls.balloonDirection:
                if canvas.coords(balloon)[1] > 0:
                    canvas.move(balloon, 0, -cls.speed)
                else:
                    cls.balloonSwitchCountdown = 0
            else:
                if canvas.coords(balloon)[1] < 700 - 100:
                    canvas.move(balloon, 0, cls.speed)
                else:
                    cls.balloonSwitchCountdown = 0

            # move cannon
            if cls.upKeyActive and not cls.downKeyActive and canvas.coords(cannon)[1] > 0:
                canvas.move(cannon, 0, -cls.speed * 2)
            if not cls.upKeyActive and cls.downKeyActive and canvas.coords(cannon)[1] < 700 - 66:
                canvas.move(cannon, 0, cls.speed * 2)

            # move projectiles
            for ball in cls.balls:
                ball.move()

            if cls.gameOver:                # if a projectile hit the balloon
                cls.isRunning = False

                # delete other projectiles still on canvas
                for ball in cls.balls:
                    canvas.delete(ball.id)
                cls.balls.clear()

                # display game over text/retry button
                text = canvas.create_text(625, 250, font=("Comic Sans MS", 30), justify=CENTER)
                button = ttk.Button(canvas, text="Retry", width=50)
                if cls.missedShots == 0:
                    message = "Nice, you hit on the first try!"
                    bWindow = canvas.create_window(625, 375, window=button)
                elif cls.missedShots == 1:
                    message = f"Nice you hit!\nBut you missed\n{cls.missedShots}\nshot"
                    bWindow = canvas.create_window(625, 425, window=button)
                else:
                    message = f"Good, you hit!\nBut you missed\n{cls.missedShots}\nshots"
                    bWindow = canvas.create_window(625, 425, window=button)

                canvas.itemconfigure(text, text=message)
                button.configure(command=lambda: cls.restart(canvas, cannon, balloon, text, bWindow, button))

            if cls.shootCooldown > 0:
                cls.shootCooldown -= 1
            cls.window.after(cls.tickDelay, gameLoop)   # call next game loop iteration

        cls.window.after(cls.tickDelay, gameLoop)  # start game loop
        cls.window.mainloop()


if __name__ == "__main__":
    BalloonShooter.run()
