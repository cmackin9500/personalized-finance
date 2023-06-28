package core

import (
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
)

// @title Overmac API
// @BasePath /api

type Core struct {
	port   int
	router *chi.Mux
}

func CreateCore(port int) *Core {
	router := CreateCoreRouter()

	return &Core{
		port,
		router,
	}
}

// Will need to incorporate TLS or use TLS forwarding in the future
func (core *Core) Start() {
	http.ListenAndServe(":"+strconv.Itoa(core.port), core.router)
}
