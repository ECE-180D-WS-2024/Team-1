import random

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.interval.IntervalGlobal import Sequence

from panda3d.core import TextNode, PointLight, Spotlight, NodePath

class BombApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # Setup state
        self.secs_remain = 180
        self.timer_light_on = False
        self.wire_cut = [False] * 7
        self.ss_state = {}

        # Setup assets
        self.sound_beep = self.loader.loadSfx("assets/sound/beep.mp3")

        self.font_ssd = self.loader.loadFont("assets/font/seven_segment.ttf")
        self.font_ssd.setPixelsPerUnit(60)

        # Setup scene
        self.bomb = self.loader.loadModel("assets/model/bomb.bam")
        self.bomb.reparentTo(self.render)
        self.bomb.setPos(0, 5.5, 0)
        self.bomb.setHpr(0, 90, 0)

        self.spotlight = Spotlight("spotlight")
        self.spotlight_np = self.render.attachNewNode(self.spotlight)
        self.spotlight_np.setPos(-4, -4, 4)
        self.spotlight_np.lookAt(self.bomb)
        self.render.setLight(self.spotlight_np)
        self.render.setShaderAuto()

        # Setup post-processed components
        self.__setup_timer()
        self.__setup_num_displays()
        self.__setup_simon_says()

        self.__setup_controls()

    def __setup_timer(self):
        timer_node = self.bomb.find("**/timer")
        self.timer_text_node = TextNode(name="timer_text")
        self.timer_text_node.setText("03:00")
        self.timer_text_node.setFont(self.font_ssd)
        self.timer_text_node.setTextColor(255, 0, 0, 1)
        timer_text_bg_node = TextNode(name="timer_text_bg")
        timer_text_bg_node.setText("88:88")
        timer_text_bg_node.setFont(self.font_ssd)
        timer_text_bg_node.setTextColor(255, 0, 0, 0.2)

        timer_text_bg_np = timer_node.attachNewNode(timer_text_bg_node)
        timer_text_bg_np.setPos(-0.1, 0.225, 0.29)
        timer_text_bg_np.setScale(0.125, 0.125, 0.2)
        timer_text_bg_np.setHpr(0, 270, 90)
        
        self.timer_text_np = timer_node.attachNewNode(self.timer_text_node)
        self.timer_text_np.setPos(-0.1, 0.225, 0.3)
        self.timer_text_np.setScale(0.125, 0.125, 0.2)
        self.timer_text_np.setHpr(0, 270, 90)

        self.timer_sphere_np = self.bomb.find("**/timer.led")
        timer_light_node = PointLight("timer_light")
        timer_light_node.setColor((0, 255, 0, 0))
        self.timer_light_np = self.timer_sphere_np.attachNewNode(timer_light_node)
        self.timer_light_np.setPos(0, 0, 0.5)

        self.task_blink_colon = self.taskMgr.add(self.blink_colon, "blink_colon", delay=0.5)
        self.task_decr_time = self.taskMgr.add(self.decrement_time, "decrement_time", delay=1)
        self.task_blink_timer_light = self.taskMgr.add(self.blink_timer_light, "blink_light", delay=1)

    def __setup_num_displays(self):
        def setup_num_display(disp_np: NodePath, puzzle_name: str, posX, posY, posZ, h, p ,r) -> NodePath:
            disp_text_bg_node = TextNode(f'{puzzle_name}.disp_bg')
            disp_text_bg_node.setText("88")
            disp_text_bg_node.setTextColor(255, 255, 255, 0.3)
            disp_text_bg_node.setFont(self.font_ssd)
            disp_text_bg_np = disp_np.attach_new_node(disp_text_bg_node)
            disp_text_bg_np.setPos(posX, posY, posZ)
            disp_text_bg_np.setHpr(h, p, r)
            disp_text_bg_np.setScale(0.125, 0.125, 0.2)

            disp_text_node = TextNode(f'{puzzle_name}.disp')
            disp_text_node.setText("14")
            disp_text_node.setTextColor(255, 255, 255, 1)
            disp_text_node.setFont(self.font_ssd)
            disp_text_np = disp_np.attach_new_node(disp_text_node)
            disp_text_np.setPos(posX, posY, posZ + 0.1)
            disp_text_np.setHpr(h, p, r)
            disp_text_np.setScale(0.125, 0.125, 0.2)

            return disp_text_node
        
        hold_num_np = self.bomb.find("**/hold.num")
        seq_num_np = self.bomb.find("**/seq.num")
        ss_num_np = self.bomb.find("**/ss.num")
        wire_num_np = self.bomb.find("**/wire.num")
        self.hold_num_text = setup_num_display(hold_num_np, 'hold', -0.1, -0.1, 0.5, 90, 270, 90)
        self.seq_num_text = setup_num_display(seq_num_np, 'seq', 0.1, -0.1, -0.5, 0, 90, 180)
        self.ss_num_text = setup_num_display(ss_num_np, 'ss', 0.1, 0.1, -0.5, 0, 90, 270)
        self.wire_num_text = setup_num_display(wire_num_np, 'wire', 0.1, -0.1, 0.5, 180, -90, 90)

    def __setup_controls(self):
        self.accept('q', self.rotate_bomb_simon_says)
        self.accept('w', self.rotate_bomb_binary)
        self.accept('e', self.rotate_bomb_wires)
        self.accept('a', self.rotate_bomb_sequence)
        self.accept('s', self.rotate_bomb_timer)
        self.accept('d', self.rotate_bomb_feet)
        self.accept('r', self.set_ss_light, extraArgs=['red'])
        self.accept('g', self.set_ss_light, extraArgs=['green'])
        self.accept('y', self.set_ss_light, extraArgs=['yellow'])
        self.accept('b', self.set_ss_light, extraArgs=['blue'])
        self.accept('space', self.press_hold_button)
        self.accept('space-up', self.release_hold_button)
        self.accept('i', self.press_sequence_button, extraArgs=[(0, 0), (0.200018, 1.04975, 0.193841)])
        self.accept('o', self.press_sequence_button, extraArgs=[(0, 1), (-0.199982, 1.04975, 0.193841)])
        self.accept('k', self.press_sequence_button, extraArgs=[(1, 0), (0.200018, 1.04975, -0.206159)])
        self.accept('l', self.press_sequence_button, extraArgs=[(1, 1), (-0.199982, 1.04975, -0.206159)])


        for i in range(7):
            self.accept(str(i), self.cut_wire, extraArgs=[i])

    def __setup_simon_says(self):
        def setup_light(color_str, color_vec):
            ss_sphere_np = self.bomb.find(f"**/ss.{color_str}")
            sphere_light_node = PointLight(f"ss.{color_str}_light")
            sphere_light_node.setColor(color_vec)

            sphere_light_np = ss_sphere_np.attachNewNode(sphere_light_node)
            sphere_light_np.setPos(0, 0, 0.5)

            return (ss_sphere_np, sphere_light_np)

        ss_red_nps = setup_light('red', (255, 0, 0, 0))
        ss_green_nps = setup_light('green', (0, 255, 0, 0))
        ss_blue_nps = setup_light('blue', (0, 0, 255, 0))
        ss_yellow_nps = setup_light('yellow', (255, 255, 0, 0))

        self.ss_state['red'] = (*ss_red_nps, False)
        self.ss_state['green'] = (*ss_green_nps, False)
        self.ss_state['blue'] = (*ss_blue_nps, False)
        self.ss_state['yellow'] = (*ss_yellow_nps, False)

    def cut_wire(self, wire_idx):
        if not self.wire_cut[wire_idx]:
            direction = 1 if random.random() < 0.5 else -1
            wire_top_np = self.bomb.find(f'**/wire{wire_idx - 1}.top')
            self.set_wire_hpr(wire_top_np, direction)
            self.wire_cut[wire_idx] = True

    def set_ss_light(self, color_str):
        (ss_sphere_np, sphere_light_np, is_on) = self.ss_state[color_str]
        if not is_on:
            ss_sphere_np.setLight(sphere_light_np)
        else:
            ss_sphere_np.setLightOff(sphere_light_np)
        self.ss_state[color_str] = (ss_sphere_np, sphere_light_np, not is_on)

    def press_sequence_button(self, btn_coord, initial_pos):
        i, j = btn_coord
        x, y, z = initial_pos
        btn = self.bomb.find(f'**/seq.btn{i}{j}')
        btn.ls()
        seq = Sequence(btn.posInterval(0.2, (x, y - 0.1, z)), btn.posInterval(0.2, (x, y, z)))
        seq.start()

    def set_wire_hpr(self, wire_np, direction):
            h, p, r = wire_np.getHpr()
            angle = random.randint(18, 25)
            wire_np.setHpr(h + direction * angle, p, r)

    def press_hold_button(self):
        hold_button = self.bomb.find('**/hold.btn')
        hold_button.posInterval(0.25, (0.011577, -0.463809, 0.506159)).start()

    def release_hold_button(self):
        hold_button = self.bomb.find('**/hold.btn')
        # Magic numbers are from button_np.ls(); they're the original position
        hold_button.posInterval(0.25, (0.011577, -0.463809, 0.606159)).start()

    def rotate_bomb_timer(self):
        self.bomb.hprInterval(0.25, (0, 90, 0)).start()
        pass

    def rotate_bomb_feet(self):
        self.bomb.hprInterval(0.25, (0, -90, 0)).start()
        pass

    def rotate_bomb_simon_says(self):
        self.bomb.hprInterval(0.25, (90, 0, 0)).start()
        pass

    def rotate_bomb_wires(self):
        self.bomb.hprInterval(0.25, (-90, 0, 0)).start()
        pass

    def rotate_bomb_binary(self):
        self.bomb.hprInterval(0.25, (0, 0, 0)).start()
        pass

    def rotate_bomb_sequence(self):
        self.bomb.hprInterval(0.25, (180, 0, 0)).start()
        pass

    def blink_colon(self, task: Task):
        curr_text = self.timer_text_node.getText()
        self.timer_text_node.setText(curr_text.replace(':', ' '))
        task.delayTime = 1
        return task.again

    def decrement_time(self, task: Task):
        self.secs_remain -= 1
        mins = self.secs_remain // 60
        secs = self.secs_remain - (mins * 60)
        mins_str = str(mins).zfill(2)
        secs_str = str(secs).zfill(2)
        self.timer_text_node.setText(f'{mins_str}:{secs_str}')
        return task.again
    
    def blink_timer_light(self, task: Task):
        if not self.timer_light_on:
            self.timer_sphere_np.setLight(self.timer_light_np)
            self.timer_light_on = True
            self.sound_beep.play()
            task.delayTime = 0.5
        else:
            self.timer_sphere_np.setLightOff(self.timer_light_np)
            self.timer_light_on = False
            task.delayTime = 0.5
        return task.again

app = BombApp()
app.run()