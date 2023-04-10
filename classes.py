from PIL import Image, ImageTk
import tkinter as tk
import random
import time
import glob
import os

TRANSPARENT = 'blue'


class Goose(tk.Tk):
    # Goose constant, modify to your needs.
    UPDATE_FREQUENCY = 200
    EGG_SPAWNING_DELAY = 30

    def __init__(self, spawn_eggs: bool) -> None:
        """
        Constructor if the Goose class.
        :param spawn_eggs: set to True if you want the goose to lay eggs, False if not.
        """
        super().__init__()

        # Set window attributes.
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.wm_attributes("-transparentcolor", "blue")
        self.title('Josiane the goose')
        self.config(bg=TRANSPARENT)

        # Set every attribute needed.
        self.height = self.winfo_screenheight()
        self.width = self.winfo_screenwidth()
        self.x = self.width // 2 - 250 // 2
        self.y = self.height // 2 - 250 // 2
        self.action_end_time = time.time()
        self.spawn_egg_time = time.time()

        self.spawn_eggs = spawn_eggs

        self.geometry(f'250x250+{self.x}+{self.y}')

        # Initilisation of the first direction and animation.
        self.dir = 'west'
        self.speed = 10
        self.is_busy = False
        self.last_action = 'walk'

        self.sprite_label = tk.Label(self, image='', bg=TRANSPARENT)
        self.sprite_label.place(x=0, y=0)

        # Load all sprites in a dictionnary.
        self.sprite_img = {}
        for directory in glob.glob(os.path.join('sprite', '*')):
            # create keys according to all sprite group.
            self.sprite_img[directory] = []
            for img in sorted(glob.glob(os.path.join(directory, '*'))):
                # Append every image to the correct group.
                self.sprite_img[directory].append(img)

        # Set default sprite.
        self.current_sprite = ImageTk.PhotoImage(Image.open(self.sprite_img[os.path.join('sprite', 'idle-west')][0]))
        self.sprite_label.place(x=0, y=0)

        # List that will contain every Egg object that the Goose will lay.
        self.eggs = []

    def change_window_location(self, new_x: int, new_y: int) -> None:
        """
        Method that move the window according to the given coordinates.
        :param new_x: nex X position of the window.
        :param new_y: nex Y position of the window.
        :return: None
        """

        # Check if the new position is outside the screen if it is the case, change the location of the goose.
        if new_x < -250:
            self.x = self.width

        elif new_x > self.width:
            self.x = -250

        else:
            self.x = new_x

        if new_y < 0:
            self.y = 0

        elif new_y > self.height - 250:
            self.y = self.height - 250

        else:
            self.y = new_y

        # Move the window.
        self.geometry(f'+{self.x}+{self.y}')

    def walk(self, y_dir: int) -> None:
        """
        Method that change the animation of the Goose to walk and move it across the screen.
        :param y_dir: direction that the Goose is facing (1 or -1).
        :return: None
        """

        # Loop every sprite of the group 'walk' and move the Goose.
        for sprite in self.sprite_img[os.path.join('sprite', f'walk-{self.dir}')]:
            self.current_sprite = ImageTk.PhotoImage(Image.open(sprite))
            self.sprite_label.config(image=self.current_sprite)
            self.sprite_label.place_forget()
            self.sprite_label.place(x=0, y=0)
            self.change_window_location(self.x + ((- self.speed) if self.dir == 'west' else + self.speed),
                                        self.y + y_dir)

            # Update the sprite every 70ms.
            self.after(70, self.update())

    def idle(self) -> None:
        """
        Method that change the animation of the Goose to idle.
        :return: None
        """

        if self.spawn_eggs:
            # Check if the time to lay egg as been exceeded and lay an egg if it's the case.
            if time.time() > self.spawn_egg_time + Goose.EGG_SPAWNING_DELAY:
                # Reset the spawn time.
                self.spawn_egg_time = time.time()

                # Lay the agg accordingly to the direction the Goose is facing.
                self.eggs.append(Egg(self.x + 190 if self.dir == 'west' else self.x + 10, self.y))

        # Change facing direction randomly.
        if random.random() > 0.75:
            self.dir = 'west' if self.dir == 'east' else 'east'

            # Loop throught sprites from turning animation and update the window.
            for sprite in self.sprite_img[os.path.join('sprite', f'turn-{self.dir}')]:
                self.current_sprite = ImageTk.PhotoImage(Image.open(sprite))
                self.sprite_label.config(image=self.current_sprite)
                self.sprite_label.place_forget()
                self.sprite_label.place(x=0, y=0)
                self.after(Goose.UPDATE_FREQUENCY, self.update())

        # Loop throught 'idle' sprite and update the window.
        for sprite in self.sprite_img[os.path.join('sprite', f'idle-{self.dir}')]:
            self.current_sprite = ImageTk.PhotoImage(Image.open(sprite))
            self.sprite_label.config(image=self.current_sprite)
            self.sprite_label.place_forget()
            self.sprite_label.place(x=0, y=0)
            self.after(Goose.UPDATE_FREQUENCY, self.update())

    def loop(self) -> None:
        """
        Method that start the loop of the Goose.
        :return: None
        """
        self.wm_attributes("-topmost", True)
        self.sprite_label.config(image=self.current_sprite)

        if self.is_busy is False:
            if self.last_action == 'idle':
                self.action_end_time = int(time.time()) + random.randint(2, 4)
            else:
                self.action_end_time = int(time.time()) + random.randint(5, 10)
            self.is_busy = True

        else:
            # If the Goose is not busy and the timer of the action is not finished,
            # walk the Goose to a random location or idle.
            if not time.time() > self.action_end_time:
                if self.last_action == 'idle':
                    # Walk to a random position on the screen.
                    self.walk(random.choice((-10, 10)) if random.random() > 0.75 else 0)

                else:
                    self.idle()
                    for egg in self.eggs:
                        # Check if the egg need to be removed.
                        need_to_be_remove = egg.hatch()

                        if need_to_be_remove:
                            # Remove egg from the eggs list to save memory.
                            self.eggs.remove(egg)

            else:
                self.is_busy = False
                self.last_action = 'walk' if self.last_action == 'idle' else 'idle'

        # loop every 1ms.
        self.after(1, self.loop)


class Egg(tk.Toplevel):
    DESPAWNING_TIME = 600

    def __init__(self, x: int, y: int) -> None:
        """
        Constructor of the Egg class.
        :param x: x position on the screen.
        :param y: y position on the screen.
        """

        # Set all the TopLevel attributes.
        super().__init__()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.wm_attributes("-transparentcolor", "blue")
        self.title('Egg')
        self.config(bg=TRANSPARENT)

        # Set every attribute needed.
        self.spawn_time = time.time()
        self.x = x
        self.y = y + 200

        self.geometry(f'50x50+{self.x}+{self.y}')

        # Set the egg sprite.
        self.current_sprite = ImageTk.PhotoImage(Image.open(os.path.join('sprite', 'egg-idle', 'sprite-0.png')))
        self.sprite_label = tk.Label(self, image=self.current_sprite, bg=TRANSPARENT)
        self.sprite_label.pack()

    def hatch(self) -> bool:
        """
        Method that check if the egg nedd to be removed or not.
        :return: True if the egg has been removed from the screen, False otherwise.
        """
        if time.time() > self.spawn_time + Egg.DESPAWNING_TIME:
            self.destroy()
            return True

        return False


if __name__ == '__main__':
    print('This script need to be imported to be used.')
