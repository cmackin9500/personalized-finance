package core

import (
	"fmt"
	"net/http"
	"overmac/webcore/financials"
	"overmac/webcore/util"

	"github.com/go-chi/chi/v5"
)

type Core struct {
	router *chi.Mux
}

func CreateCore() *Core {
	router := CreateRouter()

	return &Core{
		router,
	}
}

func CreateRouter() *chi.Mux {
	r := chi.NewRouter()

	r.Get("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Overmac")
	})

	r.Mount("/api", apiRouter())

	return r
}

func (core *Core) Start() {
	http.ListenAndServe(":8080", core.router)
}

func apiRouter() http.Handler {
	r := chi.NewRouter()
	r.Route("/financials", func(r chi.Router) {
		r.Get("/", func(w http.ResponseWriter, r *http.Request) {
			fmt.Fprintf(w, "Financials API")
		})

		r.Get("/allForms/{ticker}", func(w http.ResponseWriter, r *http.Request) {
			// TODO: Sanitize ticker
			ticker := chi.URLParam(r, "ticker")
			formsBytes, err := financials.GetAllForms(ticker)
			if err != nil {
				util.HTTPErrorHandler(w, r, err,
					"Company with requested ticker not found", http.StatusInternalServerError)
				return
			}

			w.Header().Set("Content-Type", "application/json")
			w.Write(formsBytes)
		})

	})

	return r
}
