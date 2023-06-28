import board
import digitalio
import supervisor

from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC,make_key
from kmk.scanners import DiodeOrientation

from kmk.modules.encoder import EncoderHandler

from kmk.modules.mouse_keys import MouseKeys
from kmk.modules.sticky_mod import StickyMod

from kmk.handlers.sequences import send_string
from kmk.extensions.media_keys import MediaKeys
from kmk.modules.combos import Combos, Chord
from kmk.modules.layers import Layers
from kmk.modules.holdtap import HoldTap


from kmk.extensions import Extension

__ = False
LED_ON = False
LED_OFF = True
class Leds(Extension):
    def __init__( self ):
        print("In my module ctr")
        self._enabled = True
        L1 = digitalio.DigitalInOut(board.GP11)
        L2 = digitalio.DigitalInOut(board.GP12)
        L3 = digitalio.DigitalInOut(board.GP13)
        L4 = L3  # digitalio.DigitalInOut( board.GP13 ) #bug should be GP14
        L5 = digitalio.DigitalInOut(board.GP15)
        L6 = digitalio.DigitalInOut(board.GP17)
        L7 = digitalio.DigitalInOut(board.GP16)

        leds = [L1, __, L7,
                L2, __, L6,
                L3, L4, L5]

        for led in leds:
            if type(led) != type(__):
                led.direction = digitalio.Direction.OUTPUT
                led.value = LED_OFF
                led.drive_mode = digitalio.DriveMode.OPEN_DRAIN

        self.leds = [led_ for led_ in leds if type(led_) != type(__)]
        self.last_led = 0
        self.last_time = supervisor.ticks_ms()

    def __repr__(self):
        return "MyExt"

    def all(self, on_off = LED_ON ):
        for _ in self.leds:
            _.value = on_off
        return True

    def on(self, idx):
        if idx < len(self.leds):
            self.leds[idx].value = LED_ON
        return True

    def off(self, idx):
        if idx < len(self.leds):
            self.leds[idx].value = LED_OFF
        return True

    def toggle(self, idx):
        if idx < len(self.leds):
            self.leds[idx].value = not self.leds[idx].value
        return True

    def idx_row(self , idx , on_off=LED_ON ):
        if idx == 1:
            for _ in self.leds[:1]:
                _.value = on_off
        elif idx == 2:
            for _ in self.leds[2:3]:
                _.value = on_off
        elif idx == 3:
            for _ in self.leds[4:7]:
                _.value = on_off
        else:
            for _ in self.leds:
                _.value = on_off

        return True

    def last_row(self , on_off=LED_ON):
        return self.idx_row( 3 ,on_off )

    def on_runtime_enable(self, sandbox):
        return

    def on_runtime_disable(self, sandbox):
        return

    def during_bootup(self, sandbox):
        for i in range(4):
             self.leds[i].value = LED_ON

        return

    def before_matrix_scan(self, sandbox):
        if self.last_time + 500 < supervisor.ticks_ms():
            self.toggle(self.last_led % 4)
            self.last_time = supervisor.ticks_ms()
            self.last_led += 1

        return

    def after_matrix_scan(self, sandbox):
        return

    def before_hid_send(self, sandbox):
        return

    def after_hid_send(self, sandbox):
        return

    def on_powersave_enable(self, sandbox):
        return

    def on_powersave_disable(self, sandbox):
        return

'''
def onClick(*args):
    for arg in args:
        print(arg)
    if args[3] is not None:
        leds[ args[3] - 3 ].value = LED_ON
    return True

def onRelease(*args):
    if args[3] is not None:
        _l = leds[ args[3] - 3 ]
        keyboard.set_timeout( 500, lambda _l : _l.value = LED_OFF )

    return True
'''
###############
#### MAIN #####
###############

print("\n\nStarting")

keyboard = KMKKeyboard()

keyboard.col_pins = (board.GP4, board.GP5, board.GP6)
keyboard.row_pins = (board.GP0, board.GP1, board.GP2, board.GP3)
keyboard.diode_orientation = DiodeOrientation.COL2ROW

# leds = LED(led_pin=[board.GP11, board.GP12, board.GP13, board.GP14, board.GP15, board.GP17, board.GP16],brightness=100)
# LED_DEC_1_2 = KC.LED_TOG()

mouse_handler = MouseKeys()
encoder_handler = EncoderHandler()
leds_handler = Leds()
combos = Combos()
holdtap = HoldTap()

keyboard.modules = [ encoder_handler, mouse_handler, StickyMod(), MediaKeys() , Layers()  , combos , holdtap ]
keyboard.extensions.append(leds_handler)

encoder_handler.pins = (
    # regular direction encoder and a button
    (board.GP7, board.GP8, None),  # encoder #1
    # reversed direction encoder with no button handling and divisor of 2
    (board.GP9, board.GP10, None),  # encoder #2
)

Zoom_in = KC.LCTRL(KC.EQUAL)
Zoom_out = KC.LCTRL(KC.MINUS)

encoder_handler.map = [(
                            (KC.VOLU, KC.VOLD),     (KC.MW_UP, KC.MW_DN)        #Layer 1
                        ),
                        (
                            (Zoom_in, Zoom_out),    (KC.LED_INC, KC.LED_DEC)    #Layer 2
                        ),
]  # Standard
_____ = KC.NO

ALT_TAB = KC.SM(kc=KC.TAB, mod=KC.LALT)
#intelij
CTRL_TAB = KC.SM(kc=KC.TAB, mod=KC.LCTRL)

NAV_PREV = KC.LCTRL(KC.LALT(KC.LEFT))
NAV_NEXT = KC.LCTRL(KC.LALT(KC.RIGHT))

RECENT_OPEN_FILES   =  KC.LCTRL(KC.E)

LOCK = KC.LWIN(KC.L)

WECHAT = KC.LCTRL(KC.LALT(KC.W))

COMPILE = KC.LCTRL(KC.LSHIFT(KC.F9))

MIN_ALL = KC.LWIN(KC.M)

SNIP_TOOL = KC.LWIN(KC.LSFT(KC.S))

OPEN_CHROME = KC.RCTRL(KC.C)

TO_LAYER2 = KC.TO(1)
TO_LAYER1 = KC.TO(0)

#indicator of switch layers
TO_LAYER2.before_press_handler(lambda *args: leds_handler.all(LED_OFF) and leds_handler.last_row(LED_ON))
TO_LAYER1.before_press_handler(lambda *args: leds_handler.all(LED_OFF) and  leds_handler.last_row(LED_OFF))

#if hold switch layer , if tap minimize all
MIN_ALL_SW_L2 = KC.HT(MIN_ALL , TO_LAYER2 )
MIN_ALL_SW_L1 = KC.HT(MIN_ALL , TO_LAYER1 )


#combos.combos = [ Chord( ( MIN_ALL , SNIP_TOOL ) , TO_LAYER2 , timeout=500, per_key_timeout=False, fast_reset=False )]

keyboard.keymap = [
    #LAYER1
    [       KC.TRNS,              _____,              KC.TRNS,
            ALT_TAB,              _____,              KC.ENTER,
            CTRL_TAB,             _____,              OPEN_CHROME,
            LOCK,                 MIN_ALL_SW_L2,      SNIP_TOOL
    ]
    ,
    #LAYER2
    [       KC.MB_LMB,            _____,            KC.MB_RMB ,
            CTRL_TAB,             _____,            KC.TRNS,
            NAV_PREV,             _____,            NAV_NEXT,
            RECENT_OPEN_FILES,    MIN_ALL_SW_L1,    SNIP_TOOL
     ]
]

#for keys in keyboard.keymap:
 #   for key in keys:
 #       key.before_press_handler(onClick)
 #       key.before_press_handler(onRelease)

keyboard.debug_enabled = True

#keyboard.set_timeout( 2000 , lambda: my_module.all_off() )
#keyboard.set_timeout( 5000 , lambda: leds_handler.last_row_on() )
#keyboard.set_timeout( 10000 , lambda: my_module.last_row_off() )

print("All setup complete")

if __name__ == '__main__':
    keyboard.go()
