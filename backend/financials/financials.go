package financials

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// Returns JSON string with all forms
// for all parsed years
// The current implementation is a rough filesystem
// based approach for storage since everything
// is in development
func GetAllForms(ticker string) ([]byte, error) {
	res := make(map[string]interface{})
	fmt.Println(res)

	// List all files in a company store
	dirname := "store/" + ticker
	files, err := os.ReadDir(dirname)
	if err != nil {
		return nil, fmt.Errorf("Unable to read data from company store. %v", err)
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
