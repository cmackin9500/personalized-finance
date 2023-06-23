package main

import (
	"fmt"
	"overmac/webcore/core"
)

func main() {
	instance := core.CreateCore()
	instance.Start()

	fmt.Println(instance)
}
