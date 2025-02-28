package models

import (
	"bufio"
	"fmt"
	"math"
	"os"
	"strconv"
)

type ProblemData struct {
	DataName      string
	Possibilities []float64
	MutualInfo    []float64
	Enthropies    []float64
	DataType      int
}

const (
	Quantificables   = 0
	DataTransmition  = 1
	StateTransitions = 2
)

func (pd *ProblemData) SetPossibilities() {
	scanner := bufio.NewScanner(os.Stdin)
	eventNumber := 1
	events := []int{}
	fmt.Printf("Ingresa las ocurrencias de los eventos (%s), puede pulsar [ENTER] si quiere terminar de registrar los datos\n\n", pd.DataName)

	for {
		fmt.Printf("\tIngrese las ocurrencias del evento %d >> ", eventNumber)
		scanner.Scan()
		inputText := scanner.Text()

		if inputText == "" {
			if eventNumber < 2 {
				fmt.Print("Debes ingresar al menos dos eventos\n\n")
				continue
			}

			break
		}

		value, err := strconv.ParseInt(inputText, 10, 32)

		if err != nil {
			fmt.Print("Ese valor no es númerico, intenta de nuevo\n\n")
			continue
		}

		events = append(events, int(value))

		eventNumber++
	}

	nOcurrances := 0

	for i := 0; i < len(events); i++ {
		nOcurrances += events[i]
	}

	for i := 0; i < len(events); i++ {
		possibiliyValue := float64(events[i]) / float64(nOcurrances)
		pd.Possibilities = append(pd.Possibilities, possibiliyValue)
	}
}

func (pd *ProblemData) SetRawPossibilities() {
	scanner := bufio.NewScanner(os.Stdin)
	eventNumber := 1
	events := []float64{}
	fmt.Printf("Ingresa las probabilidades de los eventos (%s), puede pulsar [ENTER] si quiere terminar de registrar los datos\n\n", pd.DataName)

	for {
		fmt.Printf("\tIngrese la probabilidad del evento %d >> ", eventNumber)
		scanner.Scan()
		inputText := scanner.Text()

		if inputText == "" {

			if eventNumber < 2 {
				fmt.Print("Debes ingresar al menos dos eventos\n\n")
				continue
			}

			break
		}

		value, err := strconv.ParseFloat(inputText, 64)

		if err != nil {
			fmt.Print("Ese valor no es númerico, intenta de nuevo\n\n")
			continue
		}

		events = append(events, value)

		eventNumber++
	}

	pd.Possibilities = events
}

func (pd *ProblemData) evaluateMutualInfo() {
	for i := 0; i < len(pd.Possibilities); i++ {
		var mutualInfo float64

		switch pd.DataType {
		case Quantificables:
			mutualInfo = -math.Log(pd.Possibilities[i])
		case DataTransmition:
			mutualInfo = -math.Log2(pd.Possibilities[i])
		case StateTransitions:
			mutualInfo = -math.Log10(pd.Possibilities[i])
		}
		pd.MutualInfo = append(pd.MutualInfo, mutualInfo)
	}
}

func (pd *ProblemData) evaluateEntropies() {
	for i := 0; i < len(pd.Possibilities); i++ {
		entropy := pd.Possibilities[i] * pd.MutualInfo[i]
		pd.Enthropies = append(pd.Enthropies, entropy)
	}
}

func (pd *ProblemData) EvaluateProblem() {
	pd.evaluateMutualInfo()
	pd.evaluateEntropies()
}
