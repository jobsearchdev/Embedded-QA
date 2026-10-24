ets Jul 29 2019 12:21:46

rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
configsip: 0, SPIWP:0xee
clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00
mode:DIO, clock div:2
load:0x3fff0030,len:1156
load:0x40078000,len:11456
ho 0 tail 12 room 4
load:0x40080400,len:2972
entry 0x400805dc

ESP32 BUTTON / INTERRUPT / DEBOUNCE DEMO
----------------------------------------
GPIO18 -> INTERRUPT -> ISR -> DEBOUNCE -> EVENT

Green BUTTON = physical button with bouncing
Red NOISE    = artificial noise input

[SERIAL] Wokwi UART alive

================================
LOGICAL EVENT #1
                Button press ACCEPTED
RAW interrupts total: 59
                        RAW interrupts since previous logical event: 59
                                                                       LOGICAL events total: 1
                                                                                              ACTIONS total: 1
                                                                                                              ACTION executed ONCE
LOGGER: physical press -> RAW -> LOGICAL -> ACTION
================================
[SYSTEM] Critical operation is running...
Button RELEASE accepted

[LOGGER] RAW interrupts: 122 | Logical events: 1 | Actions: 1

================================
LOGICAL EVENT #2
                Button press ACCEPTED
RAW interrupts total: 199
                         RAW interrupts since previous logical event: 140
                                                                         LOGICAL events total: 2
                                                                                                ACTIONS total: 2
                                                                                                                ACTION executed ONCE
LOGGER: physical press -> RAW -> LOGICAL -> ACTION
================================
[SERIAL] Wokwi UART alive
Button RELEASE accepted

================================
LOGICAL EVENT #3
                Button press ACCEPTED
RAW interrupts total: 307
                         RAW interrupts since previous logical event: 108
                                                                         LOGICAL events total: 3
                                                                                                ACTIONS total: 3
                                                                                                                ACTION executed ONCE
LOGGER: physical press -> RAW -> LOGICAL -> ACTION
================================
Button RELEASE accepted
[SERIAL] Wokwi UART alive

[LOGGER] RAW interrupts: 343 | Logical events: 3 | Actions: 3

================================
LOGICAL EVENT #4
                Button press ACCEPTED
RAW interrupts total: 435
                         RAW interrupts since previous logical event: 128
                                                                         LOGICAL events total: 4
                                                                                                ACTIONS total: 4
                                                                                                                ACTION executed ONCE
LOGGER: physical press -> RAW -> LOGICAL -> ACTION
================================
Button RELEASE accepted

================================
LOGICAL EVENT #5
                Button press ACCEPTED
RAW interrupts total: 596
                         RAW interrupts since previous logical event: 161
                                                                         LOGICAL events total: 5
                                                                                                ACTIONS total: 5
                                                                                                                ACTION executed ONCE
LOGGER: physical press -> RAW -> LOGICAL -> ACTION
================================
Button RELEASE accepted
[SERIAL] Wokwi UART alive

[LOGGER] RAW interrupts: 672 | Logical events: 5 | Actions: 5
                                                             [SYSTEM] Critical operation finished.
[SERIAL] Wokwi UART alive