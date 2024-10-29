from asyncio import timeout

from pico2d import load_image, get_time

from Drill_08.state_machine import space_down, time_out, right_down, right_up, left_down, \
    left_up, start_event, a_down
from state_machine import StateMachine

#상태를 킄래스 통해서 정의
class Idle:
    @staticmethod # 함수의 기능을 조금 바꿔준다 , 클래스 안에 있는 객체와 상관이 없다.
    def enter(boy,e):
        if left_up(e) or right_down(e):
            boy.action = 2
            boy.face_dir = -1
        elif right_up(e) or left_down(e) or start_event(e):
            boy.action = 3
            boy.face_dir = 1
        boy.dir = 0 # 정지 상태 표현
        boy.frame = 0
        # 현재 시간을 저장
        boy.start_time = get_time()
        pass
    @staticmethod
    def exit(boy,e):
        pass
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time > 3:
            boy.state_machine.add_event(('TIME_OUT',0))
        pass
    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass

class Sleep:
    @staticmethod
    def enter(boy,e):
        pass
    @staticmethod
    def exit(boy,e):
        pass
    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        pass
    @staticmethod
    def draw(boy):
        if boy.face_dir == 1: # 오른쪽 바라보는 상태에서 눕기
            boy.image.clip_composite_draw(
                boy.frame*100,300,100,100,
                3.141592/2,#90도 회전
                '', #좌우상하 반전 x
            boy.x-25,boy.y-25,100,100
            )
        elif boy.face_dir == -1: # 왼쪽 바라보는 상태에서 눕기
            boy.image.clip_composite_draw(
                boy.frame * 100, 200, 100, 100,
                -3.141592 / 2,  # 90도 회전
                '',  # 좌우상하 반전 x
                boy.x + 25, boy.y - 25, 100, 100
            )
        pass
class Run:
    @staticmethod
    def enter(boy,e):
        if right_down(e) or left_up(e):
            boy.dir = 1 # 오른쪽 방향
            boy.action = 1
        elif left_down(e) or right_up(e):
            boy.dir = -1
            boy.action = 0

        boy.frame = 0
        pass
    @staticmethod
    def exit(boy,e):
        pass

    @staticmethod
    def do(boy):
        boy.x += boy.dir * 5
        if boy.x > 800:
            boy.x -= 15
        elif boy.x < 0:
            boy.x += 15
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action*100,100,100,boy.x,boy.y)
        pass

class AutoRun:
    @staticmethod
    def enter(boy,e):
        if a_down(e):
            boy.dir = 1
            boy.action = 1

        boy.frame = 0

        boy.start_run_time = get_time()
        pass

    @staticmethod
    def exit(boy,e):
        pass

    @staticmethod
    def do(boy):
        if boy.x > 800: # 경계에서 좌우 자동으로 바꿈
            boy.dir = -1
            boy.action = 0
        elif boy.x < 0:
            boy.dir = 1
            boy.action = 1
        boy.x += boy.dir * 15
        boy.frame= (boy.frame + 1) % 8
        if get_time() - boy.start_run_time > 5:
            if boy.dir == 1:
                boy.action = 3
                boy.face_dir = 1
            elif boy.dir == -1:
                boy.action = 2
                boy.face_dir = -1
            boy.state_machine.add_event(('TIME_OUT', 0))
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100,100,boy.x,boy.y + 15,150,150)
        pass


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self) # 소년 객체의 statemachine 생성
        self.state_machine.start(Idle) # 초기상태
        self.state_machine.set_transitions({Run : {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle}, # Run 상태에서 어떤 이벤트 들어와도 처리 x
                                            Idle : {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep, a_down: AutoRun},
                                            Sleep : {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle},
                                            AutoRun: {right_down: Run, left_down: Run, right_up: Idle, left_up: Idle, time_out: Idle}
                                            }
                                           )

    def update(self):
        self.state_machine.update()
        #self.frame = (self.frame + 1) % 8

    def handle_event(self, event):
        # event : 입력 이벤트 key mouse
        # 우리가 state_machine에게 전달해줄건 ( , )
        self.state_machine.add_event(('INPUT',event))

    def draw(self):
        self.state_machine.draw()
        #self.image.clip_draw(self.frame * 100, self.action * 100, 100, 100, self.x, self.y)
