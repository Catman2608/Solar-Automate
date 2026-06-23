; Fisch V11 - Original by AsphaltCake, macOS version by Catman2608
; PyWare Automate: Set playback loops to 0 for infinite playback

; Basic Settings
HoldRodCastDuration := 600
ShakeFailsafeAttempts := 80
ClickScanDelay := 80
Control := 0.3
Stabilize := 8
; Bar Colors & Tolerances
FishColor := 0x5B4B43
BarColor := 0xF1F1F1
ArrowColor := 0x878584
FishBarColorTolerance := 4
WhiteBarColorTolerance := 8
; Auto Calculations
WhiteBarSize := (Control + 0.3) * 777
FishBarTooltipHeight := FishBarBottom + 20
OutputDebug, test
; ==========
F5:: ; Start macro
    SetBatchLines, -1
    SetKeyDelay, -1
    SetMouseDelay, -1
    SetTitleMatchMode, 2
    SendMode, Input
    ; Calculations
    ; 409 748
    TooltipX := A_ScreenWidth/20
    Tooltip1 := (A_ScreenHeight/2)-(20*9)
    Tooltip2 := (A_ScreenHeight/2)-(20*8)
    Tooltip3 := (A_ScreenHeight/2)-(20*7)
    Tooltip4 := (A_ScreenHeight/2)-(20*6)
    Tooltip5 := (A_ScreenHeight/2)-(20*5)
    Tooltip6 := (A_ScreenHeight/2)-(20*4)
    Tooltip7 := (A_ScreenHeight/2)-(20*3)
    Tooltip8 := (A_ScreenHeight/2)-(20*2)
    Tooltip9 := (A_ScreenHeight/2)-(20*1)
    Tooltip10 := (A_ScreenHeight/2)
    Tooltip11 := (A_ScreenHeight/2)+(20*1)
    Tooltip12 := (A_ScreenHeight/2)+(20*2)
    Tooltip13 := (A_ScreenHeight/2)+(20*3)
    Tooltip14 := (A_ScreenHeight/2)+(20*4)
    Tooltip15 := (A_ScreenHeight/2)+(20*5)
    Tooltip16 := (A_ScreenHeight/2)+(20*6)
    Tooltip17 := (A_ScreenHeight/2)+(20*7)
    Tooltip18 := (A_ScreenHeight/2)+(20*8)
    Tooltip19 := (A_ScreenHeight/2)+(20*9)
    Tooltip20 := (A_ScreenHeight/2)+(20*10)
    FishBarTooltipHeight := A_ScreenHeight/1.1026

    ClickShakeLeft := A_ScreenWidth/4.6545
    ClickShakeRight := A_ScreenWidth/1.2736
    ClickShakeTop := A_ScreenHeight/9
    ClickShakeBottom := A_ScreenHeight/1.3409

    FishBarLeft := A_ScreenWidth/3.52
    FishBarRight := A_ScreenWidth/1.4317
    FishBarTop := A_ScreenHeight/1.203
    FishBarBottom := A_ScreenHeight/1.1512
    
    tooltip, Made By AsphaltCake, %TooltipX%, %Tooltip1%, 1
    tooltip, Ported to macOS by Catman2608, %TooltipX%, %Tooltip2%, 2
    tooltip, Press "F6" to Reload, %TooltipX%, %Tooltip4%, 4
    tooltip, Press "F7" to Exit, %TooltipX%, %Tooltip5%, 5
    Loop {
        ; Casting
        ToolTip, Action: Casting for %HoldRodCastDuration% seconds, %TooltipX%, %Tooltip6%, 6
        Click, down
        Sleep, %HoldRodCastDuration%
        Click, up

        ; Shaking (navigation only for now)
        StartCaptureThread()
        ToolTip, Action: Shaking, %TooltipX%, %Tooltip6%, 6
        Loop, %ShakeFailsafeAttempts% {
            PixelSearch, FoundX, FoundY, %FishBarLeft%, %FishBarTop%, %FishBarRight%, %FishBarBottom%, %FishColor%, %FishBarColorTolerance%, Fast
            ToolTip, %FoundX% %FoundY%, %TooltipX%, %Tooltip7%, 7
            if (ErrorLevel = 0) {
                break
            } else {
                Send, {Enter} ; Shake
            }
            Sleep, %ClickScanDelay%
        }
        StopCaptureThread()

        ; Minigame
        ToolTip, Action: Playing Bar Minigame, %TooltipX%, %Tooltip6%, 6
        StartCaptureThread()
        deadzone := 0
        LastControlSignal := 0
        LastBarLeft := 0
        Loop {
            PixelSearch, FishX, FishY, %FishBarLeft%, %FishBarTop%, %FishBarRight%, %FishBarBottom%, %FishColor%, %FishBarColorTolerance%, Fast
            Restart := ErrorLevel
            if (Restart = 0) {
                ; Continue with minigame
                PixelSearch, BarLeftX, BarY, %FishBarLeft%, %FishBarTop%, %FishBarRight%, %FishBarBottom%, %BarColor%, %WhiteBarColorTolerance%, Fast
                if (ErrorLevel = 0) {
                    ; --- Calculate Values ---
                    TargetX := BarLeftX + (WhiteBarSize / 2)
                    ControlSignal := TargetX - FishX

                    ; Tooltips
                    Tooltip, Tracking Source: Bars, %TooltipX%, %Tooltip12%, 12
                } else {
                    ; Estimate bar from arrows
                    PixelSearch, BarLeftX, BarY, %FishBarLeft%, %FishBarTop%, %FishBarRight%, %FishBarBottom%, %ArrowColor%, %WhiteBarColorTolerance%, Fast
                    Tooltip, Tracking Source: Arrows, %TooltipX%, %Tooltip12%, 12
                    MouseDown := GetKeyState("LButton", "P")
                    if (MouseDown = 1) {
                        TargetX := BarLeftX - (WhiteBarSize / 2)
                    } else {
                        TargetX := BarLeftX + (WhiteBarSize / 2)
                    }
                    ControlSignal := TargetX - FishX
                }
                ; Tooltips
                Tooltip, Bar Size: %WhiteBarSize%, %TooltipX%, %Tooltip9%, 9
                Tooltip, +, %FishX%,     %FishBarTooltipHeight%, 19   ; Fish position
                deadzone += 1
                if (deadzone = 2) {
                    deadzone := 0
                }

                ; --- Compare Fish & Bar Center ---
                Tooltip, Distance: %ControlSignal%, %TooltipX%, %Tooltip11%, 11
                if (ControlSignal > Stabilize) {
                    ; Fish is to the right of bar center → Hold click
                    Click, up
                    Tooltip, Releasing Click (Fish > BarCenter), %TooltipX%, %Tooltip10%, 10
                    Tooltip, <, %TargetX%, %FishBarTooltipHeight%, 16  ; Center bar marker
                } else if (ControlSignal < -Stabilize){
                    ; Fish is left of bar center → Release click
                    Click, down
                    Tooltip, Holding Click (Fish < BarCenter), %TooltipX%, %Tooltip10%, 10
                    Tooltip, >, %TargetX%, %FishBarTooltipHeight%, 16  ; Center bar marker
                } else {
                    if (deadzone = 0) {
                        Click, up
                    } else {
                        Click, down
                    }
                    Tooltip, Stabilizing, %TooltipX%, %Tooltip10%, 10
                    Tooltip, ., %TargetX%, %FishBarTooltipHeight%, 16  ; Center bar marker
                }
            } else {
                break ; Restart (Fish)
            }
            Sleep, 10
        }
        Sleep, 1500
        StopCaptureThread()
        ; Restart
    }
return

F7::
    ExitApp
return
; --- PyWare Compatibility Layer ---
StartCaptureThread() {
    return
}

StopCaptureThread() {
    return
}
; ---------------------------------

