package main

import (
	"bufio"
	"fmt"
	"informacion_mye/models"
	"os"
	"strings"
)

func main() {
	scanner := bufio.NewScanner(os.Stdin)
	data := readInfo()
	data.EvaluateProblem()

	totalMutualInfo := 0.0
	totalEnthropy := 0.0

	for i := 0; i < len(data.MutualInfo); i++ {
		totalMutualInfo += data.MutualInfo[i]
	}

	for i := 0; i < len(data.Enthropies); i++ {
		totalEnthropy += data.Enthropies[i]
	}

	fmt.Printf("\nLos resultados del problema de %s son:\n", data.DataName)
	fmt.Printf("La información mutua total es: %f\n", totalMutualInfo)
	fmt.Printf("La entropía total es: %f\n", totalEnthropy)

	fmt.Printf("\nIngrese cualquier tecla para continuar")
	scanner.Scan()
}

func readInfo() models.ProblemData {
	scanner := bufio.NewScanner(os.Stdin)
	data := models.ProblemData{}

	fmt.Printf("Ingresa el nombre de los datos a ingresar >> ")

	scanner.Scan()
	dataName := scanner.Text()

	if len(dataName) == 0 {
		panic("Debes ingresar un nombre para los datos")
	}

	data.DataName = dataName

	fmt.Printf("¿Ingresará las probabilidades(P) o las ocurrencias de los eventos(E)? >> ")

	scanner.Scan()
	choice := strings.ToUpper(scanner.Text())

	if choice == "P" {
		data.SetRawPossibilities()
	} else if choice == "E" {
		data.SetPossibilities()
	} else {
		panic("Debes ingresar una opción válida")
	}

	fmt.Println("\n¿Qué tipo de datos son?")
	fmt.Println("\t1.- Cuantificables")
	fmt.Println("\t2.- Transmisión de datos")
	fmt.Println("\t3.- Transiciones de estado")
	fmt.Printf("Ingrese el número correspondiente >> ")

	scanner.Scan()
	dataTypeResponse := scanner.Text()

	switch dataTypeResponse {
	case "1":
		data.DataType = models.Quantificables
	case "2":
		data.DataType = models.DataTransmition
	case "3":
		data.DataType = models.StateTransitions
	default:
		panic("Debes ingresar una opción válida")
	}

	return data
}
