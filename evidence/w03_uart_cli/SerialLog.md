S1

set speed 0

OK: speed=0

\> status

SPEED=0

TIMEOUT=10

LED=OFF

CONFIG=DIRTY



S2

set speed 255

OK: speed=255

\> status

SPEED=255

TIMEOUT=10

LED=OFF

CONFIG=DIRTY



S3

\> set speed -1

ERROR: speed out of range

\> status

SPEED=255

TIMEOUT=10

LED=OFF

CONFIG=DIRTY



S4

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set speed 256

OK: speed=255

\> status

SPEED=255

TIMEOUT=10

LED=OFF

CONFIG=DIRTY



S5

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set speed 257

ERROR: unknown command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set speed 300

ERROR: speed out of range

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set speed 1000

ERROR: speed out of range

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set speed 2147483647

ERROR: speed out of range

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set speed 99999999999

ERROR: speed out of range

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED



S6

set timeout 1

OK: timeout=1

\> status

SPEED=120

TIMEOUT=1

LED=OFF

CONFIG=DIRTY

\> set timeout 60

OK: timeout=60

\> status

SPEED=120

TIMEOUT=60

LED=OFF

CONFIG=DIRTY



S7

set timeout 0

OK: timeout=0

\> status

SPEED=120

TIMEOUT=0

LED=OFF

CONFIG=DIRTY

\> set timeout 00

OK: timeout=0

\> status

SPEED=120

TIMEOUT=0

LED=OFF

CONFIG=DIRTY



S8

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set timeout 61

ERROR: timeout out of range

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set timeout -1

ERROR: timeout out of range

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set timeout -5

ERROR: timeout out of range

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED



S9

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set speed

ERROR: invalid speed

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set speed abc

ERROR: invalid speed

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set speed 12abc

ERROR: invalid speed

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set speed 1 2

ERROR: invalid speed

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set timeout x

ERROR: invalid timeout

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED



S10

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> HELP

ERROR: unknown command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> Set Speed 10

ERROR: unknown command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> LED ON

ERROR: unknown command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED



S11

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> STATUS

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED



S12

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> !!!

OK

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> \*\*\*

OK

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> ;;

OK

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> $%^&amp;

OK

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED



S13

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> foo

ERROR: unknown command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> led

ERROR: unknown command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> led blink

ERROR: unknown command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set foo

ERROR: unknown command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> 

ERROR: empty command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED



S14

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

ERROR: unknown command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

ERROR: unknown command

\> 



S15

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> 



S16

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set speed 000000000000000000000000000010

OK: speed=10

\> status

SPEED=10

TIMEOUT=10

LED=OFF

CONFIG=DIRTY

\> 



S17

\> status

SPEED=10

TIMEOUT=10

LED=OFF

CONFIG=DIRTY

\> set speed 50

OK: speed=50

\> status

SPEED=50

TIMEOUT=10

LED=OFF

CONFIG=DIRTY

\> set speed 0000000000000000000000000000010

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> 



S18

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXled on

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> 

OK

\> status

SPEED=120

TIMEOUT=10

LED=ON

CONFIG=SAVED

\> 



S19

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXset speed 200

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> status

ERROR: invalid speed

\> 

ERROR: empty command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set speed 200

OK: speed=200

\> status

SPEED=200

TIMEOUT=10

LED=OFF

CONFIG=DIRTY

\> 



S20

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set

ERROR: unknown command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> 



S21

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set

ERROR: unknown command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set timeout 20

OK: timeout=20

\> status

SPEED=120

TIMEOUT=20

LED=OFF

CONFIG=DIRTY

\> set

\*\*\* SYSTEM FAULT \*\*\*

Reason: parser state mismatch while configuration is dirty

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> 



S22

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> led on

OK

\> status

SPEED=120

TIMEOUT=10

LED=ON

CONFIG=SAVED

\> set

ERROR: unknown command

\> status

SPEED=120

TIMEOUT=10

LED=ON

CONFIG=SAVED

\> 



S23

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> 

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> 

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> 

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> 

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> 

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> 

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> 

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> 

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> 

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> 

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> sta

\*\*\* SYSTEM FAULT \*\*\*

Reason: input line boundary failure

rst:0xc (SW\_CPU\_RESET)

Rebooting...

======================================

 UART CLI HOMEWORK DEVICE v2.0

 READY

======================================

Type 'help'

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> 



S24

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set speed 0

!!!

set speed 5

!!!

set speed 10

!!!

set speed 15

!!!

set speed 20

!!!

set speed 25

!!!

set speed 30

!!!

set speed 35

!!!

set speed 40

!!!

set speed 45

!!!

set speed 50

!!!

set speed 55

!!!

set speed 60

!!!

set speed 65

!!!

set speed 70

!!!

set speed 75

!!!

set speed 80

!!!

set speed 85

!!!

set speed 90

!!!

set speed 95

!!!

set speed 100

!!!

set speed 105

!!!

set speed 110

!!!

set speed 115

!!!

set speed 120

!!!

set speed 125

!!!

set speed 130

!!!

set speed 135

!!!

set speed 140

!!!

set speed 145

!!!

set speed 150

!!!

set speed 155

!!!

set speed 160

!!!

set speed 165

!!!

set speed 170

!!!

set speed 175

!!!

set speed 180

!!!

set speed 185

!!!

set speed 190

!!!

set speed 195

!!!

set speed 200

!!!

set speed 205

!!!

set speed 210

!!!

set speed 215

!!!

set speed 220

!!!

set speed 225

!!!

set speed 230

!!!

set speed 235

!!!

set speed 240

!!!

set speed 245

!!!

statusOK: speed=0

\> OK

\> OK: speed=5

\> OK

\> OK: speed=10

\> OK

\> OK: speed=15

\> OK

\> OK: speed=20

\> OK

\> OK: speed=25

\> OK

\> OK: speed=30

\> OK

\> OK: speed=35

\> OK

\> OK: speed=40

\> OK

\> OK: speed=45

\> OK

\> OK: speed=50

\> OK

\> OK: speed=55

\> OK

\> OK: speed=60

\> OK

\> OK: speed=65

\> OK

\> OK: speed=70

\> OK

\> OK: speed=75

\> OK

\> OK: speed=80

\> OK

\> OK: speed=85

\> OK

\> OK: speed=90

\> OK

\> OK: speed=95

\> OK

\> OK: speed=100

\> OK

\> OK: speed=105

\> OK

\> OK: speed=110

\> OK

\> OK: speed=115

\> OK

\> OK: speed=120

\> OK

\> OK: speed=125

\> OK

\> OK: speed=130

\> OK

\> OK: speed=135

\> OK

\> OK: speed=140

\> OK

\> OK: speed=145

\> OK

\> OK: speed=150

\> OK

\> OK: speed=155

\> OK

\> OK: speed=160

\> OK

\> OK: speed=165

\> OK

\> OK: speed=170

\> OK

\> OK: speed=175

\> OK

\> OK: speed=180

\> OK

\> OK: speed=185

\> OK

\> OK: speed=190

\> OK

\> status

SPEED=190

TIMEOUT=10

LED=OFF

CONFIG=DIRTY

\> 

&nbsp;

S25

status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> set   speed 10

ERROR: unknown command

\> status

SPEED=120

TIMEOUT=10

LED=OFF

CONFIG=SAVED

\> 

&nbsp;
