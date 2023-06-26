package core

import (
	"net/http"

	"github.com/go-chi/chi/v5"
)

// @title Overmac API
// @BasePath /api

type Core struct {
	router *chi.Mux
}

func CreateCore() *Core {
	router := CreateCoreRouter()

	return &Core{
		router,
	}
}

func (core *Core) Start() {
	http.ListenAndServe(":8080", core.router)
}
