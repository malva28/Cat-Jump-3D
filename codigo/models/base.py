"""
autor: Valentina Garrido
"""

from models.platforms.platform import Platform
from models.staticViewObjects import LoseCG


class Base(Platform):
    def __init__(self):
        self.enable_game_over = False
        width = 2
        depth = 3.2
        height = 0.4
        name = "Base"

        self.bg = None
        self.world_model = None
        self.game_over_cg = None
        self.update_list = None

        self.t = 0.0

        super().__init__(width, depth,height, name)

    def set_bg(self, bg):
        self.bg = bg

    def set_world_model(self, world_model):
        self.world_model = world_model

    def set_update_list(self, update_list):
        self.update_list = update_list

    def update_time(self, dt):
        self.t += dt

    def update_init_pos(self):
        self.set_init_pos(0, 0, -1)
        self.update_translate_matrix()

    def upperCollide(self, cat):
        # print('cat lower lim: {}\nplatform upper lim: {}'.format(cat.lowerLim(), self.upperLim()))
        if cat.lowerLim() <= self.upperLim() + self.delta:
            if cat.might_lose and self.enable_game_over:
                if not cat.game_over:
                    cat.on_game_over()
                    cat.notify_game_lost()
            return True
        return False

    def on_life_reduce(self, mc):
        pass

    def on_game_over(self, mc):
        pass
        #self.disable_drawing()

    #def on_game_over(self):
    #    self.bg.set_game_over_background()
    #    self.game_over_cg = LoseCG()
    #    self.world_model.children += [self.game_over_cg.model]
    #    self.update_list += [self.game_over_cg]


