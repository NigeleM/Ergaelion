package main

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

var ansiPattern = regexp.MustCompile(`\x1b\[[0-9;]*m`)

// runWithExport runs a command and saves its text output as Markdown: --export FILE anywhere in the command.
func runWithExport(args []string, games []Game) int {
	index := -1
	for i, a := range args {
		if a == "--export" {
			index = i
			break
		}
	}
	if index < 0 || index+1 >= len(args) {
		fmt.Fprintln(os.Stderr, "error: --export needs a file name")
		return 1
	}
	target := args[index+1]
	command := append(append([]string{}, args[:index]...), args[index+2:]...)

	tmp, err := os.CreateTemp("", "playbook-export-*.txt")
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		return 1
	}
	defer os.Remove(tmp.Name())
	original := os.Stdout
	os.Stdout = tmp
	code := run(command, games)
	os.Stdout = original
	tmp.Close()

	raw, err := os.ReadFile(tmp.Name())
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		return 1
	}
	text := ansiPattern.ReplaceAllString(string(raw), "")
	content := fmt.Sprintf("# playbook %s\n\n```\n%s\n```\n", strings.Join(command, " "), strings.TrimRight(text, "\n"))
	if err := os.WriteFile(filepath.Clean(target), []byte(content), 0o644); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		return 1
	}
	fmt.Println(green("Exported to " + target))
	return code
}
