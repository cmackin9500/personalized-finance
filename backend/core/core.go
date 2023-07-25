package core

import (
	"net/http"
	"overmac/webcore/ovmauth"
	"strconv"

	"github.com/go-chi/chi/v5"
)

// @title Overmac API
// @BasePath /api

type Core struct {
	port        int
	router      *chi.Mux
	authManager *ovmauth.AuthManager
}

func CreateCore(port int) *Core {
	router := chi.NewRouter()

	authManager, err := ovmauth.CreateAuthManager(ovmauth.AuthManagerConfig{
		SessionLifetime: 300,
		DBName:          "users.db",
	})

	if err != nil {
		panic(err)
	}

	core := &Core{
		port,
		router,
		authManager,
	}

	// Run initialization functions
	core.InitializeCoreRouter()

	return core
}

// Will need to incorporate TLS or use TLS forwarding in the future
func (core *Core) Start() {
	http.ListenAndServe(":"+strconv.Itoa(core.port), core.router)
}
