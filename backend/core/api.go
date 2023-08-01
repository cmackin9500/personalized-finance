package core

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"overmac/webcore/financials"
	"overmac/webcore/util"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	httpSwagger "github.com/swaggo/http-swagger/v2"
)

func WrapRoute(core *Core, route func(http.ResponseWriter, *http.Request, *Core)) func(http.ResponseWriter, *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		route(w, r, core)
	}
}

func WrapMiddleware(core *Core, middleware func(http.Handler, *Core) http.Handler) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return middleware(next, core)
	}
}

func (core *Core) InitializeCoreRouter() {
	core.router.Use(middleware.RequestID)
	core.router.Use(middleware.RealIP)
	core.router.Use(middleware.Logger)
	core.router.Use(WrapMiddleware(core, AuthMiddleware))

	core.router.Get("/", func(w http.ResponseWriter, r *http.Request) {
		// Return svelte index file
		// Right now just shows a debug result
		fmt.Fprintf(w, "Overmac")
	})

	// ========== Swagger section for API documentation ==========
	core.router.Get("/swagger/*", httpSwagger.Handler(
		httpSwagger.URL("http://localhost:8080/swagger.json"), //The url pointing to API definition
	))

	core.router.Get("/swagger.json", func(w http.ResponseWriter, r *http.Request) {
		b, err := os.ReadFile("docs/swagger.json")
		if err != nil {
			log.Println(err)
			return
		}

		w.Write(b)
	})
	// ========== END Swagger section for API documentation ==========

	core.router.Mount("/api", func() *chi.Mux {
		r := chi.NewRouter()

		// Fake route to prevent 404
		r.Post("/userLogin", WrapRoute(core, LoginHandler))

		// Financials sub-route
		// All company data will be accessed through this route
		r.Route("/financials", func(r chi.Router) {
			r.Get("/", func(w http.ResponseWriter, r *http.Request) {
				fmt.Fprintf(w, "Financials API")
			})

			r.Get("/allForms/{ticker}", allFormsHandler)
		})

		// autocomplete route
		r.Get("/tickerAutocomplete", autocompleteAssetHandler)

		return r
	}())
}

// @Description JSON-like structure of data from a financial document
type FinancialForm map[string]interface{}

// @Description Trie data structure with autocomplete information
type TickerTrieNode struct {
	Value      string                    `json:"value"`
	IsTerminal bool                      `json:"isTerminal"`
	Children   map[string]TickerTrieNode `json:"children"`
}

// @Param ticker path string true "Company Ticker"
// @Success 200 {object} map[string]FinancialForm
// @Router /api/financials/allForms/{ticker} [get]
func allFormsHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: Sanitize ticker
	ticker := chi.URLParam(r, "ticker")
	log.Println(ticker)
	formsBytes, err := financials.GetAllForms(ticker)
	if err != nil {
		util.HTTPErrorHandler(w, r, err,
			"Company with requested ticker not found", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(formsBytes)
}

// @Success 200 {object} TickerTrieNode
// @Router /tickerAutocomplete [get]
func autocompleteAssetHandler(w http.ResponseWriter, r *http.Request) {
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
}
