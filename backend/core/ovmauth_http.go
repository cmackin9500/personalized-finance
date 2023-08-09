package core

import (
	"context"
	"fmt"
	"net/http"
	"overmac/webcore/ovmauth"
	"overmac/webcore/util"
	"time"

	"golang.org/x/exp/slices"
)

var WHITELISTED_ROUTES []string = []string{
	"/userlogin", "/api/userLogin",
	"/api/registerUser",
	"/api/verifyEmail",
}

func AuthMiddleware(next http.Handler, core *Core) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if slices.Contains(WHITELISTED_ROUTES, r.URL.Path) {
			next.ServeHTTP(w, r)
			return
		}

		token, err := r.Cookie("overmacWeb")
		if err != nil {
			util.HTTPErrorHandler(w, r, err, "Unable to find user cookie", 400)
			return
		}

		userData, err := core.authMan.ValidateSession(token.Value)
		if err != nil {
			// Session is invalid and we need to expire the cookie
			http.SetCookie(w, &http.Cookie{
				Name:    "overmacWeb",
				Value:   "",
				Expires: time.Unix(0, 0),
			})

			util.HTTPErrorHandler(w, r, err, "Session expired", 400)
			return
		}

		ctx := context.WithValue(r.Context(), "userData", userData)

		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

func LoginHandler(w http.ResponseWriter, r *http.Request, core *Core) {
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

	userData, err := core.authMan.ValidateCredentials(loginData.Username, loginData.Password)
	if err != nil {
		util.HTTPErrorHandler(w, r, err, "Invalid credentials provided", 400)
		return
	}

	token, err := core.authMan.CreateSession(userData)
	if err != nil {
		util.HTTPErrorHandler(w, r, err, "Unable to create user session", 500)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "overmacWeb",
		Value:    token,
		Expires:  time.Now().Add(time.Duration(core.authMan.SessionLifetime) * time.Second),
		HttpOnly: true,
		SameSite: http.SameSiteStrictMode,
	})

	http.SetCookie(w, &http.Cookie{
		Name:     "overmacWebDummy",
		Value:    "isLoggedIn",
		Path:     "/",
		Expires:  time.Now().Add(time.Duration(core.authMan.SessionLifetime) * time.Second),
		HttpOnly: false,
		SameSite: http.SameSiteStrictMode,
	})

	fmt.Fprintf(w, `{"msg": "Successfully logged in"}`)

	return
}

type NewUserData struct {
	Username string `json:"username"`
	Password string `json:"password"`
	Email    string `json:"email"`
}

func CreateUserHandler(w http.ResponseWriter, r *http.Request, core *Core) {
	newUserData := NewUserData{}

	err := util.ReadJSONBody(r, &newUserData)
	if err != nil {
		util.HTTPErrorHandler(w, r, err, "Unable to read submitted user data", 400)
		return
	}

	_, err = core.authMan.CreateUser(newUserData.Username, newUserData.Password, 2, newUserData.Email, false)

	if err != nil {
		util.HTTPErrorHandler(w, r, err, err.Error(), 400)
		return
	}

	userData, err := core.authMan.ValidateCredentials(newUserData.Username, newUserData.Password)
	if err != nil {
		util.HTTPErrorHandler(w, r, err, "Invalid credentials provided", 400)
		return
	}

	token, err := core.authMan.CreateSession(userData)
	if err != nil {
		util.HTTPErrorHandler(w, r, err, "Unable to create user session", 500)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:    "overmacWeb",
		Value:   token,
		Expires: time.Now().Add(time.Duration(core.authMan.SessionLifetime) * time.Second),
	})

	fmt.Fprintf(w, `{"msg": "Successfully logged in"}`)

	return
}

func SendEmailVerificationHandler(w http.ResponseWriter, r *http.Request, core *Core) {
	userData, ok := r.Context().Value("userData").(ovmauth.UserData)

	if !ok {
		util.HTTPErrorHandler(w, r, fmt.Errorf("No user data found in context"), "Unable to verify email", 400)
		return
	}

	fmt.Println(userData)

	token, err := core.authMan.CreateVerificationEntry(userData.UUID)
	if err != nil {
		util.HTTPErrorHandler(w, r, err, "Unable to verify email", 400)
		return
	}
	fmt.Println("TODO:", token)

	// TODO: Actually send email with link and token
	// For now we will just send the verification link in the response

	fmt.Fprintf(w, `{"link": "/api/verifyEmail?verificationToken=%s"}`, token)
}

func VerifyEmailHandler(w http.ResponseWriter, r *http.Request, core *Core) {
	verificationToken := r.URL.Query().Get("verificationToken")

	err := core.authMan.ValidateVerification(verificationToken)
	if err != nil {
		util.HTTPErrorHandler(w, r, err, "Invalid verification link", 400)
		return
	}

	http.Redirect(w, r, "/", http.StatusSeeOther)
}
