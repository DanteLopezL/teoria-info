package main

import (
	"flag"
	"fmt"
	"math/rand"
	"os"
	"strings"
	"time"
)

func main() {

	sampleSize := flag.Int("size", 100, "Size of the sample to generate")
	outFile := flag.String("out", "trajectory-data.txt", "Output file name")

	flag.Parse()

	a := []string{"a", "b", "c", "d", "e"}
	n := len(a)

	rand.Seed(time.Now().UnixNano())

	raw := make([]float64, n)
	sum := 0.0
	for i := range raw {
		raw[i] = rand.Float64()
		sum += raw[i]
	}

	p := make([]float32, n)
	for i := range raw {
		p[i] = float32(raw[i] / sum)
	}

	fmt.Printf("Characters: %v\n", a)
	fmt.Printf("Probabilities: %v\n", p)

	cum := make([]float32, n)
	cum[0] = p[0]
	for i := 1; i < n; i++ {
		cum[i] = cum[i-1] + p[i]
	}

	var sb strings.Builder
	for range *sampleSize {
		r := rand.Float32()
		for j, cp := range cum {
			if r <= cp {
				sb.WriteString(a[j])
				break
			}
		}
	}

	file, err := os.Create(*outFile)
	if err != nil {
		fmt.Println("Error creating file:", err)
		return
	}
	defer file.Close()

	_, err = file.WriteString(sb.String())
	if err != nil {
		fmt.Println("Error writing to file:", err)
		return
	}

	fmt.Printf("Generated string saved to %s\n", *outFile)
}
