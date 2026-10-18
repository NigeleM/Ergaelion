package lineedit

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestPlainInputReadsLines(t *testing.T) {
	file := tempInput(t, "first line\nsecond\n")
	defer file.Close()
	var out strings.Builder
	e := New(file, &out)
	line, ok := e.ReadLine("> ")
	if !ok || line != "first line" {
		t.Fatalf("got %q, %v", line, ok)
	}
	line, _ = e.ReadLine("> ")
	if line != "second" {
		t.Fatalf("second line = %q", line)
	}
	if _, ok := e.ReadLine("> "); ok {
		t.Fatal("expected end of input")
	}
}

func TestTabCompletesAUniqueWord(t *testing.T) {
	words := []string{"/show", "/solve", "/sim"}
	complete := func(prefix string) []string {
		var out []string
		for _, w := range words {
			if strings.HasPrefix(w, prefix) {
				out = append(out, w)
			}
		}
		return out
	}
	buf, pos, list := CompleteAt([]rune("/sho"), 4, complete)
	if string(buf) != "/show " || pos != 6 || list != nil {
		t.Fatalf("got %q pos %d list %v", string(buf), pos, list)
	}
}

func TestTabExtendsToCommonPrefixThenListsCandidates(t *testing.T) {
	words := []string{"/solve", "/sim"}
	complete := func(prefix string) []string {
		var out []string
		for _, w := range words {
			if strings.HasPrefix(w, prefix) {
				out = append(out, w)
			}
		}
		return out
	}
	buf, _, list := CompleteAt([]rune("/s"), 2, complete)
	if string(buf) != "/s" || len(list) != 2 {
		t.Fatalf("expected a list of two candidates, got %q %v", string(buf), list)
	}
	buf, _, _ = CompleteAt([]rune("/si"), 3, complete)
	if string(buf) != "/sim " {
		t.Fatalf("got %q", string(buf))
	}
}

func TestHistorySavesAndLoads(t *testing.T) {
	path := filepath.Join(t.TempDir(), "history")
	e := New(os.Stdin, &strings.Builder{})
	e.history = []string{"sim chicken", "advise -d x"}
	if err := e.SaveHistory(path); err != nil {
		t.Fatal(err)
	}
	f := New(os.Stdin, &strings.Builder{})
	if err := f.LoadHistory(path); err != nil {
		t.Fatal(err)
	}
	if len(f.history) != 2 || f.history[0] != "sim chicken" {
		t.Fatalf("history = %v", f.history)
	}
}

func tempInput(t *testing.T, text string) *os.File {
	t.Helper()
	path := filepath.Join(t.TempDir(), "input")
	if err := os.WriteFile(path, []byte(text), 0o644); err != nil {
		t.Fatal(err)
	}
	f, err := os.Open(path)
	if err != nil {
		t.Fatal(err)
	}
	return f
}

func TestTabCompletesAWholePhrase(t *testing.T) {
	phrases := func(text string) []string {
		if strings.HasPrefix("heads or tails", text) && text != "heads or tails" {
			return []string{"heads or tails"}
		}
		return nil
	}
	complete := func(prefix string) []string { return nil }
	buf, pos, list := completeInput([]rune("heads or"), 8, complete, phrases)
	if string(buf) != "heads or tails" || pos != 14 || list != nil {
		t.Fatalf("phrase completion gave %q, %d, %v", string(buf), pos, list)
	}
}

func TestPhraseCompletionFallsBackToWords(t *testing.T) {
	phrases := func(text string) []string { return nil }
	complete := func(prefix string) []string {
		if strings.HasPrefix("tariffs", prefix) {
			return []string{"tariffs"}
		}
		return nil
	}
	buf, _, _ := completeInput([]rune("trade ta"), 8, complete, phrases)
	if string(buf) != "trade tariffs " {
		t.Fatalf("word completion gave %q", string(buf))
	}
}

func TestPhraseCompletionIsSkippedForCommands(t *testing.T) {
	phrases := func(text string) []string { return []string{"/show whatever"} }
	complete := func(prefix string) []string { return nil }
	buf, _, _ := completeInput([]rune("/sho"), 4, complete, phrases)
	if string(buf) != "/sho" {
		t.Fatalf("a command was replaced by a phrase: %q", string(buf))
	}
}
