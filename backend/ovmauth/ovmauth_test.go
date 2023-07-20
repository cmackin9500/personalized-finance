package ovmauth

import (
	"fmt"
	"os"
	"testing"
	"time"
)

func TestUserPipeline(t *testing.T) {
	os.RemoveAll("test.db")
	auth, err := CreateAuthManager(AuthManagerConfig{
		60,
		"test.db",
	})

	if err != nil {
		t.Fatalf("Unable to create AuthManager: %v", err)
	}

	err = auth.CreateUser("test1", "mypass", 0)
	if err != nil {
		t.Fatalf("Unable to create user: %v", err)
	}

	creds, err := auth.ValidateCredentials("test1", "mypass")
	if err != nil {
		t.Fatalf("Failed password comparison: %v", err)
	}
	fmt.Println(creds)

	correctUUID := creds.UUID

	creds, err = auth.ValidateCredentials("test1", "fart")
	if err == nil {
		t.Fatalf("Password check passed despite wrong password: %v", err)
	}

	err = auth.DeleteUser(correctUUID)
	if err != nil {
		t.Fatalf("Error occured when deleting user: %v", err)
	}
}

func TestSessionCreationAndValidation(t *testing.T) {
	os.RemoveAll("test.db")
	auth, err := CreateAuthManager(AuthManagerConfig{
		2,
		"test.db",
	})

	if err != nil {
		t.Fatalf("Unable to create AuthManager: %v", err)
	}

	err = auth.CreateUser("test1", "mypass", 0)
	if err != nil {
		t.Fatalf("Unable to create user: %v", err)
	}

	creds, err := auth.ValidateCredentials("test1", "mypass")
	if err != nil {
		t.Fatalf("Error validating credentials: %v", creds)
	}

	sessionToken, err := auth.CreateSession(creds)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}

	userData, err := auth.ValidateSession(sessionToken)
	if err != nil {
		t.Fatalf("Unable to validte session: %v", err)
	}

	if creds.UUID != userData.UUID ||
		creds.Username != userData.Username ||
		creds.Permissions != userData.Permissions {
		t.Fatalf("Retrieved user data is incorrect: %v, %v", creds, userData)
	}

	time.Sleep(3 * time.Second)

	_, err = auth.ValidateSession(sessionToken)
	if err == nil {
		t.Fatalf("Session should be expired but isn't")
	}
}
