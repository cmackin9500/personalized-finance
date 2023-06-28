package financials

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/rs/zerolog/log"
)

// Returns JSON string with all forms
// for all parsed years
// The current implementation is a rough filesystem
// based approach for storage since everything
// is in development
func GetAllForms(ticker string) ([]byte, error) {
	res := make(map[string]interface{})
	fmt.Println(res)

	// For now, the "database" is a directory with subdirectories corresponding
	// to stock tickers. Inside are financial forms with year and form type names in
	// a JSON format
	// To query, we list all the files in the directory. If a directory doesn't
	// exist, we try to download files and relist. If this fails, we send the
	// user an error message
	// List all files in a company store

	dirname := "store/" + ticker
	files, err := os.ReadDir(dirname)

	// Check if the error was a NotExist error and try to download missing
	// forms.
	if err != nil {
		if os.IsNotExist(err) {
			// We try to retrieve forms for the company, otherwise we fail
			err := EDGARRetrieveForms(ticker)
			if err != nil {
				return nil, fmt.Errorf("Unable to retrive forms for provided company. %v", err)
			}

			files, _ = os.ReadDir(dirname)
		} else {
			return nil, fmt.Errorf("Unable to read data from company store. %v", err)
		}
	}

	for _, f := range files {
		var temp map[string]interface{}
		name := f.Name()
		date := strings.Split(strings.TrimSuffix(name, filepath.Ext(name)), "_")[2]

		b, err := os.ReadFile(dirname + "/" + name)
		if err != nil {
			return nil, err
		}

		err = json.Unmarshal(b, &temp)
		if err != nil {
			return nil, err
		}

		res[date] = temp
	}

	return json.Marshal(res)
}

func EDGARRetrieveForms(ticker string) error {
	log.Info().
		Str("ticker", ticker).
		Msg("Retrieving company forms")

	cmd := exec.Command("python3", "../edgar/html_process.py", ticker, "10-K", "bs")
	b, err := cmd.Output()

	log.Debug().
		Str("output", string(b)).
		Msg("Output from EDGAR parser")

	if err != nil {
		return fmt.Errorf("%s. %s", err, string(b))
	}

	return nil
}
