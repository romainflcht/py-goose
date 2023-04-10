from classes import Goose

SPAWN_EGGS = True

if __name__ == '__main__':
    # Start the app.
    app = Goose(SPAWN_EGGS)
    app.loop()
    app.mainloop()
