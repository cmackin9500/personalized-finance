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
		// Return svelte index file
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

		r.Post("/field", func(w http.ResponseWriter, r *http.Request) {
			// Return all values for a given field for a company
			// Need to decode JSON body

			//b, err := io.ReadAll(r.Body)

		})
	})

	r.Get("/tickerAutocomplete", func(w http.ResponseWriter, r *http.Request) {
		// Temporary implementation for Casey to test
		w.Header().Set("Content-Type", "application/json")
		w.Write([]byte(`{
  "A": {
    "isTerminal": false,
    "value": "A",
    "children": {
      "A": {
       	"isTerminal": false,
    	"value": "AA",
    	"children": {
    	  "P": {
    	    "isTerminal": false,
    	    "value": "AAP",
    	    "children": {
    	      "L": {
    	        "isTerminal": true,
    	        "value": "AAPL",
    	        "children": {}
    	      }
    	    }
    	  }
    	}
      }
    }
  }
}`))
	})

	return r
}
