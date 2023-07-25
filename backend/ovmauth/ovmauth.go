package ovmauth

import (
	"context"
	"database/sql"
	"fmt"
	"net/http"
	"overmac/webcore/util"
	"time"

	"github.com/google/uuid"
	_ "github.com/mattn/go-sqlite3"
	"golang.org/x/crypto/bcrypt"
)

type AuthManagerConfig struct {
	SessionLifetime int64 // Lifetime in seconds
	DBName          string
}

type AuthManager struct {
	sessionLifetime int64
	userDB          *sql.DB
}

type UserData struct {
	UUID        string
	Username    string
	Permissions uint
}

func CreateAuthManager(conf AuthManagerConfig) (*AuthManager, error) {
	db, err := sql.Open("sqlite3", conf.DBName)
	if err != nil {
		return nil, err
	}

	err = prepareUserDB(db)
	if err != nil {
		return nil, err
	}

	man := &AuthManager{
		sessionLifetime: conf.SessionLifetime,
		userDB:          db,
	}

	//TODO: REMOVE THIS AS IT IS ONLY FOR TESTING
	man.CreateUser("daddy", "dwayne", 0)

	return man, nil
}

func prepareUserDB(db *sql.DB) error {
	_, err := db.Exec(`CREATE TABLE IF NOT EXISTS users(
		uuid text,
		username text, 
		hash blob,
		permissions int
	);

	CREATE TABLE IF NOT EXISTS sessions(
		session_id text,
		uuid text,
		username text,
		permissions int,
		creation_time int
	);
	CREATE TRIGGER IF NOT EXISTS raise_error_if_field_exists
	BEFORE INSERT ON users
	BEGIN
    	SELECT CASE
        	WHEN EXISTS (SELECT 1 FROM users WHERE username=NEW.username) THEN
            	RAISE(ABORT, 'username already exists.')
    	END;
	END;`)

	if err != nil {
		return err
	}

	return err
}

func (man *AuthManager) CreateUser(username string, password string, permissions uint) error {
	hash, err := bcrypt.GenerateFromPassword([]byte(password), 10)
	if err != nil {
		return err
	}

	uuid := uuid.NewString()

	_, err = man.userDB.Exec(`INSERT INTO users VALUES(?, ?, ?, ?)`,
		uuid, username, hash, permissions, username)

	if err != nil {
		return err
	}

	return nil
}

func (man *AuthManager) DeleteUser(uuid string) error {
	_, err := man.userDB.Exec("DELETE FROM users WHERE uuid=?", uuid)
	return err
}

// Returns UserData and a nil error if the credentials are correct.
// Error is non-nil otherwise.
func (man *AuthManager) ValidateCredentials(username string, password string) (UserData, error) {
	var uuid string
	var hash []byte
	var permissions uint

	row := man.userDB.QueryRow("SELECT * FROM users WHERE username=?", username)

	err := row.Scan(&uuid, &username, &hash, &permissions)

	res := bcrypt.CompareHashAndPassword(hash, []byte(password))
	if res != nil {
		return UserData{}, fmt.Errorf("Invalid credentials provided")
	}

	if err != nil {
		return UserData{}, err
	}

	return UserData{
		uuid, username, permissions,
	}, nil
}

func (man *AuthManager) CreateSession(userData UserData) (string, error) {
	uuid := uuid.NewString()
	_, err := man.userDB.Exec("INSERT INTO sessions VALUES(?, ?, ?, ?, ?)",
		uuid, userData.UUID, userData.Username, userData.Permissions, time.Now().Unix())
	return uuid, err
}

func (man *AuthManager) ValidateSession(token string) (UserData, error) {
	row := man.userDB.QueryRow("SELECT * FROM sessions WHERE session_id=?", token)

	var sessionToken string
	var uuid string
	var username string
	var permissions uint
	var creationTime int64

	err := row.Scan(&sessionToken, &uuid, &username, &permissions, &creationTime)
	if err != nil {
		return UserData{}, err
	}

	if time.Now().Unix()-creationTime > man.sessionLifetime {
		// Delete session from database
		man.userDB.Exec("DELETE FROM sessions WHERE session_id=?", token)

		return UserData{}, fmt.Errorf("Session expired")
	}

	return UserData{uuid, username, permissions}, nil
}

func (man *AuthManager) AuthMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {

		fmt.Println(r)

		if r.URL.Path == "/userLogin" || r.URL.Path == "/api/userLogin" {
			// Attempt to validate login
			loginData := struct {
				Username string `json:"username"`
				Password string `json:"password"`
			}{}

			err := util.ReadJSONBody(r, &loginData)

			if err != nil {
				util.HTTPErrorHandler(w, r, err, "No login information provided", 500)
				return
			}

			userData, err := man.ValidateCredentials(loginData.Username, loginData.Password)
			if err != nil {
				util.HTTPErrorHandler(w, r, err, "Invalid credentials provided", 400)
				return
			}

			token, err := man.CreateSession(userData)
			if err != nil {
				util.HTTPErrorHandler(w, r, err, "Unable to create user session", 500)
				return
			}

			http.SetCookie(w, &http.Cookie{
				Name:    "overmacWeb",
				Value:   token,
				Expires: time.Now().Add(time.Duration(man.sessionLifetime) * time.Second),
			})

			fmt.Fprintf(w, "Successfully logged in")

			return
		}

		ctx := context.WithValue(r.Context(), "userData", 1)

		next.ServeHTTP(w, r.WithContext(ctx))
	})
}
