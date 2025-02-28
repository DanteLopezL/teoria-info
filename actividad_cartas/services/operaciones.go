package services

import (
	"actividad_cartas/models"
	"fmt"
)

func DistribucionBinomial() (combinaciones float64) {
	k := 2
	eleccionesDisponibles := models.CantidadPaloValores - k

	a := factorial(models.CantidadPaloValores, &k)
	resultadoDivision := float64(a) / float64(k)

	nFormasEleccionQuinta := eleccionesDisponibles * models.NumeroOpcionesPalos
	combinaciones = resultadoDivision * float64(nFormasEleccionQuinta)

	fmt.Printf(`
	Número de cartas a elegir = %d
	Elecciones disponibles = %d
	Formas de elegir la quinta carta = %d
		
	`, k, eleccionesDisponibles, nFormasEleccionQuinta)

	return combinaciones
}

func factorial(valor int, limite *int) (resultado int) {
	resultado = valor
	iteraciones := 1

	for valor > 1 {
		if limite != nil && iteraciones == *limite {
			break
		}

		resultado *= valor - 1
		iteraciones++
	}

	return resultado
}
