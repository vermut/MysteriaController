import logging
import random
import threading
import time

import minimalmodbus
import pyglet
from pympler import tracker

tr = tracker.SummaryTracker()

from transitions import Machine
from transitions import State

pyglet.lib.load_library('avbin')
pyglet.have_avbin = True
# pyglet.options['debug_media'] = True

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-10s) %(message)s',
)

window = pyglet.window.Window(width=1280, height=720)
player_main = pyglet.media.Player()


class CleanupSourceGroup(pyglet.media.SourceGroup):
    def _advance(self):
        if self._sources:
            self._timestamp_offset += self._sources[0].duration
            self._dequeued_durations.insert(0, self._sources[0].duration)
            old_source = self._sources.pop(0)
            self.duration -= old_source.duration

            old_source.delete()
            del old_source


v1 = pyglet.media.load("idle/1{}.mp4".format(random.randint(1, 4)))
idle_sourcegroup = CleanupSourceGroup(v1.audio_format, v1.video_format)
del v1

player_of_static = pyglet.media.Player()
player_of_static.queue(pyglet.media.load("static720.avi"))


# noinspection PyMethodMayBeStatic
class StaticState(object):
    def start_distortion(self, dt=None, min_length=0.3):
        pyglet.clock.unschedule(static_state.clear)
        pyglet.clock.schedule_once(static_state.clear, min_length + random.random())
        player_of_static.play()
        logging.debug("Distorting")

        # player_main.pause()

    def stop_distortion(self, dt=None):
        # player_main.play()
        player_of_static.pause()

    def get_player(self):
        if self.is_static():
            return player_of_static

        return player_main


static_state = StaticState()


# noinspection PyMethodMayBeStatic
class VideoState(object):
    # def __init__(self):
    #     player_main.queue(looper_evil)
    #     player_main.play()

    def go_evil(self):
        player_main.queue(idle_sourcegroup)
        player_main.next_source()

    def go_smiling(self):
        player_main.queue(looper_smile)
        player_main.next_source()

    def do_transition(self):
        static_state.distort()
        return True


video_state = VideoState()

# TODO locking!
static_fsm = Machine(
    model=static_state,
    states=[
        State('clean', ignore_invalid_triggers=True),
        State('static', ignore_invalid_triggers=True, on_enter='start_distortion', on_exit='stop_distortion'),
    ],
    initial='clean',
    transitions=[
        {'trigger': 'distort', 'source': 'clean', 'dest': 'static'},
        {'trigger': 'clear', 'source': 'static', 'dest': 'clean'}
    ])

video_fsm = Machine(
    model=video_state,
    states=[
        State('evil', on_enter='go_evil'),
        State('smiling', on_enter='go_smiling'),
    ],
    # before_state_change='do_transition',
    initial='evil',
    transitions=[
        {'trigger': 'play_evil', 'source': '*', 'dest': 'evil'},
        {'trigger': 'play_smiling', 'source': '*', 'dest': 'smiling'},
    ])


@window.event
def on_draw():
    window.clear()

    p = static_state.get_player()

    if p.source and p.source.video_format:
        p.get_texture().blit(0, 0)
    else:
        print("nothing to play")


# @window.event
# def on_mouse_press(x, y, button, modifiers):
#     video_state.play_smiling()
#
#
# @window.event
# def on_mouse_release(x, y, button, modifiers):
#     video_state.play_evil()
#

def auto_distort_main(dt):
    if player_main.source and player_main.time >= player_main.source.duration - 0.4:  # magic timefix number
        static_state.distort(min_length=1)


def add_static(dt):
    if static_state.is_clean() and random.random() < 0.4:
        static_state.distort(min_length=0.1)


################################
@player_main.event('on_eos')
def queue_next_idle_video():
    idle_sourcegroup.queue(pyglet.media.load("idle/{}.mp4".format(random.randint(1, 4))))


player_main.queue(idle_sourcegroup)
queue_next_idle_video()
queue_next_idle_video()

player_main.play()

pyglet.clock.schedule_interval(add_static, 5)
pyglet.clock.schedule_interval(auto_distort_main, 0.1)

system_running = True


def modbus():
    minimalmodbus.BAUDRATE = 57600
    # minimalmodbus.TIMEOUT = 0.5
    instrument = minimalmodbus.Instrument('COM3', 1)  # port name, slave address (in decimal)
    # instrument.debug = True

    a = int(time.time())
    count = 0
    while system_running:
        if a < int(time.time()):
            logging.debug(count)
            count = 0
            a = int(time.time())

        count += 1

        try:
            button1 = instrument.read_registers(0, 4)
        except IOError as e:
            pass
            # print button1

            # instrument.write_register(3, button1, functioncode=6)


t_modbus = threading.Thread(name='modbus', target=modbus)

t_modbus.start()
pyglet.app.run()

# noinspection PyRedeclaration
system_running = False
