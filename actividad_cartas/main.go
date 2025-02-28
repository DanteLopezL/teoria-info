package main

import (
	"actividad_cartas/services"
	"fmt"
)

const (
	enunciado = "¿Cuántas manos diferentes de cinco cartas que contienen dos pares rojos es posible obtener a partir de un deck standard?\n"
)

func main() {
	fmt.Print(enunciado)

	resultado := services.DistribucionBinomial()

	fmt.Printf("El resultado es [%.2f]\n", resultado)
	fmt.Printf("Presione cualquier tecla para continuar...")
	fmt.Scanln()
}
