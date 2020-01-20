import logging
import threading

from mysteria.my_modbus import ModBus
from mysteria.touchpanel import TouchPanel
from mysteria.state import GameState
from mysteria.web import app as flask, eternal_flask_app

logging.basicConfig(
    level=logging.DEBUG,
    format='(%(threadName)-7s) %(asctime)s [%(name)s] %(message)s',
    datefmt='%M:%S'
)


def main():
    modbus = ModBus(port='COM19')
    touchpanel = TouchPanel()
    flask.game_state = GameState(modbus, touchpanel)
    t_modbus = threading.Thread(name='modbus', target=modbus.processor)
    # t_hud = threading.Thread(name='HUD', target=hud.processor)
    t_touchpanel = threading.Thread(name='touchpanel', target=touchpanel.processor)
    t_flask = threading.Thread(name='flask', target=eternal_flask_app,
                               kwargs={'port': 5555, 'host': '0.0.0.0', 'debug': True, 'use_reloader': False})

    # t_modbus.start()
    # t_touchpanel.start()
    t_flask.start()

    # noinspection PyRedeclaration
    # modbus.running = False


if __name__ == '__main__':
    main()



