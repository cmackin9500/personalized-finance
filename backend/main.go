package main

import (
	"fmt"
	"os"
	"overmac/webcore/core"
)

const disclaimer string = `
================================
Overmac core
Cale Overstreet, Casey MacKinnon
================================`

func main() {
	fmt.Println(disclaimer)
	fmt.Println("Creating necessary directories")
	setupDirs()

	fmt.Println("Creating core instance")
	instance := core.CreateCore(8080)
	fmt.Println("Starting core")
	instance.Start()

	fmt.Println(instance)
}

// Setup necessary directories just in case they aren't present
func setupDirs() {
	panicEarly(os.MkdirAll("store", 0755))
	panicEarly(os.MkdirAll("forms", 0755))
}

func panicEarly(err error) {
	if err != nil {
		panic(fmt.Errorf("Failure to establish proper directory structure. %s", err))
	}
}
