//go:build darwin || linux

package lineedit

import (
	"os"
	"syscall"
	"unsafe"
)

// Terminal control for macOS and Linux, using only the standard library.

func ioctlTermios(fd uintptr, request uintptr, t *syscall.Termios) error {
	_, _, errno := syscall.Syscall(syscall.SYS_IOCTL, fd, request, uintptr(unsafe.Pointer(t)))
	if errno != 0 {
		return errno
	}
	return nil
}

// IsTerminal reports whether the file is an interactive terminal.
func IsTerminal(f *os.File) bool {
	var t syscall.Termios
	return ioctlTermios(f.Fd(), getTermios, &t) == nil
}

// makeRaw switches the terminal to character-at-a-time input without echo. It returns a function
// that restores the previous settings.
func makeRaw(f *os.File) (func(), error) {
	var original syscall.Termios
	if err := ioctlTermios(f.Fd(), getTermios, &original); err != nil {
		return nil, err
	}
	raw := original
	raw.Lflag &^= syscall.ECHO | syscall.ICANON | syscall.ISIG | syscall.IEXTEN
	raw.Iflag &^= syscall.ICRNL | syscall.IXON
	raw.Cc[syscall.VMIN] = 1
	raw.Cc[syscall.VTIME] = 0
	if err := ioctlTermios(f.Fd(), setTermios, &raw); err != nil {
		return nil, err
	}
	return func() { ioctlTermios(f.Fd(), setTermios, &original) }, nil
}

// winsize mirrors the C struct returned by TIOCGWINSZ on macOS and Linux.
type winsize struct {
	Row, Col, Xpixel, Ypixel uint16
}

// TerminalRows returns the number of rows the terminal shows, or 24 if it cannot be read.
func TerminalRows(f *os.File) int {
	var ws winsize
	_, _, errno := syscall.Syscall(syscall.SYS_IOCTL, f.Fd(), uintptr(syscall.TIOCGWINSZ), uintptr(unsafe.Pointer(&ws)))
	if errno != 0 || ws.Row == 0 {
		return 24
	}
	return int(ws.Row)
}

// TerminalColumns returns the number of columns the terminal shows, or 80 if it cannot be read.
func TerminalColumns(f *os.File) int {
	var ws winsize
	_, _, errno := syscall.Syscall(syscall.SYS_IOCTL, f.Fd(), uintptr(syscall.TIOCGWINSZ), uintptr(unsafe.Pointer(&ws)))
	if errno != 0 || ws.Col == 0 {
		return 80
	}
	return int(ws.Col)
}
