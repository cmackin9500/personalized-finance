package util

import (
	"encoding/json"
	"fmt"
	"net/http"
)

// Automatically sends an error response to the caller and logs
func HTTPErrorHandler(w http.ResponseWriter, r *http.Request, err error, userErr string, code int) {
	body := struct {
		Msg string `json:"msg"`
	}{
		userErr,
	}

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
