import random

from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from panda3d.core import TextNode, DirectionalLight, PointLight, Spotlight, NodePath, PandaNode

class BombApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.secs_remain = 180
        self.timer_light_on = False
        self.wire_cut = [False] * 7

        self.sound_beep = self.loader.loadSfx("assets/sound/beep.mp3")

        self.font_ssd = self.loader.loadFont("assets/font/seven_segment.ttf")
        self.font_ssd.setPixelsPerUnit(60)

        self.bomb = self.loader.loadModel("assets/model/bomb.bam")
        self.bomb.reparentTo(self.render)
        self.bomb.setPos(0, 7.5, 0)
        self.bomb.setHpr(0, 90, 0)
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

        hold_num_np = self.bomb.find("**/hold.num")
        seq_num_np = self.bomb.find("**/seq.num")
        ss_num_np = self.bomb.find("**/ss.num")
        wire_num_np = self.bomb.find("**/wire.num")
        self.hold_num_text = self.setup_num_display(hold_num_np, 'hold', -0.1, -0.075, 0.5, 90, 270, 90)
        self.seq_num_text = self.setup_num_display(seq_num_np, 'seq', 0.1, -0.075, -0.5, 0, 90, 180)

        self.spotlight = Spotlight("spotlight")
        self.spotlight_np = self.render.attachNewNode(self.spotlight)
        self.spotlight_np.setPos(-4, -4, 4)
        self.spotlight_np.lookAt(self.bomb)
        self.render.setLight(self.spotlight_np)

        self.render.setShaderAuto()

        self.task_blink_colon = self.taskMgr.add(self.blink_colon, "blink_colon", delay=0.5)
        self.task_decr_time = self.taskMgr.add(self.decrement_time, "decrement_time", delay=1)
        self.task_blink_timer_light = self.taskMgr.add(self.blink_timer_light, "blink_light", delay=1)

        self.accept('q', self.rotate_bomb_simon_says)
        self.accept('w', self.rotate_bomb_binary)
        self.accept('e', self.rotate_bomb_wires)
        self.accept('a', self.rotate_bomb_sequence)
        self.accept('s', self.rotate_bomb_timer)
        self.accept('d', self.rotate_bomb_feet)
        for i in range(7):
            self.accept(str(i), self.cut_wire, extraArgs=[i])

        self.rotate_bomb_sequence()

    def setup_num_display(self, disp_np: NodePath, puzzle_name: str, posX, posY, posZ, h, p ,r) -> NodePath:
        disp_text_bg_node = TextNode(f'{puzzle_name}.disp_bg')
        disp_text_bg_node.setText("88")
        disp_text_bg_node.setTextColor(255, 255, 255, 0.3)
        disp_text_bg_node.setFont(self.font_ssd)
        disp_text_bg_np = disp_np.attach_new_node(disp_text_bg_node)
        disp_text_bg_np.setPos(posX, posY, posZ)
        disp_text_bg_np.setHpr(h, p, r)
        disp_text_bg_np.setScale(0.125, 0.125, 0.2)

        disp_text_node = TextNode(f'{puzzle_name}.disp')
        disp_text_node.setText("88")
        disp_text_node.setTextColor(255, 255, 255, 1)
        disp_text_node.setFont(self.font_ssd)
        disp_text_np = disp_np.attach_new_node(disp_text_node)
        disp_text_np.setPos(posX, posY, posZ + 0.1)
        disp_text_np.setHpr(h, p, r)
        disp_text_np.setScale(0.125, 0.125, 0.2)

        return disp_text_node

    def cut_wire(self, wire_idx):
        if not self.wire_cut[wire_idx]:
            direction = 1 if random.random() < 0.5 else -1
            wire_top_np = self.bomb.find(f'**/wire{wire_idx - 1}.top')
            self.set_wire_hpr(wire_top_np, direction)
            self.wire_cut[wire_idx] = True

    def set_wire_hpr(self, wire_np, direction):
            h, p, r = wire_np.getHpr()
            angle = random.randint(18, 25)
            wire_np.setHpr(h + direction * angle, p, r)

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
        self.sound_beep.play()
        return task.again
    
    def blink_timer_light(self, task: Task):
        if not self.timer_light_on:
            self.timer_sphere_np.setLight(self.timer_light_np)
            self.timer_light_on = True
            task.delayTime = 0.5
        else:
            self.timer_sphere_np.setLightOff(self.timer_light_np)
            self.timer_light_on = False
            task.delayTime = 0.5
        return task.again



app = BombApp()
app.run()