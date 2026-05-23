; Fisch V11 - Original by AsphaltCake, macOS version by Catman2608
; PyWare Automate: Set playback loops to 0 for infinite playback

; Basic Settings
HoldRodCastDuration := 600
ShakeFailsafeAttempts := 80
ClickScanDelay := 10
Control := 0
; Bar Colors & Tolerances
FishColor := 0x5B4B43
BarColor := 0xFFFFFF
FishBarColorTolerance := 4
WhiteBarColorTolerance := 8
; Bar Areas
ClickShakeLeft := 198
ClickShakeTop := 118
ClickShakeRight := ClickShakeLeft + 1520
ClickShakeBottom := ClickShakeTop + 726
FishBarLeft := 543
FishBarTop := 864
FishBarRight := FishBarLeft + 829
FishBarBottom := FishBarTop + 43
; Auto Calculations
WhiteBarSize := (Control + 0.3) * 777
FishBarTooltipHeight := FishBarBottom + 20
; ==========
F5:: ; Start macro
    SetBatchLines, -1
    SetKeyDelay, -1
    SetMouseDelay, -1
    SetTitleMatchMode, 2
    SendMode, Input
    ; Casting
    Click, down
    Sleep, HoldRodCastDuration
    Click, up

    ; Shaking (navigation only for now)
    StartCaptureThread()
    Loop, %ShakeFailsafeAttempts% {
        PixelSearch, FoundX, FoundY, FishBarLeft, FishBarTop, FishBarRight, FishBarBottom, %FishColor%, %FishBarColorTolerance%, Fast
        if (ErrorLevel = 0) {
            break ; Fish detected - entering minigame
        } else {
            Send, {Enter} ; Shake
        }
        Sleep, %ClickScanDelay%
    }
    StopCaptureThread()

    ; Minigame
    Loop {
        PixelSearch, FishX, FishY, FishBarLeft, FishBarTop, FishBarRight, FishBarBottom, %FishColor%, %FishBarColorTolerance%, Fast
        Restart := ErrorLevel
        if (Restart = 0) {
            ; Continue with minigame
            PixelSearch, BarLeftX, BarY, FishBarLeft, FishBarTop, FishBarRight, FishBarBottom, %BarColor%, %WhiteBarColorTolerance%, Fast
            ; Add arrow tracking based on coordinates
            ; --- Calculate Bar Center ---
            BarCenterX := BarLeftX + (WhiteBarSize / 2)
            BarRightX  := BarLeftX + WhiteBarSize

            ; Tooltips
            Tooltip, <, %BarLeftX%,  %FishBarTooltipHeight%, 18   ; Left bar marker
            Tooltip, >, %BarRightX%, %FishBarTooltipHeight%, 17   ; Right bar marker
            Tooltip, |, %BarCenterX%, %FishBarTooltipHeight%, 16  ; Center bar marker
            Tooltip, +, %FishX%,     %FishBarTooltipHeight%, 19   ; Fish position

            ; --- Compare Fish & Bar Center ---
            if (FishX > BarCenterX) {
                ; Fish is to the right of bar center → Hold click
                Click, down
                Tooltip, Holding Click (Fish > BarCenter), %TooltipX%, %Tooltip10%, 10
            } else {
                ; Fish is left of bar center → Release click
                Click, up
                Tooltip, Releasing Click (Fish < BarCenter), %TooltipX%, %Tooltip10%, 10
            }
        } else {
            break ; Restart (Fish)
        }
    }
    ; Restart
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

