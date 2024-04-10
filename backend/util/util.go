package util

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"github.com/rs/zerolog/log"
)

// Automatically sends an error response to the caller and logs
func HTTPErrorHandler(w http.ResponseWriter, r *http.Request, err error, userErr string, code int) {
	body := struct {
		Msg string `json:"msg"`
	}{
		userErr,
	}

	log.Error().
		Err(err).
		Msg("Error in http handler")

	b, err := json.Marshal(&body)
	if err != nil {
		w.WriteHeader(http.StatusInternalServerError)
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"msg": "Unable to process error message correctly"}`)

		return
	}

	w.WriteHeader(code)
	w.Header().Set("Content-Type", "application/json")
	w.Write(b)
	fmt.Println(string(b))
}

func ReadJSONBody(r *http.Request, dest interface{}) error {
	b, err := io.ReadAll(r.Body)
	if err != nil {
		return err
	}

	return json.Unmarshal(b, &dest)
}
