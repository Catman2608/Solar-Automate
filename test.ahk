SendMode, Input
F5::
	GoSub, StartMacro
	Return

StartMacro:
	ClickPos := 1
	Click, 900, 900
	Loop, 10 {
        Send, %ClickPos%
		Sleep, 1000
		ClickPos += 1
	}
	Return